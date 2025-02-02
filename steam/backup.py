#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import zipfile

from discord import discord
from rcon import rcon

def msg(client, msg):
    client.run('Broadcast', msg.replace(' ', '\t'))

def backup_folder(source_path, backups_dir, max_backups):
    # Prepare server
    #discord("Backing up the server here, don't mind me...")
    with rcon() as client:
        msg(client, 'Saving world for backup...')
        save_resp = client.run('Save')
        if save_resp == 'Complete Save\n':
            msg(client, 'Save Complete! Backing up now...')
        else:
            msg(client, 'Unable to complete save, backing up anyways...')

    # Get the current time in ISO format
    current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    backup_filename = f'Backup_{current_time}.zip'

    # Create the backup directory if it doesn't exist
    os.makedirs(backups_dir, exist_ok=True)

    # Compress the source folder into a zip file
    with zipfile.ZipFile(os.path.join(backups_dir, backup_filename), 'w', zipfile.ZIP_DEFLATED) as backup_zip:
        for root, dirs, files in os.walk(source_path):
            for file in files:
                backup_zip.write(os.path.join(root, file))

    print(f'Successfully backed up {source_path} to {os.path.join(backups_dir, backup_filename)}')

    # Delete the oldest backup if there are more than max_backups
    backups = [f for f in os.listdir(backups_dir) if f.startswith('Backup_') and f.endswith('.zip')]
    if len(backups) > max_backups:
        backups.sort()
        oldest_backup = backups[0]
        os.remove(os.path.join(backups_dir, oldest_backup))
        print(f'Deleted oldest backup: {oldest_backup}')

    # Let them know we did it
    #discord("Server is backed up! Carry on :3")
    with rcon() as client:
        msg(client, 'Backup Complete!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backup a folder to a zip file')
    parser.add_argument('config_file', help='JSON configuration file containing source path and backups directory')
    args = parser.parse_args()

    # Load the configuration file
    with open(args.config_file) as f:
        config = json.load(f)

    # Backup the folder
    backup_folder(config['source_path'], config['backups_dir'], config['max_backups'])
