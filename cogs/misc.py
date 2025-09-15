from FlightRadar24.api import FlightRadar24API
import FlightRadar24
import discord
import traceback
from discord.ext import commands, menus
from discord import Intents, app_commands
import pandas as pd
import asyncio
import wikipedia as wp
import json
import aiohttp
from datetime import date
import datetime
import regex as re
fr_api = FlightRadar24API()





class Miscellaneous(commands.Cog):
    """Miscellaneous commands, used for server-side changes."""

    def __init__(self, bot):
        self.bot = bot



    @commands.hybrid_command()
    async def donate(self, ctx):
        """Sends the Bot patreon page."""
        await ctx.send(embed=discord.Embed(color=discord.Color.gold(), title="Flight Tracker Patreon Page", description = "https://www.patreon.com/flighttracker", timestamp=discord.utils.utcnow()))



        
    @app_commands.command()
    async def invite(self, ctx):
        """Sends the Bot Invite"""
        await ctx.send(embed=discord.Embed(color=discord.Color.blurple(), title="Flight Tracker Invite", description = "https://discord.com/api/oauth2/authorize?client_id=930250495732375623&permissions=3072&scope=bot", timestamp=discord.utils.utcnow()))


    @commands.hybrid_command()
    async def uptime(self, ctx):
        """This command shows how long the bot has been running."""
        delta_uptime = datetime.datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"I have been online for: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds.")


    @commands.hybrid_command()
    async def about(self, ctx):
        """Sends information about the bot"""
        embed = discord.Embed(color=discord.Color.gold(), timestamp=discord.utils.utcnow(), title="About FlightTracker")
        embed.add_field(name="Who are we?", value="FlightTracker was made by a team of aviation enthusiasts who noticed the lack of a free, accurate, and reliable discord bot for tracking aircrafts.")
        embed.add_field(name="Development Credits:", value="Head Developer: nahhhhh#2920\nTesters: Around the World#0666 and Chelsea#1160\nCommand Creation Assisting: Peanut#1031", inline=False)
        embed.add_field(name="About the developer:", value="Hey everyone, my name is Ameya! I love aviation and simming. I currently fly and control on VATSIM! Want to fly to my airspace? I usually control Portland Tower at 7-9PM PST, hope to see ya there!", inline=False)
        embed.add_field(name="API Credits:", value="WIP", inline=False)
        embed.add_field(name="Support the Bot:", value="Patreon: https://www.patreon.com/flighttracker\nTop.gg: https://top.gg/bot/930250495732375623\nSupport Server: https://discord.gg/BtVFu7nmYS", inline=False)
        embed.add_field(name="Privacy Policy:", value="https://gist.github.com/ameyanori/a67645d3bf94619bf6266af86bbf782a")
        await ctx.send(embed=embed)
    @commands.hybrid_command()
    async def support(self, ctx):
        """Sends the support server of the bot."""
        embed = discord.Embed(color=discord.Color.gold(), title='FlightTracker Support Server', description='[Click Here](https://discord.gg/BtVFu7nmYS)')
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def ping(self, ctx):
        """Sends the bot's ping."""
        await ctx.send(f':ping_pong:{int(self.bot.latency * 1000)}ms is my ping.')






async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
