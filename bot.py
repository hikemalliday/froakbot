import discord
import database
import imageprocessing
from decouple import config
import responses

TOKEN = config("BOT_TOKEN")


def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    database.create_tables()
    allowed_roles = [
        "Brain Trust",
        "Admin",
        "Froak",
    ] 

    @client.event
    async def on_ready():
        print(f"{client.user} is now running!")

    @client.event
    async def on_message(message):
        commands = {
            "!add_player": database.add_player,
            "!add_char": database.add_char,
            "!add_character": database.add_char,
            "!delete_player": database.delete_player,
            "!delete_char": database.delete_char,
            "!delete_character": database.delete_char,
            "!edit_player": database.edit_player,
            "!edit_char": database.edit_char,
            "!edit_character": database.edit_char,
            "!who": database.who,
            "!get_chars": database.get_chars,
            "!get_characters": database.get_chars,
            "!players_db": database.get_players_db,
            "!chars_db": database.get_characters_db,
            "!characters_db": database.get_characters_db,
            "!snip": imageprocessing.parse_image,
            "!commands": responses.get_commands,
        }

        # Parse the command:
        input_text = message.content.split()
        command = input_text[0].lower()

        if message.author == client.user:
            return

        if command in commands:
            print("command in commands test")
            user_roles = [role.name for role in message.author.roles]
            if any(role in allowed_roles for role in user_roles):
                database_entry = await commands[command](message)
                if database_entry is None:
                    return
                await message.channel.send(database_entry)

        elif command[0] == "!":
            return await message.channel.send("Unknown command")

    client.run(TOKEN)
