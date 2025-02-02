#!/usr/bin/env bash

# Parse command line arguments
INSTALL_WINE=false
RCON_ADMIN_PASSWORD="RCON_DISABLED"
DISCORD_WEBHOOK_URL="DISCORD_DISABLED"
while [[ $# -gt 0 ]]; do
    case $1 in
        --wine)
            INSTALL_WINE=true
            shift
            ;;
        --rcon)
            RCON_ADMIN_PASSWORD=$2
            shift
            shift
            ;;
        --discord)
            DISCORD_WEBHOOK_URL=$2
            shift
            shift
            ;;
        *)
            exit 1
            ;;
    esac
done

# Setup
sudo apt update
sudo apt upgrade -y
sudo apt install -y supervisor nginx python3 python-is-python3 python3-pip python3-venv
SCRIPT_DIR="$( dirname "$0" )"

# steamCMD configuration
sudo useradd -m steam
sudo add-apt-repository -y multiverse; sudo dpkg --add-architecture i386; sudo apt update
# https://stackoverflow.com/a/78004674
echo steam steam/question select "I AGREE" | sudo debconf-set-selections
echo steam steam/license note '' | sudo debconf-set-selections
sudo apt install -y steamcmd
# Copy our scripts over
sudo -u steam -s /bin/bash -c "echo 'export PATH=$PATH:/usr/games' >> /home/steam/.bashrc"
sudo cp $SCRIPT_DIR/steam/* /home/steam/

# Setup python
sudo -u steam -s /bin/bash -c "python -m venv /home/steam/venv && /home/steam/venv/bin/pip install -r /home/steam/requirements.txt"
sudo -u steam -s /bin/bash -c "echo 'export RCON_ADMIN_PASSWORD=$RCON_ADMIN_PASSWORD' >> /home/steam/.bashrc"
sudo -u steam -s /bin/bash -c "echo 'export DISCORD_WEBHOOK_URL=$DISCORD_WEBHOOK_URL' >> /home/steam/.bashrc"

if $INSTALL_WINE; then
  # Wine installation (https://github.com/bonsaibauer/enshrouded_server_ubuntu)
  sudo apt install -y software-properties-common lsb-release wget
  sudo mkdir -pm755 /etc/apt/keyrings
  sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
  sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/dists/$(lsb_release -cs)/winehq-$(lsb_release -cs).sources
  sudo dpkg --add-architecture i386
  sudo apt update
  sudo apt install -y --install-recommends winehq-staging
  sudo apt install -y cabextract winbind screen xvfb
fi

# nginx configuration
sudo cp $SCRIPT_DIR/nginx/supervisor.conf /etc/nginx/sites-available/supervisor.conf
sudo ln -s /etc/nginx/sites-available/supervisor.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# supervisor configuration
sudo cp $SCRIPT_DIR/supervisor/supervisord.conf /etc/supervisor/supervisord.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo systemctl enable supervisor

# crontab configuration
crontab -l > /tmp/crontab.tmp
cat $SCRIPT_DIR/crontab/cron >> /tmp/crontab.tmp
crontab /tmp/crontab.tmp
rm /tmp/crontab.tmp
