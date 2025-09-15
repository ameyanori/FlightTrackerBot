from FlightRadar24.api import FlightRadar24API
import discord
import aiohttp
import asyncio
import pdf2image
import os
import json
import traceback
from discord.ext import commands, menus
from discord import Intents
fr_api = FlightRadar24API()

class EmbedPageSource(menus.ListPageSource):
    async def format_page(self, menu, items):
        try:
            xzyz = items[0][6]
        except IndexError:
            embed=discord.Embed(color=discord.Color.red(), title = "Error!", description="No charts were available for the specified airport.")
            return embed
        if items[0][6] == False:
            try:
                name = items[1][0]
            except IndexError:
                embed=discord.Embed(color=discord.Color.red(), title = "Error!", description="No charts were available for the specified airport.")
                return embed
            title = items[0][1]
            embed = discord.Embed(color=discord.Color.blue())
            embed.set_footer(text=f'{menu.current_page + 1}/{self.get_max_pages()}')
            embed.set_author(name=f'{name} {title} Charts')
            for item in items:
                embed.add_field(name=item[2], value=f'[{item[4]}]({item[3]})', inline=False)
        else:
            try:
                name = items[0][0]
            except IndexError:
                try:
                    name = items[1][0]
                except IndexError:
                    try:
                        name = items[2][0]
                    except IndexError:
                        embed=discord.Embed(color=discord.Color.red(), title = "Error!", description="No charts were available for the specified airport.")
                        return embed
            embed = discord.Embed(color=discord.Color.blue())
            embed.set_footer(text=f'{menu.current_page + 1}/{self.get_max_pages()}')
            embed.set_author(name=f'{name} Charts')
            for item in items:
                if item[5] == "DP":
                    embed.add_field(name="Departure Charts:", value="\u200B", inline=False)
                    break
            for item in items:
                if item[5] == "DP":
                    embed.add_field(name=item[2], value=f'[{item[4]}]({item[3]})', inline=False)
            for item in items:
                if item[5] == "STAR":
                    embed.add_field(name="Arrival Charts:", value="\u200B", inline=False)
                    break
            for item in items:
                if item[5] == "STAR":
                    embed.add_field(name=item[2], value=f'[{item[4]}]({item[3]})', inline=False)
            for item in items:
                if item[5] == "IAP":
                    embed.add_field(name="Approach Charts:", value="\u200B", inline=False)
                    break
            for item in items:
                if item[5] == "IAP":
                    embed.add_field(name=item[2], value=f'[{item[4]}]({item[3]})', inline=False)

        return embed



class Charts(commands.Cog):
    """Sends information about charts from an airport."""

    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def apd(self, ctx, airport):
        """Sends the Airport Diagram of the specified American Airport."""
        airport = ''.join(filter(str.isalpha, airport))
        async with aiohttp.ClientSession() as cs:
            try:
                async with cs.get(f"https://api.aviationapi.com/v1/charts?apt={airport}&group=2") as r:
                    res = await r.json()
                url = res[f'{airport}'][0]['pdf_path']
                name = res[f'{airport}'][0]['airport_name'] + "AIRPORT DIAGRAM"
            except IndexError:
                await ctx.send(embed=discord.Embed(color=discord.Color.red(), title = "ERROR!", description="Airport Invalid or Unavailable! Ensure you are using the ICAO code of the airport."))
                return
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    content = await response.content.read()
                img = pdf2image.convert_from_bytes(content)
                for im in img:
                    im.save(f'/home/admin/APDs/{airport}.jpg', 'JPEG')
                file = discord.File(fp=f"/home/admin/APDs/{airport}.jpg", filename=f"{airport}.jpg")
                embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow(), title=name)
                embed.set_image(url=f"attachment://{airport}.jpg")
                await ctx.send(embed=embed, file=file)
                os.remove(f"/home/admin/APDs/{airport}.jpg")




    @commands.command()
    async def vfr(self, ctx, icao):
        """Sends the corresponding VFR Sectional chart of the specified American Airport"""
        try:
            resp = await fr_api.get_airport(icao)
            lon = resp['position']['longitude']
            lat = resp['position']['latitude']
        except KeyError:
            await ctx.send('Invalid Airport')
            return
        embed = discord.Embed(color=discord.Color.blue(), title=f"{resp['name']} VFR Sectional Chart")
        embed.set_image(url=f"http://vfrmap.com/api?req=map&type=sectc&lat={lat}&lon={lon}&zoom=10&width=500&height=500&api_key=1234")
        await ctx.send(embed=embed)


    @commands.command()
    async def charts(self, ctx, airport, type = None):
        """Sends the specified airport's charts or the specified type of chart from airport."""
        try:
            airport = ''.join(filter(str.isalpha, airport))
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://api.aviationapi.com/v1/charts?apt={airport}&group=7") as r:
                    res = await r.json()
            if type == "SID":
                query = "DP"
                title = "SID"
            elif type == "STAR":
                query = "STAR"
                title = "STAR"
            elif type == "approach" or type == "CAPP" or type == "IAP":
                query = "CAPP"
                title = "Approach"
            elif type == None:
                query = None
                title = ""
            else:
                query = None
                title = ""
            if query != None:
                res = res[airport][query]
                items = []
                for entry in res:
                    item = [entry['airport_name'], title, entry['chart_name'], entry['pdf_path'], entry['pdf_name'], entry['chart_code'], False]
                    items.append(item)
 
            else:
                res = res[airport]
                items = []
                for entry in res['DP']:
                    item = [entry['airport_name'], title, entry['chart_name'], entry['pdf_path'], entry['pdf_name'], entry['chart_code'], True]
                    items.append(item)
                for entry in res['STAR']:
                    item = [entry['airport_name'], title, entry['chart_name'], entry['pdf_path'], entry['pdf_name'], entry['chart_code'], True]
                    items.append(item)
                for entry in res['CAPP']:
                    item = [entry['airport_name'], title, entry['chart_name'], entry['pdf_path'], entry['pdf_name'], entry['chart_code'], True]
                    items.append(item)
            menu = menus.MenuPages(EmbedPageSource(items, per_page=7))
            await menu.start(ctx)
        except KeyError:
            await ctx.send('invalid icao code')


    @commands.command()
    async def navaid(self, ctx, identifier):
        """If available sends the corresponding navigational aid(VOR, VOR-DME, VORTAC, etc) along with it's frequency and location"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.core.openaip.net/api/navaids?page=1&limit=100&sortDesc=true&approved=true&searchOptLwc=true&search={identifier}", headers={'accept' : 'application/json', 'x-openaip-client-id' : ''}) as r:
                res = await r.read()
                try:
                    pes = json.loads(res.decode('UTF-8'))['items']
                    for item in pes:
                        if item['identifier'] == identifier:
                            res = item
                            break
                    else:
                        res = pes[0]
                except:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description="Unknown/Invalid Navaid!"))
                    return
        type = res['type']
        if type == 0:
            tt = "DME"
        elif type == 1:
            tt = "TACAN"
        elif type == 2:
            tt = "NDB"
        elif type == 3:
            tt = "VOR"
        elif type == 4:
            tt = "VOR-DME"
        elif type == 5:
            tt = "VORTAC"
        elif type == 6:
            tt = "DVOR"
        elif type == 7:
            tt = "DVOR-DME"
        elif type == 8:
            tt = "DVORTAC"
        embed = discord.Embed(color=discord.Color.gold(), timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{res['name']} {tt}")
        embed.add_field(name="Identifier:", value=res['identifier'])
        embed.add_field(name="Type:", value=tt)
        embed.add_field(name="Name:", value=res['name'])
        embed.add_field(name="Frequency:", value=res['frequency']['value'])
        try:
            embed.add_field(name="Channel:", value=res['channel'])
        except:
            embed.add_field(name="Channel:", value="N/A")
        embed.add_field(name="Elevation:", value=f"{res['elevation']['value']} meters")
        embed.add_field(name="Latitude:", value=res['geometry']['coordinates'][1])
        embed.add_field(name="Longitude:", value=res['geometry']['coordinates'][0])
        embed.add_field(name="Country:", value=res['country'])
        if res['country'] == "US":
            embed.set_image(url=f"http://vfrmap.com/api?req=map&type=ifrlc&lat={res['geometry']['coordinates'][1]}&lon={res['geometry']['coordinates'][0]}&zoom=10&width=500&height=500&api_key=1234")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Charts(bot))
