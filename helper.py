import discord
import data.config as config

def add_person_embed(person_name: str, relation: int, guild: str) -> object:
    if relation == 0:
        relation = "Enemy"
    if relation == 1:
        relation = "Friendly"
    if relation == 2:
        relation = "Neutral"
    embed = discord.Embed(title='/add_person', description='Person successfully added:', color=discord.Color.random())
    embed.set_thumbnail(url=f'{config.froak_icon}')
    embed.add_field(name='Person Name', value=person_name)
    embed.add_field(name='Relation', value=relation)
    embed.add_field(name='Guild', value=guild)
    return embed

def add_character_embed(character_name: str, character_class: str, level: int, person_name: str) -> object:
    embed = discord.Embed(title='/add_character', description='Character successfully added:', color=discord.Color.random())
    embed.set_thumbnail(url=f'{config.froak_icon}')
    embed.add_field(name='Character Name', value=character_name)
    embed.add_field(name='Character Class', value=character_class)
    embed.add_field(name='Level', value=level)
    embed.add_field(name='Person Name', value=person_name)
    return embed

async def get_most_populated_channel(guild):
    max_members = 0
    most_populated_channel = None
    raiders = []
    for channel in guild.channels:
        if isinstance(channel, discord.VoiceChannel):
            member_count = len(channel.members)
            if member_count > max_members:
                raiders = [member.global_name for member in channel.members]
                max_members = member_count
                most_populated_channel = channel

    if most_populated_channel:
        print(f"The most populated voice channel is {most_populated_channel.name} with {len(most_populated_channel.members)} members.")
        print('Raiders: ', str(raiders))
        return raiders
    else:
        return "There are no members in any voice channels."
    