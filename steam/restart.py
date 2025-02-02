#!/usr/bin/env python3

from time import sleep
import subprocess

from discord_msg import discord
from rcon_msg import rcon

def msg(client, msg):
    client.run('Broadcast', msg.replace(' ', '\t'))

def restart_server():
    # Prepare server
    discord("Hiya friends! It's time for a scheduled restart.\n"+
            "I'll be restarting in 5 min, so just hop out of your dungeons or finish that boss :D")

    with rcon() as client:
        msg(client, 'Server scheduled restart in 5min...')

    sleep(3 * 60)

    with rcon() as client:
        msg(client, 'Server scheduled restart in 2min...')

    sleep(1 * 60)

    with rcon() as client:
        msg(client, 'Server scheduled restart in 1min...')

    sleep(30)

    with rcon() as client:
        msg(client, 'Server scheduled restart in 30sec...')

    sleep(20)

    with rcon() as client:
        msg(client, 'Server scheduled restart in 10sec!')

    sleep(10)
    
    with rcon() as client:
        msg(client, 'Saving world before restart...')
        save_resp = client.run('Save')
        if save_resp == 'Complete Save\n':
            msg(client, 'Save Complete! Restarting now...')
        else:
            msg(client, 'Unable to complete save, skipping restart.')
            msg(client, 'Alert server mod of following error:')
            msg(client, save_resp)
            return
        client.run('DoExit')

    discord("Restarting the server! See ya soon ;)")
    subprocess.run(['supervisorctl', 'restart', 'palworld-server'])
        

if __name__ == '__main__':
    restart_server()
