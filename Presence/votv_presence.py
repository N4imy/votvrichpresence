import os
import time

import psutil
from pypresence import Presence


CLIENT_ID = "1554800211958829086"

GAME_PROCESS = "VotV.exe"

STATE_FILE = (
    r"C:\Program Files (x86)\VotV\WindowsNoEditor"
    r"\Presence\presence_state.txt"
)

CHECK_INTERVAL = 2


def is_game_running():
    for process in psutil.process_iter(["name"]):
        try:
            if process.info["name"] == GAME_PROCESS:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return False


def read_game_state():
    if not os.path.exists(STATE_FILE):
        return None

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            text = file.read().strip()
    except OSError:
        return None

    if not text:
        return None

    if text == "menu":
        return {
            "state": "menu",
            "day": None,
            "time": None,
        }

    parts = text.split("|")

    if len(parts) != 3:
        return None

    return {
        "state": parts[0],
        "day": parts[1],
        "time": parts[2],
    }


rpc = None
game_start_time = None
last_presence = None


while True:

    running = is_game_running()

    # ------------------------------------------------
    # GAME CLOSED
    # ------------------------------------------------

    if not running:

        if rpc is not None:
            try:
                rpc.clear()
                rpc.close()
            except Exception:
                pass

        rpc = None
        game_start_time = None
        last_presence = None

        time.sleep(CHECK_INTERVAL)
        continue


    # ------------------------------------------------
    # CONNECT DISCORD RPC
    # ------------------------------------------------

    if rpc is None:

        try:
            rpc = Presence(CLIENT_ID)
            rpc.connect()

            game_start_time = int(time.time())
            last_presence = None

        except Exception:
            rpc = None

            time.sleep(CHECK_INTERVAL)
            continue


    # ------------------------------------------------
    # READ UE4SS STATE
    # ------------------------------------------------

    game = read_game_state()


    # ------------------------------------------------
    # GAME STARTING / UE4SS NOT READY
    # ------------------------------------------------

    if game is None:

        presence = (
            "Launching the game...",
            "Starting..."
        )


    # ------------------------------------------------
    # MAIN MENU
    # ------------------------------------------------

    elif game["state"] == "menu":

        presence = (
            "Main Menu",
            "Preparing..."
        )


    # ------------------------------------------------
    # PAUSED
    # ------------------------------------------------

    elif game["state"] == "paused":

        presence = (
            "Paused",
            f"Day {game['day']} — {game['time']}"
        )


    # ------------------------------------------------
    # PLAYING
    # ------------------------------------------------

    else:

        presence = (
            "Stargazing and facing the horrors...",
            f"Day {game['day']} — {game['time']}"
        )


    # ------------------------------------------------
    # UPDATE DISCORD ONLY WHEN SOMETHING CHANGED
    # ------------------------------------------------

    if presence != last_presence:

        try:

            details, state = presence

            rpc.update(
                details=details,
                state=state,
                start=game_start_time
            )

            last_presence = presence

        except Exception:

            try:
                rpc.close()
            except Exception:
                pass

            rpc = None
            last_presence = None


    time.sleep(CHECK_INTERVAL)