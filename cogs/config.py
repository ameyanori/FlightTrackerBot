from FlightRadar24.api import FlightRadar24API
import FlightRadar24
import discord
import traceback
from discord.ext import commands, menus
from discord import Intents
import pandas as pd
import asyncio
import wikipedia as wp
import json
import aiohttp
from datetime import datetime
import regex as re
fr_api = FlightRadar24API()





class Config(commands.Cog):
    """Client-side changes, most commands require administrator."""

    def __init__(self, bot):
        self.bot = bot
    

        
        
        
    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        """Sends the server's prefix."""
        connection = await self.bot.pg_con.acquire()
        async with connection.transaction():
            prefixn = await connection.fetch('SELECT prefix FROM prefixs WHERE guild_id = $1', ctx.guild.id)
        await self.bot.pg_con.release(connection)
        await ctx.send(f"{ctx.guild.name}'s prefix is: {prefixn[0][0]}.")
    
    
    @prefix.command()
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def set(self, ctx, prefix = None):
        """This command sets the bot's prefix for the server only. Requires administrator."""
        connection = await self.bot.pg_con.acquire()
        async with connection.transaction():
            await connection.execute('UPDATE prefixs SET prefix = $1 WHERE guild_id = $2', prefix, ctx.guild.id)
        await self.bot.pg_con.release(connection)
        await ctx.send(f'Updated the prefix to {prefix}.')  




async def setup(bot):
    await bot.add_cog(Config(bot))