#!/usr/bin/env python3

from pydoc import plain
import pandas as pd
from io import StringIO
import subprocess
import os
from steam import SteamQuery

from discord import discord
from rcon import rcon

HISTORY_FILE_PATH = 'PlayerHistory.csv'
RECENT_HIST_MINUTES = 13 # Contains three 5-minute ticks (0, 5, 10 min ago)
RECENT_HIST_MIN_MINUTES = 9 # Need to have at least 9 minutes of history
STORE_HIST_DAYS = 3 # Store 3 days of history, cause why not
STEAM_QUERY_PORT = 15637

# Example using RCON for PalWorld
def get_players_palworld():
    with rcon() as client:
        response = client.run('ShowPlayers')
    return pd.read_csv(StringIO(response)) if response else []

def get_players_steam():
    server = SteamQuery("localhost", STEAM_QUERY_PORT)
    return server.query_server_info()['players']

def get_players():
    return get_players_steam()

def get_history():
    schema = {'time': 'datetime64[ns]', 'numPlayers': 'int'}
    try:
        hist = pd.read_csv(HISTORY_FILE_PATH, parse_dates=['time'])
    except:
        hist = pd.DataFrame(columns=schema.keys()).astype(schema)
    return hist

def update_history():
    players_df = get_players()
    num_players = len(players_df)
    hist = get_history()
    hist.loc[len(hist)] = (pd.Timestamp.now(), num_players)
    store_hist = hist[hist['time'] > pd.Timestamp.now() - pd.Timedelta(days=STORE_HIST_DAYS)]
    store_hist.to_csv(HISTORY_FILE_PATH, index=False)
    return hist

def check_empty():
    hist = update_history()
    recent_hist = hist[hist['time'] > pd.Timestamp.now() - pd.Timedelta(minutes=RECENT_HIST_MINUTES)]
    recently_empty = (recent_hist['numPlayers'] == 0).all()
    have_recent_hist = (pd.Timestamp.now() - recent_hist['time']).max() > pd.Timedelta(minutes=RECENT_HIST_MIN_MINUTES)
    print(f"Recently empty: {recently_empty}")
    print(f"Have recent history: {have_recent_hist}")
    if recently_empty and have_recent_hist:
        print("Server was recently continuously empty!")
        discord("It's so lonely here... guess I'll just go to sleep :sleepy:\n" +
                "Nobody was online for the past 15min. Shutting the server machine down.\n" +
                "To reboot, err, ping Dane.")
        shutdown_server()

def shutdown_server():
    print("Shutting down server...")
    with rcon() as client:
        client.run('Save')
        client.run('DoExit')
    subprocess.run(['supervisorctl', 'stop', 'palworld-server'])
    
    print("Shutting down instance...")
    os.system("shutdown now -h")

if __name__ == '__main__':
    check_empty()
