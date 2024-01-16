import discord
import data.config as config
from bot.bot_instance import bot
from datetime import datetime
import requests
import json
from decouple import config as env
db_path = env('DB_PATH')
url = env('URL')

def send_message_to_website(message: dict=None, image_url=None):
    return
    payload = {'date': str(datetime.now().strftime("%m-%d-%Y")), 
               'message': None, 
               'image_url': None}
    if message:
        message = (
            message.replace("[0;31;40m", "")
            .replace("[0;36;40m", "")
            .replace("[0;37;40m", "")
            .replace("ansi", "")
            .replace("`", "")
        )
        payload['message'] = message
    if image_url:
        payload['image_url'] = image_url
    if payload:
        try:
            response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            if response.status_code == 201:
                print('JSON payload sent successfully')
            else:
                print('Failed to send JSON payload.')
        except Exception as e:
            print('send_message_to_website() error:', str(e))
            return str(e)

def add_person_embed(person_name: str, relation: int, guild: str) -> object:
    if relation == 0:
        relation = "Enemy"
    if relation == 1:
        relation = "Friendly"
    if relation == 2:
        relation = "Neutral"
    embed = discord.Embed(title='/add_person', description='Person successfully added:', color=discord.Color.random())
    embed.set_thumbnail(url=f'{config.froak_icon}')
    embed.add_field(name='Person Name', value=person_name)
    embed.add_field(name='Relation', value=relation)
    embed.add_field(name='Guild', value=guild)
    return embed

def add_character_embed(character_name: str, character_class: str, level: int, person_name: str) -> object:
    embed = discord.Embed(title='/add_character', description='Character successfully added:', color=discord.Color.random())
    embed.set_thumbnail(url=f'{config.froak_icon}')
    embed.add_field(name='Character Name', value=character_name)
    embed.add_field(name='Character Class', value=character_class)
    embed.add_field(name='Level', value=level)
    embed.add_field(name='Person Name', value=person_name)
    return embed

async def get_most_populated_channel(guild):
    max_members = 0
    most_populated_channel = None
    raiders = []
    for channel in guild.channels:
        if isinstance(channel, discord.VoiceChannel):
            member_count = len(channel.members)
            if member_count > max_members:
                raiders = [member.global_name for member in channel.members]
                max_members = member_count
                most_populated_channel = channel

    if most_populated_channel:
        print(f"The most populated voice channel is {most_populated_channel.name} with {len(most_populated_channel.members)} members.")
        print('Raiders: ', str(raiders))
        return raiders
    else:
        print("There are no members in any voice channels.")
        return None
    
async def fetch_raid_names(raid_name: str):
    print('helper.fetch_raid_names() start')
    try:
        like_pattern = f'{raid_name}%'
        c = bot.db_connection.cursor()
        print('helper.fetch_raid_names() 1')
        c.execute('''SELECT * FROM raid_master_test WHERE raid_name LIKE ?''', (like_pattern,))
        bot.db_connection.commit()
        results = c.fetchall()
        print('helper.fetch_raid_names() 2')
        if results:
            print('helper.fetch_raid_names() 3')
            results = [result for result in results]
            return results
        else:
            print('helper.fetch_raid_names() 4')
            print('No results found (fetch_raid_names)')
            return None
    except Exception as e:
        print('fetch_raid_names() error:', str(e))
        return None

async def fetch_raider_names(person_name: str):
    try:
        like_pattern = f'{person_name}%'
        conn = bot.db_connection
        c = conn.cursor()
        c.execute('''
                SELECT person_name FROM person_test WHERE relation = 1 AND person_name LIKE ?
                ''', 
                (like_pattern,))
        conn.commit()
        results = c.fetchall()
        if results:
            print('fetch raider names results:')
            print(results)
            results = [result[0] for result in results]
            return results
        else:
            print('No names found for that raid.')
            return None
    except Exception as e:
        print('fetch_raider_names() error:', str(e))
        return str(e)