#!/usr/bin/env python3

# Based on https://github.com/Rapptz/discord.py/blob/master/examples/app_commands/basic.py

import logging
import pathlib
import discord
from discord import app_commands

discord.utils.setup_logging()
LOGGER = logging.getLogger(__name__)


class NopeClient(discord.Client):
    # Suppress error on the User attribute being None since it fills up later
    user: discord.ClientUser

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync global commands. Will take up to an hour until they are shown to the end-user.
        await self.tree.sync()


intents = discord.Intents.default()
client = NopeClient(intents=intents)

# Contains nope count for each guild seperately
nopes_per_guild = dict()


@client.event
async def on_ready():
    LOGGER.info(f'Logged in as {client.user} (ID: {client.user.id})\n------')


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

@client.tree.command()
async def no(interaction: discord.Interaction):
    """Loudly add a Nope"""
    add_nope(interaction.guild_id)
    await interaction.response.send_message(f'{interaction.user.mention} has added a Nope! 😱')

@client.tree.command()
async def nope(interaction: discord.Interaction):
    """Silently add a Nope"""
    add_nope(interaction.guild_id)
    await interaction.response.send_message('Nope added 🥲', ephemeral=True)

def add_nope(guild_id: int|None) -> None:
    """Add a nope for the guild with the provided ID"""
    global nopes_per_guild
    nopes = nopes_per_guild.get(guild_id, 0)
    nopes += 1
    nopes_per_guild[guild_id] = nopes 

@client.tree.command()
async def count(interaction: discord.Interaction):
    """Count the nopes"""
    global nopes_per_guild
    nopes = nopes_per_guild.get(interaction.guild_id, 0)
    await interaction.response.send_message(f'I have counted {nopes} nope{'' if nopes == 1 else 's'} so far 🧐')

@client.tree.command()
async def reset(interaction: discord.Interaction):
    """Remove the nopes"""
    global nopes_per_guild
    nopes_per_guild[interaction.guild_id] = 0
    await interaction.response.send_message('The nopes have gone! 🥳')

# Get token

tokenPath = pathlib.Path(__file__).parent / 'nope_bot.token'
with open(tokenPath, 'r', encoding="utf-8") as tokenFile:
    token = tokenFile.readline()

# Run and connect    

client.run(token, log_handler=None)