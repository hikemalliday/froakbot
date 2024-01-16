# V2 (slash commands API)
import discord
import bot.bot_commands_logic as logic
from discord import app_commands
import helper
selected_raid_id = None

@app_commands.command(name='add_person')
@app_commands.describe(person_name='Enter a person name', relation='Enter relation status', guild='Enter a guild')
async def add_person(interaction: discord.Interaction, person_name: str, relation: str, guild: str):
    results = await logic.add_person(person_name, relation, guild)
    if type(results) == str:
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message(embed=results)

@app_commands.command(name='add_character')
@app_commands.describe(character_name='Enter a character name', character_class='Enter a character class', level='Enter level', person_name='Enter a person name')
async def add_character(interaction: discord.Interaction, character_name: str, character_class: str, level: int,  person_name: str):
    results = await logic.add_character(character_name, character_class, level, person_name)
    if type(results) == str:
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message(embed=results)

@app_commands.command(name='delete_person')
@app_commands.describe(person_name='Enter a person name')
async def delete_person(interaction: discord.Interaction, person_name: str):
    results = await logic.delete_person(person_name)
    await interaction.response.send_message(results)

@app_commands.command(name='delete_character')
@app_commands.describe(character_name='Enter a character name')
async def delete_character(interaction: discord.Interaction, character_name: str):
    results = await logic.delete_character(character_name)
    await interaction.response.send_message(results)

@app_commands.command(name='edit_person')
@app_commands.describe(person_name='Enter a person name', person_name_new='Enter new person name', relation='Enter relation status', guild='Enter a guild')
async def edit_person(interaction: discord.Interaction, person_name: str, person_name_new: str, relation: str, guild: str):
    results = await logic.edit_person(person_name, person_name_new, relation, guild)
    await interaction.response.send_message(results)

@app_commands.command(name='edit_character')
@app_commands.describe(character_name='Enter a character name', character_name_new='Enter new character name', character_class='Enter a character class', level='Enter level', person_name='Enter a person name')
async def edit_character(interaction: discord.Interaction, character_name: str, character_name_new: str, character_class: str, level: int, person_name: str):
    results = await logic.edit_character(character_name, character_name_new, character_class, level, person_name)
    await interaction.response.send_message(results)

@app_commands.command(name='who')
@app_commands.describe(character_name='Enter a character name')
async def who(interaction: discord.Interaction, character_name: str):
    results = await logic.who(character_name)
    await interaction.response.send_message(results)

@app_commands.command(name='get_characters')
@app_commands.describe(person_name='Enter a person name')
async def get_characters(interaction: discord.Interaction, person_name: str):
    await interaction.response.defer()
    results = await logic.get_characters(person_name)
    if len(results) > 1994:
        for i in range(0, len(results), 1994):
            chunk = results[i : i + 1994]
            chunk = "```" + chunk + "```"
            await interaction.followup.send(chunk)
    else:
        await interaction.followup.send(results)

@app_commands.command(name='get_person_table')
@app_commands.describe(guild='Optional: Enter a guild')
async def get_person_table(interaction: discord.Interaction, guild: str = None):
   await interaction.response.defer()
   results = await logic.get_person_table(guild)
   if len(results) > 1994:
        for i in range(0, len(results), 1994):
            chunk = results[i : i + 1994]
            chunk = "```" + chunk + "```"
            await interaction.followup.send(chunk)
   else:
        await interaction.followup.send(results)

@app_commands.command(name='get_characters_table')
@app_commands.describe(guild='Optional: Enter a guild', character_class='Optional: Enter a character class')
async def get_characters_table(interaction: discord.Interaction, guild: str = None, character_class: str = None):
    await interaction.response.defer()
    results = await logic.get_characters_table(guild, character_class)
    if len(results) > 1994:
        for i in range(0, len(results), 1994):
            chunk = results[i : i + 1994]
            chunk = "```" + chunk + "```"
            await interaction.followup.send(chunk)
    else:
        await interaction.followup.send(results)

async def parse_image(message: dict):
    await logic.parse_image(message)

@app_commands.command(name='item_search')
@app_commands.describe(item_name='Enter an item name')
async def item_search(interaction: discord.Interaction, item_name: str):
    results = await logic.item_search(item_name)
    await interaction.response.send_message(results)



@app_commands.command(name='biggest_channel')
async def get_most_populated_channel(interaction: discord.Interaction):
    if interaction.guild:
        results = await helper.get_most_populated_channel(interaction.guild)
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message("Error (biggest_channel): no guild passed.")

@app_commands.command(name='add_raid_event')
@app_commands.describe(raid_name='Enter a raid name')
async def add_raid_event(interaction: discord.Interaction, raid_name: str):
    if interaction.guild:
        results = await logic.add_raid_event(interaction.guild, raid_name)
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message("Error (add_raid): no guild passed.")

@app_commands.command(name='add_person_to_raid')
@app_commands.describe(person_name='Enter person', raid_id='Enter raid id')
async def add_person_to_raid(interaction: discord.Interaction, person_name: str, raid_id: int):
    print('interface.add_person_to_raid() start')
    results = await logic.add_person_to_raid(person_name, raid_id)
    await interaction.response.send_message(results)
   
@add_person_to_raid.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    print('interface.raid_name_autocompletion() start')
    raid_names = await helper.fetch_raid_names(current)
    print('interface.raid_name_autocompletion() 1')
    if raid_names is None:
        return ['No raids of that name found.']
    choices = [discord.app_commands.Choice(name=str(name).replace('(','').replace(')',''), value=int(name[0])) for name in raid_names]
    return choices

@add_person_to_raid.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    person_names = await helper.fetch_raider_names(current)
    if person_names is None:
        return ['/add_person_to_raid.person_name_autocompletion() error.']
    choices = [discord.app_commands.Choice(name=name, value=name) for name in person_names]
    return choices

# Need to fetch pulldown for this, and delete raid_master, raid_master_backup, dkp, dkp_backup 
@app_commands.command(name='delete_raid_event')
@app_commands.describe(raid_id='Enter raid id')
async def delete_raid_event(interaction: discord.Interaction, raid_id: int):
    results = await logic.delete_raid_event(raid_id)
    await interaction.response.send_message(results)
   
@delete_raid_event.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    raid_names = await helper.fetch_raid_names(current)
    if raid_names is None:
        return ['No raids of that name found.']
    choices = [discord.app_commands.Choice(name=str(name).replace('(','').replace(')',''), value=int(name[0])) for name in raid_names]
    return choices

@app_commands.command(name='delete_person_from_raid')
@app_commands.describe(raid_id='Enter raid id', person_name='Enter person')
async def delete_person_from_raid(interaction: discord.Interaction, person_name: str, raid_id: int):  
    results = await logic.delete_person_from_raid(person_name, raid_id)
    print('delete_person_from_raid() results: ', )
    await interaction.response.send_message(results)
   
@delete_person_from_raid.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    person_names = await helper.fetch_raider_names(current)
    if person_names is None:
        return ['Raid has no raiders.']
    choices = [discord.app_commands.Choice(name=name, value=name) for name in person_names]
    return choices

@delete_person_from_raid.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    raid_names = await helper.fetch_raid_names(current)
    if raid_names is None:
        return ['No raids of that name found.']
    choices = [discord.app_commands.Choice(name=str(name).replace('(','').replace(')',''), value=int(name[0])) for name in raid_names]
    return choices


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
    item_search,
    get_most_populated_channel,
    add_raid_event,
    add_person_to_raid,
    delete_raid_event,
    delete_person_from_raid
    ]