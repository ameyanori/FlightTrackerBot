from FlightRadar24.api import FlightRadar24API
from httpx import AsyncClient
from httpx_html import AsyncHTMLSession
import FlightRadar24
import discord
from discord import app_commands
import traceback
from discord.ext import commands, menus, tasks
from discord import Intents
from staticmap import StaticMap, CircleMarker, IconMarker, Line
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

from io import BytesIO
from PIL import Image
from math import radians, cos, sin, asin, sqrt
regs = [{"prefix": "A2-", "country": "Botswana"}, {"prefix": "A3-", "country": "Tonga"}, {"prefix": "A4O-", "country": "Oman"}, {"prefix": "A5-", "country": "Bhutan"}, {"prefix": "A6-", "country": "United Arab Emirates"}, {"prefix": "A7-", "country": "Qatar"}, {"prefix": "A9C-", "country": "Bahrain"}, {"prefix": "AP-", "country": "Pakistan"}, {"prefix": "B-", "country": "China (People's Republic of China)"}, {"prefix": "B-", "country": "Taiwan (Republic of China)"}, {"prefix": "B-M", "country": "China, Macau"}, {"prefix": "C-", "country": "Canada"}, {"prefix": "C2-", "country": "Naura"}, {"prefix": "C3-", "country": "Andorra"}, {"prefix": "C5-", "country": "The Gambia"}, {"prefix": "C6-", "country": "Bahamas"}, {"prefix": "C9-", "country": "Mozambique"}, {"prefix": "CC-", "country": "Chile"}, {"prefix": "CN-", "country": "Morocco"}, {"prefix": "CP-", "country": "Bolivia"}, {"prefix": "CS-", "country": "Portugal"}, {"prefix": "CU-", "country": "Cuba"}, {"prefix": "CX", "country": "Christmas Islands"}, {"prefix": "CX-", "country": "Uruguay"}, {"prefix": "D-", "country": "Germany"}, {"prefix": "D2-", "country": "Angola"}, {"prefix": "D4-", "country": "Cape Verde Islands"}, {"prefix": "D6-", "country": "Comores"}, {"prefix": "DQ-", "country": "Fiji"}, {"prefix": "E3-", "country": "Eritrea"}, {"prefix": "E5-", "country": "Cook Islands"}, {"prefix": "E7-", "country": "Bosnia Hercegovina"}, {"prefix": "EC-", "country": "Spain"}, {"prefix": "EI-", "country": "Ireland"}, {"prefix": "EK-", "country": "Armenia"}, {"prefix": "EL-", "country": "Liberia"}, {"prefix": "EP-", "country": "Iran"}, {"prefix": "ER-", "country": "Moldova, Rep. of"}, {"prefix": "ES-", "country": "Estonia"}, {"prefix": "ET-", "country": "Ethiopia"}, {"prefix": "EW-", "country": "Belarus"}, {"prefix": "EX-", "country": "Kyrgyzstan"}, {"prefix": "EY-", "country": "Tajikistan"}, {"prefix": "EZ-", "country": "Turkmenistan"}, {"prefix": "F-", "country": "France"}, {"prefix": "F-O", "country": "Reunion Island"}, {"prefix": "F-OD", "country": "New Caledonia"}, {"prefix": "F-OG", "country": "Guadeloupe"}, {"prefix": "F-OG", "country": "Martinique"}, {"prefix": "F-OH", "country": "Tahiti"}, {"prefix": "G-", "country": "United Kingdom"}, {"prefix": "GL-", "country": "Greenland"}, {"prefix": "H4-", "country": "Solomon Islands"}, {"prefix": "HA-", "country": "Hungary"}, {"prefix": "HB-", "country": "Switzerland"}, {"prefix": "HC-", "country": "Ecuador"}, {"prefix": "HH-", "country": "Haiti"}, {"prefix": "HI-", "country": "Dominican Republic"}, {"prefix": "HK-", "country": "Colombia"}, {"prefix": "HL", "country": "Korea, Rep. of"}, {"prefix": "HP-", "country": "Panama"}, {"prefix": "HR-", "country": "Honduras"}, {"prefix": "HS-", "country": "Thailand"}, {"prefix": "HV-", "country": "Vatican City"}, {"prefix": "HZ-", "country": "Saudi Arabia"}, {"prefix": "I-", "country": "Italy"}, {"prefix": "J2-", "country": "Djibouti"}, {"prefix": "J3-", "country": "Grenada"}, {"prefix": "J5-", "country": "Guinea Bissau"}, {"prefix": "J6-", "country": "St. Lucia"}, {"prefix": "J7-", "country": "Dominica"}, {"prefix": "J8-", "country": "St. Vincent and Grenadines"}, {"prefix": "JA", "country": "Japan"}, {"prefix": "JY-", "country": "Jordan"}, {"prefix": "LN-", "country": "Norway"}, {"prefix": "LQ-", "country": "Argentina (Government)"}, {"prefix": "LV-", "country": "Argentina"}, {"prefix": "LX-", "country": "Luxembourg"}, {"prefix": "LY-", "country": "Lithuania"}, {"prefix": "LZ-", "country": "Bulgaria"}, {"prefix": "M-", "country": "Isle of Man"}, {"prefix": "MT-", "country": "Mongolia"}, {"prefix": "N", "country": "United States of America"}, {"prefix": "OB-", "country": "Peru"}, {"prefix": "OD-", "country": "Lebanon"}, {"prefix": "OE-", "country": "Austria"}, {"prefix": "OH-", "country": "Finland"}, {"prefix": "OK-", "country": "Czech Republic"}, {"prefix": "OM-", "country": "Slovakia"}, {"prefix": "OO-", "country": "Belgium"}, {"prefix": "OY-", "country": "Denmark"}, {"prefix": "P-", "country": "Korea, Dem. People's Rep. of"}, {"prefix": "P2-", "country": "Papua New Guinea"}, {"prefix": "P4-", "country": "Aruba"}, {"prefix": "PH-", "country": "Netherlands"}, {"prefix": "PJ-", "country": "Nehterlands Antilles"}, {"prefix": "PK-", "country": "Indonesia"}, {"prefix": "PP-", "country": "Brazil"}, {"prefix": "PR-", "country": "Brazil"}, {"prefix": "PT-", "country": "Brazil"}, {"prefix": "PZ-", "country": "Suriname"}, {"prefix": "RA-", "country": "Russian Federation"}, {"prefix": "RDPL-", "country": "Lao"}, {"prefix": "RF-", "country": "Russian Federation (State owned aircraft)"}, {"prefix": "RP-", "country": "Philippines"}, {"prefix": "S2-", "country": "Bangladesh"}, {"prefix": "S3-", "country": "Bangladesh"}, {"prefix": "S5-", "country": "Slovenia"}, {"prefix": "S7-", "country": "Seychelles"}, {"prefix": "S9-", "country": "Sao Tome and Principe"}, {"prefix": "SE-", "country": "Sweden"}, {"prefix": "SP-", "country": "Poland"}, {"prefix": "ST-", "country": "Sudan"}, {"prefix": "SU-", "country": "Egypt"}, {"prefix": "SX-", "country": "Greece"}, {"prefix": "T3-", "country": "Kiribati"}, {"prefix": "T7-", "country": "San Marino"}, {"prefix": "TC-", "country": "Turkey"}, {"prefix": "TF-", "country": "Iceland"}, {"prefix": "TG-", "country": "Guatemala"}, {"prefix": "TI-", "country": "Costa Rica"}, {"prefix": "TJ-", "country": "Cameroon"}, {"prefix": "TL-", "country": "Central African Republic"}, {"prefix": "TN-", "country": "Congo"}, {"prefix": "TR-", "country": "Gabon"}, {"prefix": "TS-", "country": "Tunisia"}, {"prefix": "TT-", "country": "Chad"}, {"prefix": "TU-", "country": "Cote D'Ivoire"}, {"prefix": "TY-", "country": "Benin"}, {"prefix": "TZ-", "country": "Mali"}, {"prefix": "UK-", "country": "Uzbekistan"}, {"prefix": "UN-", "country": "Kazakhstan"}, {"prefix": "UP-", "country": "Kazakhstan"}, {"prefix": "UR-", "country": "Ukraine"}, {"prefix": "V2-", "country": "Antigua"}, {"prefix": "V3-", "country": "Belize"}, {"prefix": "V4-", "country": "St. Kitts and Nevis"}, {"prefix": "V5-", "country": "Namibia"}, {"prefix": "V7-", "country": "Marshall Islands"}, {"prefix": "V8-", "country": "Brunei"}, {"prefix": "VH-", "country": "Australia"}, {"prefix": "VN-", "country": "Vietnam"}, {"prefix": "VP-B", "country": "Bermuda"}, {"prefix": "VP-C", "country": "Caymen Islands"}, {"prefix": "VP-F", "country": "Falkland Islands"}, {"prefix": "VP-LMA-LUZ", "country": "Montserrat"}, {"prefix": "VP-LV", "country": "British Virgin Islands"}, {"prefix": "VQ-H", "country": "St. Helena"}, {"prefix": "VQ-T", "country": "Turks and Caicos Islands"}, {"prefix": "VT-", "country": "India"}, {"prefix": "XA-", "country": "Mexico"}, {"prefix": "XB-", "country": "Mexico"}, {"prefix": "XC-", "country": "Mexico"}, {"prefix": "XT-", "country": "Burkina Faso"}, {"prefix": "XU-", "country": "Cambodia"}, {"prefix": "XY-", "country": "Myanmar"}, {"prefix": "XZ-", "country": "Myanmar"}, {"prefix": "YA-", "country": "Afghanistan"}, {"prefix": "YI-", "country": "Iraq"}, {"prefix": "YJ-", "country": "Vanuatu"}, {"prefix": "YK-", "country": "Syria"}, {"prefix": "YL-", "country": "Latvia"}, {"prefix": "YN-", "country": "Nicaragua"}, {"prefix": "YR-", "country": "Romania"}, {"prefix": "YS-", "country": "El Salvador"}, {"prefix": "YU-", "country": "Serbria"}, {"prefix": "YV-", "country": "Venezuela"}, {"prefix": "Z-", "country": "Zimbabwe"}, {"prefix": "Z3-", "country": "Macedonia"}, {"prefix": "ZA-", "country": "Albania"}, {"prefix": "ZJ-", "country": "Jersey"}, {"prefix": "ZK-", "country": "New Zealand"}, {"prefix": "ZL-", "country": "New Zealand"}, {"prefix": "ZP-", "country": "Paraguay"}, {"prefix": "ZS-", "country": "South Africa"}, {"prefix": "ZT-", "country": "South Africa"}, {"prefix": "ZU-", "country": "South Africa"}, {"prefix": "2-", "country": "Guernsey"}, {"prefix": "3A-", "country": "Monaco"}, {"prefix": "3B-", "country": "Mauritius"}, {"prefix": "3C-", "country": "Equatorial Guinea"}, {"prefix": "3D-", "country": "Swaziland"}, {"prefix": "3X-", "country": "Guinea"}, {"prefix": "4K-", "country": "Azerbaijan"}, {"prefix": "4L-", "country": "Georgia"}, {"prefix": "4O-", "country": "Montenegro"}, {"prefix": "4R-", "country": "Sri Lanka"}, {"prefix": "4X-", "country": "Israel"}, {"prefix": "5A-", "country": "Libya"}, {"prefix": "5B-", "country": "Cyprus"}, {"prefix": "5H-", "country": "Tanzania"}, {"prefix": "5N-", "country": "Nigeria"}, {"prefix": "5R-", "country": "Madagascar"}, {"prefix": "5T-", "country": "Mauritania"}, {"prefix": "5U-", "country": "Niger"}, {"prefix": "5V-", "country": "Togo"}, {"prefix": "5W-", "country": "Samoa"}, {"prefix": "5X-", "country": "Uganda"}, {"prefix": "5Y-", "country": "Kenya"}, {"prefix": "6O-", "country": "Somalia"}, {"prefix": "6V-", "country": "Senegal"}, {"prefix": "6W-", "country": "Senegal"}, {"prefix": "6Y-", "country": "Jamaica"}, {"prefix": "7O-", "country": "Yemen"}, {"prefix": "7P-", "country": "Lesotho"}, {"prefix": "7Q-", "country": "Malawi"}, {"prefix": "7T-", "country": "Algeria"}, {"prefix": "8P-", "country": "Barbados"}, {"prefix": "8Q-", "country": "Maldives"}, {"prefix": "8R-", "country": "Guyana"}, {"prefix": "9A-", "country": "Croatia"}, {"prefix": "9G-", "country": "Ghana"}, {"prefix": "9H-", "country": "Malta"}, {"prefix": "9J-", "country": "Zambia"}, {"prefix": "9K-", "country": "Kuwait"}, {"prefix": "9L-", "country": "Sierra Leone"}, {"prefix": "9M-", "country": "Malaysia"}, {"prefix": "9N-", "country": "Nepal"}, {"prefix": "9Q-", "country": "Zaire"}, {"prefix": "9U-", "country": "Burundi"}, {"prefix": "9V-", "country": "Singapore"}, {"prefix": "9XR-", "country": "Rwanda"}, {"prefix": "9Y-", "country": "Trinidad and Tobago"}]
def distance(lat1, lat2, lon1, lon2):
     
 
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    r = 3956
      
    return(c * r)

fr_api = FlightRadar24API() 
asession = AsyncHTMLSession()

async def get_icao(iata):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(f"https://iata-and-icao-codes.p.rapidapi.com/airline?iata_code={iata}", headers={'x-rapidapi-host': 'iata-and-icao-codes.p.rapidapi.com', 'x-rapidapi-key': ''}) as resp:
            results = await resp.json()
            try:
                return results[0]['icao_code']
            except TypeError:
                return None
async def get_airport_name(iata):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(f"https://www.airport-data.com/api/ap_info.json?iata={iata}") as res:
            resp = await res.json()
            try:
                return resp['name']
            except:
                try:
                    res = await fr_api.get_airport(iata)
                    return res['name']
                except:
                    return None
async def get_airport_name_icao(icao):
    async with   aiohttp.ClientSession() as cs:
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

async def make_model(ICAO):
    f = open ('/home/admin/FlightTracker/data.json', "r")
    j = json.loads(f.read())
    f.close()
    for item in j['ICAOCode[3]']:
        value = j['ICAOCode[3]'].get(item)
        if value == ICAO:
            return j['Model'][item]
   

async def getflights(ICAO, message):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }
    async with aiohttp.ClientSession() as cs:
        async with cs.get(f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?faa=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&gliders=1&stats=1&maxage=14400&airline={ICAO}", headers=headers) as r:
            res = await r.read()
            res = json.loads(res.decode('UTF-8'))
    res.pop("full_count")
    res.pop("version")
    res.pop("stats")
    dict = {}
    num = 1
    for plane in res:
        plane = FlightRadar24.flight.Flight(plane, res.get(plane))
        #plane = await fr_api.get_flight_details(plane)
        await message.edit(content=f"Working on {plane.callsign} ({num}/{len(res)}) <a:loading:829781249945370654>")
        if plane.on_ground == 0:
            yesno = "No."
        else:
            yesno = "Yes."
        oldie = {f"{plane.number}" : [f"{await get_airport_name(plane.origin_airport_iata)}",  f"{await get_airport_name(plane.destination_airport_iata)}", f"{await make_model(plane.aircraft_code)}", f"{plane.callsign}", f"{yesno}"]}
        dict.update(oldie)
        num = num + 1
    return dict

async def get_airline_name(icao):
    airlines = await fr_api.get_airlines()
    for airline in airlines:
        if airline['ICAO'] == icao:
            return airline['Name']
            
            
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


async def getlogo(ICAO):
    airlines = await fr_api.get_airlines()
    for airline in airlines:
        if airline['ICAO'] == ICAO:
            return await fr_api.get_airline_logo(icao=airline['ICAO'], iata=airline['Code'])
            



class EmbedPageSource(menus.ListPageSource):
    async def format_page(self, menu, items):
        icccao = items[0][5]
        logo = await getlogo(icccao)
        name = await get_airline_name(items[0][5])
        embed = discord.Embed(color=discord.Color.blue())
        if logo != None:
            embed.set_thumbnail(url=logo)
        embed.set_footer(text=f'{menu.current_page + 1}/{self.get_max_pages()}')
        embed.set_author(name=name)
        for item in items:
            embed.add_field(name=f"Flight Number: {item[0]}", value=f"Origin Airport: {item[1]}\nDestination Airport: {item[2]}\nAircraft Type: {item[3]}\nAircraft Callsign: {item[4]}\nOn Ground: {item[6]}", inline=False)
        return embed


class Button(discord.ui.View):
    def __init__(self, bot, identifier, embed, flight):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot
        self.identifier = identifier
        self.embed = embed
        self.flight = flight
        try:
            url = flight.aircraft_images['large'][0]['src']
            self.bb = True
            self.bm = False
        except:
            self.bb = True
            self.bm = True

    @discord.ui.button(label='Map', style=discord.ButtonStyle.green, emoji="\U0001f5fa", custom_id='persistent_view:blue', disabled=False)
    async def map(self, interaction: discord.Interaction, button: discord.ui.Button):
        plane_icon_path = "home/admin/plane_icon.png"
        flight = self.flight
        m = StaticMap(720, 540)
        origin_marker = CircleMarker((flight.origin_airport_longitude, flight.origin_airport_latitude), 'green', 12)
        destination_marker = CircleMarker((flight.destination_airport_longitude, flight.destination_airport_latitude), 'red', 12)
        m.add_marker(origin_marker)
        m.add_marker(destination_marker)
        with Image.open(plane_icon_path) as img:
            img = img.rotate(flight.heading-180, expand=True)
            airplane_marker = IconMarker((flight.longitude, flight.latitude), img, 0, 0)
        m.add_marker(airplane_marker)
        line = Line([[flight.origin_airport_longitude, flight.origin_airport_latitude], [flight.longitude, flight.latitude]], "green", 1)
        m.add_line(line)
        line = Line([[flight.longitude, flight.latitude], [flight.destination_airport_longitude, flight.destination_airport_latitude]], "green", 1)
        m.add_line(line)
        image = m.render()
        buffer = BytesIO()
        image.save(buffer, "png") 
        buffer.seek(0)
        button.disabled = self.bm
        self.embed.set_image(url="attachment://map.png")

        #self.embed.set_image(url=f"http://www.gcmap.com/map?P=c:green,{flight.origin_airport_iata}-{flight.latitude},+{flight.longitude}-{flight.destination_airport_iata},m:p:%22{flight.callsign}%22NW%2bdiamond13:blue,{flight.latitude},+{flight.longitude}&MS=bm&MR=60&MX=720x540&PM=b:pentagon13%2b%25i")
        v = Button1(self.bot, self.identifier, self.embed, self.flight)
        await interaction.response.edit_message(view=v, embed=self.embed, attachments=[discord.File(fp=buffer,filename='map.png')])





    @discord.ui.button(label='Bookmark', style=discord.ButtonStyle.green, emoji="\U0001f516", custom_id='persistent_view:green')
    async def bmark(self, interaction: discord.Interaction, button: discord.ui.Button):
        identifier = self.identifier
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                exists = await connection.fetchval('SELECT exists(SELECT callsign from bookmarks WHERE id = $1 and nique = $2)', interaction.user.id, identifier)
                if exists == True:
                    await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), title="Error!", description = "You've already bookmarked this flight!"))
                    return
                try:
                    if identifier[2].isalpha() == True:
                        query = identifier[0:3]
                    else:
                        airlines = await fr_api.get_airlines()
                        for airline in airlines:
                            if airline['Code'] == identifier[0:2]:
                                query = airline['ICAO']
                        if "query" not in locals():
                            embed = discord.Embed(color=discord.Color.red())
                            embed.set_author(name='Invalid Flight')
                            embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
                            await interaction.response.send_message(embed=embed, content=interaction.user.mention)
                            return
                except IndexError:
                    embed = discord.Embed(color=discord.Color.red())
                    embed.set_author(name='Invalid Flight')
                    embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
                    await interaction.response.send_message(embed=embed, content=interaction.user.mention)
                    return
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
                    }
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?airline={query}", headers=headers) as r:
                        res = await r.read()
                        res = json.loads(res.decode('UTF-8'))
                res.pop("full_count")
                res.pop("version")
                num = 1
                for item in res:
                    flight = FlightRadar24.flight.Flight(item, res.get(item))
                    if identifier in [flight.callsign, flight.number]:
                        await connection.execute('INSERT INTO bookmarks (id, callsign, landed, channel, nique) VALUES ($1, $2, $3, $4, $5)', interaction.user.id, flight.id, False, interaction.channel.id, identifier)
                        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), title="Success!", description = "You have bookmarked this flight!"))

class DelButton(discord.ui.View):
    def __init__(self, bot, identifier):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot
        self.identifier = identifier




    @discord.ui.button(label='Delete', style=discord.ButtonStyle.red, custom_id='persistent_view:red', disabled=False)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
         async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                await connection.execute("DELETE from bookmarks where id = $1 and nique = $2", interaction.user.id, self.identifier)
                await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), title="Success!", description=f"I have deleted the bookmark ``{self.identifier}``."))
            

class Button1(discord.ui.View):
    def __init__(self, bot, identifier, embed, flight):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot
        self.identifier = identifier
        self.embed = embed
        self.flight = flight



    @discord.ui.button(label='Photo', style=discord.ButtonStyle.green, emoji="\U0001f4f7", custom_id='persistent_view:blue', disabled=False)
    async def photo(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.set_image(url=self.flight.aircraft_images['large'][0]['src'])
        v = Button(self.bot, self.identifier, self.embed, self.flight)
        await interaction.response.edit_message(view=v, embed=self.embed)


    @discord.ui.button(label='Bookmark', style=discord.ButtonStyle.green, emoji="\U0001f516", custom_id='persistent_view:green')
    async def bmark(self, interaction: discord.Interaction, button: discord.ui.Button):
        identifier = self.identifier
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                exists = await connection.fetchval('SELECT exists(SELECT callsign from bookmarks WHERE id = $1 and nique = $2)', interaction.user.id, identifier)
                if exists == True:
                    await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), title="Error!", description = "You've already bookmarked this flight!"))
                    return
                try:
                    if identifier[2].isalpha() == True:
                        query = identifier[0:3]
                    else:
                        airlines = await fr_api.get_airlines()
                        for airline in airlines:
                            if airline['Code'] == identifier[0:2]:
                                query = airline['ICAO']
                        if "query" not in locals():
                            embed = discord.Embed(color=discord.Color.red())
                            embed.set_author(name='Invalid Flight')
                            embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
                            await interaction.response.send_message(embed=embed, content=interaction.user.mention)
                            return
                except IndexError:
                    embed = discord.Embed(color=discord.Color.red())
                    embed.set_author(name='Invalid Flight')
                    embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
                    await interaction.response.send_message(embed=embed, content=interaction.user.mention)
                    return
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
                    }
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?airline={query}", headers=headers) as r:
                        res = await r.read()
                        res = json.loads(res.decode('UTF-8'))
                res.pop("full_count")
                res.pop("version")
                num = 1
                for item in res:
                    flight = FlightRadar24.flight.Flight(item, res.get(item))
                    if identifier in [flight.callsign, flight.number]:
                        await connection.execute('INSERT INTO bookmarks (id, callsign, landed, channel, nique, guild) VALUES ($1, $2, $3, $4, $5, $6)', interaction.user.id, flight.id, False, interaction.channel.id, identifier, interaction.guild.id)
                        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), title="Success!", description = "You have bookmarked this flight!"))





class Tracking(commands.Cog):
    """Used for tracking aircrafts in LIVE time. Uses flightradar24's API."""

    def __init__(self, bot):
        self.bot = bot
        self.bookmarkstatus.start()



    def custom_cooldown(message):
        if message.author.id == 752706993017454654:
            return None  # no cooldown
        return commands.Cooldown(1, 15)


    @tasks.loop(minutes=1)
    async def bookmarkstatus(self):
        await self.bot.wait_until_ready()
        print("pls")
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                flights = await connection.fetch('SELECT callsign, id, channel, landed, guild from bookmarks')
                print(flights)
                for f in flights:
        #            headers = {
         #               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
          #          }
           #         async with aiohttp.ClientSession() as cs:
            #            async with cs.get(f"https://data-live.flightradar24.com/clickhandler/?flight={f[0]}", headers=headers) as r:
             #               res = json.loads(r[0].decode('UTF-8'))
                            res = await fr_api.get_flight_details(f[0])
                            print(res)
                            if res['status']['generic']['status']['text'] == "landed" and f[3] == False:
                                g = self.bot.get_guild(f[4])
                                user = g.get_member(f[1])
                                embed = discord.Embed(color=discord.Color.green(), title=f" {res['identification']['callsign']} - {res['aircraft']['model']['code']} has landed at {res['airport']['destination']['name']}", description="Press the delete button to stop receiving notifications for this aircraft.", timestamp=datetime.fromtimestamp(res['time']['real']['arrival']))
                                embed.set_footer(text="Aircraft landed ")
                                embed.add_field(name="Route:", value=f"{res['airport']['origin']['code']['icao']}-{res['airport']['destination']['code']['icao']}")
                                embed.add_field(name="Departure Time:", value=f"{datetime.fromtimestamp(res['time']['real']['departure']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC")
                                embed.add_field(name="Arrival Time:", value=f"{datetime.fromtimestamp(res['time']['real']['arrival']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC")
                                if res['airport']['destination']['info']['terminal'] != None:
                                    try:
                                        embed.add_field(name="Arrival Gate:", value=f"Terminal {['airport']['destination']['info']['terminal']} Gate {['airport']['destination']['info']['gate']}")
                                    except:
                                        pass
                                else:
                                    try:
                                        embed.add_field(name="Arrival Gate:", value=f"Gate {['airport']['destination']['info']['gate']}")
                                    except:
                                        pass
                                try:
                                    embed.add_field(name="Baggage Claim:", value=f"Carousel {['airport']['destination']['info']['baggage']}")
                                except:
                                    pass
                                butt = DelButton(self.bot, res['identification']['callsign'])
                                await user.send(embed=embed, content=f"<@{f[1]}>", view=butt)

                                
                                await connection.execute("UPDATE bookmarks set landed = true WHERE callsign = $1", f[0])
                    
                            elif res['status']['generic']['status']['text'] not in ["landed", "scheduled"] and f[3] == True:
                                user = self.bot.get_partial_messageable(f[2])
                                embed = discord.Embed(color=discord.Color.green(), title=f" {res['identification']['callsign']} - {res['aircraft']['model']['code']} has departed from {res['airport']['origin']['name']}", description="Press the delete button to stop receiving notifications for this aircraft.", timestamp=datetime.fromtimestamp(res['time']['real']['departure']))
                                embed.set_footer(text="Aircraft departed ")
                                embed.add_field(name="Route:", value=f"{res['airport']['origin']['code']['icao']}-{res['airport']['destination']['code']['icao']}")
                                embed.add_field(name="Departure Time:", value=f"{datetime.fromtimestamp(res['time']['real']['departure']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC")
                                embed.add_field(name="Estimated Arrival Time:", value=f"{datetime.fromtimestamp(res['time']['estimated']['arrival']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC")
                                butt = DelButton(self.bot, res['identification']['callsign'])
                                await user.send(embed=embed, content=f"<@{f[1]}>", view=butt)

                                
                                await connection.execute("UPDATE bookmarks set landed = false WHERE callsign = $1", f[0])
                    
   



    @commands.hybrid_command()
    async def bookmark(self, ctx, identifier):
        """Add the aircraft to your bookmarks, you will get notified whenever the aircraft lands"""
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                exists = await connection.fetchval('SELECT exists(SELECT callsign from bookmarks WHERE id = $1 and nique = $2)', ctx.author.id, identifier)
                if exists == True:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description = "You've already bookmarked this flight!"))
                    return
                try:
                    if identifier[2].isalpha() == True:
                        query = identifier[0:3]
                    else:
                        airlines = await fr_api.get_airlines()
                        for airline in airlines:
                            if airline['Code'] == identifier[0:2]:
                                query = airline['ICAO']
                        if "query" not in locals():
                            embed = discord.Embed(color=discord.Color.red())
                            embed.set_author(name='Invalid Flight')
                            embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
                            await ctx.send(embed=embed, content=ctx.author.mention)
                            return
                except IndexError:
                    embed = discord.Embed(color=discord.Color.red())
                    embed.set_author(name='Invalid Flight')
                    embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
                    await ctx.send(embed=embed, content=ctx.author.mention)
                    return
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
                    }
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?airline={query}", headers=headers) as r:
                        res = await r.read()
                        res = json.loads(res.decode('UTF-8'))
                res.pop("full_count")
                res.pop("version")
                num = 1
                for item in res:
                    flight = FlightRadar24.flight.Flight(item, res.get(item))
                    if identifier in [flight.callsign, flight.number]:
                        details = await fr_api.get_flight_details(flight.id)
                        flight.set_flight_details(details)
                        if flight.status_text.split(" ")[0] in ['landed', 'scheduled']:
                            ff = False
                        else:
                            ff = True
                        await connection.execute('INSERT INTO bookmarks (id, callsign, landed, channel, nique, guild) VALUES ($1, $2, $3, $4, $5, $6)', ctx.author.id, flight.id, True, ctx.channel.id, identifier, ctx.guild.id)
                        await ctx.send(embed=discord.Embed(color=discord.Color.green(), title="Success!", description = "You have bookmarked this flight!"))






    
    async def remind(self, ctx, identifier):
        try:
            if identifier[2].isalpha() == True:
                query = identifier[0:3]
            else:
                airlines = await fr_api.get_airlines()
                for airline in airlines:
                    if airline['Code'] == identifier[0:2]:
                        query = airline['ICAO']
                if "query" not in locals():
                    embed = discord.Embed(color=discord.Color.red())
                    embed.set_author(name='Invalid Flight')
                    embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
                    await ctx.send(embed=embed, content=ctx.author.mention)
                    return
        except IndexError:
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(name='Invalid Flight')
            embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
            await ctx.send(embed=embed, content=ctx.author.mention)
            return
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
            }
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?airline={query}", headers=headers) as r:
                res = await r.read()
                res = json.loads(res.decode('UTF-8'))
        res.pop("full_count")
        res.pop("version")
        num = 1
        for item in res:
            flight = FlightRadar24.flight.Flight(item, res.get(item))
            if identifier in [flight.callsign, flight.number]:
                details = await fr_api.get_flight_details(flight.id)
                flight.set_flight_details(details)
                embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow())
                try:
                    embed.set_image(url=flight.aircraft_images['large'][0]['src'])
                except:
                    embed.set_image(url=f"http://www.gcmap.com/map?P=c:green,{flight.origin_airport_iata}-{flight.latitude},+{flight.longitude}-{flight.destination_airport_iata},m:p:%22{flight.callsign}%22NW%2bdiamond13:blue,{flight.latitude},+{flight.longitude}&MS=bm&MR=60&MX=720x540&PM=b:pentagon13%2b%25i")
                headers = {
            	    "X-RapidAPI-Key": "",
            	    "X-RapidAPI-Host": "adsbexchange-com1.p.rapidapi.com"
                }
                async with aiohttp.ClientSession() as cs:
                     async with cs.get(f"https://adsbexchange-com1.p.rapidapi.com/v2/callsign/{flight.callsign}/", headers=headers) as b:
                        try:
                            squawk = await b.json()
                            squawk = squawk["ac"][0]['squawk']
                        except:
                            squawk = "Unavailable"
                embed.set_author(name=f'{flight.number}/{flight.callsign}')
                embed.add_field(name='Airline:', value=flight.airline_name, inline=True)
                embed.add_field(name='Transponder Code:', value=squawk, inline=True)                
                embed.add_field(name='Type:', value=flight.aircraft_model, inline=True)
                embed.add_field(name='Registration:', value=flight.registration, inline=True)
                embed.add_field(name='Latitude:', value=flight.latitude, inline=True)
                embed.add_field(name='Longitude:', value=flight.longitude, inline=True)
                embed.add_field(name='Altitude:', value=flight.altitude, inline=True)
                embed.add_field(name='Heading:', value=flight.heading, inline=True)
                embed.add_field(name='Ground Speed:', value=flight.ground_speed, inline=True)
                embed.add_field(name='Vertical Speed:', value=str(flight.vertical_speed) + " feet per minute", inline=True)
                embed.add_field(name='Origin:', value=flight.origin_airport_name, inline=True)
                embed.add_field(name='Destination:', value=flight.destination_airport_name, inline=True)

                try:
                    auth_header = {'x-apikey':''}
                    async with aiohttp.ClientSession() as cs:
                        async with cs.get(f"https://aeroapi.flightaware.com/aeroapi/flights/{flight.callsign}", headers=auth_header) as res:
                            for r in res['flights']:
                                if r['status'].startswith("En Route"):
                                    embed.add_field(name="Route:", value=f"```{r['route']}```", inline=True)
                except:
                    try:
                        j = await asession.get(f"https://flightaware.com/live/flight/{flight.callsign}")
                        js = json.loads(j.html.search('<script>var trackpollBootstrap = {};</script>')[0])
                        route = js['flights'][list(js['flights'].keys())[0]]['flightPlan']['route']
                        embed.add_field(name="Route:", value=f"```{route}```", inline=True)
                    except:
                        pass
                await ctx.send(embed=embed, content=ctx.author.mention) 
                return
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
            }
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?faa=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&gliders=1&stats=1&maxage=14400", headers=headers) as r:
                res = await r.read()
                res = json.loads(res.decode('UTF-8'))
        res.pop("full_count")
        res.pop("version")
        res.pop("stats")
        num = 1
        for item in res:
             flight = FlightRadar24.flight.Flight(item, res.get(item))
             if identifier in [flight.callsign, flight.number]:
                details = await fr_api.get_flight_details(flight.id)
                flight.set_flight_details(details)
                embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow())
                try:
                    embed.set_image(url=flight.aircraft_images['large'][0]['src'])
                except:
                    embed.set_image(url=f"http://www.gcmap.com/map?P=c:green,{flight.origin_airport_iata}-{flight.latitude},+{flight.longitude}-{flight.destination_airport_iata},m:p:%22{flight.callsign}%22NW%2bdiamond13:blue,{flight.latitude},+{flight.longitude}&MS=bm&MR=60&MX=720x540&PM=b:pentagon13%2b%25i")
                headers = {
            	    "X-RapidAPI-Key": "",
            	    "X-RapidAPI-Host": "adsbexchange-com1.p.rapidapi.com"
                }
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://adsbexchange-com1.p.rapidapi.com/v2/callsign/{flight.callsign}/", headers=headers) as b:
                        try:
                            squawk = await b.json()
                            squawk = squawk["ac"][0]['squawk']
                        except:
                            squawk = "Unavailable"
                embed.set_author(name=f'{flight.number}/{flight.callsign}')
                embed.add_field(name='Airline:', value=flight.airline_name, inline=True)
                embed.add_field(name='Transponder Code:', value=squawk, inline=True)
                embed.add_field(name='Type:', value=flight.aircraft_model, inline=True)
                embed.add_field(name='Registration:', value=flight.registration, inline=True)
                embed.add_field(name='Latitude:', value=flight.latitude, inline=True)
                embed.add_field(name='Longitude:', value=flight.longitude, inline=True)
                embed.add_field(name='Altitude:', value=flight.altitude, inline=True)
                embed.add_field(name='Heading:', value=flight.heading, inline=True)
                embed.add_field(name='Ground Speed:', value=flight.ground_speed, inline=True)
                embed.add_field(name='Vertical Speed:', value=str(flight.vertical_speed) + " feet per minute", inline=True)
                embed.add_field(name='Origin:', value=flight.origin_airport_name, inline=True)
                embed.add_field(name='Destination:', value=flight.destination_airport_name, inline=True)

                try:
                    auth_header = {'x-apikey':''}
                    async with aiohttp.ClientSession() as cs:
                        async with cs.get(f"https://aeroapi.flightaware.com/aeroapi/flights/{flight.callsign}", headers=auth_header) as res:
                            for r in res['flights']:
                                if r['status'].startswith("En Route"):
                                    embed.add_field(name="Route:", value=f"```{r['route']}```", inline=True)
                except:
                    try:
                        j = await asession.get(f"https://flightaware.com/live/flight/{flight.callsign}")
                        js = json.loads(j.html.search('<script>var trackpollBootstrap = {};</script>')[0])
                        route = js['flights'][list(js['flights'].keys())[0]]['flightPlan']['route']
                        embed.add_field(name="Route:", value=f"```{route}```", inline=True)
                    except:
                        pass
                await ctx.send(embed=embed, content=ctx.author.mention)
                return
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name='Invalid Flights')
        embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
        await ctx.send(embed=embed, content=ctx.author.mention)
        return


    @commands.hybrid_command()
    async def remindme(self, ctx, identifier: str, hours: int=0, minutes: int=0):
        """Pings you with the aircraft information in the set time"""
        if minutes > 0 or hours > 0:
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), title=f"Success! I will send you the flight's data in {hours}h and {minutes}m"))
            secs = hours * 3600
            msecs = minutes * 60
            await asyncio.sleep(secs + msecs)
            await self.remind(ctx, identifier)
            

    @commands.hybrid_command()
    async def registration(self, ctx, reg: str):
        """Sends info on a specific aircraft based on registration."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.flightradar24.com/common/v1/flight/list.json?query={reg}&fetchBy=reg&token=", headers=headers) as r:
                resp = await r.read()
                resp = json.loads(resp.decode('UTF-8'))
                res = resp['result']['response']['aircraftInfo']
        try:
            embed = discord.Embed(color=discord.Color.blurple(), timestamp=datetime.now(), title=res['registration'])
            embed.add_field(name="Type:", value=res['model']['text'])
            embed.add_field(name="Country:", value=res['country']['name'])
            try:
                embed.add_field(name="Owner:", value=f"{res['owner']['name']}({res['owner']['code']['iata']}/{res['owner']['code']['icao']})")
            except:
                foo = "fo"
            try:
                embed.add_field(name="Airline:", value=f"{res['airline']['name']}({res['airline']['code']['iata']}/{res['airline']['code']['icao']})")
            except:
                embed.add_field(name="Airline:", value=f"{res['airline']['name']}")
            try:
                embed.set_image(url=resp['result']['response']['aircraftImages'][0]['images']['large'][0]['src'])
            except:
                embed.set_image(url=resp['result']['response']['aircraftImages'][0]['images']['thumbnails'][0]['src'])

            await ctx.send(embed=embed)
        except:
            await ctx.send("I was unable to fetch that aircraft!")

    @commands.hybrid_command()
    async def trackreg(self, ctx, identifier: str):
        """Tracks an aircraft by it's registration."""
        try:            
            headers = {
                 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
            }

            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://api.flightradar24.com/common/v1/flight/list.json?query={identifier}&fetchBy=reg&token=-", headers=headers) as r:
                    res = await r.read()
                    res = json.loads(res.decode('UTF-8'))
                try:
                    for item in res["result"]["response"]["data"]:
                        if item['status']['live'] == True:
                            flight = item
                except:
                    flight = res['result']['response']
                    if res['result']['response']['data'] == None:
                        embed = discord.Embed(color=discord.Color.blue())
                        try:
                            embed.set_image(url=flight['aircraftImages']['images']['large'][0]['src'])
                        except:
                            embed.set_image(url=flight['aircraftImages']['images']['sideview'])
                        embed.add_field(name="Registration:", value=flight['aircraftInfo']['registration'])
                        embed.add_field(name="Aircraft Type:", value=flight['aircraftInfo']['model']['text'])
                        embed.add_field(name="Country of Registration:", value=flight['aircraftInfo']['country']['name'])
                        embed.add_field(name="Owner:", value=flight['aircraftInfo']['airline']['name'])

                        await ctx.send(embed=embed)
                    return
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
                }
                async with cs.get(f"https://data-live.flightradar24.com/clickhandler/?flight={flight['identification']['id']}", headers=headers) as res:
                    res = await res.read()
                    res = json.loads(res.decode('UTF-8'))
                embed = discord.Embed(color=discord.Color.blue())
                try:
                    embed.set_image(url=res['aircraft']['images']['large'][0]['src'])
                except:
                    hhdhshf = 1
                embed.set_author(name=flight['identification']['callsign'])
                embed.add_field(name="Aircraft Type:", value=flight['aircraft']['model']['text'])
                try:
                    embed.add_field(name="Origin:", value=res['airport']['origin']['name'])
                except:
                    embed.add_field(name="Origin:", value="None")
                try:
                    embed.add_field(name="Destination:", value=res['airport']['destination']['name'])
                except:
                    embed.add_field(name="Destination:", value="None")

                embed.add_field(name="Owner:", value=flight['airline']['name'])
                embed.add_field(name="Latitude:", value=res['trail'][0]['lat'])
                embed.add_field(name="Longitude:", value=res['trail'][0]['lng'])
                embed.add_field(name="Altitude:", value=res['trail'][0]['alt'])
                embed.add_field(name="Ground Speed:", value=res['trail'][0]['spd'])
                embed.add_field(name="Heading:", value=res['trail'][0]['hd'])
                await ctx.send(embed=embed)
        except:
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(name='Invalid Flight')
            embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
            await ctx.send(embed=embed)
            return
    
    
    async def removebookmark(self, ctx, callsign):
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                exists = await connection.fetchval('SELECT exists(SELECT callsign from bookmarks WHERE id = $1 and nique = $2)', ctx.author.id, callsign)
                if exists == False:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description="That bookmark does not exist! Add it using ``/bookmark {callsign}``!"))
                    return
                await connection.execute("DELETE from bookmarks where id = $1 and nique = $2", ctx.author.id, callsign)
                await ctx.send(embed=discord.Embed(color=discord.Color.green(), title="Success!", description=f"I have deleted the bookmark ``{callsign}``."))
                    
    @commands.hybrid_command()
    async def deletebookmark(self, ctx, callsign):
        """Deletes specified bookmark"""
        await self.removebookmark(ctx, callsign)


    @commands.hybrid_command()
    async def image(self, ctx, file: discord.Attachment):
        api_key = ''
        api_secret = ''
        url = file.url.split("?")[0]
        auth = aiohttp.BasicAuth(login=api_key, password=api_secret)
        await ctx.defer()
        async with aiohttp.ClientSession(auth=auth) as cs:
            async with cs.get(f'https://api.imagga.com/v2/text?image_url={url}') as r:
                j = await r.json()

                texts = []
                for i in j['result']['text']:
                    for item in regs:
                        if i['data'].startswith(item['prefix']):
                            reg = i['data'].replace(" ", "")

                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
                            }
                            async with cs.get(f"https://api.flightradar24.com/common/v1/flight/list.json?query={i['data']}&fetchBy=reg&token=", headers=headers) as r:
                                resp = await r.read()
                                resp = json.loads(resp.decode('UTF-8'))
                                res = resp['result']['response']['aircraftInfo']

                                embed = discord.Embed(color=discord.Color.blurple(), timestamp=datetime.now(), title=res['registration'])
                                embed.add_field(name="Type:", value=res['model']['text'])
                                embed.add_field(name="Country:", value=res['country']['name'])
                                try:
                                    embed.add_field(name="Owner:", value=f"{res['owner']['name']}({res['owner']['code']['iata']}/{res['owner']['code']['icao']})")
                                except:
                                    foo = "fo"
                                try:
                                    embed.add_field(name="Airline:", value=f"{res['airline']['name']}({res['airline']['code']['iata']}/{res['airline']['code']['icao']})")
                                except:
                                    embed.add_field(name="Airline:", value=f"{res['airline']['name']}")
                                try:
                                    embed.set_thumbnail(url=resp['result']['response']['aircraftImages'][0]['images']['large'][0]['src'])
                                except:
                                    embed.set_thumbnail(url=resp['result']['response']['aircraftImages'][0]['images']['thumbnails'][0]['src'])
                                embed.set_image(url=url)                 

                                await ctx.send(embed=embed)
                        





    @commands.hybrid_command()
    async def bookmarks(self, ctx):
        """Lists all bookmarks active"""
        m = await ctx.send("Loading :gear:")
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                u = await connection.fetch("SELECT callsign, nique, landed from bookmarks where id = $1", ctx.author.id)

                b = [u[i:i+5] for i in range(0, len(u), 5)]


                embeds = []
                for p in b:
                    embed = discord.Embed(color=discord.Color.blue(), title="Your Bookmarks", timestamp=datetime.now())
                    for i in p:
                        
                        res = await fr_api.get_flight_details(i[0])
                        if res['status']['generic']['status']['text'] == "landed":
                            status = "landed"
                            embed.add_field(name=f"{res['identification']['callsign']} - {res['aircraft']['model']['code']}:", value=f"Route: {res['airport']['origin']['code']['icao']}-{res['airport']['destination']['code']['icao']}\nStatus: {status}\nDeparture Time: {datetime.fromtimestamp(res['time']['real']['departure']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC\nArrival Time: {datetime.fromtimestamp(res['time']['real']['arrival']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC", inline=False)
                        elif res['status']['generic']['status']['text'] == "estimated":
                            status = "airborne"
                            dist = round(distance(res['trail'][0]['lat'], res['trail'][0]['lng'], res['airport']['destination']['position']['latitude'], res['airport']['destination']['position']['longitude']), 0)
                            embed.add_field(name=f"{res['identification']['callsign']} - {res['aircraft']['model']['code']}:", value=f"Route: {res['airport']['origin']['code']['icao']}-{res['airport']['destination']['code']['icao']}\nStatus: {status}\nDeparture Time: {datetime.fromtimestamp(res['time']['real']['departure']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC\nEstimated Arrival Time: {datetime.fromtimestamp(res['time']['estimated']['arrival']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC\nDistance Remaining: {dist} mi", inline=False)
                        elif res['status']['generic']['status']['text'] == "delayed":
                            status = "delayed"
                            dist = round(distance(res['trail'][0]['lat'], res['trail'][0]['lng'], res['airport']['destination']['position']['latitude'], res['airport']['destination']['position']['longitude']), 0)
                            embed.add_field(name=f"{res['identification']['callsign']} - {res['aircraft']['model']['code']}:", value=f"Route: {res['airport']['origin']['code']['icao']}-{res['airport']['destination']['code']['icao']}\nStatus: {status}\nDeparture Time: {datetime.fromtimestamp(res['time']['real']['departure']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC\nEstimated Arrival Time: {datetime.fromtimestamp(res['time']['estimated']['arrival']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC\nDistance Remaining: {dist} mi", inline=False)
                        elif res['status']['generic']['status']['text'] == "scheduled":
                            status = "scheduled"
                            dist = round(distance(res['trail'][0]['lat'], res['trail'][0]['lng'], res['airport']['destination']['position']['latitude'], res['airport']['destination']['position']['longitude']), 0)
                            embed.add_field(name=f"{res['identification']['callsign']} - {res['aircraft']['model']['code']}:", value=f"Route: {res['airport']['origin']['code']['icao']}-{res['airport']['destination']['code']['icao']}\nStatus: {status}\nScheduled Departure Time: {datetime.fromtimestamp(res['time']['scheduled']['departure']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC\nScheduled Arrival Time: {datetime.fromtimestamp(res['time']['scheduled']['arrival']).strftime('%-m/%d/%Y at %I:%M:%S')} UTC", inline=False)
    

                    embeds.append(embed)
                menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbed)
                for e in embeds: 
                    menu.add_page(e)
                menu.add_button(ViewButton.back())
                menu.add_button(ViewButton.next())
                await m.delete()
                await menu.start()



                
   # @commands.hybrid_command()
  #  async def track(self, ctx, identifier: str):
    #    headers = {
   	#        "X-RapidAPI-Key": "",
    #   	    "X-RapidAPI-Host": "adsbexchange-com1.p.rapidapi.com"
    #    }
    #    header1 = {
    #        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    #    }

        #async with aiohttp.ClientSession() as cs:
         #   async with cs.get(f"https://adsbexchange-com1.p.rapidapi.com/v2/callsign/{identifier}/", headers=headers) as b:
          #      try:
           #         b = await b.json()
            #        async with cs.get(f"https://api.flightradar24.com/common/v1/flight/list.json?query={b['ac'][0]['r']&fetchBy=reg&token=", headers=header1) as n:
             #           n = await n.json()
              #          callsign = n['result']['response']['aircraftInfo']['airline']['code']['iata']
               #         async with cs.get(f"https://api.flightradar24.com/common/v1/flight/list.json?query={b['ac'][0]['r']&fetchBy=reg&token=", headers=header1) as p:
                #            p = await p.json()
                            
               # except:
                


    @commands.hybrid_command()
    async def findflight(self, ctx, identifier: str):
        """Tracks a flight from its flight number or its callsign."""
        await ctx.defer()
        try:
            if identifier[2].isalpha() == True:
                query = identifier[0:3]
            else:
                airlines = await fr_api.get_airlines()
                for airline in airlines:
                    if airline['Code'] == identifier[0:2]:
                        query = airline['ICAO']
                if "query" not in locals():
                    embed = discord.Embed(color=discord.Color.red())
                    embed.set_author(name='Invalid Flight')
                    embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
                    await ctx.send(embed=embed)
                    return
        except IndexError:
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(name='Invalid Flight')
            embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
            await ctx.send(embed=embed)
            return
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
            }
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?airline={query}", headers=headers) as r:
                res = await r.read()
                res = json.loads(res.decode('UTF-8'))
        res.pop("full_count")
        res.pop("version")
        num = 1
        for item in res:
            flight = FlightRadar24.flight.Flight(item, res.get(item))
            if identifier in [flight.callsign, flight.number]:
                details = await fr_api.get_flight_details(flight.id)
                flight.set_flight_details(details)
                embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow())
                try:
                    embed.set_image(url=flight.aircraft_images['large'][0]['src'])
                except:
                    embed.set_image(url=f"http://www.gcmap.com/map?P=c:green,{flight.origin_airport_iata}-{flight.latitude},+{flight.longitude}-{flight.destination_airport_iata},m:p:%22{flight.callsign}%22NW%2bdiamond13:blue,{flight.latitude},+{flight.longitude}&MS=bm&MR=60&MX=720x540&PM=b:pentagon13%2b%25i")
                headers = {
            	    "X-RapidAPI-Key": "",
            	    "X-RapidAPI-Host": "adsbexchange-com1.p.rapidapi.com"
                }
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://adsbexchange-com1.p.rapidapi.com/v2/callsign/{flight.callsign}/", headers=headers) as b:
                        try:
                            squawk = await b.json()
                            squawk = squawk["ac"][0]['squawk']
                        except:
                            squawk = "Unavailable"
                embed.set_author(name=f'{flight.number}/{flight.callsign}')
                embed.add_field(name='Airline:', value=flight.airline_name, inline=True)
                embed.add_field(name='Transponder Code:', value=squawk, inline=True)                
                embed.add_field(name='Type:', value=flight.aircraft_model, inline=True)
                embed.add_field(name='Registration:', value=flight.registration, inline=True)
                embed.add_field(name='Latitude:', value=flight.latitude, inline=True)
                embed.add_field(name='Longitude:', value=flight.longitude, inline=True)
                embed.add_field(name='Altitude:', value=flight.altitude, inline=True)
                embed.add_field(name='Heading:', value=flight.heading, inline=True)
                embed.add_field(name='Ground Speed:', value=flight.ground_speed, inline=True)
                embed.add_field(name='Vertical Speed:', value=str(flight.vertical_speed) + " feet per minute", inline=True)
                embed.add_field(name='Origin:', value=flight.origin_airport_name, inline=True)
                embed.add_field(name='Destination:', value=flight.destination_airport_name, inline=True)
                try:
                    auth_header = {'x-apikey':''}
                    async with aiohttp.ClientSession() as cs:
                        async with cs.get(f"https://aeroapi.flightaware.com/aeroapi/flights/{flight.callsign}", headers=auth_header) as res:
                            for r in res['flights']:
                                if r['status'].startswith("En Route"):
                                    embed.add_field(name="Route:", value=f"```{r['route']}```", inline=True)
                except:
                    try:
                        j = await asession.get(f"https://flightaware.com/live/flight/{flight.callsign}")
                        js = json.loads(j.html.search('<script>var trackpollBootstrap = {};</script>')[0])
                        route = js['flights'][list(js['flights'].keys())[0]]['flightPlan']['route']
                        embed.add_field(name="Route:", value=f"```{route}```", inline=True)
                    except:
                        pass
                view = Button(self.bot, identifier, embed, flight)
                await ctx.send(embed=embed, view=view) 
                return
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
            }
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?faa=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&gliders=1&stats=1&maxage=14400", headers=headers) as r:
                res = await r.read()
                res = json.loads(res.decode('UTF-8'))
        res.pop("full_count")
        res.pop("version")
        res.pop("stats")
        num = 1
        for item in res:
            flight = FlightRadar24.flight.Flight(item, res.get(item))
            if identifier in [flight.callsign, flight.number]:
                details = await fr_api.get_flight_details(flight.id)
                flight.set_flight_details(details)
                embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow())
                try:
                    embed.set_image(url=flight.aircraft_images['large'][0]['src'])
                except:
                    embed.set_image(url=f"http://www.gcmap.com/map?P=c:green,{flight.origin_airport_iata}-{flight.latitude},+{flight.longitude}-{flight.destination_airport_iata},m:p:%22{flight.callsign}%22NW%2bdiamond13:blue,{flight.latitude},+{flight.longitude}&MS=bm&MR=60&MX=720x540&PM=b:pentagon13%2b%25i")
                headers = {
                    "X-RapidAPI-Key": "",
                    "X-RapidAPI-Host": "adsbexchange-com1.p.rapidapi.com"
                }
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f"https://adsbexchange-com1.p.rapidapi.com/v2/callsign/{flight.callsign}/", headers=headers) as b:
                        try:
                            squawk = await b.json()
                            squawk = squawk["ac"][0]['squawk']
                        except:
                            squawk = "Unavailable"
                embed.set_author(name=f'{flight.number}/{flight.callsign}')
                embed.add_field(name='Airline:', value=flight.airline_name, inline=True)
                embed.add_field(name='Transponder Code:', value=squawk, inline=True)
                embed.add_field(name='Type:', value=flight.aircraft_model, inline=True)
                embed.add_field(name='Registration:', value=flight.registration, inline=True)
                embed.add_field(name='Latitude:', value=flight.latitude, inline=True)
                embed.add_field(name='Longitude:', value=flight.longitude, inline=True)
                embed.add_field(name='Altitude:', value=flight.altitude, inline=True)
                embed.add_field(name='Heading:', value=flight.heading, inline=True)
                embed.add_field(name='Ground Speed:', value=flight.ground_speed, inline=True)
                embed.add_field(name='Vertical Speed:', value=str(flight.vertical_speed) + " feet per minute", inline=True)
                embed.add_field(name='Origin:', value=flight.origin_airport_name, inline=True)
                embed.add_field(name='Destination:', value=flight.destination_airport_name, inline=True)

                try:
                    auth_header = {'x-apikey':''}
                    async with aiohttp.ClientSession() as cs:
                        async with cs.get(f"https://aeroapi.flightaware.com/aeroapi/flights/{flight.callsign}", headers=auth_header) as res:
                            for r in res['flights']:
                                if r['status'].startswith("En Route"):
                                    embed.add_field(name="Route:", value=f"```{r['route']}```", inline=True)
                except:
                    try:
                        j = await asession.get(f"https://flightaware.com/live/flight/{flight.callsign}")
                        js = json.loads(j.html.search('<script>var trackpollBootstrap = {};</script>')[0])
                        route = js['flights'][list(js['flights'].keys())[0]]['flightPlan']['route']
                        embed.add_field(name="Route:", value=f"```{route}```", inline=True)
                    except:
                        pass
                view = Button(self.bot, identifier, embed, flight)
                await ctx.send(embed=embed, view=view)
                return
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name='Invalid Flights')
        embed.add_field(name="Error:" , value="Unfortunately that is not a valid flight, ensure that the flight is valid, and squawking mode charlie.")
        await ctx.send(embed=embed)
        return





    
    
    

    @commands.hybrid_command()
    async def airline(self, ctx, identifier: str):
        """Gets information about the specified airline."""
        f = open ('/home/admin/FlightTracker/airlines.json', "r")
        j = json.loads(f.read())
        f.close()
        if identifier in j['iata'] or identifier in j['icao']:
            if len(identifier) == 2:
                ICAO = j['icao'][j['iata'].indexOf(identifier)]
            else:
                ICAO = identifier
            res = j['airlines'][ICAO]
            
            logo = await fr_api.get_airline_logo(icao=ICAO, iata=res['iata'])
            embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow())
            embed.set_author(name=res['name'])
            if logo != None:
                embed.set_image(url=logo)
            embed.add_field(name="Name:", value=res['name'], inline=False)
            embed.add_field(name="Country:", value=res['country'], inline=False)
            embed.add_field(name="Fleet Size: ", value=res['fleet'], inline=False)
            embed.add_field(name="ICAO:", value=ICAO, inline=False)
            embed.add_field(name="IATA:", value=res['iata'], inline=False)
            embed.add_field(name="Callsign:", value=res['callsign'], inline=False)
            embed.set_footer(text="Information may be outdated/inaccurate.")
            await ctx.send(embed=embed)
            
            return
        headers = {
        	"X-RapidAPI-Key": ""
        }
        async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://aviation-reference-data.p.rapidapi.com/airline/{identifier}", headers=headers) as resp:
                    results = await resp.json()
                    try:
                        iata = results['iataCode']
                        ICAO = results['icaoCode']
                    except:
                        await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="ERROR", description="Invalid airline identifier, please double check here: https://airlinecodes.info/icao"))
                        return 
                    logo = await fr_api.get_airline_logo(icao=ICAO, iata=iata)

                    country = results['alpha3countryCode']

                    async with cs.get(f"https://airlines-by-api-ninjas.p.rapidapi.com/v1/airlines?icao={ICAO}", headers=headers) as re:
                        re = await re.json()
                    name = re[0]['name']
                    fleet = re[0]['fleet']['total']
                    callsign = results['callSign']
                    embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow())
                    embed.set_author(name=name)
                    if logo != None:
                        embed.set_image(url=logo)
                    embed.set_footer(text="Information may be outdated/inaccurate.")
                    embed.add_field(name="Name:", value=name, inline=False)
                    embed.add_field(name="Country:", value=country, inline=False)
                    embed.add_field(name="Fleet Size: ", value=fleet, inline=False)
                    embed.add_field(name="ICAO:", value=ICAO, inline=False)
                    embed.add_field(name="IATA:", value=iata, inline=False)
                    embed.add_field(name="Callsign:", value=callsign, inline=False)
                    await ctx.send(embed=embed)
                    
                    prr = {"country" : country, "fleet" : fleet, "icao" : ICAO, "iata" : iata, "callsign" : callsign, "name" : name}
                    data = {ICAO : prr}
                    with open("/home/admin/FlightTracker/airlines.json" ,'r+') as file:

                        file_data = json.load(file)

                        file_data["airlines"][ICAO] = prr
                        file_data["icao"].append(ICAO)
                        file_data["iata"].append(iata)
                        file.seek(0)

                        json.dump(file_data, file, indent = 4)
                        return
 
            





#    @commands.command(aliases=['findflights', 'searchflights'])
#    @commands.dynamic_cooldown(custom_cooldown, commands.BucketType.user)
#    async def trackflights(self, ctx, identifier):
#        """Tracks all the flights from the specified airline."""
#        airline_ICAO = identifier
#        try:
#            airname = await get_airline_name(airline_ICAO.upper())
#        except AttributeError:
#            airline_ICAO = await get_icao(identifier)
#        try:
#            airname = await get_airline_name(airline_ICAO.upper())
#        except AttributeError:
#            embed = discord.Embed(color=discord.Color.red(), title='Error!', description='That is not a valid airline!')
#            await ctx.send(embed=embed)
#            return
#        message = await ctx.send(f':white_check_mark: Getting flights from {airname}, please wait <a:loading:829781249945370654>')
#        async with ctx.typing():
#            flights = await getflights(airline_ICAO.upper(), message)
#            erm = []
#            if len(flights) == 0:
#                 embed = discord.Embed(color=discord.Color.red(), title='Error!', description='There are no current flights from that airline!')
#                 await ctx.send(embed=embed)
#                 return
#            await message.edit(content=f'<a:loading:829781249945370654> Embedding data, please wait. <a:loading:829781249945370654>')
#            for item in flights:
#                values = flights.get(item)
#                data = [item, values[0], values[1], values[2], values[3], airline_ICAO, values[4]]
#                erm.append(data)
#                menu = menus.MenuPages(EmbedPageSource(erm, per_page=3))        
#        await menu.start(ctx)
#        await message.delete()
#
#
#    @trackflights.error
#    async def trackflights_handler(self, ctx, error):
#        if isinstance(error, commands.CommandOnCooldown):
#            await ctx.send(embed=discord.Embed(color=discord.Color.red(), timestamp=discord.utils.utcnow(), title="Slow Down!", description=f"This command has a cooldown! You may retry the command after ``{round(error.retry_after)}`` seconds."))



async def setup(bot):
    await bot.add_cog(Tracking(bot))
