"""
Copyright © Dennisjr13 2026-Present - https://github.com/dennisjr13
Description:
Simple standalone RW stats script
"""
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

# Setup API Key and request params
#API_KEY = 'abc123'
API_KEY = os.getenv("TORNSTATS_API_KEY")
PARAMS = {
    "key": API_KEY,
    "timestamp": int(datetime.now().timestamp()),
    "comment": "RW report"
}

FACTION_ID = 16040  # Winter is Coming
WAR_ID = '36456'  # Find ID in URL: torn.com/war.php?step=rankreport&rankID=36456
CHAIN_ID = '58280540'  # Find ID in URL: torn.com/war.php?step=chainreport&chainID=58280540

def torn_get(url):
    r = requests.get(url, params=PARAMS, timeout=10)
    r.raise_for_status()
    return r.json()

def get_chain_report(chain_id):
    url = f"https://api.torn.com/v2/faction/{chain_id}/chainreport"
    data = torn_get(url)
    return data.get("chainreport", {})

def get_war_report(war_id):
    url = f"https://api.torn.com/v2/faction/{war_id}/rankedwarreport?selections=members,raw"
    data = torn_get(url)
    return data.get('rankedwarreport', {})

# Fetch Ranked War Data
war_report = get_war_report(war_id=WAR_ID)

# Fetch Chain Data
chain_report = get_chain_report(chain_id=CHAIN_ID)

# Navigate to the factions list
factions = war_report.get('factions', [])

# Find your specific faction
our_faction = next((f for f in factions if f['id'] == FACTION_ID), None)

if our_faction:
    print(f"Report for {our_faction['name']} (ID: {FACTION_ID})")
    print(f"Total Score: {our_faction['score']}")
    print(f"War Respect Reward: {our_faction['rewards']['respect']}")

    # ---- MAP BONUS RESPECT PER ATTACKER ----
    bonus_by_attacker = {}
    for bonus in chain_report.get("bonuses", []):
        attacker = str(bonus["attacker_id"])
        bonus_by_attacker[attacker] = (
            bonus_by_attacker.get(attacker, 0)
            + bonus.get("respect", 0)
        )

    chain_members = chain_report.get("members", {})

    # ---- MEMBER PERFORMANCE ----
    print("\nMember Stats:")
    for member in our_faction['members']:
        uid = str(member['id'])

        chain_member = chain_members.get(uid, {})
        raw_chain_respect = chain_member.get("respect", 0)
        bonus_chain_respect = bonus_by_attacker.get(uid, 0)
        adjusted_chain_respect_member = raw_chain_respect - bonus_chain_respect

        line = (
            f"- {member['name']} [{member['id']}]: "
            f"{member['attacks']} war hits, "
            f"{member['score'] - bonus_chain_respect} score"
        )

        if bonus_chain_respect > 0:
            line += f", removed chain bonus ({bonus_chain_respect})"

        print(line)
else:
    print(f"Faction {FACTION_ID} not found in this war report.")