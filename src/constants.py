import os

CHORE_DATA_FILE_NAME = os.path.join(os.getenv("DATA_FILE_DIRECTORY"), os.getenv("CHORE_DATA_FILE_NAME"))
ROOM_ASSIGNMENTS_FILE_NAME = os.path.join(os.getenv("DATA_FILE_DIRECTORY"), os.getenv("ROOM_ASSIGNMENTS_FILE_NAME"))
REGISTRATION_REQUESTS_FILE_NAME = os.path.join(os.getenv("DATA_FILE_DIRECTORY"), os.getenv("REGISTRATION_REQUESTS_FILE_NAME"))
PENALTY_LOG_FILE_NAME = os.path.join(os.getenv("DATA_FILE_DIRECTORY"), os.getenv("PENALTY_LOG_FILE_NAME"))
ROLES_FILE_NAME = "data/roles.json"

# Bot messages
START_MESSAGE = "Hallo! Ich bin der WG-Bot. Nutze /hilfe um zu sehen, was ich alles kann!"

HELP_TEXT = """
Verfügbare Befehle:
/aufgaben - Zeigt die aktuellen Aufgaben dieser Woche
/meindienst - Zeigt deinen Dienst für diese Woche
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


# Room rotation order as seen on the board
ROOM_ORDER = [17, 15, 10, 2, 5, 7, 9, 16, 13, 1, 8, 4, 3, 6, 12, 14, 11]

# Penalty messages
PENALTY_LOG_HEADER = "⚠️ Nicht erledigte Aufgaben der letzten Woche:"
PENALTY_LOG_ENTRY = "Zimmer {}: {} (fällig {})"

# Penalty notification
PENALTY_NOTIFICATION = "⚠️ Du hast letzte Woche deine Aufgabe nicht erledigt:\n{}"

# Personal chore messages
YOUR_CHORE = "Dein Dienst diese Woche:\n{}"

# Admin command messages
ERROR_UNAUTHORIZED = "Du hast keine Berechtigung für diesen Befehl."
NO_PENDING_REQUESTS = "Es gibt keine ausstehenden Einzugsanfragen."
MOVE_IN_APPROVED = "Deine Einzugsanfrage für Zimmer {} wurde genehmigt! Willkommen!"
REQUESTS_PROCESSED = "Einzugsanfragen verarbeitet:\n✅ {} genehmigt\n❌ {} abgelehnt (Zimmer bereits belegt)"

# Registration request messages
PENDING_REQUESTS_HEADER = "📝 Ausstehende Einzugsanfragen:"
REQUEST_ENTRY = "Zimmer {}: {} (ID: {})"

# Role management messages
SET_ROLE_USAGE = "Verwendung: /set_role <user_id> <role>\nMögliche Rollen: admin, sprecher"
INVALID_ROLE = "Ungültige Rolle. Mögliche Rollen sind: admin, sprecher"
ROLE_UPDATED = "{} wurde die Rolle {} zugewiesen."
ROLE_ASSIGNED = "Dir wurde die Rolle {} zugewiesen."

