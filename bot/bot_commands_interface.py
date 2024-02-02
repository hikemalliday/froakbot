# V2 (slash commands API)
import discord
import bot.bot_commands_logic as logic
from discord import app_commands
import helper
from data.config import test_mode
from discord.app_commands import MissingAnyRole
selected_raid_id = None
# Object to store autocomplete values for input fields
current_inputs = {}

# 'Test' that runs all slash commands, and expects the returned 'exceptions' array to only contain None as every element.
# This implies that no exceptions were thrown inside any of the slash commands.
# This allows me to run all commands after adding a feature, to help find bugs.
# Technically only runs the commands inside the 'bot_commands_logic.py' module, which is not the same as manually running each command individually through
# 'bot_bommands_interface.py', still very useful though.

#NOTE: KEep commented out until we want to actually use it
# @app_commands.command(name='test_run_all_commands')
# @app_commands.checks.has_any_role('Brain Trust')
# async def test_run_all_commands(interaction: discord.Interaction):
#     if test_mode == False:
#         print('data.config.test_mode == False, aborting interface.test_run_all_commands().')
#         return
#     await interaction.response.defer()
#     results, exceptions = await logic.test_run_all_commands(interaction.guild, True)
#     for result in results:
#         if len(result) > 1994:
#             await helper.print_large_message(interaction, result)
#         else:
#             if type(result) == str:
#                 await interaction.followup.send(result)
#             else:
#                 await interaction.followup.send(embed=result)

#     for exception in exceptions:
#         if exception:
#             print(exception)
#             await interaction.followup.send(exception)
    
#     if all(exception is None for exception in exceptions):
#         print('bot_commands_interface.run_all_commands:')
#         print('✅No undesired exceptions found.')
#         await interaction.followup.send(f'✅bot_commands_interface.run_all_commands: No undesired exceptions found.')
# @test_run_all_commands.error
# async def test_run_all_commands_error(interaction: discord.Interaction, error):
#     if isinstance(error, MissingAnyRole):
#         print(f'EXCEPTION: interaface.test_run_all_commands(): {str(error)}')
#         await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='add_person')
@app_commands.describe(person_name='Enter a person name', relation='Enter relation status', guild='Enter a guild')
@app_commands.checks.has_any_role('Brain Trust', 'Members')
async def add_person(interaction: discord.Interaction, person_name: str, relation: str, guild: str):
        results, exception = await logic.add_person(person_name, relation, guild)
        if type(results) == str:
            await interaction.response.send_message(results)
        else:
            await interaction.response.send_message(embed=results)
@add_person.error
async def add_person_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.add_person(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='add_character')
@app_commands.describe(character_name='Enter a character name', character_class='Enter a character class', level='Enter level', person_name='Enter a person name')
@app_commands.checks.has_any_role('Brain Trust', 'Members')
async def add_character(interaction: discord.Interaction, character_name: str, character_class: str, level: int,  person_name: str):
    results, exception = await logic.add_character(character_name, character_class, level, person_name)
    if type(results) == str:
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message(embed=results)
@add_character.error
async def add_character_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.add_character(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='delete_person')
@app_commands.describe(person_name='Enter a person name')
@app_commands.checks.has_any_role('Brain Trust', 'Members')
async def delete_person(interaction: discord.Interaction, person_name: str):
    results, exception = await logic.delete_person(person_name)
    await interaction.response.send_message(results)
@delete_person.error
async def delete_person_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.delete_person(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='delete_character')
@app_commands.describe(character_name='Enter a character name')
@app_commands.checks.has_any_role('Brain Trust', 'Members')
async def delete_character(interaction: discord.Interaction, character_name: str):
    results, exception = await logic.delete_character(character_name)
    await interaction.response.send_message(results)
@delete_character.error
async def delete_character_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.delete_character(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')


@app_commands.command(name='edit_person')
@app_commands.describe(person_name='Enter a person name', person_name_new='Enter new person name', relation='Enter relation status', guild='Enter a guild')
@app_commands.checks.has_any_role('Brain Trust', 'Members')
async def edit_person(interaction: discord.Interaction, person_name: str, person_name_new: str, relation: str, guild: str):
    results, exception = await logic.edit_person(person_name, person_name_new, relation, guild)
    await interaction.response.send_message(results)
@edit_person.error
async def edit_person_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.edit_person(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='edit_character')
@app_commands.describe(character_name='Enter a character name', character_name_new='Enter new character name', character_class='Enter a character class', level='Enter level', person_name='Enter a person name')
@app_commands.checks.has_any_role('Brain Trust', 'Members')
async def edit_character(interaction: discord.Interaction, character_name: str, character_name_new: str, character_class: str, level: int, person_name: str):
    results, exception = await logic.edit_character(character_name, character_name_new, character_class, level, person_name)
    await interaction.response.send_message(results)
@edit_character.error
async def edit_character_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.edit_character(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='who')
@app_commands.describe(character_name='Enter a character name')
@app_commands.checks.has_any_role('Brain Trust','Members')
async def who(interaction: discord.Interaction, character_name: str):
    results, exception = await logic.who(character_name)
    await interaction.response.send_message(results)
@who.error
async def who_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.who(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='get_characters')
@app_commands.describe(person_name='Enter a person name')
@app_commands.checks.has_any_role('Brain Trust','Members')
async def get_characters(interaction: discord.Interaction, person_name: str):
    await interaction.response.defer()
    results, exception = await logic.get_characters(person_name)
    if len(results) > 1994:
        await helper.print_large_message(interaction, results)
    else:
        await interaction.followup.send(results)
@get_characters.error
async def get_characters_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.get_characters(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='get_person_table')
@app_commands.describe(guild='Optional: Enter a guild')
@app_commands.checks.has_any_role('Brain Trust','Members')
async def get_person_table(interaction: discord.Interaction, guild: str = None):
   await interaction.response.defer()
   results, exception = await logic.get_person_table(guild)
   if len(results) > 1994:
        await helper.print_large_message(interaction, results)
   else:
        await interaction.followup.send(results)
@get_person_table.error
async def get_person_table_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.get_person_table(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='get_characters_table')
@app_commands.describe(guild='Optional: Enter a guild', character_class='Optional: Enter a character class')
@app_commands.checks.has_any_role('Brain Trust','Members')
async def get_characters_table(interaction: discord.Interaction, guild: str = None, character_class: str = None):
    await interaction.response.defer()
    results, exception = await logic.get_characters_table(guild, character_class)
    if len(results) > 1994:
        await helper.print_large_message(interaction, results)
    else:
        await interaction.followup.send(results)
@get_characters_table.error
async def get_characters_table_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.get_characters_table(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

async def parse_image(message: dict):
    await logic.parse_image(message)

@app_commands.command(name='add_raid_event')
@app_commands.describe(raid_name='Enter a raid name')
@app_commands.checks.has_any_role('Brain Trust')
async def add_raid_event(interaction: discord.Interaction, raid_name: str):
    if interaction.guild:
        results, exception = await logic.add_raid_event(interaction.guild, raid_name)
        if type(results) == str:
            await interaction.response.send_message(results)
        else:
            await interaction.response.send_message(embed=results)
    else:
        await interaction.response.send_message("❌ERROR interface.add_raid_event(): no discord_server passed.")
@add_raid_event.error
async def add_raid_event_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.add_raid_event(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='add_person_to_raid')
@app_commands.describe(person_name='Enter person', raid_id='Enter raid id')
@app_commands.checks.has_any_role('Brain Trust')
async def add_person_to_raid(interaction: discord.Interaction, person_name: str, raid_id: int):
    results, exception = await logic.add_person_to_raid(person_name, raid_id)
    await interaction.response.send_message(results)

@add_person_to_raid.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

# person_name is passed as NONE here, as it should (We dont want to autofill based on person_name)
@add_person_to_raid.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current, None)

@add_person_to_raid.error
async def add_person_to_raid_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.add_person_to_raid(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='get_raid')
@app_commands.describe(raid_id='Enter raid id')
@app_commands.checks.has_any_role('Brain Trust','Members')
async def get_raid(interaction: discord.Interaction, raid_id: int):
    results, exception = await logic.get_raid(raid_id)
    if type(results) == str:
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message(embed=results)

@add_person_to_raid.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current, None)

@get_raid.error
async def get_raid_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.get_raid(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='get_all_raids')
@app_commands.describe(person_name='Enter person')
@app_commands.checks.has_any_role('Brain Trust','Members')
async def get_all_raids(interaction: discord.Interaction, person_name: str = None):
    results, exception = await logic.get_all_raids(person_name)
    if type(results) == str:
        await interaction.response.send_message(results)
    else:
        await interaction.response.send_message(embed=results)

@get_all_raids.error
async def get_all_raids_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.get_all_raids(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='delete_raid_event')
@app_commands.describe(raid_id='Enter raid id')
@app_commands.checks.has_any_role('Brain Trust')
async def delete_raid_event(interaction: discord.Interaction, raid_id: int):
    results, exception = await logic.delete_raid_event(raid_id)
    await interaction.response.send_message(results)

@delete_raid_event.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.raid_name_autocompletion(interaction, current, None)

@delete_raid_event.error
async def delete_raid_event_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.delete_raid_event(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

# person_name is passed to helper.raid_name_autocomplete here, so we can return raid list where user attended
@app_commands.command(name='delete_person_from_raid')
@app_commands.describe(raid_id='Enter raid id', person_name='Enter person')
@app_commands.checks.has_any_role('Brain Trust')
async def delete_person_from_raid(interaction: discord.Interaction, person_name: str, raid_id: int):
    try:
        user_id = interaction.user.id
        results, exception = await logic.delete_person_from_raid(person_name, raid_id)
        await interaction.response.send_message(results)
    finally:
        if user_id in current_inputs:
            current_inputs[user_id] = {}

@delete_person_from_raid.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    user_id = interaction.user.id
    if user_id not in current_inputs:
        current_inputs[user_id] = {}
    
    current_inputs[user_id]['person_name'] = current
    return await helper.person_name_autocompletion(interaction, current)

@delete_person_from_raid.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    user_id = interaction.user.id
    person_name = current_inputs[user_id]['person_name']
    return await helper.raid_name_autocompletion(interaction, current, person_name)

@delete_person_from_raid.error
async def delete_person_from_raid_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.delete_person_from_raid(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

# Need to return an embed here:
@app_commands.command(name='award_loot')
@app_commands.describe(item_name='Enter item_name', person_name='Enter person', raid_id='Enter raid ID')
@app_commands.checks.has_any_role('Brain Trust')
async def award_loot(interaction: discord.Interaction, item_name: str, person_name: str, raid_id: int):
    try:
        user_id = interaction.user.id
        item_name_result, icon_id = await helper.item_search(item_name)
        if 'Couldnt find item:' in item_name_result:
            return await interaction.response.send_message(f'❌ERROR: Item {item_name} not found.')
        results, image_file, exception = await logic.award_loot(item_name_result, person_name, raid_id, icon_id)
        if type(results) == str:
            await interaction.response.send_message(results)
        else:
            await interaction.response.send_message(file=image_file, embed=results)
    finally:
        if user_id in current_inputs:
            current_inputs[user_id] = {}
        
@award_loot.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
        user_id = interaction.user.id
        if user_id not in current_inputs:
            current_inputs[user_id] = {}

        current_inputs[user_id]['person_name'] = current
        return await helper.person_name_autocompletion(interaction, current)
    
@award_loot.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    # Perhaps pass in 'current_inputs[user_id]['person_name']'
    user_id = interaction.user.id
    person_name = current_inputs[user_id]['person_name']
    return await helper.raid_name_autocompletion(interaction, current, person_name)

@award_loot.error
async def award_loot_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.award_loot(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='remove_loot')
@app_commands.describe(item_name='Enter item_name', person_name='Enter person', raid_id='Enter raid ID')
@app_commands.checks.has_any_role('Brain Trust')
async def remove_loot(interaction: discord.Interaction, item_name: str, person_name: str, raid_id: int):  
    try:
        user_id = interaction.user.id
        item_name_result, icon_id = await helper.item_search(item_name)
        print(f'interface.remove_loot.item_name_result: {str(item_name_result)}')
        if 'Couldnt find item:' in item_name_result:
            return await interaction.response.send_message(f'❌ERROR: Item {item_name} not found.')
        results, image_file, exception = await logic.remove_loot(item_name_result, icon_id, person_name, raid_id)
        if type(results) == str:
            await interaction.response.send_message(results)
        else:
            await interaction.response.send_message(file=image_file, embed=results)
    finally:
        if user_id in current_inputs:
            current_inputs[user_id] = {}

@remove_loot.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    user_id = interaction.user.id
    if user_id not in current_inputs:
        current_inputs[user_id] = {}
    
    current_inputs[user_id]['person_name'] = current
    return await helper.person_name_autocompletion(interaction, current)

@remove_loot.autocomplete('raid_id')
async def raid_name_autocompletion(interaction: discord.Interaction, current: str):
    user_id = interaction.user.id
    person_name = current_inputs[user_id]['person_name']
    return await helper.raid_name_autocompletion(interaction, current, person_name)

@remove_loot.error
async def remove_loot_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.remove_loot(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='register_person')
@app_commands.describe(person_name='Enter person')
@app_commands.checks.has_any_role('Brain Trust')
async def register_person(interaction: discord.Interaction, person_name: str, user_name: str):  
    results, exception = await logic.register_person(person_name, user_name)
    await interaction.response.send_message(results)

@register_person.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@register_person.error
async def register_person_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.register_person(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='unregister_person')
@app_commands.describe(person_name='Enter person')
@app_commands.checks.has_any_role('Brain Trust')
async def unregister_person(interaction: discord.Interaction, person_name: str):  
    results, exception = await logic.unregister_person(person_name)
    await interaction.response.send_message(results)

@register_person.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@unregister_person.error
async def unregister_person_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.unregister_person(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

@app_commands.command(name='get_loot')
@app_commands.describe(person_name='Enter person')
@app_commands.checks.has_any_role('Brain Trust', 'Members')
async def get_loot(interaction: discord.Interaction, person_name: str):
        results, exception = await logic.get_loot(person_name)
        if type(results) == str:
            await interaction.response.send_message(results)
        else:
            await interaction.response.send_message(embed=results)

@register_person.autocomplete('person_name')
async def person_name_autocompletion(interaction: discord.Interaction, current: str):
    return await helper.person_name_autocompletion(interaction, current)

@get_loot.error
async def get_loot_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingAnyRole):
        print(f'EXCEPTION: interaface.get_loot(): {str(error)}')
        await interaction.response.send_message(f'❌ERROR: You are missing at least one of the required roles: {error.missing_roles}')

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
    test_run_all_commands,
    get_loot,
    get_all_raids,
    get_raid
    ]
