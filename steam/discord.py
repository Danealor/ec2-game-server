import requests
import os

WEBHOOK_URL = os.environ('DISCORD_WEBHOOK_URL', "DISCORD_DISABLED")

def discord(msg):
    if WEBHOOK_URL == "DISCORD_DISABLED":
        return
    data = { "content": msg }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 200:
        print(f"Discord webhook sent: {msg}")
    else:
        print(f"Error sending webhook: {response.status_code}")
