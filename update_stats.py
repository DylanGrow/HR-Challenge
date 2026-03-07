"""
update_stats.py
Fetches current season + career HR totals for active players from the free MLB Stats API.
Runs as a GitHub Action to keep players.json fresh.
"""

import json
import requests
import time
import sys

PLAYERS_FILE = "players.json"
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"

def get_career_hr(player_id):
    """Fetch career HR total for a player from MLB Stats API."""
    url = f"{MLB_API_BASE}/people/{player_id}/stats"
    params = {
        "stats": "career",
        "group": "hitting",
        "sportId": 1
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        splits = data.get("stats", [{}])[0].get("splits", [])
        if splits:
            return int(splits[0].get("stat", {}).get("homeRuns", 0))
    except Exception as e:
        print(f"  Warning: Could not fetch HR for player ID {player_id}: {e}")
    return None

def search_player(name):
    """Search for a player by name to get their MLB ID."""
    url = f"{MLB_API_BASE}/people/search"
    params = {"names": name, "sportId": 1}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        people = data.get("people", [])
        if people:
            return people[0].get("id")
    except Exception as e:
        print(f"  Warning: Could not find player '{name}': {e}")
    return None

def main():
    print("Loading players.json...")
    with open(PLAYERS_FILE, "r") as f:
        players = json.load(f)

    active_players = [p for p in players if p.get("active")]
    print(f"Found {len(active_players)} active players to update.")

    updated_count = 0
    errors = []

    for i, player in enumerate(players):
        if not player.get("active"):
            continue

        name = player["name"]
        print(f"  [{i+1}/{len(players)}] Fetching: {name}...", end=" ")

        # Search for the player to get their MLB ID
        mlb_id = search_player(name)
        if not mlb_id:
            print(f"NOT FOUND")
            errors.append(name)
            continue

        # Get career HR
        career_hr = get_career_hr(mlb_id)
        if career_hr is None:
            print(f"HR FETCH FAILED")
            errors.append(name)
            continue

        old_hr = player.get("hr", 0)
        if career_hr != old_hr:
            player["hr"] = career_hr
            updated_count += 1
            print(f"Updated: {old_hr} → {career_hr} HR")
        else:
            print(f"No change ({career_hr} HR)")

        # Be polite to the API — small delay between requests
        time.sleep(0.3)

    print(f"\n✅ Update complete: {updated_count} players updated.")
    if errors:
        print(f"⚠️  Could not update {len(errors)} players: {', '.join(errors)}")

    print("Writing updated players.json...")
    with open(PLAYERS_FILE, "w") as f:
        json.dump(players, f, indent=2)

    print("Done.")

    # Exit with error code if too many failures (more than 20%)
    if len(errors) > len(active_players) * 0.2:
        print("ERROR: Too many update failures. Check MLB API availability.")
        sys.exit(1)

if __name__ == "__main__":
    main()
