# V2 (slash commands API)
from data.char_classes import class_names, emojis
from decouple import config as env
from data.config import test_mode, tesseract
import pytesseract
import helper
from datetime import datetime
from PIL import Image
from io import BytesIO
import re
from bot.bot_instance import bot

db_path = env('DB_PATH')
url = env('URL')
pytesseract.pytesseract.tesseract_cmd = tesseract

async def add_person(person_name: str, relation: str, guild: str) -> tuple:
    try:
        exception = None
        if relation.lower() in ['enemy', 'foe', 'opponent']:
            relation = 0
        elif relation.lower() in ['friend', 'friendly', 'pal']:
            relation = 1
        elif relation.lower() in ['neutral']:
            relation = 2
        else:
            return ('❌ERROR: Invalid input. Please enter "friendly", "enemy", or "neutral"', None)
    
        person_name = person_name.title()
        guild = guild.title()

        conn = bot.db_connection
        c = conn.cursor()
        c.execute(
            f"""INSERT INTO person (person_name, relation, guild) VALUES (?, ?, ?)""",
            ((person_name, relation, guild)),
        )
        conn.commit()
        message = (
            f'```✅Player "{person_name}" successfully inserted into "person" table.```'
        )
        helper.send_message_to_website(message)
        
        return (helper.add_person_embed(person_name, relation, guild), None)
    except Exception as e:
        # Returning None value 'error' for UNIQUE constraint. Its not the type of bug I am looking for in the test.
        if "UNIQUE constraint failed" in str(e):
            message = f'```❌ERROR: Person "{person_name}" already exists in table "person" table. Aborting insert.```'
            helper.send_message_to_website(message)
            return (message, exception)
        else:
            exception = f"EXCEPTION: logic.add_person(): {str(e)}"
            print(exception)
            return (exception, exception)
      
async def add_character(character_name: str, character_class: str, level: int, person_name: str) -> tuple:
    try:
        exception = None
        character_name = character_name.title()
        if character_class.lower() == "mage":
            character_class = "Magician"
        if character_class.lower() in ['shadowknight', 'shadow knight']:
            character_class = "Shadowknight"

        if character_class.title() not in class_names:
            return (f'❌ERROR: Invalid input. Please provide a valid class name: {str(class_names)}', None)
        conn = bot.db_connection
        c = conn.cursor()
        c.execute(f"SELECT * FROM person WHERE person_name = ?", (person_name,))
        if not c.fetchall():
            message = f'```❌ERROR: Person "{person_name}" does not exist in "person" table. Please create a "person" entry first. Aborting insert.```'
            helper.send_message_to_website(message)
            return (message, exception)

        c.execute(f"SELECT * FROM character WHERE char_name = ?", (character_name,))
        if c.fetchall():
            message = (
                f'```❌ERROR: Character "{character_name}" already exists in table "character". Aborting insert.```'
            )
            helper.send_message_to_website(message)
            return (message, exception)

        c.execute(
            f"INSERT INTO character (char_name, char_class, person_name, level) VALUES (?, ?, ?, ?)",
            (character_name, character_class, person_name, level),
        )
        conn.commit()

        c.execute(f"SELECT * FROM character WHERE char_name = ?", (character_name,))
        result = c.fetchone()

        if result:
            message = f'```✅Character "{character_name}" inserted successfully: {result}```'
            helper.send_message_to_website(message)

            
            return (helper.add_character_embed(character_name, character_class, level, person_name), None)

    except Exception as e:
        exception = f'EXCEPTION: logic.add_char(): {str(e)}'
        print(exception)
        return (exception, exception)
        
async def delete_person(person_name: str) -> tuple:
    try:
        person_name = person_name.title()
        conn = bot.db_connection
        c = conn.cursor()
        c.execute(f"""DELETE FROM person WHERE person_name = ?""", (person_name,))
        conn.commit()
        if c.rowcount > 0:
            message = f'```✅Person "{person_name}" successfully deleted!```'
            helper.send_message_to_website(message)
            return (message, None)
        else:
            message = f'```✅Person "{person_name}" does not exist```'
            helper.send_message_to_website(message)
            return (message, None)
    except Exception as e:
        exception = f'EXCEPTION: logic.delete_person(): {str(e)}'
        print(exception)
        return(exception, exception)

async def delete_character(character_name: str) -> tuple:
    try:
        character_name = character_name.title()
        conn = bot.db_connection
        c = bot.db_connection.cursor()
        c.execute(f"""DELETE FROM character WHERE char_name = ?""", (character_name,))
        conn.commit()

        if c.rowcount > 0:
            message = f'```✅Character "{character_name}" successfully deleted!```'
            helper.send_message_to_website(message)
            return (message, None)
        else:
            message = f'```❌ERROR: Character "{character_name}" does not exist.```'
            helper.send_message_to_website(message)
            return (message, None)

    except Exception as e:
        exception = f'EXCEPTION: logic.delete_character(): {str(e)}'
        print(exception)
        return (exception, exception)
        
async def edit_person(person_name: str, person_name_new: str, relation: str, guild: str) -> tuple:
    try:
        if relation.lower() in ['enemy', 'foe', 'opponent']:
            relation = 0
        elif relation.lower() in ['friend', 'friendly', 'pal']:
            relation = 1
        elif relation.lower() in ['neutral']:
            relation = 2
        else:
            return ('❌ERROR: Invalid input. Please enter "friendly", "enemy", or "neutral"', None)

        person_name = person_name.title()
        person_name_new = person_name_new.title()
        guild = guild.title()
        conn = bot.db_connection
        c = conn.cursor()
        c.execute(
            f"""SELECT * FROM person WHERE person_name = ?""", (person_name,)
        )
        results = c.fetchall()
        conn.commit()

        if not results:
            message = f'```❌ERROR: Person "{person_name}" does not exist in "person" table. Aborting EDIT.```'
            helper.send_message_to_website(message)
            return (message, None)

    except Exception as e:
        exception = f'EXCEPTION: logic.edit_person() (first condition): {str(e)}'
        print(exception)
        return (exception, exception)
    try:
        c.execute(
            f"""UPDATE person SET person_name = ?, relation = ?, guild = ? WHERE person_name = ?""",
            (person_name_new, relation, guild, person_name),
        )
        results = c.fetchall()
        conn.commit()
        
        if relation == 0:
            relation = "Enemy"
        if relation == 1:
            relation = "Friendly"
        if relation == 2:
            relation = "Neutral"
        message = f"```✅Person CHANGED: person_name = {person_name_new}, relation = {relation}, guild = {guild}```"
        helper.send_message_to_website(message)
        return (message, None)
    except Exception as e:
        exception = f'EXCEPTION: logic.edit_person() (second condition): {str(e)}'
        print(exception)
        return (exception, exception)

async def edit_character(character_name: str, character_name_new: str, character_class: str, level: int, person_name: str) -> tuple:
    try:
        character_name = character_name.title()
        character_name_new = character_name_new.title()
        person_name = person_name.title()

        if character_class.lower() == "mage":
            character_class = "Magician"
        if character_class.lower() in ['shadowknight', 'shadow knight']:
            character_class = "Shadowknight"
        if character_class.title() not in class_names:
            return (f'❌ERROR: Invalid input. Please provide a valid class name: {str(class_names)}', None)
        conn = bot.db_connection
        c = conn.cursor()
        c.execute(
            f"""SELECT * FROM character WHERE char_name = ?""", (character_name,)
        )
        results = c.fetchall()

        if not results:
            message = f'```❌ERROR: Character "{character_name}" does not exist in "character" table. Aborting EDIT.```'
            helper.send_message_to_website(message)
            return (message, None)

    except Exception as e:
        error_message = f'EXCEPTION: logic.edit_char(): {str(e)}'
        print(error_message)
        return (error_message, error_message)

    try:
        c.execute(
            f"""UPDATE character SET char_name = ?, char_class = ?, person_name = ?, level = ? WHERE char_name = ?""",
            (character_name_new, character_class, person_name, level, character_name),
        )
        results = c.fetchall()
        conn.commit()
        message = f"```✅Character CHANGED: char_name = {character_name_new}, char_class = {character_class}, person_name = {person_name}, level = {level}```"
        helper.send_message_to_website(message)
        return (message, None)
    except Exception as e:
        error_message = f'EXCEPTION: logic.edit_character():  {str(e)}'
        print(error_message)
        return (error_message, error_message)
    
async def who(character_name: str) -> tuple:
    try:
        character_name = character_name.title()
        conn = bot.db_connection
        c = conn.cursor()
        c.execute(f"""SELECT * FROM character WHERE char_name = ?""", (character_name,))
        results = c.fetchone()

        if results is None:
            message = f'```❌ERROR: Character "{character_name}" doesnt exist in "character" table```'
            helper.send_message_to_website(message)
            return (message, None)
        char_class = results[1]
        person_name = results[2]

        c2 = conn.cursor()
        c2.execute(f"""SELECT * from person WHERE person_name = ?""", (person_name,))
        results = c2.fetchone()

        if results is None:
            message = f'```❌ERROR: Person "{person_name} doesnt exist in "person" table```'
            helper.send_message_to_website(message)
            return (message, None)

        if results[1] == 0:
            relation = "Enemy"
        if results[1] == 1:
            relation = "Friendly"
        if results[1] == 2:
            relation = "Neutral"
        results_string = f"```Character: {character_name}, Class: {char_class}```"
        results_string += f'```Person info for "{character_name}": Person: {results[0]}, Relation: {relation}, Guild: {results[2]}```'
        helper.send_message_to_website(results_string)
        return (results_string, None)

    except Exception as e:
        error_message = f'EXCEPTION: logic.who(): {str(e)}'
        print(error_message)
        return (error_message, error_message)

async def get_characters(person_name: str) -> tuple:
    try:
        exception = None
        person_name = person_name.title()
        conn = bot.db_connection
        c = conn.cursor()
        c.execute(
            f"""SELECT * FROM character WHERE person_name = ?""", (person_name,)
        )
        results = c.fetchall()
        sorted_results = sorted(results, key=lambda result: result[0])
        formatted_characters = ""

        for result in sorted_results:
            char_name, char_class, person_name, level = result
            row = f"Character: {char_name}, Class: {char_class}, Person: {person_name}, Level: {level}"
            formatted_characters += row
            formatted_characters += "\n"
        helper.send_message_to_website(formatted_characters)
        return ("```" + formatted_characters + "```", exception)
    except Exception as e:
        error_message = f'EXCEPTION: logic.get_characters(): {str(e)}'
        print(error_message)
        return (error_message, error_message)
    
async def get_person_table(guild: str) -> tuple:
    try:
        conn = bot.db_connection
        if guild:
            guild = guild.title()
            c = conn.cursor()
            c.execute(f"""SELECT * FROM person WHERE guild = ?""", (guild,))
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
            helper.send_message_to_website(results_string)
            results_string = "```" + results_string + "```"
            return (results_string, None)
    except Exception as e:
        error_message = f'EXCEPTION: logic.get_person_table()(first conditional): {str(e)}'
        print(error_message)
        return (error_message, error_message)
    else:
        try:
            c = conn.cursor()
            c.execute(f"""SELECT * FROM person""")
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
            helper.send_message_to_website(results_string)
            return (results_string, None)
        except Exception as e:
            error_message = f'EXCEPTION: logic.get_person_table()(else statement): {str(e)}'
            print(error_message)
            return (error_message, error_message)
        
async def get_characters_table(guild: str, character_class: str) -> tuple:
    try:
        if guild:
            guild = guild.title()
        if character_class:
            character_class = character_class.title()
        if character_class and character_class.lower() == "mage":
            character_class = "Magician"
        if character_class and character_class.lower() in ['shadowknight', 'shadow knight']:
            character_class = "Shadowknight"
        if character_class and character_class not in class_names:
            return (f'❌ERROR: Invalid input. Please provide a valid class name: {str(class_names)}', None)
        conn = bot.db_connection
        c = conn.cursor()
        if character_class and guild:
            c.execute(
                f"""SELECT * FROM character
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
                f"""SELECT * FROM character
                         WHERE person_name IN (SELECT person_name FROM person WHERE guild = ?)
                         """,
                (guild,),
            )
        else:
            c.execute(f"SELECT * FROM character")
        results = c.fetchall()
    except Exception as e:
        error_message = f'EXCEPTION: logic.get_characters_table(): {str(e)}'
        print(error_message)
        return (error_message, error_message)

    sorted_results = sorted(results, key=lambda result: result[0])
    results_string = ''
    for result in sorted_results:
        char_name, char_class, person_name, level = result
        row = f"{char_name}, {char_class}, {person_name}, {level}"
        results_string += row + "\n"
    results_string = "```" + results_string + "```"
    helper.send_message_to_website(results_string)
    print(results_string)
    return (results_string, None)

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
        conn = bot.db_connection
        c = conn.cursor()
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
            website_string = formatted_string
        else:
            website_string = formatted_string
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
        helper.send_message_to_website(website_string, image_url)
        await message.channel.send(formatted_string)
    except Exception as e:
        print('EXCEPTION: logic.parse_image():', str(e))
        return str(e)
#NOTE: Need to SELECT and see if user already has username
async def register_person(person_name: str, username: str) -> tuple:
    try:
        person_name = person_name.title()
        conn = bot.db_connection
        c = conn.cursor()
        # SELECT first to make sure person exists
        c.execute(f'''SELECT person_name FROM person WHERE person_name = ?''', (person_name,))
        result = c.fetchone()
        if not result:
            return (f'❌ERROR: Person {person_name} not found. (logic.register_person())', None)
        c.execute(f'''SELECT username FROM person WHERE person_name = ?''', (person_name,))
        result = c.fetchone()
        if result and result[0]:
            return (f'❌ERROR: Username "{result[0]}" already exists for person "{person_name}". (logic.register_person())', None)
        c.execute(f'''UPDATE person SET username = ? WHERE person_name = ?''', (username, person_name))
        conn.commit()
        return (f'✅Username: "{username}" registered for person: "{person_name}"', None)
        
    except Exception as e:
        error_message = f'EXCEPTION: logic.register_person(): {str(e)}'
        print(error_message)
        return (error_message, error_message)
    
async def unregister_person(person_name: str) -> tuple:
    try:
        conn = bot.db_connection
        c = conn.cursor()
        # SELECT first to make sure person exists
        c.execute(f'''SELECT person_name FROM person WHERE person_name = ?''', (person_name,))
        result = c.fetchone()
        if not result:
            return (f'❌ERROR: Person {person_name} not found. (logic.unregister_person())', None)
        c.execute(f'''SELECT username from person WHERE person_name = ?''', (person_name,))
        result = c.fetchone()
        if result:
            username = result[0]
        c.execute(f'''UPDATE person SET username = NULL WHERE person_name = ?''', (person_name,))
        conn.commit()
        return (f'✅Username: "{username}" unregistered for person: "{person_name}"', None)
        
    except Exception as e:
        error_message = f'EXCEPTION: logic.register_person(): {str(e)}'
        print(f'EXCEPTION: logic.register_person(): {str(e)}')
        return (error_message, error_message)

# NOTE: Possibly remove error message when we refactor / revamp the way we input raids  
# We need to SELECT the actual person_names, derived with the USERNAMES returned from get_most_populated_channel()
async def add_raid_event(discord_server: object, raid_name: str) -> tuple:
    try:
        timestamp = datetime.now().strftime("%m-%d-%Y")
        raiders, usernames = await helper.get_most_populated_channel(discord_server)
        
        if raiders is None:
            return ('❌ERROR: There are no members in any voice channels.', None)
        print('raiders')
        print(raiders)
        conn = bot.db_connection
        with conn:
            c = conn.cursor()
            c.execute(f'''INSERT INTO raid_master (raid_name, raid_date) VALUES (?, ?)''', (raid_name, timestamp))
            raid_id = c.lastrowid
            username_inserts = [(user, raid_id, 1) for user in usernames]
            for entry in username_inserts:
                username = entry[0]
                raid_id = entry[1]
                dkp_points = entry[2]
                c.execute(f'''INSERT INTO dkp (username, raid_id, dkp_points) VALUES (?, ?, ?)''', (username, raid_id, dkp_points))
            conn.commit()
            # Add a 'skip' for None raiders inside helper.add_raid_event()
            embed = helper.add_raid_embed(raid_name, raiders)
        return (embed, None)
    except Exception as e:
        error_message = f'EXCEPTION: logic.add_raid_event(): {str(e)}'
        print(error_message)
        return (error_message, error_message)

async def get_all_raids(person_name: str) -> tuple:
    try:
        conn = bot.db_connection
        with conn:
            c = conn.cursor()
            if person_name:
                person_name = person_name.title()
                c.execute(f'''SELECT person_name FROM person WHERE person_name = ?''', (person_name,))
                result = c.fetchone()
                if not result:
                    return (f'❌ERROR: Person {person_name} does not exist.', None)
                c.execute(f'''SELECT rm.*
                            FROM raid_master rm
                            JOIN dkp d ON rm.raid_id = d.raid_id
                            JOIN person p ON d.username = p.username
                            WHERE p.person_name = ?''', (person_name,))
                results = c.fetchall()
                print(f'RESULTS: {person_name}: {str(results)}')
                if not results:
                    return (f'❌ERROR: Person no raids found for person: {str(person_name)}.', None)
                embed = helper.get_raids_embed(results, person_name)
                return (embed, None)
            else:
                c.execute('''SELECT * FROM raid_master''')
                results = c.fetchall()
                if not results:
                    return (f'❌ERROR: No raids found.', None)
                embed = helper.get_raids_embed(results)
                return (embed, None)
    except Exception as e:
        exception = f'EXCEPTION: helper.get_all_raids(): {str(e)}'
        return (exception, exception)

async def get_raid(raid_id: int)  -> tuple:
    try:
        conn = bot.db_connection
        with conn:
            print('test1')
            c = conn.cursor()
            c.execute(f'''SELECT a.raid_name, a.raid_date, b.username 
                      FROM raid_master a 
                      INNER JOIN dkp b
                      ON a.raid_id = b.raid_id
                      WHERE a.raid_id = ?
                      ''', (raid_id,))
            results = c.fetchall()
            print('test2')
            print(f'Results: {results}')
            if not results:
                return (f'❌ERROR: Person raid found for ID: {str(raid_id)}.', None)
            embed = helper.get_raid_embed(results)
            if embed:
                return (embed, None)
    except Exception as e:
        exception = f'EXCEPTION: helper.get_raid(): {str(e)}'
        print(exception)
        return (exception, exception)

async def delete_raid_event(raid_id: int) -> tuple:
    try:
        conn = bot.db_connection
        with conn:
            c = bot.db_connection.cursor()
            c.execute(f'''SELECT raid_name, raid_date FROM raid_master WHERE raid_id = ?''', (raid_id,))
            result = c.fetchall()
            if result and result[0]:
                raid_name, raid_date = result[0]
            else:
                print('Raid not found.')
                return ('❌ERROR: Raid not found', None)
            c.execute(f'''DELETE FROM raid_master WHERE raid_id = ?''', (raid_id,))
            c.execute(f'''DELETE FROM dkp WHERE raid_id = ?''', (raid_id,))
            conn.commit()
            message = f'✅Raid deleted: {raid_name}, {raid_date}.'
            helper.send_message_to_website(message)
            return (message, None)
    except Exception as e:
        error_message = f'EXCEPTION: logic.delete_raid_event() error: {str(e)}'
        print(error_message)
        return (error_message, error_message)

# NOTE: Add a SELECT to convert person_name to username
async def add_person_to_raid(person_name: str, raid_id: int) -> tuple:
    try:
        person_name = person_name.title()
        conn = bot.db_connection
        c = conn.cursor()
        # SELECT first to make sure char exists
        c.execute(f'''SELECT username FROM person WHERE person_name = ?''', (person_name,))
        result = c.fetchone()
        if result and result[0]:
            username = result[0]
        else:
            error_message = f'❌ERROR: No username found for person "{person_name}"'
            return (error_message, error_message)
        print(f'logic.add_person_to_raid.SELECT: {result}')
        if not result:
            return (f'❌ERROR: Username for "{person_name}" not found.', None)
        c.execute(f'''INSERT INTO dkp (username, raid_id, dkp_points) VALUES (?, ?, ?)''', (username, raid_id, 1))
        conn.commit()
        message = f'✅Person {person_name} added to raid: {raid_id}.'
        helper.send_message_to_website(message)
        return (message, None)
    except Exception as e:
        if 'UNIQUE constraint failed' in str(e):
            print(f'EXCEPTION: logic.add_person_to_raid() UNIQUE constraint: {str(e)}')
            return (f'❌ERROR: Username "{username}" is already in raid {raid_id}.', None)
        error_message = f'EXCEPTION: logic.add_person_to_raid(): {str(e)}'
        print(error_message)
        return (error_message, error_message)

async def delete_person_from_raid(person_name: str, raid_id: int) -> tuple:
    try:
        person_name = person_name.title()
        conn = bot.db_connection
        with conn:
            c = bot.db_connection.cursor()
            c.execute(f'''SELECT raid_name, raid_date FROM raid_master WHERE raid_id = ?''', (raid_id,))
            result = c.fetchone()
            if result:
                raid_name, raid_date = result
            else:
                print('❌ERROR: logic.delete_person_from_raid(): Raid not found.')
                return ('❌ERROR: logic.delete_person_from_raid(): Raid not found.', None)
            c.execute(f'''SELECT username FROM person WHERE person_name = ?''', (person_name,))
            result = c.fetchone()
            if result and result[0]:
                username = result[0]
            else:
                print('❌ERROR: logic.delete_person_from_raid(): username not found.')
                return ('❌ERROR: logic.delete_person_from_raid(): username not found.', None)
            c.execute(f'''DELETE FROM dkp WHERE username = ?''', (username,))
            conn.commit()
            message = f'✅"{person_name}" removed from: "{raid_name}", "{raid_date}".'
            helper.send_message_to_website(message)
            return (message, None)
    except Exception as e:
        error_message = f'EXCEPTION: logic.delete_person_from_raid(): {str(e)}'
        print(error_message)
        return (error_message, error_message)
# Very, very odd return statement, lets see if it works
#NOTE: Bad code smell on error / exception handling
async def award_loot(item_name: str, person_name: str, raid_id: int, icon_id: int) -> list:
    try:
        person_name = person_name.title()
        conn = bot.db_connection
        with conn:
            print('logic.award_loot.test1')
            c = conn.cursor()
            c.execute(f'''SELECT person_name FROM person WHERE person_name = ?''', (person_name,))
            result = c.fetchone()
            if not result:
                return (f'❌ERROR: Person {person_name} does not exist.', None, None)
            print('logic.award_loot.test2')
            c.execute(f'''SELECT raid_name FROM raid_master WHERE raid_id = ?''', (raid_id,))
            result = c.fetchone()
            if not result:
                return (f'❌ERROR: Raid_id {raid_id} does not exist.', None, None)
            print('logic.award_loot.test3')
            raid_name = result[0]
            c.execute(f'''INSERT INTO person_loot (person_name, item_name, raid_id) VALUES (?, ?, ?)''', (person_name, item_name, raid_id))
            conn.commit()
            print(f'✅Item "{item_name}" awarded to "{person_name}" at "{raid_name}"')
            # helper.award_loot_embed returns list, we need to append it to 
            results = helper.award_loot_embed(item_name, icon_id, person_name, raid_name)
            results.append(None)
            return results
    except Exception as e:
        exception = f'EXCEPTION: logic.award_item(): {str(e)}'
        print(exception)
        return (exception, None, exception)
    
async def remove_loot(item_name: str, icon_id: int, person_name: str, raid_id: int) -> list:
    try:
        person_name = person_name.title()
        conn = bot.db_connection
        with conn:
            c = conn.cursor()
            c.execute(f'''SELECT person_name FROM person WHERE person_name = ?''', (person_name,))
            result = c.fetchone()
            if not result:
                return (f'❌ERROR: Person {person_name} does not exist.', None)
            c.execute(f'''SELECT raid_name FROM raid_master WHERE raid_id = ?''', (raid_id,))
            result = c.fetchone()
            if not result:
                return (f'❌ERROR: Raid ID: {raid_id} does not exist.', None)
            raid_name = result[0]
            c.execute(f'''SELECT * FROM person_loot WHERE item_name = ? AND person_name = ? AND raid_id = ?''', (item_name, person_name, raid_id))
            results = c.fetchall()
            if not results:
                error_message = f'❌ERROR: Item: {item_name} for person: {person_name} NOT FOUND at raid: {raid_name}'
                print(error_message)
                return (error_message, None, None)
            c.execute(f'''DELETE FROM person_loot WHERE item_name = ? AND person_name = ? AND raid_id = ?''', (item_name, person_name, raid_id))
            
            conn.commit()
            message = f'✅Item {item_name} removed from {person_name} at {raid_name}.'
            helper.send_message_to_website(message)
            results = helper.remove_loot_embed(item_name, icon_id, person_name, raid_name)
            results.append(None)
            return results
    except Exception as e:
        exception = f'EXCEPTION: logic.remove_loot(): {e}'
        print(exception)
        return (exception, None, exception)

# NOTE: Only returning 2 vals, because we have not yet created an embed
async def get_loot(person_name: str) -> list:
    try:
        person_name = person_name.title()
        conn = bot.db_connection
        with conn:
            c = conn.cursor()
            c.execute(f'''SELECT person_name FROM person WHERE person_name = ?''', (person_name,))
            result = c.fetchone()
            if not result:
                return (f'❌ERROR: Person {person_name} does not exist.', None)
            c.execute(f'''SELECT person_name, item_name, raid_id FROM person_loot WHERE person_name = ?''', (person_name,))
            results = c.fetchall()
            # Need to take raid_ids and SELECT raid_name from raid_master
            if not results:
                print(f'❌ERROR: No loot found for {person_name}.')
            loot_list = []
            for result in results:
                c.execute('''SELECT raid_name FROM raid_master WHERE raid_id = ?''', (result[2],))
                raid_name = c.fetchone()
                if not raid_name:
                    print('❌ERROR: raid name not found')
                    return
                row = []
                row.append(result[0])
                row.append(result[1])
                row.append(raid_name[0])
                loot_list.append(row)
            print(loot_list)
            embed = await helper.get_loot_embed(person_name, loot_list)
            return (embed, None)
    except Exception as e:
        exception = f'EXCEPTION: logic.get_loot(): {str(e)}'
        print(exception)
        return (exception, exception)

#NOTE: Refactor more Exception wrappers for each function call.
async def test_run_all_commands(discord_server: object, succeed: bool) -> list:
    if test_mode == False:
        print('data.config.test_mode == False, aborting "logic.test_run_all_commands()".')
        return
    person_name = 'Grixus' if succeed else False
    person_name_new = 'Grixus' if succeed else False
    relation = 'Friendly' if succeed else False
    guild = 'Tempest' if succeed else False
    character_name = 'Penalty' if succeed else False
    character_name_new = 'Penalty' if succeed else False
    character_class = 'Monk' if succeed else False
    level = 60 if succeed else False
    username = 'grixus.' if succeed else False
    raid_name = 'Golems' if succeed else False
    raid_id = 1 if succeed else False
    item_name = 'Amulet of Necropotence' if succeed else False
    
    results = []
    exceptions = []

    print(f'test_mode: {str(test_mode)}')
    
    try:
        try:
            add_person_result, add_person_exception = await add_person(person_name, relation, guild)
            results.append(add_person_result)
            exceptions.append(add_person_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.add_person(): {str(e)}')  
        try:
            add_character_result, add_character_exception = await add_character(character_name, character_class, level, person_name)
            results.append(add_character_result)
            exceptions.append(add_character_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.add_character(): {str(e)}') 
        try:
            edit_person_result, edit_person_exception = await edit_person(person_name, person_name_new, relation, guild)
            results.append(edit_person_result)
            exceptions.append(edit_person_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.edit_person(): {str(e)}') 
        try:
            edit_character_result, edit_character_exception = await edit_character(character_name, character_name_new, character_class, level, person_name)
            results.append(edit_character_result)
            exceptions.append(edit_character_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.edit_character(): {str(e)}') 
        try:
            who_result, who_exception = await who(character_name)
            results.append(who_result)
            exceptions.append(who_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.who(): {str(e)}') 
        try:
            get_characters_result, get_characters_excetion = await get_characters(person_name)
            results.append(get_characters_result)
            exceptions.append(get_characters_excetion)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.get_characters(): {str(e)}')             
        try:
            get_person_table_result, get_person_table_exception = await get_person_table(guild)
            results.append(get_person_table_result)
            exceptions.append(get_person_table_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.get_person_table(): {str(e)}') 
        try:
            get_characters_table_result, get_characters_table_exception = await get_characters_table(guild, character_class)
            results.append(get_characters_table_result)
            exceptions.append(get_characters_table_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.get_characters_table(): {str(e)}') 
        try:
            add_raid_event_result, add_raid_event_exception = await add_raid_event(discord_server, raid_name)
            results.append(add_raid_event_result)
            exceptions.append(add_raid_event_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.add_raid_event(): {str(e)}') 
        try:
            add_person_to_raid_result, add_person_to_raid_exception = await add_person_to_raid(person_name, raid_id)
            results.append(add_person_to_raid_result)
            exceptions.append(add_person_to_raid_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.add_person_to_raid(): {str(e)}')     
        try:
            # NOTE: Have to pass in mock 'file' var, to accept the 3rd value returned, even tho its irrelevant otherwise for the test
            award_loot_result, file, award_loot_exception = await award_loot(item_name, person_name, raid_id, 800)
            results.append(award_loot_result)
            exceptions.append(award_loot_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.award_loot(): {str(e)}') 
        try:
            remove_loot_result, file, remove_loot_exception = await remove_loot(item_name, 800, person_name, raid_id)
            results.append(remove_loot_result)
            exceptions.append(remove_loot_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.remove_loot(): {str(e)}') 
        try:
            register_person_result, register_person_exception = await register_person(person_name, username)
            results.append(register_person_result)
            exceptions.append(register_person_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.register_person(): {str(e)}') 
        try:
            delete_person_from_raid_result, delete_person_from_raid_exception = await delete_person_from_raid(person_name, raid_id)
            results.append(delete_person_from_raid_result)
            exceptions.append(delete_person_from_raid_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.delete_person_from_raid(): {str(e)}') 
        try:
            unregister_person_result, unregister_person_exception = await unregister_person(person_name)
            results.append(unregister_person_result)
            exceptions.append(unregister_person_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.unregister_person(): {str(e)}') 
        try:
            delete_raid_event_result, delete_raid_event_exception = await delete_raid_event(raid_id)
            results.append(delete_raid_event_result)
            exceptions.append(delete_raid_event_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.delete_raid_event(): {str(e)}') 
        try:
            delete_person_result, delete_person_exception = await delete_person(person_name)
            results.append(delete_person_result)
            exceptions.append(delete_person_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.delete_person(): {str(e)}') 
        try:
            delete_character_result, delete_character_exception = await delete_character(character_name)
            results.append(delete_character_result)
            exceptions.append(delete_character_exception)
        except Exception as e:
            print(f'EXCEPTION: test_run_all_commands.delete_character(): {str(e)}') 

        if succeed == False:
            print("succeed boolean == False results: ")
            print(results)
        return results, exceptions
    except Exception as e:
        print(f'EXCEPTION: logic.test_run_all_commands(): {str(e)}',)
        return (([f'EXCEPTION: logic.test_run_all_commands() exception: {str(e)}'], [e]))
        


    
