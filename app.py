from chalice import Chalice, Cron
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import boto3

secrets_manager = boto3.client("secretsmanager")
telegram_secrets = json.loads(
    secrets_manager.get_secret_value(SecretId="fuel_price_secrets")["SecretString"]
)
MONTHS = [
    "janeiro",
    "fevereiro",
    "marco",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
TELEGRAM_URL = "https://api.telegram.org"
TELEGRAM_BOT_TOKEN = telegram_secrets["telegram_bot_token"]
TELEGRAM_CHAT_ID = telegram_secrets["telegram_chat_id"]

app = Chalice(app_name="helloworld")


def get_symbol(text: str) -> str:
    if "-" in text:
        return text + " 👍"
    else:
        return text + " 👎"


@app.schedule(Cron(0, 13, "?", "*", 6, "*"))
def periodic_task(event):
    today = datetime.now()
    # today = datetime.strptime("26/04/2024", "%d/%m/%Y")
    next_monday = today + timedelta(days=3)
    next_friday = today + timedelta(days=9)
    if next_monday.month == next_friday.month:
        url_suffix = (
            f"{next_monday.day}-a-{next_friday.day}-de-{MONTHS[next_monday.month-1]}/"
        )
    else:
        url_suffix = f"{next_monday.day}-de-{MONTHS[next_monday.month-1]}-a-{next_friday.day}-de-{MONTHS[next_friday.month-1]}/"

    prices_url = (
        f"https://contaspoupanca.pt/{today.year}/{today.month}/{today.day}/combustiveis-precos-na-proxima-semana-"
        + url_suffix
    )
    print(prices_url)

    headers = {"User-Agent": USER_AGENT}
    page = requests.get(prices_url, headers=headers)

    soup = BeautifulSoup(page.content, "html.parser")
    h1_elements = soup.find_all("h1")

    for element in h1_elements:
        if element.text.startswith("Semana de"):
            week_info = element.text
            print(f"week_info: {element.text}")
        if element.text.startswith("Gasóleo"):
            diesel_info = get_symbol(element.text)
            print(f"diesel_info: {element.text}")
        if element.text.startswith("Gasolina"):
            gas_info = get_symbol(element.text)
            print(f"gas_info: {element.text}")

    message = f"""<u><b>{week_info}</b></u>
    - {diesel_info}
    - {gas_info}
    Fonte: <a href="{prices_url}">here</a>"""

    telegram_url = f"{TELEGRAM_URL}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"parse_mode": "HTML", "chat_id": TELEGRAM_CHAT_ID, "text": message}

    send_telegram_message = requests.post(telegram_url, json=params)
    print(send_telegram_message.text)

    return {"telegram_event": send_telegram_message.text}
