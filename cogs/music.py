


import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL
from FlightRadar24.api import FlightRadar24API
from httpx import AsyncClient
from httpx_html import AsyncHTMLSession
import FlightRadar24
import discord
from discord import app_commands
import traceback
from discord.ext import commands, menus, tasks
from discord import Intents
from bs4 import BeautifulSoup

from reactionmenu import ViewMenu, ViewButton
from discord.ext.commands.cooldowns import BucketType
import pandas as pd
import asyncio
import wikipedia as wp
import json
import aiohttp
from datetime import date, datetime
import regex as re
import folium
from folium.features import DivIcon
import time
from selenium import webdriver
import os
from selenium.webdriver.chrome.options import Options


class Dropdown(discord.ui.Select):
    def __init__(self, ctx, list, r):
        super().__init__(
            placeholder='Select a position.',
            min_values=1,
            max_values=1,
            row=0,
        )
        options=[]
        
        self.r = r
        self.ctx = ctx
        self.list = list
        for li in list:
            self.add_option(label=li['name'])
            
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        ctx = self.ctx
        value = self.values[0]
        for li in self.list:
            if value == li['name']:
                ctx.voice_client.stop()
                url = f"https://s1-bos.liveatc.net/{li['id']}"
                player = await YTDLSource.from_url(url, loop=self.r.bot.loop, stream=True)
                ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
                await interaction.response.edit_message(embed=discord.Embed(color=discord.Color.blue(), title="Choose the position you would like to listen to:", description=f"Now Playing: {li['name']}"), view=self.view)

class DropdownView(discord.ui.View):
    def __init__(self, ctx, list, r):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(ctx, list, r))
        
        



import youtube_dl


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot



    @commands.hybrid_command()
    async def liveatc(self, ctx, airport: str):
        """Plays the tower frequency for the specified airport."""
        airport = airport.lower()

        airports_data = {}
        try:
            with open('/home/admin/FlightTracker/atcs.json', 'r') as file:
                airports_data = json.load(file)
        except FileNotFoundError:
            pass
    
        
    
        if airport in airports_data.get('airports', {}):
            # Fetch name and ID from the atcs.json file
            list = airports_data['airports'][airport]

        else:
            url = f'https://www.liveatc.net/search/?icao={airport}'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
            try:
                soup = BeautifulSoup(html, 'html.parser')
                onclick_elements = soup.find_all(attrs={"onclick": True})
        
                onclick_data = []
                for element in onclick_elements:
                    name_element = element.find_previous('td', {'bgcolor': 'lightblue'})
                    name = name_element.text.strip() if name_element else None
                    onclick = element['onclick']
                    if "myHTML5Popup" in onclick:
                        onclick_data.append({
                            'onclick': onclick,
                            'name': name
                        })
                list = []
                for data in onclick_data:
                    onclick = data['onclick']
                    start_index = onclick.index("'") + 1
                    end_index = onclick.index("'", start_index)
                    value = onclick[start_index:end_index]
                    name = data['name']
                    bo = {
                        'name': name,
                        'id': value
                    }
                    list.append(bo)
                airports_data["airports"][airport] = list
            except:
                await ctx.send("Airport unavailable.")
        if list == []:
            await ctx.send("Airport unavailable.")
            return
        async with ctx.typing():
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
                if ctx.voice_client.channel is not ctx.author.voice.channel:    
                    await ctx.send("Joined the voice channel.")
            else:
                if ctx.author.voice is None:
                    await ctx.send("You are not in a channel. Join one, and then run the command again.")
                    return
                await ctx.author.voice.channel.connect()
                await ctx.send("Joined the voice channel.")
        

        
        with open('/home/admin/FlightTracker/atcs.json', 'w') as file:
            json.dump(airports_data, file, indent=4)
        
        view = DropdownView(ctx, list[:24], self)
        await ctx.send(embed=discord.Embed(title="Choose the position you would like to listen to:"), view=view)

    @commands.hybrid_command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected and stopped.")


async def setup(bot):
    await bot.add_cog(Music(bot))

