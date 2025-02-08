set dotenv-load := true

install:
    pip3 install -r requirements.txt
    sudo apt install docker.io

run:
    docker build -t steiler-wohnheims-bot .
    docker run -d --env-file .env steiler-wohnheims-bot

run-local:
    python3 src/SteilerWohnheimsBot.py

accept-requests:
    python3 accept_registration_requests.py

