set dotenv-load := true

install:
    pip3 install -r requirements.txt

run:
    python3 src/SteilerWohnheimsBot.py

accept-requests:
    python3 accept_registration_requests.py

