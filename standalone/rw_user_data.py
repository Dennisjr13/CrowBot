"""
Copyright © Dennisjr13 2026-Present - https://github.com/dennisjr13
Description:
Simple standalone RW stats script
"""
import csv
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

# Setup API Key
API_KEY = os.getenv("TORNSTATS_API_KEY")
if not API_KEY:
    API_KEY = 'abc123'  # manually enter API key here (if you don't have a .env file)

# Configure war and chain ids
FACTION_ID = 16040  # Winter is Coming
WAR_ID = 36456  # Find ID in URL: torn.com/war.php?step=rankreport&rankID=36456
CHAIN_IDS = [58280540, ]  # Find ID in URL: torn.com/war.php?step=chainreport&chainID=58280540

ENERGY_PER_HIT = 25


def torn_get(url):
    params = {
        "key": API_KEY,
        "timestamp": int(datetime.now().timestamp()),
        "comment": "RW report"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def get_chain_report(chain_id):
    url = f"https://api.torn.com/v2/faction/{str(chain_id)}/chainreport"
    data = torn_get(url)
    return data.get("chainreport", {})


def get_war_report(war_id):
    url = f"https://api.torn.com/v2/faction/{str(war_id)}/rankedwarreport?selections=members,raw"
    data = torn_get(url)
    return data.get('rankedwarreport', {})


# Fetch Ranked War Data
war_report = get_war_report(war_id=WAR_ID)

# Fetch Chain Data
chain_reports = [get_chain_report(chain_id=chain_id) for chain_id in CHAIN_IDS]

# Navigate to the factions list
factions = war_report.get('factions', [])

# Find your specific faction
our_faction = next((f for f in factions if f.get('id') == FACTION_ID), None)

if our_faction:
    print(f"Report for {our_faction['name']} (ID: {FACTION_ID})")
    print(f"War ID: {WAR_ID}, Chain ID(s): {CHAIN_IDS}")
    print(f"Total Score: {our_faction['score']}")
    print(f"War Respect Reward: {our_faction['rewards']['respect']}")

    # ---- MAP BONUS RESPECT PER ATTACKER ----
    bonus_by_attacker = {}
    for chain_report in chain_reports:
        for bonus in chain_report.get("bonuses", []):
            attacker = str(bonus["attacker_id"])
            bonus_by_attacker[attacker] = (
                    bonus_by_attacker.get(attacker, 0)
                    + bonus.get("respect", 0)
            )

    # ---- MEMBER PERFORMANCE ----
    print("NOTE: any chain_bonus respect removed from chain_total_respect")
    print("\nMember Stats:")

    headers = [
        "name [id]",
        "chain_attacks",
        "chain_leave",
        "chain_mug",
        "chain_hosp",
        "chain_assists",
        "war_attacks",
        "war_combined",
        "chain_avg_respect",
        "chain_total_respect",
        "war_payout",
        "chain_losses",
        "chain_draws",
        "chain_escapes",
        "total_hits",
        "energy_used",
    ]

    rows = []
    for member in our_faction['members']:
        chain_bonus = bonus_by_attacker.get(str(member['id']), 0)

        chain_attacks = 0
        chain_leave = 0
        chain_mug = 0
        chain_hosp = 0
        chain_assists = 0
        war_attacks = member.get('attacks', 0)
        chain_total_respect = 0.0
        chain_avg_respect = 0.0
        chain_losses = 0
        chain_draws = 0
        chain_escapes = 0

        for chain_report in chain_reports:
            chain_member = next((d for d in chain_report.get("attackers", []) if d.get('id') == member['id']), None)
            if chain_member:
                chain_attacks += chain_member.get("attacks", 0).get("total", 0)
                chain_leave += chain_member.get("attacks", 0).get("leave", 0)
                chain_mug += chain_member.get("attacks", 0).get("mug", 0)
                chain_hosp += chain_member.get("attacks", 0).get("hospitalize", 0)
                chain_assists += chain_member.get("attacks", 0).get("assists", 0)
                chain_total_respect += chain_member.get("respect", 0).get("total", 0)
                chain_avg_respect += chain_member.get("respect", 0).get("average", 0)
                chain_losses += chain_member.get("attacks", 0).get("losses", 0)
                chain_draws += chain_member.get("attacks", 0).get("draws", 0)
                chain_escapes += chain_member.get("attacks", 0).get("escapes", 0)

        total_hits = chain_assists + war_attacks + chain_losses + chain_draws + chain_escapes

        rows.append([
            f"{member.get('name', 'Unknown')} [{member.get('id', 0)}]",
            chain_attacks,
            chain_leave,
            chain_mug,
            chain_hosp,
            chain_assists,
            war_attacks,
            chain_assists + war_attacks,
            f"{chain_avg_respect:.2f}",
            f"{chain_total_respect - chain_bonus:.2f}",
            "TBD",
            chain_losses,
            chain_draws,
            chain_escapes,
            total_hits,
            total_hits * ENERGY_PER_HIT,
        ])

    # Pretty console table
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

    # CSV output
    with open("rw_user_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

else:
    print(f"Faction {FACTION_ID} not found in this war report.")
