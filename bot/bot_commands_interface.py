# V2 (slash commands API)
import discord
import bot.bot_commands_logic as logic
from discord import app_commands
import helper
selected_raid_id = None

# 'Test' that runs all slash commands, and expects the returned 'exceptions' array to only contain None as every element.
# This implies that no exceptions were thrown inside any of the slash commands.
# This allows me to run all commands after adding a feature, to help find bugs.
# Technically only runs the commands inside the 'bot_commands_logic.py' module, which is not the same as manually running each command individually through
# 'bot_bommands_interface.py', still very useful though.
@app_commands.command(name='test_run_all_commands')
async def test_run_all_commands(interaction: discord.Interaction):
    await interaction.response.defer()
    results, exceptions = await logic.test_run_all_commands(interaction.guild, True)
    for result in results:
        if len(result) > 1994:
            await helper.print_large_message(interaction, result)
        else:
            await interaction.followup.send(result)

    for exception in exceptions:
        if exception:
            print(exception)
            await interaction.followup.send(exception)
    
    if all(exception is None for exception in exceptions):
        print('bot_commands_interface.run_all_commands:')
        print('No exceptions found.')
        await interaction.followup.send(f'bot_commands_interface.run_all_commands: No exceptions found.')


@app_commands.command(name='add_person')
@app_commands.describe(person_name='Enter a person name', relation='Enter relation status', guild='Enter a guild')
async def add_person(interaction: discord.Interaction, person_name: str, relation: str, guild: str):
    results, exception = await logic.add_person(person_name, relation, guild)
    if type(results) == str:
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message(embed=results)

@app_commands.command(name='add_character')
@app_commands.describe(character_name='Enter a character name', character_class='Enter a character class', level='Enter level', person_name='Enter a person name')
async def add_character(interaction: discord.Interaction, character_name: str, character_class: str, level: int,  person_name: str):
    results, exception = await logic.add_character(character_name, character_class, level, person_name)
    if type(results) == str:
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message(embed=results)

@app_commands.command(name='delete_person')
@app_commands.describe(person_name='Enter a person name')
async def delete_person(interaction: discord.Interaction, person_name: str):
    results, exception = await logic.delete_person(person_name)
    await interaction.response.send_message(results)

@app_commands.command(name='delete_character')
@app_commands.describe(character_name='Enter a character name')
async def delete_character(interaction: discord.Interaction, character_name: str):
    results, exception = await logic.delete_character(character_name)
    await interaction.response.send_message(results)

@app_commands.command(name='edit_person')
@app_commands.describe(person_name='Enter a person name', person_name_new='Enter new person name', relation='Enter relation status', guild='Enter a guild')
async def edit_person(interaction: discord.Interaction, person_name: str, person_name_new: str, relation: str, guild: str):
    results, exception = await logic.edit_person(person_name, person_name_new, relation, guild)
    await interaction.response.send_message(results)

@app_commands.command(name='edit_character')
@app_commands.describe(character_name='Enter a character name', character_name_new='Enter new character name', character_class='Enter a character class', level='Enter level', person_name='Enter a person name')
async def edit_character(interaction: discord.Interaction, character_name: str, character_name_new: str, character_class: str, level: int, person_name: str):
    results, error = await logic.edit_character(character_name, character_name_new, character_class, level, person_name)
    await interaction.response.send_message(results)

@app_commands.command(name='who')
@app_commands.describe(character_name='Enter a character name')
async def who(interaction: discord.Interaction, character_name: str):
    results, exception = await logic.who(character_name)
    await interaction.response.send_message(results)

@app_commands.command(name='get_characters')
@app_commands.describe(person_name='Enter a person name')
async def get_characters(interaction: discord.Interaction, person_name: str):
    await interaction.response.defer()
    results, exception = await logic.get_characters(person_name)
    if len(results) > 1994:
        await helper.print_large_message(interaction, results)
    else:
        await interaction.followup.send(results)

@app_commands.command(name='get_person_table')
@app_commands.describe(guild='Optional: Enter a guild')
async def get_person_table(interaction: discord.Interaction, guild: str = None):
   await interaction.response.defer()
   results, exception = await logic.get_person_table(guild)
   if len(results) > 1994:
        await helper.print_large_message(interaction, results)
   else:
        await interaction.followup.send(results)

@app_commands.command(name='get_characters_table')
@app_commands.describe(guild='Optional: Enter a guild', character_class='Optional: Enter a character class')
async def get_characters_table(interaction: discord.Interaction, guild: str = None, character_class: str = None):
    await interaction.response.defer()
    results, exception = await logic.get_characters_table(guild, character_class)
    if len(results) > 1994:
        await helper.print_large_message(interaction, results)
    else:
        await interaction.followup.send(results)

async def parse_image(message: dict):
    await logic.parse_image(message)

@app_commands.command(name='add_raid_event')
@app_commands.describe(raid_name='Enter a raid name')
async def add_raid_event(interaction: discord.Interaction, raid_name: str):
    if interaction.guild:
        results, error = await logic.add_raid_event(interaction.guild, raid_name)
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message("Error (add_raid): no guild passed.")

@app_commands.command(name='add_person_to_raid')
@app_commands.describe(person_name='Enter person', raid_id='Enter raid id')
async def add_person_to_raid(interaction: discord.Interaction, person_name: str, raid_id: int):
    results, exception = await logic.add_person_to_raid(person_name, raid_id)
    await interaction.response.send_message(results)

@add_person_to_raid.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current)

@add_person_to_raid.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@app_commands.command(name='delete_raid_event')
@app_commands.describe(raid_id='Enter raid id')
async def delete_raid_event(interaction: discord.Interaction, raid_id: int):
    results, exception = await logic.delete_raid_event(raid_id)
    await interaction.response.send_message(results)
   
@delete_raid_event.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current)

@app_commands.command(name='delete_person_from_raid')
@app_commands.describe(raid_id='Enter raid id', person_name='Enter person')
async def delete_person_from_raid(interaction: discord.Interaction, person_name: str, raid_id: int):  
    results, exception = await logic.delete_person_from_raid(person_name, raid_id)
    await interaction.response.send_message(results)

@delete_person_from_raid.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@delete_person_from_raid.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current)

# Need to return an embed here:
@app_commands.command(name='award_loot')
@app_commands.describe(item_name='Enter item_name', person_name='Enter person', raid_id='Enter raid ID')
async def award_loot(interaction: discord.Interaction, item_name: str, person_name: str, raid_id: int):  
    item_name_result, icon_id = await helper.item_search(item_name)
    if not item_name_result:
        print(f'Item {item_name} not found.')
        return await interaction.response.send_message(f'Item {item_name} not found.')
    results, image_file, exception = await logic.award_loot(item_name_result, person_name, raid_id, icon_id)
    await interaction.response.send_message(file=image_file, embed=results)

@award_loot.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@award_loot.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current)

@app_commands.command(name='remove_loot')
@app_commands.describe(item_name='Enter item_name', person_name='Enter person', raid_id='Enter raid ID')
async def remove_loot(interaction: discord.Interaction, item_name: str, person_name: str, raid_id: int):  
    item_name_result = await helper.item_search(item_name)
    if not item_name_result:
        print(f'Item {item_name} not found.')
        return await interaction.response.send_message(f'Item {item_name} not found.')
    results, exception = await logic.remove_loot(item_name_result, person_name, raid_id)
    await interaction.response.send_message(results)

@remove_loot.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@remove_loot.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current)

@app_commands.command(name='register_person')
@app_commands.describe(person_name='Enter person')
async def register_person(interaction: discord.Interaction, person_name: str, user_name: str):  
    results, exception = await logic.register_person(person_name, user_name)
    await interaction.response.send_message(results)

@register_person.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@app_commands.command(name='unregister_person')
@app_commands.describe(person_name='Enter person')
async def unregister_person(interaction: discord.Interaction, person_name: str):  
    results, exception = await logic.unregister_person(person_name)
    await interaction.response.send_message(results)

@register_person.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

slash_commands = [
    add_person, 
    add_character, 
    delete_person, 
    delete_character, 
    edit_person, 
    edit_character, 
    who, 
    get_characters, 
    get_person_table, 
    get_characters_table, 
    add_raid_event,
    add_person_to_raid,
    delete_raid_event,
    delete_person_from_raid,
    award_loot,
    remove_loot,
    register_person,
    unregister_person,
    test_run_all_commands
    ]
