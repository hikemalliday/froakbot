import discord
from decouple import config as env
import config
import bot_commands
import db_migration

TOKEN = env("BOT_TOKEN")

def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    # commented out for now, we are mid db-revamp
    #bot_commands.create_tables()
    #db_migration.create_tables()
    #db_migration.migrate_players_db()
    db_migration.migrate_characters_db()
    
    @client.event
    async def on_ready():
        print(f"{client.user} is now running!")

    @client.event
    async def on_message(message):
        commands = {
            "!add_player": bot_commands.add_player,
            "!add_char": bot_commands.add_char,
            "!add_character": bot_commands.add_char,
            "!delete_player": bot_commands.delete_player,
            "!delete_char": bot_commands.delete_char,
            "!delete_character": bot_commands.delete_char,
            "!edit_player": bot_commands.edit_player,
            "!edit_char": bot_commands.edit_char,
            "!edit_character": bot_commands.edit_char,
            "!who": bot_commands.who,
            "!get_chars": bot_commands.get_chars,
            "!get_characters": bot_commands.get_chars,
            "!players_db": bot_commands.get_players_db,
            "!chars_db": bot_commands.get_characters_db,
            "!characters_db": bot_commands.get_characters_db,
            "!snip": bot_commands.parse_image,
            "!commands": bot_commands.get_commands,
            "!test": bot_commands.test
        }
        # Parse the command:
        input_text = message.content.split()
        command = input_text[0].lower()

        if message.author == client.user:
            return

        if command in commands:
            user_roles = [role.name for role in message.author.roles]
            if any(role in config.allowed_roles for role in user_roles):
                database_entry = await commands[command](message)
                if database_entry is None:
                    return

                await message.channel.send(database_entry)

    client.run(TOKEN)
