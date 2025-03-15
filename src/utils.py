from enum import Enum
import logging
from typing import List, Dict
import json
import os
from constants import ROOM_ORDER, CHORE_DATA_FILE_NAME, ROOM_ASSIGNMENTS_FILE_NAME, REGISTRATION_REQUESTS_FILE_NAME, PENALTY_LOG_FILE_NAME, ROLES_FILE_NAME, SHOPPING_LIST_FILE_NAME, TELL_TO_SEND_PRIVATE_MESSAGE
from datetime import datetime
import csv


class UserRole(Enum):
    """Enumeration of all possible user roles in the dormitory."""
    ADMIN = 0
    WOHNHEIMSSPRECHER = 1

class ChoreType(Enum):
    """Enumeration of all possible chore types in the dormitory.
    
    Each chore type represents a specific task that needs to be done.
    The FREI type indicates no chore assignment for that slot.
    """
    EINKAUFSDIENST = 0
    MUELLDIENST = 1
    GETRAENKE = 2
    KUECHE = 3
    MASCHINEN = 4
    GESCHIRRTUECHER = 5
    FREI = 6

    def __str__(self):
        """Convert chore type to its German display name."""
        return {
            ChoreType.EINKAUFSDIENST: "Einkaufsdienst",
            ChoreType.MUELLDIENST: "Mülldienst",
            ChoreType.GETRAENKE: "Getränkedienst",
            ChoreType.KUECHE: "Küchendienst",
            ChoreType.MASCHINEN: "Maschinendienst",
            ChoreType.GESCHIRRTUECHER: "Geschirrtücher",
            ChoreType.FREI: "Frei"
        }[self]


class DueDay(Enum):
    """Enumeration of weekdays when chores are due.
    
    Includes a special NONE value for FREI chores that have no due date.
    Values 0-6 correspond to Monday through Sunday.
    """
    MO = 0
    DI = 1
    MI = 2
    DO = 3
    FR = 4
    SA = 5
    SO = 6
    NONE = 7

    def __str__(self):
        """Convert weekday to its German display name."""
        return {
            DueDay.MO: "Montag",
            DueDay.DI: "Dienstag",
            DueDay.MI: "Mittwoch",
            DueDay.DO: "Donnerstag",
            DueDay.FR: "Freitag",
            DueDay.SA: "Samstag",
            DueDay.SO: "Sonntag",
            DueDay.NONE: "Kein Tag"
        }[self]


class Chore:
    """Represents a single chore with its type and due day.
    
    Attributes:
        type (ChoreType): The type of chore to be done
        due (DueDay): The weekday when the chore should be completed
    """
    def __init__(self, type: ChoreType, due: DueDay):
        self.type = type
        self.due = due

    def __dict__(self):
        """Convert chore to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "due": self.due.value
        }

    def to_dict(self):
        """Alias for __dict__ for explicit serialization calls."""
        return self.__dict__()

    @staticmethod
    def from_dict(dict: dict):
        """Create a Chore instance from a dictionary.
        
        Args:
            dict (dict): Dictionary containing 'type' and 'due' values
            
        Returns:
            Chore: New Chore instance with the specified values
        """
        return Chore(ChoreType(dict["type"]), DueDay(dict["due"]))

    def __str__(self):
        """Create a human-readable string representation of the chore."""
        if self.type == ChoreType.FREI:
            return "Frei"
        return f"{self.type} (fällig {self.due})"


class ChoreStatus:
    """Represents the status of a chore assignment for a specific room.
    
    Attributes:
        completed (bool): Whether the chore has been marked as done
        assigned_to_room (int): Room number this chore is assigned to
        chore (Chore): The actual chore that needs to be done
    """
    def __init__(self, completed: bool, assigned_to_room: int, chore: Chore):
        self.completed = completed
        self.assigned_to_room = assigned_to_room
        self.chore = chore

    def with_completed(self):
        """Create a new ChoreStatus instance with completed=True.
        
        Returns:
            ChoreStatus: New instance with same attributes but marked as completed
        """
        return ChoreStatus(True, self.assigned_to_room, self.chore)

    def __dict__(self):
        """Convert chore status to dictionary for JSON serialization."""
        return {
            "completed": self.completed,
            "assigned_to_room": self.assigned_to_room,
            "chore": self.chore.to_dict()
        }

    def to_dict(self):
        """Alias for __dict__ for explicit serialization calls."""
        return self.__dict__()

    @staticmethod
    def from_dict(dict: dict):
        """Create a ChoreStatus instance from a dictionary.
        
        Args:
            dict (dict): Dictionary containing status information
            
        Returns:
            ChoreStatus: New ChoreStatus instance with the specified values
        """
        return ChoreStatus(dict["completed"], dict["assigned_to_room"], Chore.from_dict(dict["chore"]))

    def __str__(self):
        """Create a human-readable string representation of the chore status."""
        status = "✅" if self.completed or self.chore.type == ChoreType.FREI else "❌"
        return f"Zimmer {self.assigned_to_room}: {self.chore} {status}"

CHORES = [
    Chore(ChoreType.EINKAUFSDIENST, DueDay.SO),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.MUELLDIENST, DueDay.DI),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.MUELLDIENST, DueDay.FR),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.GETRAENKE, DueDay.SO),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.KUECHE, DueDay.DI),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.KUECHE, DueDay.SA),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.GESCHIRRTUECHER, DueDay.SO),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.MUELLDIENST, DueDay.SO),
    Chore(ChoreType.FREI, DueDay.NONE)
]

class ChoreInformation:
    """Container for all chore statuses in a given week.
    
    Attributes:
        chore_states (List[ChoreStatus]): List of all chore assignments and their status
    """
    def __init__(self, chore_states: List[ChoreStatus]):
        self.chore_states = chore_states

    def with_completed(self, room_number: int):
        """Create a new list of chore states with one room's chore marked as completed.
        
        Args:
            room_number (int): The room number whose chore should be marked completed
            
        Returns:
            List[ChoreStatus]: New list with the specified room's chore marked as completed
        """
        return ChoreInformation([chore.with_completed() if chore.assigned_to_room == room_number else chore for chore in self.chore_states])

    def with_completed_all(self):
        """Create a new list of chore states with all chores marked as completed."""
        return ChoreInformation([chore.with_completed() for chore in self.chore_states])

    def __dict__(self):
        """Convert all chore information to dictionary for JSON serialization."""
        return {
            "chore_states": [chore.to_dict() for chore in self.chore_states]
        }

    def to_dict(self):
        """Alias for __dict__ for explicit serialization calls."""
        return self.__dict__()

    @staticmethod
    def from_dict(dict: dict):
        """Create a ChoreInformation instance from a dictionary.
        
        Args:
            dict (dict): Dictionary containing chore states
            
        Returns:
            ChoreInformation: New instance with the specified chore states
        """
        return ChoreInformation([ChoreStatus.from_dict(chore) for chore in dict["chore_states"]])

    def __str__(self):
        """Create a human-readable string representation of all chore statuses."""
        return "\n".join([str(chore_status) for chore_status in self.chore_states])


def save_chore_data(data: ChoreInformation):
    """Save chore information to JSON file.
    
    Args:
        data (ChoreInformation): The chore data to save
    """
    with open(CHORE_DATA_FILE_NAME, "w") as f:
        json.dump(data.to_dict(), f)


def load_chore_data() -> ChoreInformation:
    """Load chore information from JSON file.
    
    Returns:
        ChoreInformation: The loaded chore data
        
    Raises:
        FileNotFoundError: If the chore data file doesn't exist
    """
    with open(CHORE_DATA_FILE_NAME, "r") as f:
        return ChoreInformation.from_dict(json.load(f))


def save_room_assignments(assignments: Dict[str, int]):
    """Save user ID to room number mappings to JSON file.
    
    Args:
        assignments (Dict[str, int]): Dictionary mapping user IDs to room numbers
    """
    with open(ROOM_ASSIGNMENTS_FILE_NAME, "w") as f:
        json.dump(assignments, f)


def load_room_assignments() -> Dict[str, int]:
    """Load user ID to room number mappings from JSON file.
    
    Returns:
        Dict[str, int]: Dictionary mapping user IDs to room numbers
    """
    try:
        with open(ROOM_ASSIGNMENTS_FILE_NAME, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def get_user_room(user_id: str) -> int:
    """Get the room number assigned to a specific user.
    
    Args:
        user_id (str): Telegram user ID
        
    Returns:
        int: Assigned room number
        
    Raises:
        KeyError: If the user is not assigned to any room
        FileNotFoundError: If the room assignments file doesn't exist
    """
    assignments = load_room_assignments()
    if str(user_id) not in assignments:
        raise KeyError(f"User {user_id} not assigned to any room")
    return assignments[str(user_id)]


def get_room_assignments_reversed() -> Dict[int, str]:
    """Get room number to user ID mappings.
    
    Returns:
        Dict[int, str]: Dictionary mapping room numbers to user IDs
    """
    assignments = load_room_assignments()
    return {v: k for k, v in assignments.items()}


def save_registration_requests(requests: Dict[str, int]):
    """Save pending room registration requests to JSON file.
    
    Args:
        requests (Dict[str, int]): Dictionary mapping user IDs to requested room numbers
    """
    with open(REGISTRATION_REQUESTS_FILE_NAME, "w") as f:
        json.dump(requests, f)


def load_registration_requests() -> Dict[str, int]:
    """Load pending room registration requests from JSON file.
    
    Returns:
        Dict[str, int]: Dictionary mapping user IDs to requested room numbers
    """
    try:
        with open(REGISTRATION_REQUESTS_FILE_NAME, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def add_registration_request(user_id: str, room_number: int) -> bool:
    """Add a new room registration request.
    
    Args:
        user_id (str): Telegram user ID requesting the room
        room_number (int): Requested room number
        
    Returns:
        bool: False if room already has a pending request, True if request was added
    """
    requests = load_registration_requests()
    
    # Check if room already has a pending request
    if any(room == room_number for room in requests.values()):
        return False
    
    requests[user_id] = room_number
    save_registration_requests(requests)
    return True


def generate_chore_data_week_start(week_number: int):
    """Generate new chore assignments for a given week.
    
    Rotates the room assignments based on the week number to ensure
    fair distribution of chores over time.
    
    Args:
        week_number (int): ISO week number to generate assignments for
        
    Returns:
        ChoreInformation: New chore assignments for the week
    """
    # Calculate offset based on week number
    offset = -(week_number % len(ROOM_ORDER))
    
    # Rotate room order by offset
    rotated_rooms = ROOM_ORDER[offset:] + ROOM_ORDER[:offset]
    
    # Create ChoreStatus objects pairing each chore with a room
    chore_states = []
    for chore, room in zip(CHORES, rotated_rooms):
        chore_states.append(ChoreStatus(False, room, chore))
        
    return ChoreInformation(chore_states)


def remove_room_assignment(user_id: str) -> tuple[bool, int]:
    """Remove a user's room assignment.
    
    Args:
        user_id (str): Telegram user ID to remove
        
    Returns:
        tuple[bool, int]: (success, room_number if success else 0)
    """
    assignments = load_room_assignments()
    user_id_str = str(user_id)
    
    if user_id_str not in assignments:
        return False, 0
        
    room_number = assignments[user_id_str]
    del assignments[user_id_str]
    save_room_assignments(assignments)
    return True, room_number


def save_penalty_log(penalties: List[ChoreStatus]):
    """Save penalty entries to a CSV file.
    
    Creates the CSV file if it doesn't exist and appends new penalties.
    Each entry includes the date, room number, chore type, and due day.
    
    Args:
        penalties (List[ChoreStatus]): List of incomplete chores to log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Create CSV file if it doesn't exist and write headers
    try:
        with open(PENALTY_LOG_FILE_NAME, "x", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Room", "Chore", "DueDay"])
    except FileExistsError:
        pass
    
    # Append new penalties
    with open(PENALTY_LOG_FILE_NAME, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for chore in penalties:
            writer.writerow([
                timestamp,
                chore.assigned_to_room,
                str(chore.chore.type),
                str(chore.chore.due)
            ])


def get_incomplete_chores(data: ChoreInformation) -> List[ChoreStatus]:
    """Get all incomplete chores that aren't 'FREI'.
    
    Args:
        data (ChoreInformation): Current chore assignments
        
    Returns:
        List[ChoreStatus]: List of incomplete, non-FREI chores
    """
    return [
        chore for chore in data.chore_states 
        if not chore.completed 
        and chore.chore.type != ChoreType.FREI
    ]


def load_user_roles() -> Dict[str, UserRole]:
    """Load user role assignments from JSON file.
    
    Returns:
        Dict[str, UserRole]: Dictionary mapping user IDs to their roles
    """
    try:
        with open(ROLES_FILE_NAME, "r") as f:
            role_data = json.load(f)
            # Convert the stored integer values back to UserRole enum
            res = {k: UserRole(v) for k, v in role_data.items()}
            if os.getenv("ADMIN_USER_ID"):
                res[os.getenv("ADMIN_USER_ID")] = UserRole.ADMIN
            return res
    except FileNotFoundError:
        if os.getenv("ADMIN_USER_ID"):
            return {os.getenv("ADMIN_USER_ID"): UserRole.ADMIN}
        else:
            return {}

def get_user_role(user_id: str) -> UserRole | None:
    """Get the role assigned to a specific user.
    
    Args:
        user_id (str): Telegram user ID
        
    Returns:
        UserRole | None: The user's role if assigned, None otherwise
    """
    roles = load_user_roles()
    return UserRole(roles[str(user_id)]) if str(user_id) in roles else None

def set_user_role(user_id: str, role: UserRole | None):
    """Set the role for a specific user.
    
    Args:
        user_id (str): Telegram user ID
        role (UserRole): The role to set for the user
    """
    roles = load_user_roles()
    if role is None:
        del roles[str(user_id)]
    else:
        roles[str(user_id)] = role
    save_user_roles(roles)

def save_user_roles(roles: Dict[str, UserRole]):
    """Save user role assignments to JSON file.
    
    Args:
        roles (Dict[str, UserRole]): Dictionary mapping user IDs to their roles
    """
    # Convert UserRole enum to integer for JSON serialization
    role_data = {k: v.value for k, v in roles.items()}
    with open(ROLES_FILE_NAME, "w") as f:
        json.dump(role_data, f)

def add_to_shopping_list(item: str):
    """Add an item to the shopping list.
    
    Args:
        item (str): The item to add to the shopping list
    """
    shopping_list = load_shopping_list()
    shopping_list.append(item)
    save_shopping_list(shopping_list)

def clear_shopping_list():
    """Clear the shopping list.
    """
    with open(SHOPPING_LIST_FILE_NAME, "w") as f:
        json.dump([], f)

def load_shopping_list() -> List[str]:
    """Load the shopping list from the JSON file.
    
    Returns:
        List[str]: The shopping list
    """
    try:
        with open(SHOPPING_LIST_FILE_NAME, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_shopping_list(shopping_list: List[str]):
    """Save the shopping list to the JSON file.
    
    Args:
        shopping_list (List[str]): The shopping list to save
    """
    with open(SHOPPING_LIST_FILE_NAME, "w+") as f:
        json.dump(shopping_list, f)

def censor_in_groups(func):

    async def wrapper(*args, **kwargs):
        try:
            update, context = args
            chat_id = update.effective_chat.id
            user_id = update.effective_user.id
            user_role = get_user_role(user_id)
        except:
            return await func(*args, **kwargs)
        
        if chat_id < 0 and user_role != UserRole.ADMIN and user_role != UserRole.WOHNHEIMSSPRECHER:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            await context.bot.send_message(chat_id=user_id, text=TELL_TO_SEND_PRIVATE_MESSAGE)
            return

        return await func(*args, **kwargs)

    return wrapper
