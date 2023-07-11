import os
import asyncio
import schedule
import time
from telegram import Bot
from telegram.constants import ParseMode
from datetime import date
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
import subprocess
from votes_service import save_votes
from votes_service import get_votes

prf_position_in_rank = -1

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = 'https://brasilparticipativo.presidencia.gov.br/processes/programas/f/2/proposals?order=most_voted'
LAST_24_HOURS = []
DIFF_MESSAGE = ''

def get_date():
    return date.today().strftime("%d/%m/%Y")


def get_time():
    return datetime.now().strftime("%H:%M:%S")


def get_proposal_id(proposalElement):
    return proposalElement.get('id')


def calc_votes_diff(current_votes):
    print('[+] Gerando relatório das últimas 24 horas')
    all_votes_from_api = get_votes()
    differences = []

    for current_vote in current_votes:
        reference_name = current_vote['name']
        reference_vote = int(current_vote['votes'])
        reference_date = datetime.fromisoformat(current_vote['date'])

        for vote in all_votes_from_api:
            vote_date = datetime.fromisoformat(vote['date'])
            vote_name = vote['name']
            vote_votes = int(vote['votes'])

            if vote_name != reference_name:
                continue

            time_difference = abs(reference_date - vote_date)

            if time_difference >= timedelta(hours=24):
                differences.append({**current_vote, 'difference_hours': time_difference, 'difference_votes': int(reference_vote -vote_votes) })
                break

    return differences


def get_message():
    all_votes = []

    result = subprocess.run(['curl', URL], capture_output=True, text=True)
    html = result.stdout
    soup = BeautifulSoup(html, 'html.parser')
    top_5_cards = soup.select('div.column[id^="proposal_"]')[:10]

    for i, card in enumerate(top_5_cards):
        proposal_id = get_proposal_id(card)

        name = card.select_one('div.card__title')
        name = name.text
        name = name.replace('´', '').strip()

        global prf_position_in_rank
        if 'PRF' in name:
            prf_position_in_rank = i + 1

        votes = card.select_one('span.progress__bar__number')
        votes = votes.text.strip()

        all_votes.append({"id": proposal_id, "name": name,
                         "votes": votes, "date": datetime.now().isoformat()})

    
    global LAST_24_HOURS
    global DIFF_MESSAGE
    if not LAST_24_HOURS:
        LAST_24_HOURS = calc_votes_diff(all_votes)
        DIFF_MESSAGE += '\n\n*-----Evolução nas últimas horas-----*'
        for d in LAST_24_HOURS:
            name = d['name']
            difference_votes = d['difference_votes']
            difference_hours = d['difference_hours']
            DIFF_MESSAGE += f'\n{name} \nVotos: *{difference_votes}* em {difference_hours.days} dias\n'

    save_votes(all_votes)

    message = ""

    prf_votes = int(all_votes[prf_position_in_rank - 1]["votes"])

    if prf_position_in_rank > -1:
        message += 'Dia {} - {}\n\n'.format(get_date(), get_time())
        message += '*🚨Estamos em {}º lugar com {} votos!🚨*\n\n'.format(
            prf_position_in_rank, prf_votes)
    for index, position in enumerate(all_votes):
        difference = int(position["votes"]) - prf_votes
        difference = difference * -1 if difference < 0 else difference

        if difference > 0:
            message += '- Diferença de *{}* votos do {}º lugar\n'.format(
                difference, index + 1)

    prf_position_in_rank = -1

    return message


async def send_message(message):
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)


async def main():
    message = get_message()
    await send_message(message)


schedule.every(2).minutes.do(lambda: asyncio.run(main()))

if __name__ == "__main__":
    print('[+] Bot running...')
    while True:
        schedule.run_pending()
        time.sleep(1)
