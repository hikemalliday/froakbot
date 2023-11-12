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
            print("test error refactor")
            await message.channel.send(f"```{help_messages[flag]}```")
        except Exception as e:
            print(e)


async def get_commands(message: dict) -> str:
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
    return commands
