"""
Copyright © Dennisjr13 2026-Present - https://github.com/dennisjr13
Description:
Simple standalone RW stats script
"""

import requests

# Setup API Key and Faction ID
API_KEY = 'abc123'
FACTION_ID = 16040  # this is WiC

# Find ID in URL: torn.com/factions.php?step=your#/war/12345
WAR_ID = '36456'

# Fetch Ranked War Data
url = f"https://api.torn.com/v2/faction/{WAR_ID}/rankedwarreport?selections=members,raw&key={API_KEY}"
response = requests.get(url)
data = response.json()

# Navigate to the factions list
factions = data.get('rankedwarreport', {}).get('factions', [])

# Find your specific faction
our_faction = next((f for f in factions if f['id'] == FACTION_ID), None)

if our_faction:
    print(f"Report for {our_faction['name']} (ID: {FACTION_ID})")
    print(f"Total Score: {our_faction['score']}")
    print(f"Respect Reward: {our_faction['rewards']['respect']}")

    # List member performance
    print("\nMember Stats:")
    for member in our_faction['members']:
        print(f"- {member['name']} [{member['id']}]: {member['attacks']} attacks, {member['score']} score")
else:
    print(f"Faction {FACTION_ID} not found in this war report.")