import discord
import data.config as config
from data.config import table_flag
from bot.bot_instance import bot
from datetime import datetime
import requests
import json
from decouple import config as env
import db_functions
db_path = env('DB_PATH')
url = env('URL')

async def raid_name_autocompletion(interaction: discord.Interaction, current: str, person_name: str) -> list:
    raid_names = await fetch_raid_names(current, person_name)
    if raid_names is None:
        return ['No raids of that name found.']
    choices = [discord.app_commands.Choice(name=str(name).replace('(','').replace(')',''), value=int(name[0])) for name in raid_names]
    return choices

async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    person_names = await fetch_raider_names(current)
    if person_names is None:
        return ['ERROR: helper.add_person_to_raid.person_name_autocompletion(): no names found.']
    choices = [discord.app_commands.Choice(name=name, value=name) for name in person_names]
    return choices

# NOTE: Disabled temporarily
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

# NOTE:Possibly add DATE:
def award_loot_embed(item_name: str, icon_id: int, person_name: str, raid_name: str) -> list:
        embed = discord.Embed(title='/award_loot', description='Loot awarded:', color=discord.Color.random())
        file_name = f'Item_{icon_id}.png'
        file_path = f'./data/icons/{file_name}'
        file = discord.File(file_path, filename=file_name)
        embed.set_thumbnail(url=f'attachment://{file_name}')
        embed.add_field(name='Item Name', value=item_name)
        embed.add_field(name='Person Name', value=person_name)
        embed.add_field(name='Raid ', value=raid_name)
        return [embed, file]
# NOTE:Possibly add DATE:
def remove_loot_embed(item_name: str, icon_id: int, person_name: str, raid_name: str) -> list:
        embed = discord.Embed(title='/remove_loot', description='Loot removed:', color=discord.Color.random())
        file_name = f'Item_{icon_id}.png'
        file_path = f'./data/icons/{file_name}'
        file = discord.File(file_path, filename=file_name)
        embed.set_thumbnail(url=f'attachment://{file_name}')
        embed.add_field(name='Item Name', value=item_name)
        embed.add_field(name='Person Name', value=person_name)
        embed.add_field(name='Raid ', value=raid_name)
        return [embed, file]
# NOTE: Need to pass channel member list to this embed
def add_raid_embed(raid_name: str, raiders: list):
    embed = discord.Embed(title='/add_raid_event', description='Raid event created:', color=discord.Color.random())
    embed.set_thumbnail(url=f'{config.froak_icon}')
    embed.add_field(name='Raid Name', value=raid_name)
    embed.add_field(name='Date', value=datetime.now().strftime("%m-%d-%Y"))
    embed.add_field(name='Raiders', value=", ".join(raiders))
    return embed

# Refactor 'most_populated_channel' to list, and allow user to pick
async def get_most_populated_channel(guild):
    max_members = 0
    most_populated_channel = None
    raiders = []
    for channel in guild.channels:
        if isinstance(channel, discord.VoiceChannel):
            member_count = len(channel.members)
            if member_count > max_members:
                raiders = [member.display_name for member in channel.members]
                usernames = [member.name for member in channel.members]
                max_members = member_count
                most_populated_channel = channel

    if most_populated_channel:
        print(f"The most populated voice channel is {most_populated_channel.name} with {len(most_populated_channel.members)} members.")
        print('Raiders: ', str(raiders))
        print('Usernames: ', str(usernames))
        return [raiders, usernames]
    else:
        print("There are no members in any voice channels.")
        return [None, None]
    
# If person_name is None, we return all raid names (Possibly need to limit this eventually)
async def fetch_raid_names(raid_name: str, person_name: str = None):
    try:
        raid_name = f'{raid_name}%'
        c = bot.db_connection.cursor()
        if person_name:
            person_name = f'{person_name}%'
            print('helper.fetch_raid_names() person_name NOT NULL:')
            print(f'helper.fetch_raid_names() person_name LIKE var: {person_name}')
            # First, SELECT username FROM dkp a INNER JOIN person b ON a.username = b.username WHERE b.person LIKE ?
            # c.execute(f'''SELECT * FROM raid_master{table_flag} a
            #              INNER JOIN dkp{table_flag} b ON a.raid_id = b.raid_id
            #              WHERE a.raid_name LIKE ? AND b.person_name LIKE ?''', (raid_name, person_name,))
            
            c.execute(f'''SELECT * FROM raid_master{table_flag} a
                          INNER JOIN dkp{table_flag} b ON a.raid_id = b.raid_id
                          WHERE b.username IN (
                          SELECT p.username FROM person{table_flag} p INNER JOIN dkp{table_flag} d
                          ON p.username = d.username 
                          AND p.person_name LIKE ?
                          )''', (person_name,))
            
            bot.db_connection.commit()
            results = c.fetchall()
            print('helper.fetch_raid_names() 2')
            print(f'helper.fetch_raid_names() results: {results}')
            if results:
                print('helper.fetch_raid_names() 3')
                results = [result for result in results]
                return results
            else:
                print('No results found (helper.fetch_raid_names)')
                return None
        else:
            print('helper.fetch_raid_names() person_name IS NULL:')
            c.execute(f'''SELECT * FROM raid_master{table_flag} WHERE raid_name LIKE ?''', (raid_name,))
            bot.db_connection.commit()
            results = c.fetchall()
            if results:
                results = [result for result in results]
                return results
            else:
                print('No results found (fetch_raid_names)')
                return None
    #NOTE: Why are we returning None instead of exception?
    except Exception as e:
        print('EXCEPTION: helper.fetch_raid_names()', str(e))
        return None
# NOTE: Refactor to fetch_person_names?
async def fetch_raider_names(person_name: str):
    try:
        like_pattern = f'{person_name}%'
        conn = bot.db_connection
        c = conn.cursor()
        c.execute(f'''
                SELECT person_name FROM person{table_flag} WHERE relation = 1 AND person_name LIKE ?
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

# Possibly refactor first condition to = instead of LIKE
# Possibly not the best practice for error handling, we are returning 'Couldnt find item' string , and searching substring at the caller level, perhaps try to return some sort of exception instead of string
# ^^ Or, return empty string or None instead of 'Couldnt find item' string
async def item_search(item_name: str) -> tuple:
    error = None
    if item_name:
        try:
            db_functions.create_levenshtein_function(bot)
            c = bot.db_connection.cursor()
            # Attempt to find exact string match first:
            c.execute('''SELECT name, icon FROM items_master WHERE name LIKE ?''', (item_name,))
            results = c.fetchall()
            if results and results[0][0] and results[0][1]:
                print('Exact string found:')
                item_name = results[0][0]
                icon_id = results[0][1]
                send_message_to_website(f'Item found: {results[0][1]}')
                return (item_name, icon_id)
            else:
                c.execute('''SELECT subquery.name, icon
                    FROM (
                    SELECT name, icon FROM items_master WHERE name LIKE ? || '%'
                    ) AS subquery
                    WHERE levenshtein(subquery.name, ?) <= 20;''', (item_name, item_name))
                results = c.fetchall()
                if results and results[0][0] and results[0][1]:
                    print('Levenshtein search:')
                    item_name = results[0][0]
                    icon_id = results[0][1]
                    send_message_to_website(f'Item found: {item_name}')
                    return (item_name, icon_id)
                else:
                    return (f'Couldnt find item: "{item_name}"', error)
        except Exception as e:
            error_message = f'EXCEPTION: helper.item_search(): {str(e)}'
            print(error_message)
            return (error_message, error_message)

async def print_large_message(interaction: object, result: str) -> str:
     for i in range(0, len(result), 1994):
                chunk = result[i : i + 1994]
                chunk = "```" + chunk + "```"
                await interaction.followup.send(chunk)