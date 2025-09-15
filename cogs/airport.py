from FlightRadar24.api import FlightRadar24API
import discord
import aiohttp
from datetime import datetime
import asyncio
import pdf2image
from discord.ui import Select
import os
import json
import traceback
import typing
from bs4 import BeautifulSoup
import aiocsv
import aiofiles
from aiocsv import AsyncReader
from discord.ext import commands, menus
from discord import app_commands
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

class Airport(commands.Cog):
    """Commands associated with airports/navigational aids."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="fix")
    async def fix(self, ctx, name):
        async with aiofiles.open('/home/admin/FlightTracker/FIX_BASE.csv', 'r') as f:
            async for row in AsyncReader(f):
                if row[1] == name.upper():
                    n = row[1]
                    state = row[3]
                    lat = row[9]
                    lon = row[14]
                    await ctx.send(f"{row[1]} - {row[3]} - {row[9]} - {row[14]}")
                    await ctx.send(f"http://vfrmap.com/api?req=map&type=ifrlc&lat={row[9]}&lon={row[14]}&zoom=10&width=500&height=500&api_key=1234")

    @commands.hybrid_command(name="atis")
    async def atis(self, ctx, icao: str):
        """Fetches the specified airport's ATIS from the FAA's DATIS if available."""
        try:
            resp = await fr_api.get_airport(icao)
            ICAO = resp['code']['icao']
        except Exception as e:
            await ctx.send(f"Invalid Airport!")
            return
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://api.flybywiresim.com/atis/{ICAO}") as res:
                    res = await res.json()
                    embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow())
                    embed.set_author(name=f"{resp['name']} ATIS")
                    try:
                        embed.add_field(name="Raw:", value=f"```{res['combined']}```")
                    except KeyError:
                        embed.add_field(name="Arrival:", value=f"```{res['arr']}```")
                        embed.add_field(name="Departure:", value=f"```{res['dep']}```")
                    embed.set_footer(text="Retrieved from FAA's Digital ATIS(DATIS).")
                    await ctx.send(embed=embed)
        except:
            await ctx.send(f"There is currently no DATIS available for {ICAO}!")
            
    @commands.hybrid_command(name="airport")
    async def airport(self, ctx, ident:str):
        """Sends information about the specified airport."""
        try:
            resp = await fr_api.get_airport(ident)
        except Exception as e:
            await ctx.send("Airport Unavailable!")
            return
        embed = discord.Embed(color=discord.Color.blurple(), timestamp=discord.utils.utcnow())
        embed.set_author(name=resp['name'])
        embed.add_field(name="ICAO:", value=resp['code']['icao'])
        embed.add_field(name="IATA:", value=resp['code']['iata'])
        embed.add_field(name="Position:", value=f"{resp['position']['latitude']}, {resp['position']['longitude']}")
        embed.add_field(name="Country:", value=resp['position']['country']['name'])
        embed.add_field(name="City:", value=resp['position']['region']['city'])
        embed.add_field(name="Timezone:", value=f"{resp['timezone']['abbrName']} ({resp['timezone']['abbr']})")
        await ctx.send(embed=embed)


    @commands.hybrid_command()
    async def route(self, ctx, origin: str, dest: str):
        """Generates a route (including SIDs and STARs) from the origin to the destination."""
        origin = origin.lower()
        dest = dest.lower()
        routes_data = {}
        try:
            with open('/home/admin/FlightTracker/routes.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            pass
        if origin in data["airports"]:
            if dest in data["airports"][origin]:
                # Route already exists
                route = data["airports"][origin][dest]
            else:
                # Route doesn't exist, retrieve it from the website
                url = "https://flightaware.com/analysis/route.rvt?origin={}&destination={}".format(origin, dest)
        

                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                anchor = soup.find("a", href=True, target="_blank", rel="noopener noreferrer")
                route = anchor.text.strip()
        

                data["airports"][origin][dest] = route
        
        else:
            # Origin doesn't exist, create a new entry
            url = "https://flightaware.com/analysis/route.rvt?origin={}&destination={}".format(origin, dest)
        

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()

            soup = BeautifulSoup(html, "html.parser")
            anchor = soup.find("a", href=True, target="_blank", rel="noopener noreferrer")
            route = anchor.text.strip()
    
            data["airports"][origin] = {}
            data["airports"][origin][dest] = route
        
        # Write the updated JSON file
        with open("/home/admin/FlightTracker/routes.json", "w") as file:
            json.dump(data, file, indent=4)
        await ctx.send(embed=discord.Embed(color=discord.Color.green(), title=f"{origin.upper()} - {dest.upper()}", description=route))


    @commands.hybrid_command()
    async def apd(self, ctx, airport: str):
        """Sends the Airport Diagram of the specified American Airport."""
        airport = ''.join(filter(str.isalpha, airport)).upper()
        async with aiohttp.ClientSession() as cs:
            try:
                async with cs.get(f"https://api.aviationapi.com/v1/charts?apt={airport.upper()}&group=2") as r:
                    res = await r.json()
                url = res[f'{airport}'][0]['pdf_path']
                name = res[f'{airport}'][0]['airport_name'] + " AIRPORT DIAGRAM"
            except KeyError:
                await ctx.send(embed=discord.Embed(color=discord.Color.red(), title = "ERROR!", description="That airport doesn't exist! Ensure you are using the ICAO code of the airport."))
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




    @commands.hybrid_command()
    async def vfr(self, ctx, icao:str ):
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


#    @commands.hybrid_command()
#    async def charts(self, ctx, airport: str , type: typing.Optional[str]):
#        """Sends the specified airport's charts or the specified type of chart from airport."""\
#        select = Select()
#        try:
#            airport = ''.join(filter(str.isalpha, airport))
#            async with aiohttp.ClientSession() as cs:
#                async with cs.get(f"https://api.aviationapi.com/v1/charts?apt={airport}&group=7") as r:
#                    res = await r.json()
#            if type == "SID":
#                query = "DP"
#                title = "SID"
#            elif type == "STAR":
#                query = "STAR"
#                title = "STAR"
#            elif type == "approach" or type == "CAPP" or type == "IAP":
#                query = "CAPP"
#                title = "Approach"
#            elif type == None:
#                query = None
#                title = ""
#            else:
#                query = None
#                title = ""
#            if query != None:
#                res = res[airport][query]
#                items = []
#                for entry in res:
#                    item = [entry['airport_name'], title, entry['chart_name'], entry['pdf_path'], entry['pdf_name'], entry['chart_code'], False]
#                    items.append(item)
# 
#            else:
#                res = res[airport]
#                items = []
#                for entry in res['DP']:
#                    item = [entry['airport_name'], title, entry['chart_name'], entry['pdf_path'], entry['pdf_name'], entry['chart_code'], True]
#                    items.append(item)
#                for entry in res['STAR']:
#                    item = [entry['airport_name'], title, entry['chart_name'], entry['pdf_path'], entry['pdf_name'], entry['chart_code'], True]
#                    items.append(item)
#                for entry in res['CAPP']:
#                    item = [entry['airport_name'], title, entry['chart_name'], entry['pdf_path'], entry['pdf_name'], entry['chart_code'], True]
#                    items.append(item)
#            menu = menus.MenuPages(EmbedPageSource(items, per_page=7))
#            await menu.start(ctx)
#        except KeyError:
#            await ctx.send('invalid icao code')


    @commands.hybrid_command()
    async def navaid(self, ctx, identifier: str):
        """Sends the corresponding navigational aid along with it's frequency and location"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.core.openaip.net/api/navaids?page=1&limit=100&sortDesc=true&approved=true&searchOptLwc=true&search={identifier}", headers={'accept' : 'application/json', 'x-openaip-client-id' : 'ef15eb9d92a985824d66ff4dd1bdd727'}) as r:
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

    @commands.hybrid_command()
    async def metar(self, ctx, icao: str):
        """Gets the METAR information from the specified airport."""
        token = ""
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://avwx.rest/api/metar/" + ''.join(filter(str.isalpha, icao)), headers={"Authorization": "BEARER " + token}) as resp:
                res = await resp.json()
        if 'error' in res:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), title='Error!', description=f'{icao} is not a valid ICAO/IATA code! Please try again with a valid ICAO/IATA code!'))
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
        try:
            winds = str(res['wind_direction']['value']) + " at " + str(res['wind_speed']['value']) + " knots, gusts "  + str(gust)
        except:
            winds = "Missing"
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
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Airport(bot))
