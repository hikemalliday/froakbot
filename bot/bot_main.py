# Refactoring to use superior 'slash commands' api, instead text based commands
from decouple import config as env
import data.config as config
import  bot.bot_commands_interface as bot_commands
from db_connection import DatabaseConnection
from contextlib import contextmanager
from bot.bot_instance import bot
import helper

db_path = config.db_path
TOKEN = env("BOT_TOKEN")
exit_flag = False

helper.intro_prompt()
   
def run_discord_bot():
    db = DatabaseConnection(db_path)
    try:
        db.open()
        bot.db_connection = db.connection
        @bot.event
        async def on_ready():
            try:
                for command in bot_commands.slash_commands:
                    bot.tree.add_command(command)
                    print(f'Adding command: {command.name}')
                synced = await bot.tree.sync()
                print(f'Synced {len(synced)} command(s)')
            except Exception as e:
                print(e)
        # There is only 1 text based command. This particular command is not well suited for Slash Commands:
        @bot.event
        async def on_message(message):
            commands = {
                '!snip': bot_commands.parse_image
            }

            if message and message.content:
                input_text = message.content.split()
                command = input_text[0].lower()

                if message.author == bot.user:
                    return

                if command in commands:
                    user_roles = [role.name for role in message.author.roles]
                    if any(role in config.allowed_roles for role in user_roles):
                        results = await commands[command](message)
                        if results is None:
                            return

                        await message.channel.send(results)
                await bot.process_commands(message)
        bot.run(TOKEN)
    finally:
        db.close()
    


