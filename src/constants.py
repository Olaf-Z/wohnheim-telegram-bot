import os

CHORE_DATA_FILE_NAME = os.path.join(os.getenv("DATA_FILE_DIRECTORY"), os.getenv("CHORE_DATA_FILE_NAME"))
ROOM_ASSIGNMENTS_FILE_NAME = os.path.join(os.getenv("DATA_FILE_DIRECTORY"), os.getenv("ROOM_ASSIGNMENTS_FILE_NAME"))
REGISTRATION_REQUESTS_FILE_NAME = os.path.join(os.getenv("DATA_FILE_DIRECTORY"), os.getenv("REGISTRATION_REQUESTS_FILE_NAME"))
PENALTY_LOG_FILE_NAME = os.path.join(os.getenv("DATA_FILE_DIRECTORY"), os.getenv("PENALTY_LOG_FILE_NAME"))
SHOPPING_LIST_FILE_NAME = os.path.join(os.getenv("DATA_FILE_DIRECTORY"), os.getenv("SHOPPING_LIST_FILE_NAME"))
ROLES_FILE_NAME = "data/roles.json"

# Bot messages
START_MESSAGE = "Hallo! Ich bin der steile Wohnheimsbot. Nutze /hilfe um zu sehen, was ich an der Tasse kann!"

HELP_TEXT = """
Verfügbare Befehle:
/aufgaben - Zeigt die aktuellen Aufgaben dieser Woche
/meindienst - Zeigt deinen Dienst für diese Woche
/erledigt - Markiert deine Aufgabe als erledigt
/hilfe - Zeigt diese Nachricht
/movein - Ziehe in ein Zimmer ein
/moveout - Ziehe aus deinem Zimmer aus
/start - Zeigt die Willkommensnachricht
/einkaufen - Fügt einen Artikel zur Einkaufsliste hinzu
/einkaufsliste - Zeigt die aktuelle Einkaufsliste

Admin-Befehle:
/accept_all - Genehmigt alle ausstehenden Einzugsanfragen
/show_requests - Zeigt alle ausstehenden Einzugsanfragen
/set_role - Setzt die Rolle eines Benutzers
/complete_all - Markiert alle Aufgaben als erledigt
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
DAILY_REMINDER = "Erinnerung: {} ist noch fällig!"

# Room registration messages
MOVE_IN_REQUESTED = "Willkommen! Dein Einzug in Zimmer {} wurde beantragt. Ein Administrator wird die Anfrage prüfen."
MOVE_IN_ROOM_OCCUPIED = "Für dieses Zimmer gibt es bereits eine ausstehende Einzugsanfrage."
INVALID_ROOM = "Ungültige Zimmernummer. Bitte gib eine Zahl zwischen 1 und 17 ein."
MOVE_IN_USAGE = "Bitte gib deine Zimmernummer an, z.B.: /movein 12"

# Move out messages
MOVE_OUT_SUCCESS = "Tschüss! Du wurdest erfolgreich aus Zimmer {} ausgetragen. Danke für deine Mitarbeit!"
MOVE_OUT_FAILED = "Du bist momentan keinem Zimmer zugeordnet."


# Room rotation order as seen on the board
ROOM_ORDER = [9, 16, 13, 1, 8, 4, 3, 6, 12, 14, 11, 17, 15, 10, 2, 7, 5]

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

# All chores completed message
ALL_CHORES_COMPLETED = "Alle Aufgaben wurden vom Administrator als erledigt markiert! 🎉"

# Shopping list messages
SHOPPING_LIST_HEADER = "🛒 Einkaufsliste:"
SHOPPING_LIST_USAGE = "Verwendung: /einkaufen <item>\nBeispiel: /einkaufen Milch"
SHOPPING_LIST_ENTRY_ADDED = "{} wurde zur Einkaufsliste hinzugefügt!"
SHOPPING_LIST_INVALID_ITEM = "Ungültiges Einkaufsitem. Bitte verwende nur Buchstaben, Zahlen und Leerzeichen."
SHOPPING_LIST_DUPLICATE_ITEM = "Dieser Artikel ist bereits in der Einkaufsliste enthalten."

TELL_TO_SEND_PRIVATE_MESSAGE = "Bitte verwende diesen Befehl nur im privaten Chat mit dem Bot!"