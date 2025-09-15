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

async def get_airport_name_icao(icao):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(f"https://www.airport-data.com/api/ap_info.json?icao={icao}") as res:
            resp = await res.json()
            try:
                return resp['name']
            except:
                try:
                    res = await fr_api.get_airport(icao)
                    return res['name']
                except:
                    return None


async def get_facility(id):
    async with aiohttp.ClientSession() as cs:
        async with cs.get("https://data.vatsim.net/v3/vatsim-data.json") as res:
                resp = await res.json()
        for item in resp['facilities']:
            if item['id'] == id:
                return item['short']

async def get_rating(id):
    async with aiohttp.ClientSession() as cs:
        async with cs.get("https://data.vatsim.net/v3/vatsim-data.json") as res:
                resp = await res.json()
        for item in resp['ratings']:
            if item['id'] == id:
                return item['short']

class Vatsim(commands.Cog):
    """Commands associated with the Virtual Air Traffic Simulation Network(VATSIM)."""

    def __init__(self, bot):
        self.bot = bot
    @commands.hybrid_command()
    async def vatsim(self, ctx, callsign: str):
        """Fetches the specific VATSIM flight associated with that callsign."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://data.vatsim.net/v3/vatsim-data.json") as res:
                resp = await res.json()
            for pilot in resp['pilots']:
                if pilot['callsign'] == callsign.upper(): 
                    embed = discord.Embed(color=discord.Color.blurple(), timestamp=discord.utils.utcnow())
                    embed.set_author(name=f'{pilot["callsign"]} - VATSIM')
                    embed.add_field(name="Callsign:", value=pilot['callsign'])
                    embed.add_field(name="CID:", value=pilot['cid'])
                    embed.add_field(name="Server:", value=pilot['server'])
                    embed.add_field(name="Name:", value=pilot['name'])
                    
                    if pilot['flight_plan'] is None:
                        await ctx.send("That flight does not have a flight plan filed.")
                        return
                    
                    embed.add_field(name="Origin:", value=await get_airport_name_icao(pilot['flight_plan']['departure']) + f" ({pilot['flight_plan']['departure']})")
                    embed.add_field(name="Arrival:", value=await get_airport_name_icao(pilot['flight_plan']['arrival']) + f" ({pilot['flight_plan']['arrival']})")
                    embed.add_field(name="Transponder:", value=pilot['transponder'])
                    embed.add_field(name="Flight Rules:", value=pilot['flight_plan']['flight_rules'] + "FR")
                    embed.add_field(name="Altitude:", value=pilot['altitude'])
                    embed.add_field(name="Heading:", value=pilot['heading'])
                    embed.add_field(name="Ground Speed:", value=pilot['groundspeed'])
                    embed.add_field(name="Aircraft:", value=pilot['flight_plan']['aircraft_short'])
                    embed.add_field(name="Latitude:", value=pilot['latitude'])
                    embed.add_field(name="Longitude:", value=pilot['longitude'])
                    embed.add_field(name="Altimeter:", value=pilot['qnh_i_hg'])
                    embed.add_field(name="Assigned Altitude:", value=pilot['flight_plan']['altitude'])
                    embed.add_field(name="Assigned Squawk:", value=pilot['flight_plan']['assigned_transponder'])
                    embed.add_field(name="Departure Time:", value=pilot['flight_plan']['assigned_transponder'] + "z")
                    embed.add_field(name="Route:", value=pilot['flight_plan']['route'])
                    await ctx.send(embed=embed)
                    return
        await ctx.send(embed=discord.Embed(color=discord.Color.red(), timestamp=discord.utils.utcnow(), title="Invalid Flight", description="Make sure you have entered a valid callsign and retry!"))


    @commands.hybrid_command()
    async def vatcontrol(self, ctx, callsign: str):
        """Fetches the specific VATSIM controller associated with that callsign. Case sensitive!"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://data.vatsim.net/v3/vatsim-data.json") as res:
                resp = await res.json()
                for item in resp['controllers']:
                    if item['callsign'].upper() == callsign.upper():
                        embed = discord.Embed(color=discord.Color.blurple(), timestamp=discord.utils.utcnow())
                        embed.set_author(name=f"{item['callsign']} - VATSIM")
                        embed.add_field(name="Callsign:", value=item['callsign'])
                        embed.add_field(name="CID:", value=item['cid'])
                        embed.add_field(name="Name:", value=item['name'])
                        embed.add_field(name="Server:", value=item['server'])
                        embed.add_field(name="Range:", value=str(item['visual_range']) + "nm")
                        embed.add_field(name="Rating:", value=await get_rating(item['rating']))
                        embed.add_field(name="Facility:", value=await get_facility(item['facility']))
                        embed.add_field(name="Frequency:", value=item['frequency'])
                        time = datetime.fromisoformat(item['logon_time'][:19])
                        now = datetime.utcnow()
                        duration = now - time
                        hours, remainder = divmod(int(duration.total_seconds()), 3600)
                        minutes, seconds = divmod(remainder, 60)
                        #days, hours = divmod(hours, 24)
                        embed.add_field(name="Time Online:", value=f"{hours}:{minutes}:{seconds}")
                        embed.add_field(name="Text ATIS:", value=f'```{item["text_atis"]}```', inline=False)
                        await ctx.send(embed=embed)
                        return
        await ctx.send(embed=discord.Embed(color=discord.Color.red(), timestamp=discord.utils.utcnow(), title="Invalid Controller", description="Make sure you have entered a valid callsign and retry!"))







async def setup(bot):
    await bot.add_cog(Vatsim(bot))

