import discord
from discord.ext import commands
import datetime
from datetime import date
import regex as re
import os
import json

def is_owner():
    def predicate(ctx):
        if ctx.author.id == 752706993017454654:
            return True
        else:
            return False
    return commands.check(predicate)
    
class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    """These commands are meant for the owner only.."""
    def __init__(self, bot):
        self.bot = bot

   
    @commands.group()
    @commands.is_owner()
    async def dev(self, ctx):
        return
        



    @dev.command()
    @commands.is_owner()
    async def reboot(self, ctx):
        """This is a bot owner only command."""
        await ctx.send(':gear: Rebooting now. :gear:')
        await self.bot.close()

    @dev.command()
    @commands.is_owner()
    async def presence(self, ctx, *, presence):
        """This is a bot owner only command."""
        await self.bot.change_presence(activity=discord.Game(name=presence))
        await ctx.send(':white_check_mark: Changed the presence!')


    @dev.command()
    @commands.is_owner() 
    async def reload(self, ctx, extension):
        """This is a bot owner only command."""
        await self.bot.reload_extension(f'cogs.{extension}')
        await self.bot.tree.sync()
        await ctx.send(f'Reloaded {extension}.')
    
    @reload.error
    async def reload_error(self, ctx, error):
        embed = discord.Embed(color=discord.Color.red(), timestamp=datetime.datetime.utcnow(), title='ERROR', description=str(error))
        await ctx.send(embed=embed)




    @dev.command() 
    @commands.is_owner()
    async def reloadall(self, ctx):
        """This is a bot owner only command."""
        for file in os.curdir: 
            if file.endswith(".py"):
                name = file[:-3]
                await self.bot.reload_extension(f'cogs.{name}')
                await self.bot.tree.sync()
                await ctx.send(f'Reloaded {name}.')


    @reloadall.error
    async def reloadall_error(self, ctx, error):
        embed = discord.Embed(color=discord.Color.red(), timestamp=datetime.datetime.utcnow(), title='ERROR', description=str(error))
        await ctx.send(embed=embed)






async def setup(bot):
    await bot.add_cog(Owner(bot))
