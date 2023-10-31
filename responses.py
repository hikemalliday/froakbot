
async def invalid_input(message, flag):
    help_messages = {
        '!add_player': "Invalid format, correct format is: player_name, relation, guild",
        '!edit_player': "Invalid format, correct format is: player_name_old, player_name_new, relation, guild",
        '!add_char': "Invalid format, correct format is: char_name, char_class, player_name, level",
        '!edit_char': "Invalid format, correct format is: char_name_old, char_name_new, char_class, player_name, level",
        '!delete_player': "Invalid format, correct format is: player_name",
        '!delete_char': "Invalid format, correct format is: char_name",
        '!who': "Invalid format, correct format is: char_name"
    }

    if flag in help_messages:
        try:
            print('test error refactor')
            await message.channel.send(f"```{help_messages[flag]}```")
        except Exception as e:
            print(e)

def return_snip_text(extracted_text) -> str:
    return extracted_text

def return_db_entry_info(row: tuple) -> str:
    return row