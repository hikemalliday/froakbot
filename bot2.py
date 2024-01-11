# Refactoring to use superior 'slash commands' api, instead text based commands
import discord
from discord.ext import commands
from decouple import config as env
import  bot_commands_interface as bot_commands
import config
TOKEN = env("BOT_TOKEN")

def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    @bot.event
    async def on_ready():
        print('Bot is Up and Ready!')
        try:
            for command in bot_commands.slash_commands:
                bot.tree.add_command(command)
                print(f'Adding command: {command.name}')
            synced = await bot.tree.sync()
            print(f'Synced {len(synced)} command(s)')
        except Exception as e:
            print(e)
    # Text input command for !snip (slash commands was harder to implement for this function)
    @bot.event
    async def on_message(message):
        commands = {
            '!snip': bot_commands.parse_image
        }

        input_text = message.content.split()
        print(input_text)
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

