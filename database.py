import sqlite3
import responses
import re
import config
import os
import char_classes

current_working_dir = os.getcwd()
print("Current Working Directory:", current_working_dir)

guilds = ["Tempest", "Pumice", "Sanctuary", "Serenity", "Guildless"]


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
    print("config.db_path debug: " + config.db_path)
    try:
        conn = sqlite3.connect(config.db_path)
        c = conn.cursor()
        c.execute(sql_Players_db)
        c.execute(sql_Characters_db)
        conn.commit()
        print("Tables created!")

    except Exception as e:
        print("database.py, create_tables()")
        print(e)
        return str(e)
    finally:
        conn.close()


async def get_players_db(message: dict) -> str:
    message.content = message.content.split()[1:]
    if message.content == []:
        try:
            conn = sqlite3.connect(config.db_path)
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
            print(results_string)
            return "```" + results_string + "```"
        except Exception as e:
            print(e)
            return str(e)
        finally:
            conn.close()
    else:
        try:
            guild = message.content[0]
            conn = sqlite3.connect(config.db_path)
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
            print(results_string)
            if len(results_string) > 1994:
                for i in range(0, len(results_string), 1994):
                    chunk = results_string[i : i + 1994]
                    chunk = "```" + chunk + "```"
                    await message.channel.send(chunk)
            return "```" + results_string + "```"
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
            if param in guilds:
                guild = param

    try:
        conn = sqlite3.connect(config.db_path)
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
    else:
        results_string = "```" + results_string + "```"
        return results_string


async def add_char(message: dict) -> str:
    character_info = message.content.split()[1:]
    character_info = [elem.replace(",", "") for elem in character_info]

    if len(character_info) != 4:
        return await responses.invalid_input(message, "!add_char")

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
        conn = sqlite3.connect(config.db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM Players_db WHERE player_name = ?", (player_name,))
        if not c.fetchall():
            return f'```Player "{player_name}" does not exist in "Players" database. Please create a "Players" db entry first. Aborting insert.```'

        c.execute("SELECT * FROM Characters_db WHERE char_name = ?", (char_name,))
        if c.fetchall():
            return f'```"{char_name}" already exists in table "Characters". Aborting insert.```'

        c.execute(
            "INSERT INTO Characters_db (char_name, char_class, player_name, level) VALUES (?, ?, ?, ?)",
            (char_name, char_class, player_name, level),
        )
        conn.commit()

        # Get instert to we can return it:
        c.execute("SELECT * FROM Characters_db WHERE char_name = ?", (char_name,))
        result = c.fetchone()

        conn.close()

        if result:
            return f'```Character "{char_name}" inserted successfully: {result}```'

    except Exception as e:
        print("SQLite error, database.add_char():")
        print(e)
        return str(e)


async def add_player(message: dict) -> str:
    character_info = message.content.split()[1:]
    character_info = [elem.replace(",", "") for elem in character_info]

    if len(character_info) != 3:
        return await responses.invalid_input(message, "!add_player")

    player_name, relation, guild = character_info
    player_name = player_name.title()
    relation = int(relation)
    guild = guild.title()

    if relation not in (0, 1, 2):
        return '```Invalid "relation" field. Must be 0, 1, or 2```'

    try:
        conn = sqlite3.connect(config.db_path)
        c = conn.cursor()
        c.execute(
            """INSERT INTO Players_db (player_name, relation, guild) VALUES (?, ?, ?)""",
            ((player_name, relation, guild)),
        )
        conn.commit()
        return f'```Player "{player_name}" successfully inserted into "Players" database.```'
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return f'```Player "{player_name}" already exists in table "Players". Aborting insert.```'
        else:
            print("SQLite error, database.add_player():")
            print(e)
            return str(e)
    finally:
        conn.close()


async def delete_char(message: dict) -> str:
    if len(message.content.split()) != 2:
        return await responses.invalid_input(message, "!delete_player")

    char_name = message.content.split()[1:][0]
    char_name = char_name.title()

    try:
        conn = sqlite3.connect(config.db_path)
        c = conn.cursor()
        c.execute("""DELETE FROM Characters_db WHERE char_name = ?""", (char_name,))
        conn.commit()

        if c.rowcount > 0:
            return f"```Character {char_name} successfully deleted!```"
        else:
            return f"```Character {char_name} does not exist.```"

    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()


async def delete_player(message: dict) -> str:
    if len(message.content.split()) != 2:
        return await responses.invalid_input(message, "!delete_player")

    player_name = message.content.split()[1:][0]
    player_name = player_name.title()

    try:
        conn = sqlite3.connect(config.db_path)
        c = conn.cursor()
        c.execute("""DELETE FROM Players_db WHERE player_name = ?""", (player_name,))
        conn.commit()

        if c.rowcount > 0:
            return f"```Player {player_name} successfully deleted!```"
        else:
            return f"```Character {player_name} does not exist```"

    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()


async def edit_char(message: dict) -> str:
    character_info = message.content.split()[1:]
    character_info = [elem.replace(",", "") for elem in character_info]

    if len(character_info) != 5:
        return await responses.invalid_input(message, "!edit_char")

    char_name_old, char_name_new, char_class, player_name, level = character_info
    char_name_old = char_name_old.title()
    char_name_new = char_name_new.title()
    player_name = player_name.title()
    level = int(level)

    if char_class == "Mage":
        char_class = "Magician"

    if type(level) != int:
        return '```error, "level" must be of type int```'

    try:
        conn = sqlite3.connect(config.db_path)
        c = conn.cursor()
        c.execute(
            """SELECT * FROM Characters_db WHERE char_name = ?""", (char_name_old,)
        )
        results = c.fetchall()

        if not results:
            return f'```Character "{char_name_old}" does not exist in "Players" database. Aborting EDIT.```'

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
        return f"```Character CHANGED: char_name = {char_name_new}, char_class = {char_class}, player_name = {player_name}, level = {level}```"
    finally:
        conn.close()


async def edit_player(message: dict) -> str:
    character_info = message.content.split()[1:]
    character_info = [elem.replace(",", "") for elem in character_info]

    if len(character_info) != 4:
        return await responses.invalid_input(message, "!edit_char")

    player_name_old, player_name_new, relation, guild = character_info
    player_name_old = player_name_old.title()
    player_name_new = player_name_new.title()
    relation = int(relation)
    guild = guild.title()

    if type(relation) != int:
        return '```error, "relation" must be of type int```'

    try:
        conn = sqlite3.connect(config.db_path)
        c = conn.cursor()
        c.execute(
            """SELECT * FROM Players_db WHERE player_name = ?""", (player_name_old,)
        )
        results = c.fetchall()
        conn.commit()

        if not results:
            return f'```Player "{player_name_old}" does not exist in "Players" database. Aborting EDIT.```'

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
        return f"```Player CHANGED: player_name = {player_name_new}, relation = {relation}, guild = {guild}```"
    finally:
        conn.close()


async def who(message: dict) -> str:
    char_name = message.content.split()[1:][0]
    char_name = char_name.title()

    try:
        conn = sqlite3.connect(config.db_path)
        c = conn.cursor()
        c.execute("""SELECT * FROM Characters_db WHERE char_name = ?""", (char_name,))
        results = c.fetchone()

        if results is None:
            return f'```Character "{char_name}" doesnt exist in "Characters" db```'
        char_class = results[1]
        player_name = results[2]

        c2 = conn.cursor()
        c2.execute("""SELECT * from Players_db WHERE player_name = ?""", (player_name,))
        results = c2.fetchone()

        if results is None:
            return f'```Player "{player_name} doesnt exist in "Players" db```'

        if results[1] == 0:
            relation = "Enemy"
        if results[1] == 1:
            relation = "Friendly"
        if results[1] == 2:
            relation = "Neutral"

        results_string = f"```Character: {char_name}, Class: {char_class}```"
        results_string += f'```Player info for "{char_name}": Player: {results[0]}, Relation: {relation}, Guild: {results[2]}```'
        print(results_string)
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
        conn = sqlite3.connect(config.db_path)
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
        else:
            return "```" + formatted_characters + "```"

    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()


async def parse_image(extracted_text: str, message: dict):
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
        if char_names[i] in ("Yuu", "Yuuy", "Yuuv"):
            char_names[i] = "Yuuvy"

    try:
        conn = sqlite3.connect(config.db_path)
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
        print(len(formatted_string))
        if len(formatted_string) > 1994:
            for i in range(0, len(formatted_string), 1994):
                chunk = formatted_string[i : i + 1994]
                chunk = "```" + chunk + "```"
                await message.channel.send(chunk)
        else:
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
            formatted_string += f"""**Friendly Classes:** \n"""

            for char_class, count in sorted(
                friendly_class_comp.items(), key=lambda x: x[1], reverse=True
            ):
                formatted_string += (
                    f"""```{char_class} {char_classes.emojis[char_class]}: {count}```"""
                )

        # Send class comp count
        await message.channel.send(formatted_string)
    except Exception as e:
        print(e)
        return str(e)
    finally:
        conn.close()
