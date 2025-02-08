import json
import os
def main():
    try:
        with open("registration_requests.json", "r") as f:
            requests = json.load(f)
    except:
        return

    try:
        with open("room_assignments.json", "r") as f:
            room_assignments = json.load(f)
    except:
        room_assignments = {}

    for user_id, room_number in requests.items():
        print(f"Accepting registration request for user {user_id} in room {room_number}")
        room_assignments[user_id] = room_number

    with open("room_assignments.json", "w+") as f:
        json.dump(room_assignments, f)

    os.remove("registration_requests.json")

if __name__ == "__main__":
    main()
