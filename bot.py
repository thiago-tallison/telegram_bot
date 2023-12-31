import os
import asyncio
from bcolors import bcolors
import schedule
import time
from telegram import Bot
from telegram.constants import ParseMode
from datetime import date
from datetime import datetime
from votes_service import save_votes
from votes import get_prf_proposal, get_top_ten_votes, get_prf_ranking

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LAST_24_HOURS = []
DIFF_MESSAGE = ""
total_messages_sent = 0


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def get_date():
    return date.today().strftime("%d/%m/%Y")


def get_time():
    return datetime.now().strftime("%H:%M:%S")


def get_message():
    top_ten_votes = get_top_ten_votes()

    if not top_ten_votes:
        return ""

    save_votes(top_ten_votes)

    message = ""

    prf_position_in_rank = get_prf_ranking(top_ten_votes)
    prf_proposal = get_prf_proposal(top_ten_votes)
    prf_votes = prf_proposal["votes"]

    if prf_position_in_rank > -1:
        message += "Dia {} - {}\n\n".format(get_date(), get_time())
        message += "*🚨Estamos em {}º lugar com {} votos!🚨*\n\n".format(
            prf_position_in_rank, prf_votes
        )

    for index, position in enumerate(top_ten_votes):
        difference = int(position["votes"]) - int(prf_votes)
        difference = difference * -1 if difference < 0 else difference

        if difference > 0:
            message += "- Diferença de *{}* votos do {}º lugar\n".format(
                difference, index + 1
            )

    return message


async def send_message(message):
    global total_messages_sent
    total_messages_sent += 1

    print(
        f"\r{bcolors.OKGREEN}[+] Sending message ({total_messages_sent})...{bcolors.ENDC}",
        end="",
    )

    bot = Bot(BOT_TOKEN)

    if not message:
        return

    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)


async def main():
    message = get_message()
    await send_message(message)


schedule.every(2).seconds.do(lambda: asyncio.run(main()))

if __name__ == "__main__":
    clear_console()
    print(f"{bcolors.OKGREEN}[+] Bot running...{bcolors.ENDC}")

    while True:
        schedule.run_pending()
        time.sleep(1)
