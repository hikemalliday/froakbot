# V2 (slash commands API)
import discord
import bot.bot_commands_logic as logic
from discord import app_commands
import helper
selected_raid_id = None

# Runs all commands and prints logs. Much easier than testing things by hand. Not a true 'unit test' or testing library, but I find it very useful
@app_commands.command(name='run_all_commands')
async def run_all_commands(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        results = await logic.run_all_commands()
    except Exception as e:
        assert False, f'run_all_commands raised an exception: {e}'
    for result in results:
        if len(result) > 1994:
            await helper.print_large_message(interaction, result)
        else:
            await interaction.followup.send(result)

#NOTE: added to test command
@app_commands.command(name='add_person')
@app_commands.describe(person_name='Enter a person name', relation='Enter relation status', guild='Enter a guild')
async def add_person(interaction: discord.Interaction, person_name: str, relation: str, guild: str):
    results = await logic.add_person(person_name, relation, guild)
    if type(results) == str:
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message(embed=results)
#NOTE: added to test command
@app_commands.command(name='add_character')
@app_commands.describe(character_name='Enter a character name', character_class='Enter a character class', level='Enter level', person_name='Enter a person name')
async def add_character(interaction: discord.Interaction, character_name: str, character_class: str, level: int,  person_name: str):
    results = await logic.add_character(character_name, character_class, level, person_name)
    if type(results) == str:
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message(embed=results)
#NOTE: added to test command
@app_commands.command(name='delete_person')
@app_commands.describe(person_name='Enter a person name')
async def delete_person(interaction: discord.Interaction, person_name: str):
    results = await logic.delete_person(person_name)
    await interaction.response.send_message(results)
#NOTE: added to test command
@app_commands.command(name='delete_character')
@app_commands.describe(character_name='Enter a character name')
async def delete_character(interaction: discord.Interaction, character_name: str):
    results = await logic.delete_character(character_name)
    await interaction.response.send_message(results)
#NOTE: added to test command
@app_commands.command(name='edit_person')
@app_commands.describe(person_name='Enter a person name', person_name_new='Enter new person name', relation='Enter relation status', guild='Enter a guild')
async def edit_person(interaction: discord.Interaction, person_name: str, person_name_new: str, relation: str, guild: str):
    results = await logic.edit_person(person_name, person_name_new, relation, guild)
    await interaction.response.send_message(results)
#NOTE: added to test command
@app_commands.command(name='edit_character')
@app_commands.describe(character_name='Enter a character name', character_name_new='Enter new character name', character_class='Enter a character class', level='Enter level', person_name='Enter a person name')
async def edit_character(interaction: discord.Interaction, character_name: str, character_name_new: str, character_class: str, level: int, person_name: str):
    results = await logic.edit_character(character_name, character_name_new, character_class, level, person_name)
    await interaction.response.send_message(results)
#NOTE: added to test command
@app_commands.command(name='who')
@app_commands.describe(character_name='Enter a character name')
async def who(interaction: discord.Interaction, character_name: str):
    results = await logic.who(character_name)
    await interaction.response.send_message(results)
#NOTE: added to test command
@app_commands.command(name='get_characters')
@app_commands.describe(person_name='Enter a person name')
async def get_characters(interaction: discord.Interaction, person_name: str):
    await interaction.response.defer()
    results = await logic.get_characters(person_name)
    if len(results) > 1994:
        await helper.print_large_message(interaction, results)
    else:
        await interaction.followup.send(results)
#NOTE: added to test command
@app_commands.command(name='get_person_table')
@app_commands.describe(guild='Optional: Enter a guild')
async def get_person_table(interaction: discord.Interaction, guild: str = None):
   await interaction.response.defer()
   results = await logic.get_person_table(guild)
   if len(results) > 1994:
        await helper.print_large_message(interaction, results)
   else:
        await interaction.followup.send(results)
#NOTE: added to test command
@app_commands.command(name='get_characters_table')
@app_commands.describe(guild='Optional: Enter a guild', character_class='Optional: Enter a character class')
async def get_characters_table(interaction: discord.Interaction, guild: str = None, character_class: str = None):
    await interaction.response.defer()
    results = await logic.get_characters_table(guild, character_class)
    if len(results) > 1994:
        await helper.print_large_message(interaction, results)
    else:
        await interaction.followup.send(results)

async def parse_image(message: dict):
    await logic.parse_image(message)
#NOTE: added to test command
@app_commands.command(name='add_raid_event')
@app_commands.describe(raid_name='Enter a raid name')
async def add_raid_event(interaction: discord.Interaction, raid_name: str):
    if interaction.guild:
        results = await logic.add_raid_event(interaction.guild, raid_name)
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message("Error (add_raid): no guild passed.")
#NOTE: added to test command
@app_commands.command(name='add_person_to_raid')
@app_commands.describe(person_name='Enter person', raid_id='Enter raid id')
async def add_person_to_raid(interaction: discord.Interaction, person_name: str, raid_id: int):
    results = await logic.add_person_to_raid(person_name, raid_id)
    await interaction.response.send_message(results)

@add_person_to_raid.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current)

@add_person_to_raid.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)
#NOTE: added to test command
@app_commands.command(name='delete_raid_event')
@app_commands.describe(raid_id='Enter raid id')
async def delete_raid_event(interaction: discord.Interaction, raid_id: int):
    results = await logic.delete_raid_event(raid_id)
    await interaction.response.send_message(results)
   
@delete_raid_event.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current)
#NOTE: added to test command
@app_commands.command(name='delete_person_from_raid')
@app_commands.describe(raid_id='Enter raid id', person_name='Enter person')
async def delete_person_from_raid(interaction: discord.Interaction, person_name: str, raid_id: int):  
    results = await logic.delete_person_from_raid(person_name, raid_id)
    await interaction.response.send_message(results)

@delete_person_from_raid.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@delete_person_from_raid.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current)
#NOTE: added to test command
@app_commands.command(name='award_loot')
@app_commands.describe(item_name='Enter item_name', person_name='Enter person', raid_id='Enter raid ID')
async def award_loot(interaction: discord.Interaction, item_name: str, person_name: str, raid_id: int):  
    item_name_result = await helper.item_search(item_name)
    if not item_name_result:
        print(f'Item {item_name} not found.')
        return await interaction.response.send_message(f'Item {item_name} not found.')
    results = await logic.award_loot(item_name_result, person_name, raid_id)
    await interaction.response.send_message(results)

@award_loot.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@award_loot.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current)
#NOTE: added to test command
@app_commands.command(name='remove_loot')
@app_commands.describe(item_name='Enter item_name', person_name='Enter person', raid_id='Enter raid ID')
async def remove_loot(interaction: discord.Interaction, item_name: str, person_name: str, raid_id: int):  
    item_name_result = await helper.item_search(item_name)
    if not item_name_result:
        print(f'Item {item_name} not found.')
        return await interaction.response.send_message(f'Item {item_name} not found.')
    results = await logic.remove_loot(item_name_result, person_name, raid_id)
    await interaction.response.send_message(results)

@remove_loot.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@remove_loot.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current)
#NOTE: added to test command
@app_commands.command(name='register_person')
@app_commands.describe(person_name='Enter person')
async def register_person(interaction: discord.Interaction, person_name: str, user_name: str):  
    results = await logic.register_person(person_name, user_name)
    await interaction.response.send_message(results)

@register_person.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)
#NOTE: added to test command
@app_commands.command(name='unregister_person')
@app_commands.describe(person_name='Enter person')
async def unregister_person(interaction: discord.Interaction, person_name: str):  
    results = await logic.unregister_person(person_name)
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
    run_all_commands
    ]