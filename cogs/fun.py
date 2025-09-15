from FlightRadar24.api import FlightRadar24API
import discord
import traceback
from discord.ext import commands, tasks
from discord import Intents
import random
import json
import aiohttp
from discord import app_commands
from discord.app_commands import Choice
from discord.ext.commands.cooldowns import BucketType
from utils import (
    generate_puzzle_embed,
    is_game_over,
    is_valid_word,
    random_puzzle_id,
    update_embed,
)
from datetime import date

class Fun(commands.Cog):
    """Commands in the "fun" section are entertainment."""

    def __init__(self, bot):
        self.bot = bot
        self.airlines = []
        self.aviation = []
        self.refresh.start()

    @tasks.loop(hours=3)
    async def refresh(self):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://gnews.io/api/v4/search?q=airlines&lang=en&in=title&token=f6abfc5d0e962577237de24f9fd8febb") as r:
                l = await r.json()
                self.airlines = l
            async with cs.get("https://gnews.io/api/v4/search?q=aviation&lang=en&in=title&token=f6abfc5d0e962577237de24f9fd8febb") as r:
                l = await r.json()
                self.aviation = l


    @commands.hybrid_command()
    @app_commands.describe(category='News Category to Choose')
    @app_commands.choices(category=[
        Choice(name='Aviation', value=1),
        Choice(name='Airlines', value=2)
    ])
    async def news(self, ctx, category: Choice[int]):
        """Gathers top 5 Aviation or Airline related news articles"""
        print(self.airlines)
        embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow(), title=f"{category.name} News")
        if category.name == "Aviation":
            for i in self.aviation['articles'][0:5]:
                embed.add_field(value=f"[{i['title']}]({i['url']})", name=i['source']['name'], inline=False)
        elif category.name == "Airlines":
            for i in self.airlines['articles'][0:5]:
                embed.add_field(value=f"[{i['title']}]({i['url']})", name=i['source']['name'], inline=False)
        await ctx.send(embed=embed)






    @commands.Cog.listener()
    async def on_message(self, message):

# get the message replied to
        ref = message.reference
        if not ref or not isinstance(ref.resolved, discord.Message):
            return
        parent = ref.resolved
        bot = self.bot
        # if the parent message is not the bot's message, ignore it
        if parent.author.id != bot.user.id:
            return
    
        # check that the message has embeds
        if not parent.embeds:
            return

        embed = parent.embeds[0]
        guess = message.content.lower()
        ctx = await self.bot.get_context(message)
        # check that the user is the one playing
        if (
            embed.author.name != message.author.name
            or embed.author.icon_url != message.author.display_avatar.url
        ):
            if embed.title == "Airportle":
                reply = f"Start a new game with /airportle command!"
                if embed.author:
                    reply = f"This game was started by {embed.author.name}. " + reply
                await message.reply(reply, delete_after=5)
                try:
                    await message.delete(delay=5)
                except Exception:
                    pass
                return
    
        # check that the game is not over
        if is_game_over(embed):
            await message.reply(
               f"The game is already over. Start a new game with /play", delete_after=5
            )
            try:
                await message.delete(delay=5)
            except Exception:
                pass
            return
    
        # check that a single word is in the message
        if len(message.content.split(" ")) > 2:
            await message.reply(
                "Please respond with a single 3-letter airport IATA code!", delete_after=5
            )
            try:
                await message.delete(delay=5)
            except Exception:
                pass
            return
    
        # check that the word is valid
        print(guess)
        if is_valid_word(guess.upper()) == False:
            await message.reply("That is not a valid airport IATA code!", delete_after=5)
            try:
                await message.delete(delay=5)
            except Exception:
                pass
            return
    
        # update the embed
        embed = await update_embed(embed, guess, message)
        await parent.edit(embed=embed)
    
        # attempt to delete the message
        try:
            await message.delete()
        except Exception:
            pass
    
        def custom_cooldown(message):
            if message.author.id == 752706993017454654:
                return None  # no cooldown
            return commands.Cooldown(1, 15)


    @commands.hybrid_command()
   # @commands.dynamic_cooldown(custom_cooldown, commands.BucketType.user)
    async def airportle(self, ctx):
        """Begins a game of airportle!"""
      #  await ctx.send("F")
        puzzle_id = random_puzzle_id()
        embed = generate_puzzle_embed(ctx.author, puzzle_id, ctx)
        await ctx.send(embed=embed)

    #@airportle.error
    #async def airportle_handler(self, ctx, error):
    #    if isinstance(error, commands.CommandOnCooldown):
    #        await ctx.send(embed=discord.Embed(color=discord.Color.red(), timestamp=discord.utils.utcnow(), title="Slow Down!", description=f"This command has a cooldown! You may retry the command after ``{round(error.retry_after)}`` seconds."))







async def setup(bot):
    await bot.add_cog(Fun(bot))
