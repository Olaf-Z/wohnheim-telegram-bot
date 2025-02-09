from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from telegram.ext import Updater
from datetime import datetime, time
import os
import logging
import logging.config
from pathlib import Path
from utils import (ChoreType, DueDay, ChoreInformation,
                       load_chore_data, save_chore_data,
                       get_user_room, get_room_assignments_reversed, add_registration_request,
                       remove_room_assignment, generate_chore_data_week_start, get_incomplete_chores,
                       save_penalty_log, get_user_role, UserRole, load_registration_requests,
                       save_room_assignments, load_room_assignments)
import constants as constants

# Set up logging from config file
def setup_logging():
    """Setup logging configuration from .conf file"""
    config_path = Path(__file__).parent.parent / 'logging.conf'
    
    if config_path.exists():
        # Set up the log file path
        data_dir = os.getenv('DATA_FILE_DIRECTORY', 'data')
        os.makedirs(data_dir, exist_ok=True)
        log_file = os.path.join(data_dir, 'bot.log')
        
        # Configure logging with the .conf file
        logging.config.fileConfig(
            config_path,
            defaults={'logfilepath': log_file},
            disable_existing_loggers=False
        )
    else:
        # Fallback configuration if conf file is not found
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        logging.warning(f"Logging config not found at {config_path}, using basic configuration")

# Initialize logging before anything else
setup_logging()

# Time to send reminders (24h format)
REMINDER_TIME = time(hour=10, minute=0)  # 10:00 AM


def get_week_number() -> int:
    """Get the current ISO week number.

    Returns:
        int: Current ISO week number (1-53)
    """
    return datetime.now().isocalendar()[1]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command by sending a welcome message.

    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    logging.info(f"User {update.effective_user.id} started the bot")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=constants.START_MESSAGE
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /hilfe command by sending a list of available commands.

    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    logging.info(f"User {update.effective_user.id} requested help")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=constants.HELP_TEXT
    )


async def show_chores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /aufgaben command by showing all chores for the current week.

    Displays a list of all rooms with their assigned chores and completion status.

    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    logging.info(f"User {update.effective_user.id} requested chores")
    data = load_chore_data()
    message = "Aufgaben dieser Woche:\n\n"
    message += str(data)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


async def mark_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /erledigt command by marking the user's chore as completed.

    Finds the user's room number, then marks their assigned chore as completed.
    Handles various error cases like unassigned rooms or already completed chores.

    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    logging.info(f"User {update.effective_user.id} marked a chore as done")
    data = load_chore_data()
    user_id = update.effective_user.id

    try:
        room_number = get_user_room(str(user_id))
    except FileNotFoundError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.ERROR_ROOM_ASSIGNMENTS
        )
        return
    except KeyError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.ERROR_NO_ROOM
        )
        return

    # Find the chore assigned to this user's room
    user_chore = None
    for chore in data.chore_states:
        if chore.assigned_to_room == room_number:
            user_chore = chore
            break

    if user_chore is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.ERROR_ROOM_NOT_FOUND
        )
        return

    if user_chore.completed:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.ERROR_ALREADY_COMPLETED
        )
        return
    if user_chore.chore.type == ChoreType.FREI:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.FREE_WEEK_MESSAGE
        )
        return

    # Mark the chore as completed
    data = data.with_completed(room_number)
    save_chore_data(data)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=constants.TASK_COMPLETED.format(user_chore.chore)
    )


async def send_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: str, message: str):
    """Send a reminder message to a specific user.

    Handles errors that might occur during message sending and logs them.

    Args:
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
        user_id (str): Telegram user ID to send the message to
        message (str): The message text to send
    """
    logging.info(f"Sending reminder to {user_id}")
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=message
        )
    except Exception as e:
        logging.error(f"Failed to send reminder to {user_id}: {e}")


async def rotate_chores(context: ContextTypes.DEFAULT_TYPE):
    """Generate new chore assignments for the week and handle penalties.

    This function runs every Monday at 3:00 AM and:
    1. Checks for incomplete chores from last week
    2. Logs penalties to CSV file
    3. Notifies users who didn't complete their chores
    4. Generates and saves new chore assignments

    Args:
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    try:
        logging.info("Starting weekly chore rotation")
        
        # Check for incomplete chores before rotating
        old_data = load_chore_data()
        incomplete_chores = get_incomplete_chores(old_data)

        if incomplete_chores:
            logging.info(f"Found {len(incomplete_chores)} incomplete chores")
            # Save to CSV log file
            save_penalty_log(incomplete_chores)

            # Get user mappings for notifications
            user_by_room = get_room_assignments_reversed()

            # Notify users with incomplete chores
            for chore in incomplete_chores:
                user_id = user_by_room.get(chore.assigned_to_room)
                if user_id:
                    logging.info(f"Sending penalty notification to room {chore.assigned_to_room}")
                    message = constants.PENALTY_NOTIFICATION.format(chore.chore)
                    await send_reminder(context, user_id, message)

            # Generate message for console/admin
            penalties = [
                constants.PENALTY_LOG_ENTRY.format(
                    chore.assigned_to_room,
                    chore.chore.type,
                    chore.chore.due
                ) for chore in incomplete_chores
            ]
            penalty_message = constants.PENALTY_LOG_HEADER + \
                "\n" + "\n".join(penalties)
            # You can add admin notification here if desired:
            # await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=penalty_message)

            print(
                f"Logged {len(incomplete_chores)} penalties for week {get_week_number()-1}")

        # Generate new chore assignments
        week_number = get_week_number()
        data = generate_chore_data_week_start(week_number)
        save_chore_data(data)
        logging.info(f"Successfully rotated chores for week {week_number}")

    except Exception as e:
        logging.error(f"Error in chore rotation: {e}", exc_info=True)


async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Send reminder messages to users about their chores.

    This function runs daily at 10:00 AM and:
    1. On Mondays: Sends everyone their chore for the week
    2. Other days: Sends reminders to users who have chores due tomorrow

    Args:
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    try:
        logging.info("Starting daily reminder check")
        data = load_chore_data()
        user_by_room = get_room_assignments_reversed()

        today = datetime.now()
        weekday = today.weekday()

        logging.info(f"Processing reminders for {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][weekday]}")

        # Convert to DueDay enum
        today_due = DueDay(weekday)
        tomorrow_due = DueDay((weekday + 1) % 7)

        reminder_count = 0
        for chore_status in data.chore_states:
            if chore_status.chore.type != ChoreType.FREI:
                user_id = user_by_room.get(chore_status.assigned_to_room)
                if user_id:
                    if weekday == 0:
                        message = constants.WEEKLY_REMINDER.format(chore_status.chore)
                        await send_reminder(context, user_id, message)
                        reminder_count += 1

                    if (not chore_status.completed and
                            chore_status.chore.due >= tomorrow_due):
                        message = constants.DAILY_REMINDER.format(chore_status.chore)
                        await send_reminder(context, user_id, message)
                        reminder_count += 1

        logging.info(f"Sent {reminder_count} reminders")

    except Exception as e:
        logging.error(f"Error in reminder job: {e}", exc_info=True)


async def move_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /movein command for new residents.

    Creates a registration request for a room that needs to be approved by an admin.
    Validates the room number and checks for existing requests.

    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback

    Usage:
        /movein <room_number>
    """
    user_id = update.effective_user.id
    logging.info(f"User {user_id} attempting to move in")
    
    if not context.args:
        logging.warning(f"User {user_id} provided no room number")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.MOVE_IN_USAGE
        )
        return

    try:
        room_number = int(context.args[0])
        if room_number < 1 or room_number > 17:
            raise ValueError()
    except ValueError:
        logging.warning(f"User {user_id} provided invalid room number: {context.args[0]}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.INVALID_ROOM
        )
        return

    if add_registration_request(str(user_id), room_number):
        logging.info(f"User {user_id} requested to move into room {room_number}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.MOVE_IN_REQUESTED.format(room_number)
        )
    else:
        logging.warning(f"Room {room_number} already has a pending request")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.MOVE_IN_ROOM_OCCUPIED
        )


async def move_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /moveout command for departing residents.

    Removes the user's room assignment and sends a farewell message.

    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    user_id = str(update.effective_user.id)
    success, room_number = remove_room_assignment(user_id)

    if success:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.MOVE_OUT_SUCCESS.format(room_number)
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.MOVE_OUT_FAILED
        )


async def show_my_chore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /meindienst command by showing the user's chore for this week.
    
    Finds the user's room number and displays their assigned chore and its status.
    
    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    data = load_chore_data()
    user_id = update.effective_user.id

    try:
        room_number = get_user_room(str(user_id))
    except (FileNotFoundError, KeyError):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.ERROR_NO_ROOM
        )
        return

    # Find the chore assigned to this user's room
    user_chore = None
    for chore in data.chore_states:
        if chore.assigned_to_room == room_number:
            user_chore = chore
            break

    if user_chore is None or user_chore.chore.type == ChoreType.FREI:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.FREE_WEEK_MESSAGE
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=constants.YOUR_CHORE.format(str(user_chore))
    )


async def complete_all_chores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /alleerledigt command to mark all chores as completed.
    
    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    user_id = str(update.effective_user.id)
    user_role = get_user_role(user_id)
    
    # Check if user has required permissions
    if user_role not in [UserRole.ADMIN]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.ERROR_UNAUTHORIZED
        )
        return
    data = load_chore_data()
    data = data.with_completed_all()
    save_chore_data(data)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=constants.ALL_CHORES_COMPLETED
    )

async def accept_all_registrations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /accept_all command to approve all pending room registration requests.
    
    Only users with ADMIN or WOHNHEIMSSPRECHER roles can use this command.
    
    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    user_id = str(update.effective_user.id)
    user_role = get_user_role(user_id)
    
    # Check if user has required permissions
    if user_role not in [UserRole.ADMIN, UserRole.WOHNHEIMSSPRECHER]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.ERROR_UNAUTHORIZED
        )
        return

    # Load pending requests and current assignments
    pending_requests = load_registration_requests()
    current_assignments = load_room_assignments()
    
    if not pending_requests:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.NO_PENDING_REQUESTS
        )
        return
    
    # Process each request
    approved_count = 0
    for user_id, room_number in pending_requests.items():
        # Check if room is already assigned
        if room_number not in [room for room in current_assignments.values()]:
            current_assignments[user_id] = room_number
            approved_count += 1
            
            # Notify the user that their request was approved
            try:
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text=constants.MOVE_IN_APPROVED.format(room_number)
                )
            except Exception as e:
                print(f"Failed to notify user {user_id}: {e}")
    
    # Save updated assignments and clear requests
    save_room_assignments(current_assignments)
    os.remove(constants.REGISTRATION_REQUESTS_FILE_NAME)
    
    # Send summary to admin
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=constants.REQUESTS_PROCESSED.format(
            approved_count,
            len(pending_requests) - approved_count
        )
    )


async def show_registration_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /show_requests command to list all pending room registration requests.
    
    Only users with ADMIN or WOHNHEIMSSPRECHER roles can use this command.
    
    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    user_id = str(update.effective_user.id)
    user_role = get_user_role(user_id)
    
    # Check if user has required permissions
    if user_role not in [UserRole.ADMIN, UserRole.WOHNHEIMSSPRECHER]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.ERROR_UNAUTHORIZED
        )
        return

    # Load pending requests
    pending_requests = load_registration_requests()
    
    if not pending_requests:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.NO_PENDING_REQUESTS
        )
        return
    
    # Format the requests list
    requests_list = []
    for user_id, room_number in pending_requests.items():
        try:
            user = await context.bot.get_chat(int(user_id))
            user_name = user.full_name
        except Exception:
            user_name = f"Unknown User ({user_id})"
        
        requests_list.append(constants.REQUEST_ENTRY.format(
            room_number,
            user_name,
            user_id
        ))
    
    message = constants.PENDING_REQUESTS_HEADER + "\n" + "\n".join(requests_list)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


async def set_user_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /set_role command to assign roles to users.
    
    Only users with ADMIN role can use this command.
    Usage: /set_role <user_id> <role>
    where role is either 'admin' or 'sprecher' or 'clear' to remove the role
    
    Args:
        update (Update): The update object containing information about the incoming message
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    user_id = str(update.effective_user.id)
    user_role = get_user_role(user_id)
    
    # Check if user has admin permissions
    if user_role != UserRole.ADMIN:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.ERROR_UNAUTHORIZED
        )
        return

    # Check command arguments
    if len(context.args) != 2:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.SET_ROLE_USAGE
        )
        return
    
    target_user_id = context.args[0]
    role_str = context.args[1].lower()
    
    # Map role string to UserRole enum
    role_mapping = {
        'admin': UserRole.ADMIN,
        'sprecher': UserRole.WOHNHEIMSSPRECHER,
        'clear': None
    }
    
    if role_str not in role_mapping:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.INVALID_ROLE
        )
        return
    
    new_role = role_mapping[role_str]
    
    set_user_role(target_user_id, new_role)
    
    # Try to get user's name for the confirmation message
    try:
        user = await context.bot.get_chat(int(target_user_id))
        user_name = user.full_name
    except Exception:
        user_name = f"User {target_user_id}"
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=constants.ROLE_UPDATED.format(
            user_name,
            str(new_role).split('.')[1].lower()  # Convert UserRole.ADMIN to "admin"
        )
    )
    
    # Notify the user about their new role
    try:
        await context.bot.send_message(
            chat_id=int(target_user_id),
            text=constants.ROLE_ASSIGNED.format(str(new_role).split('.')[1].lower())
        )
    except Exception as e:
        print(f"Failed to notify user {target_user_id} about new role: {e}")


def main():
    """Initialize and start the bot.

    Sets up:
    1. Command handlers for user interactions
    2. Daily reminder job (10:00 AM)
    3. Weekly chore rotation job (Monday 3:00 AM)
    """
    logging.info("Starting bot")
    bot_token = os.getenv("BOT_API_TOKEN")

    if not os.path.exists(constants.CHORE_DATA_FILE_NAME):
        logging.warning(f"Chore data file not found at {constants.CHORE_DATA_FILE_NAME}. Regenerating...")
        chore_data = generate_chore_data_week_start(get_week_number())
        save_chore_data(chore_data)

    # Enable job queue when building the application
    application = Application.builder().token(bot_token).build()
    
    logging.info("Setting up command handlers")
    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('hilfe', help_command))
    application.add_handler(CommandHandler('aufgaben', show_chores))
    application.add_handler(CommandHandler('erledigt', mark_done))
    application.add_handler(CommandHandler('movein', move_in))
    application.add_handler(CommandHandler('moveout', move_out))
    application.add_handler(CommandHandler('meindienst', show_my_chore))
    application.add_handler(CommandHandler('accept_all', accept_all_registrations))
    application.add_handler(CommandHandler('show_requests', show_registration_requests))
    application.add_handler(CommandHandler('set_role', set_user_role))
    application.add_handler(CommandHandler('complete_all', complete_all_chores))

    logging.info("Setting up job queue")
    # Run reminders daily at 10:00
    application.job_queue.run_daily(
        check_reminders,
        time=REMINDER_TIME,
        days=(0, 1, 2, 3, 4, 5, 6)
    )

    # Run chore rotation every Monday at 03:00 am
    application.job_queue.run_daily(
        rotate_chores,
        time=time(hour=3, minute=0),
        days=(0,)  # Monday only
    )

    logging.info("Bot started successfully")
    application.run_polling()


if __name__ == "__main__":
    main()
