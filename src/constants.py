from src.utils import Chore, ChoreType, DueDay

# Bot messages
START_MESSAGE = "Hallo! Ich bin der WG-Bot. Nutze /hilfe um zu sehen, was ich alles kann!"

HELP_TEXT = """
Verfügbare Befehle:
/aufgaben - Zeigt die aktuellen Aufgaben dieser Woche
/erledigt - Markiert deine Aufgabe als erledigt
/hilfe - Zeigt diese Nachricht
/movein - Ziehe in ein Zimmer ein
/moveout - Ziehe aus deinem Zimmer aus
/start - Zeigt die Willkommensnachricht
"""

# Error messages
ERROR_ROOM_ASSIGNMENTS = "Fehler: Raum-Zuordnungen konnten nicht geladen werden"
ERROR_NO_ROOM = "Du bist keinem Zimmer zugeordnet!"
ERROR_ROOM_NOT_FOUND = "Fehler: Dein Zimmer wurde nicht gefunden. Bitte kontaktiere einen Administrator."
ERROR_ALREADY_COMPLETED = "Diese Aufgabe wurde bereits als erledigt markiert!"

# Success messages
FREE_WEEK_MESSAGE = "Du hast diese Woche frei. Bitte setze dich provokant ins Fernsehzimmer und erzähle jedem, der vorbei kommt, dass du diese Woche keinen Dienst zu erledigen hast."
TASK_COMPLETED = "Super! {} wurde als erledigt markiert! 🎉"

# Reminder messages
WEEKLY_REMINDER = "Deine Aufgabe diese Woche ist: {}"
DAILY_REMINDER = "Erinnerung: {} ist morgen fällig!"

# Room registration messages
MOVE_IN_REQUESTED = "Willkommen! Dein Einzug in Zimmer {} wurde beantragt. Ein Administrator wird die Anfrage prüfen."
MOVE_IN_ROOM_OCCUPIED = "Für dieses Zimmer gibt es bereits eine ausstehende Einzugsanfrage."
INVALID_ROOM = "Ungültige Zimmernummer. Bitte gib eine Zahl zwischen 1 und 17 ein."
MOVE_IN_USAGE = "Bitte gib deine Zimmernummer an, z.B.: /movein 12"

# Move out messages
MOVE_OUT_SUCCESS = "Tschüss! Du wurdest erfolgreich aus Zimmer {} ausgetragen. Danke für deine Mitarbeit!"
MOVE_OUT_FAILED = "Du bist momentan keinem Zimmer zugeordnet."

# Chores as seen on the board
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
    Chore(ChoreType.MASCHINEN, DueDay.SO),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.GESCHIRRTUECHER, DueDay.SO),
    Chore(ChoreType.FREI, DueDay.NONE),
    Chore(ChoreType.MUELLDIENST, DueDay.SO),
    Chore(ChoreType.FREI, DueDay.NONE)
]

# Room rotation order as seen on the board
ROOM_ORDER = [17, 15, 10, 2, 5, 7, 9, 16, 13, 1, 8, 4, 3, 6, 12, 14, 11]

# Penalty messages
PENALTY_LOG_HEADER = "⚠️ Nicht erledigte Aufgaben der letzten Woche:"
PENALTY_LOG_ENTRY = "Zimmer {}: {} (fällig {})"

# Penalty notification
PENALTY_NOTIFICATION = "⚠️ Du hast letzte Woche deine Aufgabe nicht erledigt:\n{}"

