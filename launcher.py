from FlightRadar24.api import FlightRadar24API
import discord
import asyncpraw
import traceback
from discord.ext import commands
from discord import Intents
import string
import asyncpg
import typing
import random
import datetime 
from datetime import date
import asyncio
import json 
from utils import (
    generate_puzzle_embed,
    is_game_over,
    is_valid_word,
    random_puzzle_id,
    update_embed,
)
import logging
import folium
from folium.features import DivIcon

import io
from PIL import Image



def get_random_string(length):
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str






intents = Intents.all()
intents.presences = False
fr_api = FlightRadar24API()
class abot(commands.Bot):
    def __init__(self):
        super().__init__(intents=intents, command_prefix=";", application_id=930250495732375623, activity=discord.Game(name='FlightTracker | www.flightbot.xyz'))
    async def setup_hook(self):
        await self.tree.sync()



token = ""
bot = abot()
#bot = commands.Bot(command_prefix=get_prefix, intents=intents, ))
bot.launch_time = datetime.datetime.utcnow()
initial_extensions = ['cogs.tracking',
                     'cogs.misc',
                     'cogs.owner',
                     'cogs.airport',
                     'cogs.vatsim',
                     'cogs.fun',
                     'cogs.webserver',
                     'cogs.help',
                     'cogs.music',
                     'cogs.rpg'
                     ]
bot.reddit = asyncpraw.Reddit(client_id='',
                    client_secret ='',
                    username='',
                    password='',
                    user_agent='')


discord.utils.setup_logging()

    
        
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(color=discord.Color.red(), timestamp=discord.utils.utcnow(), title='ERROR', description=f'You are missing the correct permissions to run this command. You need {error.missing_perms[0]}.')
        await ctx.send(embed=embed)
    elif isinstance(error, commands.NotOwner):
        embed = discord.Embed(color=discord.Color.red(), timestamp=discord.utils.utcnow(), title='ERROR', description=f'You are missing the correct permissions to run this command. You need to own this bot.')
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(color=discord.Color.red(), timestamp=discord.utils.utcnow(), title='ERROR', description=f'Unknown command! Please try again with a valid command.')
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(color=discord.Color.red(), timestamp=discord.    utils.utcnow(), title='ERROR', description=f'You are missing one or more of the following required arguments:' + error.param)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandOnCooldown):
        return
    else:
        rand = get_random_string(7)
        embed = discord.Embed(color=discord.Color.red(), timestamp=discord.utils.utcnow(), title="Uh Oh!", description=f'An error has occured. Please join the support server by [clicking here](https://discord.gg/BtVFu7nmYS). Your error code is: ``' + rand + "``.")
        await ctx.send(embed=embed) 
        etype = type(error)
        trace = error.__traceback__
        lines = traceback.format_exception(etype, error, trace)
        traceback_text = ''.join(lines)
        print(traceback_text)
        channel = bot.get_channel(932360487335780422)
        embed1 = discord.Embed(color=discord.Color.red(), timestamp=discord.utils.utcnow(), title='ERROR', description=f'An error has occured: \nError Code: {rand}\nMessage ID: {ctx.message.id}\nError: ```{traceback_text}```')
        await channel.send(embed=embed1)
# 

async def create_db_pool():
    bot.pg_con = await asyncpg.create_pool(database='', user='', password='')

@bot.tree.command(name="test")
async def test(interaction:discord.Interaction):
     await interaction.response.send_message("Help", ephemeral=False)

async def main():
    await create_db_pool() 
    async with bot:
        for extension in initial_extensions:
            await bot.load_extension(extension)
        await bot.load_extension('jishaku')
        await bot.start(token)

   

asyncio.run(main())







    



