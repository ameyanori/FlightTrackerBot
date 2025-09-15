import discord
from typing import Any, Dict, List, Optional, Union
from discord.ext import commands, menus
from discord import app_commands
from discord.app_commands import Choice
from discord.ext.commands.cooldowns import BucketType

class GroupHelpPageSource(menus.ListPageSource):
    def __init__(self, group: Union[commands.Group, commands.Cog], commands: List[commands.Command], *, prefix: str):
        super().__init__(entries=commands, per_page=6)
        self.group = group
        self.prefix = prefix
        self.title = f'{self.group.qualified_name} Commands'
        self.description = self.group.description

    async def format_page(self, menu, commands):
        embed = discord.Embed(title=self.title, description=self.description, colour=discord.Colour(0xA8B9CD))

        for command in commands:
            if command.qualified_name in ['plot']:
                pass
            signature = f'{command.qualified_name} {command.signature}'
            embed.add_field(name=signature, value=command.short_doc or 'No help given...', inline=False)

        maximum = self.get_max_pages()
        if maximum > 1:
            embed.set_author(name=f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} commands)')

        embed.set_footer(text=f'Use "{self.prefix}help command" for more info on a command.')
        return embed


class Dropdown(discord.ui.Select):
    def __init__(self, ctx):
        super().__init__(
            placeholder='Select a category...',
            min_values=1,
            max_values=1,
            row=0,
        )
        options=[]
        self.ctx = ctx
        
        self.add_option(label="Airportle", value="Airportle", description=f"Help with the {self.ctx.clean_prefix}airportle command of the bot!")
        for cog in ctx.bot.cogs:
            if cog in ['Jishaku', 'Owner', 'Webserver']:
                pass
            else:
                self.add_option(label=cog, value=cog, description=ctx.bot.cogs[cog].description)
        

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        value = self.values[0]
        if value == "Airportle":
            embed = discord.Embed(color=discord.Color.blurple())
            embed.set_author(name="Airportle Help")
            embed.add_field(name="What is airportle?", value="Airportle is based on the online word game, [Wordle](https://www.nytimes.com/games/wordle/index.html)!")
            embed.add_field(name="How do I play?", value="Guess the airport IATA code in 6 tries. After each guess, the color of the tiles will change to show how close your guess was to the IATA code.\n<:1f1f8:941228571286970399><:1f1e8:941170970578812999><:1f1eb:941170970654294066>\nThe letter S is in the IATA code and in the correct spot.\n<:1f1e7:941170970159353887><:1f1e8:941170970578812999><:1f1f3:941171159167299656> \nThe letter N is in the IATA code but in the wrong spot.\n<:1f1f1:941170970608140378><:1f1e6:941170970146779218><:1f1fd:941170970515865680>\nThe letter A is not in the IATA code in any spot.",inline=False)
            await interaction.response.edit_message(embed=embed, view = self.view)
            return
        cog = self.ctx.bot.cogs[value]
        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_author(name=f'{cog.qualified_name} Help')
        embed.add_field(name='Key:', value='```[] = optional argument\n<> = required argument\nDo not type [] or <> during a command.```')

        for thing in cog.get_commands():
                embed.add_field(name=thing.qualified_name, value=f'Description: {thing.help}\nUsage: {self.ctx.clean_prefix}{thing.qualified_name} {thing.signature}', inline=False)

        source = GroupHelpPageSource(cog, cog.get_commands(), prefix=self.ctx.clean_prefix)
        await interaction.response.edit_message(embed=embed, view = self.view)

class DropdownView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(ctx))

class MyHelpCommand(commands.HelpCommand):
        # This function triggers when somone type `<prefix>help`
    async def send_bot_help(self, mapping):
            view = DropdownView(self.context)
            ctx = self.context
            embed = discord.Embed(color=discord.Color.blurple())
            embed.add_field(name='To get more info on the modules:', value=f'Choose the module you wish to get more information on from the following dropdown!')
            embed.set_author(name='FlightTracker Help')
            embed.add_field(name="Who are we?", value="FlightTracker was made by a team of aviation enthusiasts who noticed the lack of a free, accurate, and reliable discord bot for tracking aircrafts.", inline=False)
            embed.add_field(name="Development Credits:", value="Head Developer: nahhhhh#2920\nTesters: Around the World#0666 and Chelsea#1160", inline=False)
            embed.add_field(name="API Credits:", value="WIP", inline=False)
            embed.add_field(name="Support the Bot:", value="Patreon: https://www.patreon.com/flighttracker\nTop.gg: https://top.gg/bot/930250495732375623\nSupport Server: https://discord.gg/vB9V5QXDs9", inline=False)
            await ctx.send(embed=embed, view=view)
    
    # This function triggers when someone type `<prefix>help <cog>`
    async def send_cog_help(self, cog):
            ctx = self.context
            if cog == 'jishaku':
                    return
            else:
                    embed = discord.Embed(color=discord.Color.blurple())
                    embed.set_author(name=f'{cog.qualified_name} Help')
                    embed.add_field(name='Key:', value='```[] = optional argument\n<> = required argument\nDo not type [] or <> during a command.```')
 
                    for thing in cog.get_commands():
                            embed.add_field(name=thing.qualified_name, value=f'Description: {thing.help}\nUsage: {ctx.clean_prefix}{thing.qualified_name} {thing.signature}', inline=False)
                    await ctx.send(embed=embed)
            # Do what you want to do here
    
    async def send_command_help(self, command):
            ctx = self.context
            embed = discord.Embed(color=discord.Color.blue())
            embed.set_author(name=f'{command.qualified_name} Help')
            embed.add_field(name=f'Usage: {ctx.clean_prefix}{command.qualified_name} {command.signature}', value=f'Description: {command.help}', inline=False)

            embed.add_field(name='Key:', value='```[] = optional argument\n<> = required argument\nDo not type [] or <> during a command.```')
            await ctx.send(embed=embed)

    async def send_group_help(self, group):
            ctx = self.context
            embed = discord.Embed(color=discord.Color.dark_purple())
            embed.set_author(name=f'{group.qualified_name} Help')
            for thing in group.commands:
                embed.add_field(name=thing.qualified_name, value=f'Description: {thing.help}\nUsage: {ctx.clean_prefix}{thing.qualified_name} {thing.signature}', inline=False)
            await ctx.send(embed=embed)
            
                
class Help(commands.Cog):
    """Shows this command, allows for in-depth explanations."""
    def __init__(self, bot):
        self.bot = bot
        
        # Storing main help command in a variable
        self.bot._original_help_command = bot.help_command
        
        # Assiginig new help command to bot help command
        bot.help_command = MyHelpCommand()
        
        # Setting this cog as help command cog
        bot.help_command.cog = self
        
        # Event triggers when this cog unloads
        
    @app_commands.command()
    async def help(self, ctx: discord.Interaction):
        """Sends Help Command"""
        c = await self.bot.get_context(ctx)
        await c.send_help()
        
        
    
    def cog_unload(self):
                
        # Setting help command to the previous help command so if this cog unloads the help command restores to previous
        self.bot.help_command = self.bot._original_help_command

async def setup(bot):
        await bot.add_cog(Help(bot))



