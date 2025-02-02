#!/usr/bin/env bash

PUBLIC_IP=$(curl -s https://api.ipify.org)
QUERY_PORT=15637

send_discord_message() {
    JSON_DATA="{\"content\": \"$@\"}"
    curl -X POST -H "Content-Type: application/json" -d "$JSON_DATA" "$DISCORD_WEBHOOK_URL"
}

send_discord_message "Hiya friends! I am starting up the server..."
steamcmd +@sSteamCmdForcePlatformType windows +force_install_dir /home/steam/Enshrouded +login anonymous +app_update 2278520 +quit
sleep 5 && send_discord_message "The Enshrouded server is started!\nConnect using \`${PUBLIC_IP}:${QUERY_PORT}\` 😸" &
wine64 /home/steam/Enshrouded/enshrouded_server.exe
send_discord_message "Enshrouded server has been shut down.\nIf this was a crash, I'll start it back up in a jiffy!"
