from auth import client_id, client_secret
from blizzardapi import BlizzardApi
import pprint
import json
import sqlite3
import logging

# 
PVP_SEASON = 34

def get_shuffle_leaderboard(spec, c_class, region, retries=0):
    if retries > 5:
        print("failed, giving up on %s %s %s" % (spec, c_class, region))
        return None

    print("getting shuffle leaderboard")
    
    api_client = BlizzardApi(client_id, client_secret)

    mode = "shuffle"
    ladder = "%s-%s-%s" % (mode, c_class.replace(" ", "").lower(), spec.replace(" ", "").lower())
    print(ladder)
    if retries > 0:
        print("retry #%d" % retries)

    try:
        leaderboard = api_client.wow.game_data.get_pvp_leaderboard(region, "en-US", PVP_SEASON, ladder)
    except json.decoder.JSONDecodeError:
        # try again
        return get_shuffle_leaderboard(spec, c_class, region, retries+1)

    conn = sqlite3.connect('shuffle.db')
    c = conn.cursor()
    
    # Access the data
    values = []

    for k in leaderboard["entries"]:
        values.append((mode, k["rating"], k["character"]["id"], k["character"]["realm"]["slug"], k["character"]["name"], c_class, spec, k["faction"]["type"], region, 0))

    c.executemany('INSERT INTO ladder (ladder, rating, character_id, server, character_name,character_class, character_spec, faction, region, fetch_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)

    conn.commit()
    conn.close()
    print("done!")
    return

conn = sqlite3.connect('shuffle.db')
c = conn.cursor()

conn.execute("drop table if exists ladder")
conn.execute("CREATE TABLE ladder (entry_id integer primary key autoincrement, ladder TEXT, rating INTEGER, character_id INTEGER, server TEXT, character_name TEXT, character_spec TEXT,character_class TEXT, faction TEXT, region TEXT, fetch_id INTEGER, character_race TEXT)")

conn.commit()
conn.close()

specs_and_classes = []
specs_and_classes += [["Fury", "Warrior"]]
specs_and_classes += [["Arms", "Warrior"]]
specs_and_classes += [["Protection", "Warrior"]]
specs_and_classes += [["Blood", "Death Knight"]]
specs_and_classes += [["Frost", "Death Knight"]]
specs_and_classes += [["Unholy", "Death Knight"]]
specs_and_classes += [["Balance", "Druid"]]
specs_and_classes += [["Feral", "Druid"]]
specs_and_classes += [["Guardian", "Druid"]]
specs_and_classes += [["Restoration", "Druid"]]
specs_and_classes += [["Beast Mastery", "Hunter"]]
specs_and_classes += [["Marksmanship", "Hunter"]]
specs_and_classes += [["Survival", "Hunter"]]
specs_and_classes += [["Arcane", "Mage"]]
specs_and_classes += [["Fire", "Mage"]]
specs_and_classes += [["Frost", "Mage"]]
specs_and_classes += [["Brewmaster", "Monk"]]
specs_and_classes += [["Mistweaver", "Monk"]]
specs_and_classes += [["Windwalker", "Monk"]]
specs_and_classes += [["Holy", "Paladin"]]
specs_and_classes += [["Protection", "Paladin"]]
specs_and_classes += [["Retribution", "Paladin"]]
specs_and_classes += [["Discipline", "Priest"]]
specs_and_classes += [["Holy", "Priest"]]
specs_and_classes += [["Shadow", "Priest"]]
specs_and_classes += [["Assassination", "Rogue"]]
specs_and_classes += [["Subtlety", "Rogue"]]
specs_and_classes += [["Outlaw", "Rogue"]]
specs_and_classes += [["Elemental", "Shaman"]]
specs_and_classes += [["Enhancement", "Shaman"]]
specs_and_classes += [["Restoration", "Shaman"]]
specs_and_classes += [["Affliction", "Warlock"]]
specs_and_classes += [["Demonology", "Warlock"]]
specs_and_classes += [["Destruction", "Warlock"]]
specs_and_classes += [["Havoc", "Demon Hunter"]]
specs_and_classes += [["Vengeance", "Demon Hunter"]]
specs_and_classes += [["Devastation", "Evoker"]]
specs_and_classes += [["Preservation", "Evoker"]]

for region in ["us", "eu", "kr"]:
    for spec, c_class in specs_and_classes:
        get_shuffle_leaderboard(spec, c_class, region)
