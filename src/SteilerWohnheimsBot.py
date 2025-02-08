from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from telegram.ext import Updater
from datetime import datetime, time
import os
from utils import (ChoreType, DueDay, ChoreInformation,
                       load_chore_data, save_chore_data,
                       get_user_room, get_room_assignments_reversed, add_registration_request,
                       remove_room_assignment, generate_chore_data_week_start, get_incomplete_chores,
                       save_penalty_log)
import constants as constants

TOKEN_PATH = "/home/olaf/code/wohnheimsbot/token"

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
    data = ChoreInformation(data.with_completed(room_number))
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
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=message
        )
    except Exception as e:
        print(f"Failed to send reminder to {user_id}: {e}")


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
        # Check for incomplete chores before rotating
        old_data = load_chore_data()
        incomplete_chores = get_incomplete_chores(old_data)

        if incomplete_chores:
            # Save to CSV log file
            save_penalty_log(incomplete_chores)

            # Get user mappings for notifications
            user_by_room = get_room_assignments_reversed()

            # Notify users with incomplete chores
            for chore in incomplete_chores:
                user_id = user_by_room.get(chore.assigned_to_room)
                if user_id:
                    message = constants.PENALTY_NOTIFICATION.format(
                        chore.chore)
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
        print(f"Successfully rotated chores for week {week_number}")

    except Exception as e:
        print(f"Error in chore rotation: {e}")


async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Send reminder messages to users about their chores.

    This function runs daily at 10:00 AM and:
    1. On Mondays: Sends everyone their chore for the week
    2. Other days: Sends reminders to users who have chores due tomorrow

    Args:
        context (ContextTypes.DEFAULT_TYPE): The context object for the callback
    """
    try:
        data = load_chore_data()
        user_by_room = get_room_assignments_reversed()

        today = datetime.now()
        weekday = today.weekday()  # 0 = Monday, 6 = Sunday

        # Convert to DueDay enum
        today_due = DueDay(weekday)
        tomorrow_due = DueDay((weekday + 1) % 7)

        # Send weekly overview on Mondays and daily reminders for tomorrow's tasks
        for chore_status in data.chore_states:
            if chore_status.chore.type != ChoreType.FREI:
                user_id = user_by_room.get(chore_status.assigned_to_room)
                if user_id:
                    # Send weekly overview on Monday
                    if weekday == 0:
                        message = constants.WEEKLY_REMINDER.format(
                            chore_status.chore)
                        await send_reminder(context, user_id, message)

                    # Send reminder for tomorrow's tasks
                    if (not chore_status.completed and
                            chore_status.chore.due >= tomorrow_due):
                        message = constants.DAILY_REMINDER.format(
                            chore_status.chore)
                        await send_reminder(context, user_id, message)

    except Exception as e:
        print(f"Error in reminder job: {e}")


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
    if not context.args:
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
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.INVALID_ROOM
        )
        return

    user_id = str(update.effective_user.id)
    if add_registration_request(user_id, room_number):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=constants.MOVE_IN_REQUESTED.format(room_number)
        )
    else:
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


def main():
    """Initialize and start the bot.

    Sets up:
    1. Command handlers for user interactions
    2. Daily reminder job (10:00 AM)
    3. Weekly chore rotation job (Monday 3:00 AM)
    """
    bot_token = os.getenv("BOT_API_TOKEN")

    if not os.path.exists(constants.CHORE_DATA_FILE_NAME):
        print(
            f"Chore data file not found at {constants.CHORE_DATA_FILE_NAME}. Regenerating...")
        chore_data = generate_chore_data_week_start(get_week_number())
        save_chore_data(chore_data)

    # Enable job queue when building the application
    application = Application.builder().token(bot_token).build()
    

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('hilfe', help_command))
    application.add_handler(CommandHandler('aufgaben', show_chores))
    application.add_handler(CommandHandler('erledigt', mark_done))
    application.add_handler(CommandHandler('movein', move_in))
    application.add_handler(CommandHandler('moveout', move_out))
    application.add_handler(CommandHandler('meindienst', show_my_chore))


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

    application.run_polling()


if __name__ == "__main__":
    main()
