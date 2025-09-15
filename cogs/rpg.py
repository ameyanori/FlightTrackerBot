from FlightRadar24.api import FlightRadar24API
import FlightRadar24
import discord
import traceback
from discord.ext import commands, menus, tasks
from discord import Intents
import pandas as pd
import asyncio
import wikipedia as wp
import json
import aiohttp
from datetime import datetime
import regex as re
from math import radians, cos, sin, asin, sqrt
fr_api = FlightRadar24API()



class EmbedPageSource(menus.ListPageSource):
    async def format_page(self, menu, items):
        embed = discord.Embed(title="Your Fleet:")
        for item in items:
            embed.add_field(name=f"ID: {item['id']}", value=f"Type: {item['aircraft_type']}\nHours left: {item['hours_left']}", inline=False)
        return embed

def distance(lat1, lon1, lat2, lon2):
     
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers. Use 3956 for miles
    r = 3956
      
    # calculate the result
    return(c * r)

def is_airline():
    async def predicate(ctx):
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                exists = await connection.fetchval('SELECT exists(SELECT airline_name from rpg WHERE user_id = $1)', ctx.author.id)
                if exists == False:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description=f"You have not created an airline yet! Create one with the {ctx.clean_prefix}start command!"))
                return exists == True

    return commands.check(predicate)


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.payday.start()

    @tasks.loop(minutes=60)
    async def payday(self):
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                ra = await connection.fetch('SELECT * FROM routes')
                for route in ra:
                    user_id = route['user_id']
                    profit = route['profit']
                    await connection.execute('UPDATE rpg set money = money + $1 where user_id  = $2', profit, user_id)


    @payday.before_loop
    async def before_payday(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def bal(self, ctx):
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                res = await connection.fetch('SELECT * FROM RPG where user_id = $1', ctx.author.id)
                try:
                    res = res[0]
                    money = res['money']
                    money = "{:,}".format(money)
                    await ctx.send(embed=discord.Embed(title=f"{res['airline_name']}", description=f"Balance: {money}\nBase: {res['base']}"))
                except IndexError:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description=f"You have not created an airline yet! Create one with the {ctx.clean_prefix}start command!"))




    @commands.command()
    async def shop(self, ctx):
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                exists = await connection.fetchval('SELECT exists(SELECT airline_name from rpg WHERE user_id = $1)', ctx.author.id)
                if exists == False:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description=f"You have not created an airline yet! Create one with the {ctx.clean_prefix}start command!"))
                    return
                with open("/home/admin/FlightTracker/aircrafts.json") as file:
                    data = json.load(file)
                embed = discord.Embed(title="Shop!")
                num = 0
                for key in data:
                    num = num + 1
                    value = data[key]
                    if value['long_haul'] == "unable":
                        long_haul = "unable"
                    else:
                        long_haul = '{:,}'.format(value['long_haul'])
                    if (num % 2) == 0: #if is even
                        embed.add_field(name=value['text'], value=f"ID: {value['id']}\nCode: {key}\nPrice: {'{:,}'.format(value['price'])}\nLong Haul Revenue: {long_haul}\nShort Haul Revenue: {'{:,}'.format(value['short_haul'])}", inline=True)
                        embed.add_field(name='\u200b', value='\u200b', inline=True)

                    else: # if is odd
                        embed.add_field(name=value['text'], value=f"ID: {value['id']}\nCode: {key}\nPrice: {'{:,}'.format(value['price'])}\nLong Haul Revenue: {long_haul}\nShort Haul Revenue: {'{:,}'.format(value['short_haul'])}", inline=True)
                await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, id):
        try:
            id = int(id)
        except:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description=f"You did not choose a valid ID! Please try again from the {ctx.clean_prefix}shop command!"))
            return
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                exists = await connection.fetchval('SELECT exists(SELECT airline_name from rpg WHERE user_id = $1)', ctx.author.id)
                if exists == False:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description=f"You have not created an airline yet! Create one with the {ctx.clean_prefix}start command!"))
                    return
                with open("/home/admin/FlightTracker/aircrafts.json") as file:
                    data = json.load(file)
                for plane in data:
                    if data[plane]['id'] == id:
                        aircraft = data[plane]
                        try:
                            bal = await connection.fetchval('SELECT money from rpg WHERE user_id = $1', ctx.author.id)
                        except:
                            await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description=f"You did not choose a valid ID! Please try again from the {ctx.clean_prefix}shop command!"))

                        if bal > aircraft['price']:
                            bal = bal - aircraft['price']
                            await connection.execute('UPDATE rpg SET money = $1 WHERE user_id = $2', bal, ctx.author.id)
                            await connection.execute('INSERT INTO aircrafts (user_id, aircraft_type, hours_left) VALUES ($1, $2, $3)', ctx.author.id, plane, 50)
                            await ctx.send(embed=discord.Embed(color=discord.Color.green(), title=f"Congratulations! You bought a {aircraft['text']}", description=f"You may access it from the {ctx.clean_prefix}myfleet command!"))
                            return
                        else:
                            await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Uh oh!", description=f"You do not have enough money to buy this aircraft!"))
                            return
                await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description=f"You did not choose a valid ID! Please try again from the {ctx.clean_prefix}shop command!"))
    

    @commands.command()
    async def createroute(self, ctx, origin = None, dest = None, id = None):
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                exists = await connection.fetchval('SELECT exists(SELECT airline_name from rpg WHERE user_id = $1)', ctx.author.id)
                if exists == False:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description=f"You have not created an airline yet! Create one with the {ctx.clean_prefix}start command!"))
                    return
                if origin is not None and dest is not None and id is not None:
                    try:
                        origair = await fr_api.get_airport(origin)
                        try:
                            home = origair['name']
                        except:
                            await ctx.send(embed=discord.Embed(title=f"Uh oh! Your origin doesn't seem to be a valid ICAO/IATA code!", description="Please run the command again and use a valid code!"))
                            return
                        destair = await fr_api.get_airport(dest)
                        try:
                            home = destair['name']
                        except:
                            await ctx.send(embed=discord.Embed(title=f"Uh oh! Your destination doesn't seem to be a valid ICAO/IATA code!", description="Please run the command again and use a valid code!"))
                            return
                        try:
                            exists = await connection.fetchval('SELECT exists(SELECT aircraft_type from aircrafts where id = $1 and user_id = $2)', int(id), ctx.author.id)
                        except:
                            await ctx.send(embed=discord.Embed(title=f"Uh oh! That doesn't seem to be a valid aircraft ID!", description=f"Please run the command again and use a valid ID from the {ctx.clean_prefix}myfleet command!"))
                            return
                        if exists == False:
                            await ctx.send(embed=discord.Embed(title=f"Uh oh! That doesn't seem to be a valid aircraft ID!", description=f"Please run the command again and use a valid ID from the {ctx.clean_prefix}myfleet command."))
                            return
                        with open("/home/admin/FlightTracker/aircrafts.json") as file:
                            data = json.load(file)
                        aircraft = await connection.fetchval('SELECT aircraft_type from aircrafts where id = $1', int(id))
                        val = data[aircraft]
                        hours = await connection.fetchval('SELECT hours_left from aircrafts where id = $1', int(id))
                        dist =  distance(origair['position']['latitude'], origair['position']['longitude'], destair['position']['latitude'], destair['position']['longitude'])
                        if dist > 3001:
                            type = "long_haul"
                            if val['long_haul'] == "unable":
                                await ctx.send(embed=discord.Embed(title=f"Uh oh! That aircraft doesn't seem to be able to fly a long haul route!", description=f"Please run the command again and use an aircraft that can fly that route from the {ctx.clean_prefix}myfleet command."))
                                return
                            num = 10
                            money = val['long_haul']
                        else:
                            money = val['short_haul']
                            num = 5
                            type = "short_haul"
                        if hours < num:
                            await ctx.send(embed=discord.Embed(title="Whoops!", description="Looks like you don't have enough hours on this aircraft to create this route! Please run the command again with an aircraft that has enough hours. \n**Remember:**\nLong Haul = 10 hours\nShort Haul = 5 hours"))
                            return
                        await connection.execute("INSERT into routes (user_id, origin, dest, profit) VALUES ($1, $2, $3, $4)", ctx.author.id, origin, dest, money)
                        await connection.execute("UPDATE aircrafts SET hours_left = hours_left - $1 WHERE id = $2", num, int(id))
                        await ctx.send(embed=discord.Embed(color=discord.Color.green(), title="Success!", description=f"Your route is:\nOrigin: {origair['name']}\nDestination: {destair['name']}\nAircraft Type: {aircraft}\nRoute Type: {type}\nMoney gained per flight: {money}\nDistance: {dist}"))
                        return
                    except Exception as e:
                        await ctx.send(embed=discord.Embed(title=f"Uh oh! That doesn't seem to be a valid ICAO/IATA code!", description="Please run the command again and use a valid code!"))
                        return



                await ctx.send(embed=discord.Embed(title="Create a route!", description="Please send the 3 or 4 letter ICAO or IATA code associated with your origin airport!"))
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                origin = msg.content
                try:
                    origair = await fr_api.get_airport(origin)
                    await ctx.send(embed=discord.Embed(title=f"Great! You have chosen {origair['name']} as your origin airport!", description="Now please send the 3 or 4 letter ICAO or IATA code associated with your destination airport!"))
                except:
                    await ctx.send(embed=discord.Embed(title=f"Uh oh! That doesn't seem to be a valid ICAO/IATA code!", description="Please run the command again and use a valid code!"))
                    return
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                dest = msg.content
                try:
                    destair = await fr_api.get_airport(dest)
                    await ctx.send(embed=discord.Embed(title=f"Great! You have chosen {destair['name']} as your destination airport!", description="Now, please send the identifier of the aircraft you wish to use for this route!"))
                    msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    id = msg.content
                    try:
                        exists = await connection.fetchval('SELECT exists(SELECT aircraft_type from aircrafts where id = $1 and user_id = $2)', int(id), ctx.author.id)
                    except:
                        await ctx.send(embed=discord.Embed(title=f"Uh oh! That doesn't seem to be a valid aircraft ID!", description=f"Please run the command again and use a valid ID from the {ctx.clean_prefix}myfleet command!"))
                        return
                    if exists == False:
                        await ctx.send(embed=discord.Embed(title=f"Uh oh! That doesn't seem to be a valid aircraft ID!", description=f"Please run the command again and use a valid ID from the {ctx.clean_prefix}myfleet command."))
                        return
                    with open("/home/admin/FlightTracker/aircrafts.json") as file:
                        data = json.load(file)
                    aircraft = await connection.fetchval('SELECT aircraft_type from aircrafts where id = $1', int(id))
                    val = data[aircraft]
                    hours = await connection.fetchval('SELECT hours_left from aircrafts where id = $1', int(id))
                    dist =  distance(origair['position']['latitude'], origair['position']['longitude'], destair['position']['latitude'], destair['position']['longitude'])
                    if dist > 3001:
                        type = "long_haul"
                        if val['long_haul'] == "unable":
                            await ctx.send(embed=discord.Embed(title=f"Uh oh! That aircraft doesn't seem to be able to fly a long haul route!", description=f"Please run the command again and use an aircraft that can fly that route from the {ctx.clean_prefix}myfleet command."))
                            return
                        num = 10
                        money = val['long_haul']
                    else:
                        money = val['short_haul']
                        num = 5
                        type = "short_haul"
                    if hours < num:
                        await ctx.send(embed=discord.Embed(title="Whoops!", description="Looks like you don't have enough hours on this aircraft to create this route! Please run the command again with an aircraft that has enough hours. \n**Remember:**\nLong Haul = 10 hours\nShort Haul = 5 hours"))
                        return
                    await connection.execute("INSERT into routes (user_id, origin, dest, profit) VALUES ($1, $2, $3, $4)", ctx.author.id, origin, dest, money)
                    await connection.execute("UPDATE aircrafts SET hours_left = hours_left - $1 WHERE id = $2", num, int(id))
                    await ctx.send(embed=discord.Embed(color=discord.Color.green(), title="Success!", description=f"Your route is:\nOrigin: {origair['name']}\nDestination: {destair['name']}\nAircraft Type: {aircraft}\nRoute Type: {type}\nMoney gained per flight: {money}\nDistance: {dist}"))
                
                except Exception as e:
                    await ctx.send(embed=discord.Embed(title=f"Uh oh! That doesn't seem to be a valid ICAO/IATA code!", description="Please run the command again and use a valid code!"))
                    return


    @commands.command()
    async def myfleet(self, ctx):
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                fleet = await connection.fetch('SELECT aircraft_type, id, hours_left from aircrafts WHERE user_id = $1', ctx.author.id)
                menu = menus.MenuPages(EmbedPageSource(fleet, per_page=7))
                await menu.start(ctx)
    @commands.command()
    async def myroutes(self, ctx):
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                routes = await connection.fetch('SELECT origin, dest, profit, id from routes WHERE user_id = $1', ctx.author.id)
                menu = menus.MenuPages(EmbedPageSource(routes, per_page=7))
                await menu.start(ctx)

    @commands.command()
    async def start(self, ctx):
        async with self.bot.pg_con.acquire() as connection:
            async with connection.transaction():
                exists = await connection.fetchval('SELECT exists(SELECT airline_name from rpg WHERE user_id = $1)', ctx.author.id)
                if exists == True:
                    await ctx.send(embed=discord.Embed(color=discord.Color.red(), title="Error!", description = "Unfortunately only premium users may create more than 1 airline, if you want to buy premium, head over to https://www.patreon.com/flighttracker"))
                    return
                await ctx.send(embed=discord.Embed(title="Welcome to FlightTracker's Economy!", description="Please send the name of an airline you want to create!"))
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                airline_name = msg.content
                await ctx.send(embed=discord.Embed(title=f"Great! I can't wait to see the future of {airline_name}!", description="Now, please send a 3-letter ICAO code you wish to use as your ICAO callsign!"))        
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                icao = msg.content
                await ctx.send(embed=discord.Embed(title=f"Perfect!", description="Now, please send a 2-letter IATA code you wish to use as your IATA code!"))
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                iata = msg.content
                await ctx.send(embed=discord.Embed(title=f"One last step!", description="Please send the 3-letter or 4-letter IATA or ICAO code of the airport you wish to use as your home base!"))
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                base = msg.content
                try:
                    res = await fr_api.get_airport(base)
                    mes = await ctx.send(embed=discord.Embed(title=f"Awesome! You have chosen {res['name']} as your home base!", description=f"Now it's time to choose your starting aircraft!\nReact with :one: to start with the Boeing 737-800.\nReact with :two: to start with the Airbus A320-232.\nReact with :three: to start with the Tupolev TU-204-500. "))
                    await mes.add_reaction('1\N{variation selector-16}\N{combining enclosing keycap}')
                    await mes.add_reaction('2\N{variation selector-16}\N{combining enclosing keycap}')
                    await mes.add_reaction('3\N{variation selector-16}\N{combining enclosing keycap}')
                    reaction, user  = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author and reaction.message == mes and str(reaction.emoji) in ['1\N{variation selector-16}\N{combining enclosing keycap}', '2\N{variation selector-16}\N{combining enclosing keycap}', '3\N{variation selector-16}\N{combining enclosing keycap}'])
                    if str(reaction.emoji) == "1\N{variation selector-16}\N{combining enclosing keycap}":
                        airplane = "B737"
                    elif str(reaction.emoji) == "2\N{variation selector-16}\N{combining enclosing keycap}":
                        airplane = "A320"
                    elif str(reaction.emoji) == "3\N{variation selector-16}\N{combining enclosing keycap}":
                        airplane = "TU204"
                    plane = {airplane : 50}
                    await ctx.send(embed=discord.Embed(color=discord.Color.green(), title=f"Great! You have chosen the {airplane}!", description="Now you can start creating routes with the ;createroute command! Welcome to the skies!"))
                    await connection.execute('INSERT INTO rpg (user_id, airline_name, money, icao, iata, long_routes, short_routes, base, premium) VALUES ($1, $2, 0, $3, $4, 0, 0, $5, False)', ctx.author.id, airline_name, icao, iata, base) 
                    await connection.execute('INSERT INTO aircrafts (user_id, aircraft_type, hours_left) VALUES ($1, $2, 50)', ctx.author.id, airplane)    
                except:
                    await ctx.send(embed=discord.Embed(title=f"Uh oh! That doesn't seem to be a valid ICAO/IATA code!", description="Please run the command again and use a valid code!"))
                    return







async def setup(bot):
    await bot.add_cog(Economy(bot))

