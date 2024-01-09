import sqlite3
import re
import config
import os
import char_classes
import pytesseract
from PIL import Image
from io import BytesIO
import requests
import json
import datetime
from decouple import config as env
db_path = env('DB_PATH')
url = env('URL')


current_working_dir = os.getcwd()
print("Current Working Directory:", current_working_dir)

def send_message_to_website(message: dict, image_url=None):
    payload = {'date': str(datetime.datetime.now()), 
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
   

async def invalid_input(message, flag):
    help_messages = {
        "!add_player": "Invalid format, correct format is: player_name, relation, guild",
        "!edit_player": "Invalid format, correct format is: player_name_old, player_name_new, relation, guild",
        "!add_char": "Invalid format, correct format is: char_name, char_class, player_name, level",
        "!edit_char": "Invalid format, correct format is: char_name_old, char_name_new, char_class, player_name, level",
        "!delete_player": "Invalid format, correct format is: player_name",
        "!delete_char": "Invalid format, correct format is: char_name",
        "!who": "Invalid format, correct format is: char_name",
    }

    if flag in help_messages:
        try:
            help_message = f"```{help_messages[flag]}```"
            send_message_to_website(help_message)
            await message.channel.send(help_message)
        except Exception as e:
            print(e)

async def test(message: dict) -> str:
    test_string = """THIS IS A TEST FOR DEBUG PURPOSES"""
    send_message_to_website(test_string)
    return test_string



async def get_commands(message: dict) -> str:
    # NOTE:
    # Paramter 'message' is a 'placeholder' param. Its not used. Its simply there to be compatible with the way the commands are called in 'bot.py'
    commands = """```COMMANDS:

    !add_player: player_name, relation, guild_name
    !add_char: char_name, char_class, player_name, level
    !edit_player: player_name_old, player_name_new, relation, guild_name
    !edit_char: char_name_old, char_name_new, char_class, player_name, level
    !delete_player: player_name
    !delete_char: char_name
    !who: character_name
    !get_chars: char_name

    **!players_db accepts zero or one parameters**
    !players_db: empty field returns entire 'Players_db' OR: 
                 !players_db guild_name
    
    **!characters_db accepts zero, one, or two parameters. Order DOES NOT matter**
    !characters_db: empty field returns entire 'Characters_db' OR:
                    !characters_db guild_name, char_class OR:
                    !characters_db char_class, guild_name OR:
                    !characters_db char_class OR:
                    !characters_db guild_name
    !snip: image_file
    ```"""
    send_message_to_website(commands)
    return commands


def create_tables():
    sql_Players_db = """ CREATE Table IF NOT EXISTS Players_db (
                            player_name text PRIMARY KEY,
                            relation integer,
                            guild text                
    )"""

    sql_Characters_db = """CREATE Table IF NOT EXISTS Characters_db (
                            char_name text PRIMARY KEY, 
                            char_class text NOT NULL,
                            player_name text,
                            level integer                     
    )"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(sql_Players_db)
        c.execute(sql_Characters_db)
        conn.commit()
        print("Tables created!")

    except Exception as e:
        print("database.py, create_tables() error:")
        print(e)
        return str(e)
    finally:
        conn.close()


async def get_players_db(message: dict) -> str:
    message.content = message.content.split()[1:]
    if message.content == []:
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("""SELECT * FROM Players_db""")
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
        finally:
            conn.close()
    else:
        try:
            guild = message.content[0]
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("""SELECT * FROM Players_db WHERE guild = ?""", (guild,))
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
            if len(results_string) > 1994:
                for i in range(0, len(results_string), 1994):
                    chunk = results_string[i : i + 1994]
                    chunk = "```" + chunk + "```"
                    await message.channel.send(chunk)
            send_message_to_website(results_string)
            results_string = "```" + results_string + "```"
            return results_string
        except Exception as e:
            print(e)
            return str(e)
        finally:
            conn.close()


async def get_characters_db(message: dict) -> str:
    message.content = message.content.split()[1:]
    message.content = [elem.replace(",", "") for elem in message.content]
    char_class = None
    guild = None

    # Greater scoped variables to avoid repeating myself (DRY)
    results = []
    results_string = ""

    if message.content:
        for param in message.content:
            if param in char_classes.class_names:
                char_class = param
            if param in config.guilds:
                guild = param

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        if char_class and guild:
            c.execute(
                """SELECT * FROM Characters_db
                         WHERE char_class = ? AND player_name IN (SELECT player_name FROM Players_db WHERE guild = ?)
                         """,
                (char_class, guild),
            )
        elif char_class:
            c.execute(
                """SELECT * FROM Characters_db WHERE char_class = ?""", (char_class,)
            )
        elif guild:
            c.execute(
                """SELECT * FROM Characters_db
                         WHERE player_name IN (SELECT player_name FROM Players_db WHERE guild = ?)
                         """,
                (guild,),
            )
        else:
            c.execute("SELECT * FROM Characters_db")
        results = c.fetchall()
    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()
    sorted_results = sorted(results, key=lambda result: result[0])
    for result in sorted_results:
        char_name, char_class, player_name, level = result
        row = f"{char_name}, {char_class}, {player_name}, {level}"
        results_string += row + "\n"

    if len(results_string) > 1994:
        for i in range(0, len(results_string), 1994):
            chunk = results_string[i : i + 1994]
            chunk = "```" + chunk + "```"
            await message.channel.send(chunk)
        send_message_to_website(results_string)
    else:
        results_string = "```" + results_string + "```"
        send_message_to_website(results_string)
        return results_string


async def add_char(message: dict) -> str:
    character_info = message.content.split()[1:]
    character_info = [elem.replace(",", "") for elem in character_info]

    if len(character_info) != 4:
        return await invalid_input(message, "!add_char")

    char_name, char_class, player_name, level = character_info
    char_name = char_name.title()
    char_class = char_class.title()
    player_name = player_name.title()
    level = int(level)

    if char_class == "Mage":
        char_class = "Magician"
    if char_class == "ShadowKnight":
        char_class = "Shadowknight"

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM Players_db WHERE player_name = ?", (player_name,))
        if not c.fetchall():
            message = f'```Player "{player_name}" does not exist in "Players" database. Please create a "Players" db entry first. Aborting insert.```'
            send_message_to_website(message)
            return message

        c.execute("SELECT * FROM Characters_db WHERE char_name = ?", (char_name,))
        if c.fetchall():
            message = (
                f'```"{char_name}" already exists in table "Characters". Aborting insert.```'
            )
            send_message_to_website(message)
            return message

        c.execute(
            "INSERT INTO Characters_db (char_name, char_class, player_name, level) VALUES (?, ?, ?, ?)",
            (char_name, char_class, player_name, level),
        )
        conn.commit()

        c.execute("SELECT * FROM Characters_db WHERE char_name = ?", (char_name,))
        result = c.fetchone()

        conn.close()

        if result:
            message = f'```Character "{char_name}" inserted successfully: {result}```'
            send_message_to_website(message)
            return message

    except Exception as e:
        print("SQLite error, database.add_char():")
        print(e)
        return str(e)


async def add_player(message: dict) -> str:
    character_info = message.content.split()[1:]
    character_info = [elem.replace(",", "") for elem in character_info]

    if len(character_info) != 3:
        return await invalid_input(message, "!add_player")

    player_name, relation, guild = character_info
    player_name = player_name.title()
    relation = int(relation)
    guild = guild.title()

    if relation not in (0, 1, 2):
        message = '```Invalid "relation" field. Must be 0, 1, or 2```'
        send_message_to_website(message)
        return message

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(
            """INSERT INTO Players_db (player_name, relation, guild) VALUES (?, ?, ?)""",
            ((player_name, relation, guild)),
        )
        conn.commit()
        message = (
            f'```Player "{player_name}" successfully inserted into "Players" database.```'
        )
        send_message_to_website(message)
        return message
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            message = f'```Player "{player_name}" already exists in table "Players". Aborting insert.```'
            send_message_to_website(message)
            return message
        else:
            print("SQLite error, database.add_player():")
            print(e)
            return str(e)
    finally:
        conn.close()


async def delete_char(message: dict) -> str:
    if len(message.content.split()) != 2:
        return await invalid_input(message, "!delete_player")

    char_name = message.content.split()[1:][0]
    char_name = char_name.title()

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""DELETE FROM Characters_db WHERE char_name = ?""", (char_name,))
        conn.commit()

        if c.rowcount > 0:
            message = f'```Character "{char_name}" successfully deleted!```'
            send_message_to_website(message)
            return message
        else:
            message = f'```Character "{char_name}" does not exist.```'
            send_message_to_website(message)
            return message

    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()


async def delete_player(message: dict) -> str:
    if len(message.content.split()) != 2:
        return await invalid_input(message, "!delete_player")

    player_name = message.content.split()[1:][0]
    player_name = player_name.title()

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""DELETE FROM Players_db WHERE player_name = ?""", (player_name,))
        conn.commit()

        if c.rowcount > 0:
            message = f'```Player "{player_name}" successfully deleted!```'
            send_message_to_website(message)
            return message
        else:
            message = f'```Character "{player_name}" does not exist```'
            send_message_to_website(message)
            return message

    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()


async def edit_char(message: dict) -> str:
    character_info = message.content.split()[1:]
    character_info = [elem.replace(",", "") for elem in character_info]

    if len(character_info) != 5:
        send_message_to_website(await invalid_input(message, "!edit_char"))
        return await invalid_input(message, "!edit_char")

    char_name_old, char_name_new, char_class, player_name, level = character_info
    char_name_old = char_name_old.title()
    char_name_new = char_name_new.title()
    player_name = player_name.title()
    level = int(level)

    if char_class == "Mage":
        char_class = "Magician"

    if type(level) != int:
        message = '```Error: "level" must be of type int```'
        send_message_to_website(message)
        return message

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(
            """SELECT * FROM Characters_db WHERE char_name = ?""", (char_name_old,)
        )
        results = c.fetchall()

        if not results:
            message = f'```Character "{char_name_old}" does not exist in "Players" database. Aborting EDIT.```'
            send_message_to_website(message)
            return message

    except Exception as e:
        print("SQLite error, database.edit_char():")
        print(e)
        return e

    try:
        c.execute(
            """UPDATE Characters_db SET char_name = ?, char_class = ?, player_name = ?, level = ? WHERE char_name = ?""",
            (char_name_new, char_class, player_name, level, char_name_old),
        )
        results = c.fetchall()
        conn.commit()
        message = f"```Character CHANGED: char_name = {char_name_new}, char_class = {char_class}, player_name = {player_name}, level = {level}```"
        send_message_to_website(message)
        return message
    finally:
        conn.close()


async def edit_player(message: dict) -> str:
    character_info = message.content.split()[1:]
    character_info = [elem.replace(",", "") for elem in character_info]

    if len(character_info) != 4:
        send_message_to_website(await invalid_input(message, "!edit_char"))
        return await invalid_input(message, "!edit_char")

    player_name_old, player_name_new, relation, guild = character_info
    player_name_old = player_name_old.title()
    player_name_new = player_name_new.title()
    relation = int(relation)
    guild = guild.title()

    if type(relation) != int:
        message = '```Error: "relation" must be of type int```'
        send_message_to_website(message)
        return message

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(
            """SELECT * FROM Players_db WHERE player_name = ?""", (player_name_old,)
        )
        results = c.fetchall()
        conn.commit()

        if not results:
            message = f'```Player "{player_name_old}" does not exist in "Players" database. Aborting EDIT.```'
            send_message_to_website(message)
            return message

    except Exception as e:
        print("SQLite error, database.edit_char():")
        print(e)
        return e

    try:
        c.execute(
            """UPDATE Players_db SET player_name = ?, relation = ?, guild = ? WHERE player_name = ?""",
            (player_name_new, relation, guild, player_name_old),
        )
        results = c.fetchall()
        conn.commit()
        message = f"```Player CHANGED: player_name = {player_name_new}, relation = {relation}, guild = {guild}```"
        send_message_to_website(message)
        return message
    finally:
        conn.close()


async def who(message: dict) -> str:
    char_name = message.content.split()[1:][0]
    char_name = char_name.title()

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""SELECT * FROM Characters_db WHERE char_name = ?""", (char_name,))
        results = c.fetchone()

        if results is None:
            message = f'```Character "{char_name}" doesnt exist in "Characters" db```'
            send_message_to_website(message)
            return message
        char_class = results[1]
        player_name = results[2]

        c2 = conn.cursor()
        c2.execute("""SELECT * from Players_db WHERE player_name = ?""", (player_name,))
        results = c2.fetchone()

        if results is None:
            message = f'```Player "{player_name} doesnt exist in "Players" db```'
            send_message_to_website(message)
            return message

        if results[1] == 0:
            relation = "Enemy"
        if results[1] == 1:
            relation = "Friendly"
        if results[1] == 2:
            relation = "Neutral"
        results_string = f"```Character: {char_name}, Class: {char_class}```"
        results_string += f'```Player info for "{char_name}": Player: {results[0]}, Relation: {relation}, Guild: {results[2]}```'
        send_message_to_website(results_string)
        return results_string

    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()


async def get_chars(message: dict) -> str:
    player_name = message.content[11:].strip()
    player_name = player_name.title()

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(
            """SELECT * FROM Characters_db WHERE player_name = ?""", (player_name,)
        )
        results = c.fetchall()
        sorted_results = sorted(results, key=lambda result: result[0])

        formatted_characters = ""
        for result in sorted_results:
            char_name, char_class, player_name, level = result
            row = f"Character: {char_name}, Class: {char_class}, Player: {player_name}, Level: {level}"
            formatted_characters += row
            formatted_characters += "\n"
        if len(formatted_characters) > 1994:
            for i in range(0, len(formatted_characters), 1994):
                chunk = formatted_characters[i : i + 1994]
                chunk = "```" + chunk + "```"
                await message.channel.send(chunk)
            send_message_to_website(formatted_characters)
        else:
            send_message_to_website(formatted_characters)
            return "```" + formatted_characters + "```"

    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()


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
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        placeholders = ",".join(["?"] * len(char_names))
        query = f"""SELECT a.char_name, a.char_class, a.player_name, a.level, b.relation 
            FROM Characters_db a INNER JOIN Players_db b 
            ON a.player_name = b.player_name 
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
            char_name, char_class, player_name, level, relation = result
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
            print(char_classes.emojis[char[1]])
            formatted_string += f"""```ansi
{char[0]}: [0;31;40m{char[1]}{char_classes.emojis[char[1]]}```"""
            website_string = formatted_string
        for char in friendly_chars:
            print(char_classes.emojis[char[1]])
            formatted_string += f"""```ansi
{char[0]}: [0;36;40m{char[1]}{char_classes.emojis[char[1]]}```"""
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
                    f"""```{char_class}{char_classes.emojis[char_class]}: {count}```"""
                )
                website_string += (
                    f"""```{char_class}{char_classes.emojis[char_class]}: {count}```\n"""
                )

        if friendly_class_comp:
            formatted_string += f"""\n **Friendly Classes:** \n"""
            website_string += f"""\n **Friendly Classes:** \n"""

            for char_class, count in sorted(
                friendly_class_comp.items(), key=lambda x: x[1], reverse=True
            ):
                formatted_string += (
                    f"""```{char_class} {char_classes.emojis[char_class]}: {count}```"""
                )
                website_string += (
                    f"""```{char_class} {char_classes.emojis[char_class]}: {count}```\n"""
                )

        # Send class comp count
        send_message_to_website(website_string, image_url)
        await message.channel.send(formatted_string)
    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()


async def parse_image_backup(extracted_text: str, message: dict, image_url: str):
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
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        placeholders = ",".join(["?"] * len(char_names))
        query = f"""SELECT a.char_name, a.char_class, a.player_name, a.level, b.relation 
            FROM Characters_db a INNER JOIN Players_db b 
            ON a.player_name = b.player_name 
            WHERE char_name IN ({placeholders})"""

        c.execute(query, char_names)
        results = c.fetchall()
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
            char_name, char_class, player_name, level, relation = result
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
            print(char_classes.emojis[char[1]])
            formatted_string += f"""```ansi
{char[0]}: [0;31;40m{char[1]}{char_classes.emojis[char[1]]}```"""

        for char in friendly_chars:
            print(char_classes.emojis[char[1]])
            formatted_string += f"""```ansi
{char[0]}: [0;36;40m{char[1]}{char_classes.emojis[char[1]]}```"""

        for char in unknown_char_names:
            formatted_string += f"""```ansi
{char}: [0;37;40mUNKNOWN```"""

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
            send_message_to_website(formatted_string)
        else:
            send_message_to_website(formatted_string)
            await message.channel.send(formatted_string)

        formatted_string = ""
        if enemy_class_comp:
            formatted_string += f"""**Enemy Classes:** \n"""

            for char_class, count in sorted(
                enemy_class_comp.items(), key=lambda x: x[1], reverse=True
            ):
                formatted_string += (
                    f"""```{char_class}{char_classes.emojis[char_class]}: {count}```"""
                )

        if friendly_class_comp:
            formatted_string += f"""\n **Friendly Classes:** \n"""

            for char_class, count in sorted(
                friendly_class_comp.items(), key=lambda x: x[1], reverse=True
            ):
                formatted_string += (
                    f"""```{char_class} {char_classes.emojis[char_class]}: {count}```"""
                )

        # Send class comp count
        send_message_to_website(formatted_string)
        await message.channel.send(formatted_string)
    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()
