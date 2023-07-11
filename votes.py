import subprocess
from datetime import datetime, timedelta
from votes_service import get_votes
from bs4 import BeautifulSoup

URL = 'https://brasilparticipativo.presidencia.gov.br/processes/programas/f/2/proposals?order=most_voted'

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

def get_proposal_id(proposalElement):
    return proposalElement.get('id')

def get_top_ten_votes():
    result = subprocess.run(['curl', URL], capture_output=True, text=True)
    html = result.stdout
    soup = BeautifulSoup(html, 'html.parser')
    top_ten_votes_html = soup.select('div.column[id^="proposal_"]')[:10]
    top_ten_votes = []

    for card in top_ten_votes_html:
        proposal_id = get_proposal_id(card)

        name = card.select_one('div.card__title')
        name = name.text
        name = name.replace('´', '').strip()


        votes = card.select_one('span.progress__bar__number')
        votes = votes.text.strip()

        top_ten_votes.append({"id": proposal_id, "name": name,
                         "votes": votes, "date": datetime.now().isoformat()})
        
    return top_ten_votes

def get_prf_ranking(top_ten_votes):
    for i, item in enumerate(top_ten_votes):
        if "prf" in item["name"].lower():
            return i + 1
    return -1

def get_prf_proposal(top_ten_votes):
    for item in top_ten_votes:
        if "prf" in item["name"].lower():
            return item
            
    print(f'top_ten: {top_ten_votes}')
    return None