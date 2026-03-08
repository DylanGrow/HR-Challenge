"""
update_stats.py
Fetches current season + career HR totals for active players from the free MLB Stats API.
Runs as a GitHub Action to keep players.json fresh.
"""

import json
import os
import requests
import time
import sys
from datetime import datetime, timezone

PLAYERS_FILE = "players.json"
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


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
        log(f"    No career hitting splits returned for player ID {player_id}")
    except requests.exceptions.Timeout:
        log(f"    TIMEOUT fetching HR for player ID {player_id}")
    except requests.exceptions.HTTPError as e:
        log(f"    HTTP {e.response.status_code} fetching HR for player ID {player_id}")
    except Exception as e:
        log(f"    ERROR fetching HR for player ID {player_id}: {type(e).__name__}: {e}")
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
        log(f"    No results from people/search for '{name}'")
    except requests.exceptions.Timeout:
        log(f"    TIMEOUT searching for '{name}'")
    except requests.exceptions.HTTPError as e:
        log(f"    HTTP {e.response.status_code} searching for '{name}'")
    except Exception as e:
        log(f"    ERROR searching for '{name}': {type(e).__name__}: {e}")
    return None


def main():
    log("=" * 50)
    log("update_stats.py — starting")
    log(f"Python {sys.version}")
    log(f"Working directory: {os.getcwd()}")
    log(f"Players file: {os.path.abspath(PLAYERS_FILE)}")
    log(f"API base: {MLB_API_BASE}")

    # Connectivity check
    try:
        r = requests.get(f"{MLB_API_BASE}/sports/1", timeout=10)
        r.raise_for_status()
        log(f"API connectivity check: OK (HTTP {r.status_code})")
    except Exception as e:
        log(f"API connectivity check: FAILED — {type(e).__name__}: {e}")
        log("The MLB Stats API may be down. Aborting.")
        sys.exit(1)

    log(f"Loading {PLAYERS_FILE}...")
    with open(PLAYERS_FILE, "r") as f:
        players = json.load(f)
    log(f"Loaded {len(players)} total players.")

    active_players = [p for p in players if p.get("active")]
    log(f"Found {len(active_players)} active players to update.")

    if not active_players:
        log("No active players found. Nothing to do.")
        return

    updated_count = 0
    skipped_count = 0
    errors = []

    for i, player in enumerate(players):
        if not player.get("active"):
            continue

        name = player["name"]
        print(f"  [{skipped_count + updated_count + len(errors) + 1}/{len(active_players)}] {name}...", end=" ", flush=True)

        mlb_id = search_player(name)
        if not mlb_id:
            print("NOT FOUND")
            errors.append({"name": name, "reason": "player not found in search"})
            continue

        career_hr = get_career_hr(mlb_id)
        if career_hr is None:
            print("HR FETCH FAILED")
            errors.append({"name": name, "reason": "career HR fetch failed", "mlb_id": mlb_id})
            continue

        old_hr = player.get("hr", 0)
        if career_hr != old_hr:
            player["hr"] = career_hr
            updated_count += 1
            print(f"UPDATED: {old_hr} -> {career_hr} HR")
        else:
            skipped_count += 1
            print(f"unchanged ({career_hr} HR)")

        time.sleep(0.3)

    log("=" * 50)
    log(f"Results: {updated_count} updated, {skipped_count} unchanged, {len(errors)} failed")

    if errors:
        log(f"Failed players ({len(errors)}):")
        for err in errors:
            log(f"  - {err['name']}: {err['reason']}")

    log(f"Writing {PLAYERS_FILE}...")
    with open(PLAYERS_FILE, "w") as f:
        json.dump(players, f, indent=2)

    file_size = os.path.getsize(PLAYERS_FILE)
    log(f"Written successfully ({file_size:,} bytes)")

    error_rate = len(errors) / len(active_players) if active_players else 0
    log(f"Error rate: {error_rate:.1%} ({len(errors)}/{len(active_players)})")

    if error_rate > 0.2:
        log("FATAL: Error rate exceeds 20%. The MLB API may be unavailable or returning unexpected data.")
        log("Check https://statsapi.mlb.com/api/v1/sports/1 manually to verify.")
        sys.exit(1)

    log("Done — update_stats.py finished successfully")


if __name__ == "__main__":
    main()
