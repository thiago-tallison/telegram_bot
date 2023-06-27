import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from datetime import date
from datetime import datetime
from bs4 import BeautifulSoup
import subprocess

prf_position_in_rank = -1

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = 'https://brasilparticipativo.presidencia.gov.br/processes/programas/f/2/proposals?order=most_voted'


def get_date():
    return date.today().strftime("%d/%m/%Y")


def get_time():
    return datetime.now().strftime("%H:%M:%S")


def get_message():
    all_votes = []

    result = subprocess.run(['curl', URL], capture_output=True, text=True)
    html = result.stdout
    soup = BeautifulSoup(html, 'html.parser')

    top_5_cards = soup.select('.column > .card')[:5]

    for i, card in enumerate(top_5_cards):
        name = card.select_one('div.card__title')
        name = name.text
        name = name.replace('´', '').strip()

        if 'PRF' in name:
            prf_position_in_rank = i + 1

        votes = card.select_one('span.progress__bar__number')
        votes = votes.text.strip()

        all_votes.append({"name": name, "votes": votes})

    message = ""

    if prf_position_in_rank > -1:
        message += '*Estamos em {}º lugar*\n'.format(prf_position_in_rank)

    prf_votes = int(all_votes[prf_position_in_rank - 1]["votes"])
    for index, position in enumerate(all_votes):
        difference = int(position["votes"]) - prf_votes
        difference = difference * -1 if difference < 0 else difference
       
        if difference > 0:
            message += '- Diferença de *{}* votos do {}º lugar\n'.format(
                difference, index + 1)

    return message


async def send_message(message):
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)


async def main():
    message = get_message()

    while True:
        await send_message(message)
        await asyncio.sleep(5)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
