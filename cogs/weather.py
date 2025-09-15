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
from datetime import datetime
import regex as re
fr_api = FlightRadar24API()


class Weather(commands.Cog):
    """Used for getting information on the weather in LIVE time."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def metar(self, ctx: discord.Interaction , icao: str):
        """Gets the METAR information from the specified airport."""
        token = ""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://avwx.rest/api/metar/" + ''.join(filter(str.isalpha, icao)), headers={"Authorization": "BEARER " + token}) as resp:
                res = await resp.json()
        if 'error' in res:
            await ctx.response.send_message(embed=discord.Embed(color=discord.Color.red(), title='Error!', description=f'{icao} is not a valid ICAO/IATA code! Please try again with a valid ICAO/IATA code!'))
            return 
        time = datetime.fromisoformat(res['meta']['timestamp'][:-8])
        altimeter =res['altimeter']['value']
        fr = res['flight_rules']
        if int(res['visibility']['value']) > 10:
            vis = str(res['visibility']['value']) + " meter(s)"
        else:
            vis = str(res['visibility']['value']) + " statute mile(s)"
        if res['wind_gust'] == None:
            gust = " none"
        else:
            gust = res['wind_gust']['value']
        winds = str(res['wind_direction']['value']) + " at " + str(res['wind_speed']['value']) + " knots, gusts "  + str(gust)
        raw = res['raw']
        temp = str(res['temperature']['value']) + '° celsius'
        dewpoint = str(res['dewpoint']['value']) + '° celsius'
        embed = discord.Embed(color=discord.Color.green())
        embed.set_author(name=f'{res["station"]} METAR')
        embed.add_field(name="Time:", value=str(time) + "Z", inline=False)
        embed.add_field(name="Altimeter:", value = altimeter, inline=False)
        for dict in res['clouds']:
            embed.add_field(name="Cloud Layer:", value=dict['repr'], inline=False)
        embed.add_field(name='Visibility:', value=vis, inline=False)
        embed.add_field(name='Winds:', value=winds, inline=False)
        embed.add_field(name='Raw METAR:', value=f'```{raw}```', inline=False)
        embed.add_field(name='Temperature:', value=temp, inline=False)
        embed.add_field(name='Dewpoint:', value=dewpoint, inline=False)
        embed.add_field(name='Flight Rules:', value=res['flight_rules'])
        await ctx.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Weather(bot))
