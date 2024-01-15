# V2 (clas commands API)
from data.char_classes import class_names, emojis
from decouple import config as env
import json
import datetime
import requests
import pytesseract
import pytesseract
import helper
from datetime import datetime
from PIL import Image
from io import BytesIO
import re
from bot.bot_instance import bot
import db_functions
db_path = env('DB_PATH')
url = env('URL')

# Move this to helper.py
def send_message_to_website(message: dict=None, image_url=None):
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
            print(str(e))
            return str(e)
    
async def add_person(person_name: str, relation: str, guild: str) -> object:
    if relation.lower() in ['enemy', 'foe', 'opponent']:
        relation = 0
    elif relation.lower() in ['friend', 'friendly', 'pal']:
        relation = 1
    elif relation.lower() in ['neutral']:
        relation = 2
    else:
        return 'Invalid input. Please enter "friendly", "enemy", or "neutral"'
    
    person_name = person_name.title()
    guild = guild.title()
    
    try:
        c = bot.db_connection.cursor()
        c.execute(
            """INSERT INTO person (person_name, relation, guild) VALUES (?, ?, ?)""",
            ((person_name, relation, guild)),
        )
        bot.db_connection.commit()
        message = (
            f'```Player "{person_name}" successfully inserted into "person" table.```'
        )
        send_message_to_website(message)
        return helper.add_person_embed(person_name, relation, guild)
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            message = f'```Person "{person_name}" already exists in table "person" table. Aborting insert.```'
            send_message_to_website(message)
            return message
        else:
            print("SQLite error, database.add_person():")
            print(e)
            return str(e)
      
async def add_character(character_name: str, character_class: str, level: int, person_name: str) -> str:
    if character_class.lower() == "mage":
        character_class = "Magician"
    if character_class.lower() in ['shadowknight', 'shadow knight']:
        character_class = "Shadowknight"
    
    if character_class.title() not in class_names:
        return f'Invalid input. Please provide a valid class name: {str(class_names)}'
    
    try:
        c = bot.db_connection.cursor()
        c.execute("SELECT * FROM person WHERE person_name = ?", (person_name,))
        if not c.fetchall():
            message = f'```Person "{person_name}" does not exist in "person" table. Please create a "person" entry first. Aborting insert.```'
            send_message_to_website(message)
            return message

        c.execute("SELECT * FROM character WHERE char_name = ?", (character_name,))
        if c.fetchall():
            message = (
                f'```Character "{character_name}" already exists in table "character". Aborting insert.```'
            )
            send_message_to_website(message)
            return message

        c.execute(
            "INSERT INTO character (char_name, char_class, person_name, level) VALUES (?, ?, ?, ?)",
            (character_name, character_class, person_name, level),
        )
        bot.db_connection.commit()

        c.execute("SELECT * FROM character WHERE char_name = ?", (character_name,))
        result = c.fetchone()

        if result:
            message = f'```Character "{character_name}" inserted successfully: {result}```'
            send_message_to_website(message)
            return helper.add_character_embed(character_name, character_class, level, person_name)

    except Exception as e:
        print("SQLite error, database.add_char():")
        print(e)
        return str(e)
        
async def delete_person(person_name: str) -> str:
    person_name = person_name.title()
    try:
        c = bot.db_connection.cursor()
        c.execute("""DELETE FROM person WHERE person_name = ?""", (person_name,))
        bot.db_connection.commit()
        if c.rowcount > 0:
            message = f'```Person "{person_name}" successfully deleted!```'
            send_message_to_website(message)
            return message
        else:
            message = f'```Person "{person_name}" does not exist```'
            send_message_to_website(message)
            return message
    except Exception as e:
        print(e)
        return str(e)

async def delete_character(character_name: str) -> str:
    character_name = character_name.title()
    try:
        c = bot.db_connection.cursor()
        c.execute("""DELETE FROM character WHERE char_name = ?""", (character_name,))
        bot.db_connection.commit()

        if c.rowcount > 0:
            message = f'```Character "{character_name}" successfully deleted!```'
            send_message_to_website(message)
            return message
        else:
            message = f'```Character "{character_name}" does not exist.```'
            send_message_to_website(message)
            return message

    except Exception as e:
        print(e)
        return str(e)
        
async def edit_person(person_name: str, person_name_new: str, relation: str, guild: str) -> str:
    if relation.lower() in ['enemy', 'foe', 'opponent']:
        relation = 0
    elif relation.lower() in ['friend', 'friendly', 'pal']:
        relation = 1
    elif relation.lower() in ['neutral']:
        relation = 2
    else:
        return 'Invalid input. Please enter "friendly", "enemy", or "neutral"'
    
    person_name = person_name.title()
    person_name_new = person_name_new.title()
    guild = guild.title()

    try:
        c = bot.db_connection.cursor()
        c.execute(
            """SELECT * FROM person WHERE person_name = ?""", (person_name,)
        )
        results = c.fetchall()
        bot.db_connection.commit()

        if not results:
            message = f'```Person "{person_name}" does not exist in "person" table. Aborting EDIT.```'
            send_message_to_website(message)
            return message

    except Exception as e:
        print("SQLite error, bot_commands.edit_char():")
        print(e)
        return e

    try:
        c.execute(
            """UPDATE person SET person_name = ?, relation = ?, guild = ? WHERE person_name = ?""",
            (person_name_new, relation, guild, person_name),
        )
        results = c.fetchall()
        bot.db_connection.commit()
        
        if relation == 0:
            relation = "Enemy"
        if relation == 1:
            relation = "Friendly"
        if relation == 2:
            relation = "Neutral"
        message = f"```Person CHANGED: person_name = {person_name_new}, relation = {relation}, guild = {guild}```"
        send_message_to_website(message)
        return message
    except Exception as e:
        print(e)
        return str(e)

async def edit_character(character_name: str, character_name_new: str, character_class: str, level: int, person_name: str) -> str:
    character_name = character_name.title()
    character_name_new = character_name_new.title()
    person_name = person_name.title()

    if character_class.lower() == "mage":
        character_class = "Magician"
    if character_class.lower() in ['shadowknight', 'shadow knight']:
        character_class = "Shadowknight"
    if character_class.title() not in class_names:
        return f'Invalid input. Please provide a valid class name: {str(class_names)}'

    try:
        
        c = bot.db_connection.cursor()
        c.execute(
            """SELECT * FROM character WHERE char_name = ?""", (character_name,)
        )
        results = c.fetchall()

        if not results:
            message = f'```Character "{character_name}" does not exist in "character" table. Aborting EDIT.```'
            send_message_to_website(message)
            return message

    except Exception as e:
        print("SQLite error, bot_commands.edit_char():")
        print(e)
        return e

    try:
        c.execute(
            """UPDATE character SET char_name = ?, char_class = ?, person_name = ?, level = ? WHERE char_name = ?""",
            (character_name_new, character_class, person_name, level, character_name),
        )
        results = c.fetchall()
        bot.db_connection.commit()
        message = f"```Character CHANGED: char_name = {character_name_new}, char_class = {character_class}, person_name = {person_name}, level = {level}```"
        send_message_to_website(message)
        return message
    except Exception as e:
        print(e)
        return str(e)
    
async def who(character_name: str) -> str:
    character_name = character_name.title()

    try:
        c = bot.db_connection.cursor()
        c.execute("""SELECT * FROM character WHERE char_name = ?""", (character_name,))
        results = c.fetchone()

        if results is None:
            message = f'```Character "{character_name}" doesnt exist in "character" table```'
            send_message_to_website(message)
            return message
        char_class = results[1]
        person_name = results[2]

        c2 = bot.db_connection.cursor()
        c2.execute("""SELECT * from person WHERE person_name = ?""", (person_name,))
        results = c2.fetchone()

        if results is None:
            message = f'```Person "{person_name} doesnt exist in "person" table```'
            send_message_to_website(message)
            return message

        if results[1] == 0:
            relation = "Enemy"
        if results[1] == 1:
            relation = "Friendly"
        if results[1] == 2:
            relation = "Neutral"
        results_string = f"```Character: {character_name}, Class: {char_class}```"
        results_string += f'```Person info for "{character_name}": Person: {results[0]}, Relation: {relation}, Guild: {results[2]}```'
        send_message_to_website(results_string)
        return results_string

    except Exception as e:
        print(e)
        return str(e)

async def get_characters(person_name: str) -> str:
    person_name = person_name.title()
    try:
        c = bot.db_connection.cursor()
        c.execute(
            """SELECT * FROM character WHERE person_name = ?""", (person_name,)
        )
        results = c.fetchall()
        sorted_results = sorted(results, key=lambda result: result[0])
        formatted_characters = ""

        for result in sorted_results:
            char_name, char_class, person_name, level = result
            row = f"Character: {char_name}, Class: {char_class}, Person: {person_name}, Level: {level}"
            formatted_characters += row
            formatted_characters += "\n"
        send_message_to_website(formatted_characters)
        return "```" + formatted_characters + "```"
    except Exception as e:
        print(e)
        return str(e)
    
async def get_person_table(guild: str) -> str:
    if guild:
        guild = guild.title()
        try:
            c = bot.db_connection.cursor()
            c.execute("""SELECT * FROM person WHERE guild = ?""", (guild,))
            results = c.fetchall()
            sorted_results = sorted(results, key=lambda result: result[0])
            results_string = ""
            for result in sorted_results:
                results_string += (
                    str(result)
                    .replace("'", "")
                    .replace("(", "")
                    .replace(")", "")
                    .replace("0", "Enemy")
                    .replace("1", "Friendly")
                    .replace("2", "Neutral")
                )
                results_string += "\n"
            send_message_to_website(results_string)
            results_string = "```" + results_string + "```"
            return results_string
        except Exception as e:
            print(e)
            return str(e)
    else:
        try:
            c = bot.db_connection.cursor()
            c.execute("""SELECT * FROM person""")
            results = c.fetchall()
            sorted_results = sorted(results, key=lambda result: result[0])
            results_string = ""
            for result in sorted_results:
                results_string += (
                    str(result)
                    .replace("'", "")
                    .replace("(", "")
                    .replace(")", "")
                    .replace("0", "Enemy")
                    .replace("1", "Friendly")
                    .replace("2", "Neutral")
                )
                results_string += "\n"
            results_string = "```" + results_string + "```"
            send_message_to_website(results_string)
            return results_string
        except Exception as e:
            print(e)
            return str(e)
        
async def get_characters_table(guild: str, character_class: str) -> str:
    if guild:
        guild = guild.title()
    if character_class:
        character_class = character_class.title()
    if character_class and character_class.lower() == "mage":
        character_class = "Magician"
    if character_class and character_class.lower() in ['shadowknight', 'shadow knight']:
        character_class = "Shadowknight"
    if character_class and character_class not in class_names:
        return f'Invalid input. Please provide a valid class name: {str(class_names)}'

    try:
        c = bot.db_connection.cursor()
        if character_class and guild:
            c.execute(
                """SELECT * FROM character
                         WHERE char_class = ? AND person_name IN (SELECT person_name FROM person WHERE guild = ?)
                         """,
                (character_class, guild),
            )
        elif character_class:
            c.execute(
                """SELECT * FROM character WHERE char_class = ?""", (character_class,)
            )
        elif guild:
            c.execute(
                """SELECT * FROM character
                         WHERE person_name IN (SELECT person_name FROM person WHERE guild = ?)
                         """,
                (guild,),
            )
        else:
            c.execute("SELECT * FROM character")
        results = c.fetchall()
    except Exception as e:
        print(e)
        return str(e)

    sorted_results = sorted(results, key=lambda result: result[0])
    results_string = ''
    for result in sorted_results:
        char_name, char_class, person_name, level = result
        row = f"{char_name}, {char_class}, {person_name}, {level}"
        results_string += row + "\n"
    results_string = "```" + results_string + "```"
    send_message_to_website(results_string)
    print(results_string)
    return results_string

async def parse_image(message: dict):
    
    if (
        message.attachments
        and message.content
        and message.content[:5].lower() == "!snip"
    ):
        for attachment in message.attachments:
            if attachment.width and attachment.height:
                image_raw = await attachment.read()
                image = Image.open(BytesIO(image_raw))
                image_url = attachment.url
                extracted_text = pytesseract.image_to_string(image)

    pattern = r"\[[^\]]+\] ([^\s<]+)"
    char_names = re.findall(pattern, extracted_text)

    for i in range(len(char_names)):
        original_name = char_names[i]
        char_name = original_name.strip()
        char_name = (
            char_name.replace(".", "")
            .replace(",", "")
            .replace("'", "")
            .replace("’", "")
        )
        char_names[i] = char_name

    try:
        c = bot.db_connection.cursor()
        placeholders = ",".join(["?"] * len(char_names))
        query = f"""SELECT a.char_name, a.char_class, a.person_name, a.level, b.relation 
            FROM character a INNER JOIN person b 
            ON a.person_name = b.person_name 
            WHERE char_name IN ({placeholders})"""

        c.execute(query, char_names)
        results = c.fetchall()
        # A diffrent output to send to the website:
        website_string = ''
        formatted_string = ""
        friendly_chars = []
        friendly_char_names = []
        enemy_chars = []
        enemy_char_names = []
        unknown_char_names = []
        friendly_count = 0
        enemy_count = 0
        unknown_count = 0
        friendly_class_comp = {}
        enemy_class_comp = {}

        for result in results:
            result = list(result)
            char_name, char_class, person_name, level, relation = result
            if relation == 0:
                enemy_chars.append([char_name, char_class, level])
                enemy_char_names.append(char_name)
            elif relation == 1:
                friendly_chars.append([char_name, char_class, level])
                friendly_char_names.append(char_name)

        # Find the 'Unknown' characters:
        for char in char_names:
            if char not in friendly_char_names and char not in enemy_char_names:
                unknown_count += 1
                unknown_char_names.append(char)

        enemy_chars.sort(key=lambda x: x[1])
        friendly_chars.sort(key=lambda x: x[1])

        for char in enemy_chars:
            print(emojis[char[1]])
            formatted_string += f"""```ansi
{char[0]}: [0;31;40m{char[1]}{emojis[char[1]]}```"""
            website_string = formatted_string
        for char in friendly_chars:
            print(emojis[char[1]])
            formatted_string += f"""```ansi
{char[0]}: [0;36;40m{char[1]}{emojis[char[1]]}```"""
            website_string = formatted_string
        for char in unknown_char_names:
            formatted_string += f"""```ansi
{char}: [0;37;40mUNKNOWN```"""
            website_string += formatted_string
        # Get the class comps:
        for char in enemy_chars:
            char_class = char[1]
            enemy_count += 1
            if char_class not in enemy_class_comp:
                enemy_class_comp[char_class] = 1
            else:
                enemy_class_comp[char_class] += 1

        for char in friendly_chars:
            char_class = char[1]
            friendly_count += 1
            if char_class not in friendly_class_comp:
                friendly_class_comp[char_class] = 1
            else:
                friendly_class_comp[char_class] += 1

        # Send char + class list:
        if len(formatted_string) > 1994:
            for i in range(0, len(formatted_string), 1994):
                chunk = formatted_string[i : i + 1994]
                chunk = "```" + chunk + "```"
                await message.channel.send(chunk)
            # send_message_to_website(formatted_string)
            website_string = formatted_string
        else:
            website_string = formatted_string
            # send_message_to_website(formatted_string)
            await message.channel.send(formatted_string)

        formatted_string = ""
        website_string += '\n'
        if enemy_class_comp:
            formatted_string += f"""**Enemy Classes:** \n"""
            website_string += f"""**Enemy Classes:** \n"""
            for char_class, count in sorted(
                enemy_class_comp.items(), key=lambda x: x[1], reverse=True
            ):
                formatted_string += (
                    f"""```{char_class}{emojis[char_class]}: {count}```"""
                )
                website_string += (
                    f"""```{char_class}{emojis[char_class]}: {count}```\n"""
                )

        if friendly_class_comp:
            formatted_string += f"""\n **Friendly Classes:** \n"""
            website_string += f"""\n **Friendly Classes:** \n"""

            for char_class, count in sorted(
                friendly_class_comp.items(), key=lambda x: x[1], reverse=True
            ):
                formatted_string += (
                    f"""```{char_class} {emojis[char_class]}: {count}```"""
                )
                website_string += (
                    f"""```{char_class} {emojis[char_class]}: {count}```\n"""
                )
        # Send class comp count
        send_message_to_website(website_string, image_url)
        await message.channel.send(formatted_string)
    except Exception as e:
        print(e)
        return str(e)
    
async def item_search(item_name: str) -> str:
    if item_name:
        try:
            db_functions.create_levenshtein_function(bot)
            c = bot.db_connection.cursor()
            # Attempt to find exact string match first:
            c.execute('''SELECT * FROM items_master WHERE name = ?''', (item_name,))
            results = c.fetchall()
            if results and results[0][1]:
                print('Exact string found:')
                print(results[0][1])
                send_message_to_website(f'Item found: {results[0][1]}')
                return results
            else:
                c.execute('''SELECT subquery.*
                    FROM (
                    SELECT * FROM items_master WHERE name LIKE ? || '%'
                    ) AS subquery
                    WHERE levenshtein(subquery.name, ?) <= 20;''', (item_name, item_name))
                results = c.fetchall()
                print('Query results: ' + str(results))
                if results and results[0][1]:
                    print('Levenshtein search:')
                    print(results[0][1])
                    send_message_to_website(f'Item found: {results[0][1]}' )
                if results:
                    return results
                else:
                    return f'Couldnt find item: "{item_name}"'
        except Exception as e:
            print(e)

async def register_person(person_name: str, discord_username: str):
    # Create a 'discord_username' table
    pass

async def add_raid_event(guild: object, raid_name: str):
    try:
        timestamp = datetime.now().strftime("%m-%d-%Y")
        raiders = await helper.get_most_populated_channel(guild)
        if raiders is None:
            return 'There are no members in any voice channels.'
        
        c = bot.db_connection.cursor()
        c.execute('''INSERT INTO raid_master_test (raid_name, raid_date) VALUES (?, ?)''', (raid_name, timestamp))
        raid_id = c.lastrowid
        
        raider_inserts = [(raider, raid_id, 1) for raider in raiders]
        c.executemany('''INSERT INTO dkp_test (person_name, raid_id, dkp_points) VALUES (?, ?, ?)''', raider_inserts)
        bot.db_connection.commit()
        return 'Raid successfully added'
    except Exception as e:
        print(e)
        return str(e)

async def add_person_to_raid(person_name: str, raid_id: int):
    try:
        c = bot.db_connection.cursor()
        c.execute('''INSERT INTO dkp_test (person_name, raid_id, dkp_points) VALUES (?, ?, ?)''', (person_name, raid_id, 1))
        bot.db_connection.commit()
        message = f'Person {person_name} added to raid: {raid_id}.'
        send_message_to_website(message)
        return message
    except Exception as e:
        print(e)
        return str(e)
    


    
    



        
    
