# V2 (slash commands API)
import discord
import bot.bot_commands_logic as logic
from discord import app_commands

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
async def item_search(interaction: discord.Interaction, user_input: str):
    results = await logic.item_search(user_input)
    await interaction.response.send_message(results)

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
    item_search
    ]