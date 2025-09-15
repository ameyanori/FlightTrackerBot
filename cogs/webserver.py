import aiohttp_cors
from aiohttp import web
import discord
from discord.ext import commands, tasks
import datetime
from datetime import timedelta

class Webserver(commands.Cog):
    """All commands dealing with the vote tracking system on top.gg"""
    def __init__(self, bot):
        self.bot = bot
        
    async def webserver(self):
        routes = web.RouteTableDef()

        @routes.get('/stats')
        async def handler(request):
            channels = []
            for guild in self.bot.guilds:
                for channel in guild.channels:
                    channels.append(channel)
            return web.json_response({'guilds' : len(self.bot.guilds),  'channels' : len(channels)})

        @routes.get('/user/guilds')
        async def handler1(request):
            id = int(request.rel_url.query['id'])
            guilds = {}
            for guild in self.bot.guilds:
                member = guild.get_member(int(id))
                if member == None:
                    pass
                elif member.guild_permissions.administrator == True:
                    guilds[guild.name] = guild.id
            return web.json_response(guilds)


        app = web.Application()
        app.add_routes(routes)
        cors = aiohttp_cors.setup(app)

#        resource = cors.add(app.router.add_resource('/stats'))
#        resource1 = cors.add(app.router.add_resource('/user/guilds', handler))

        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            )
        })

# Configure CORS on all routes.
        for route in list(app.router.routes()):
            cors.add(route)
        #route = cors.add(
        #    app, {
        #        "*": aiohttp_cors.ResourceOptions(
        #            allow_credentials=True,
        #            expose_headers=("X-Custom-Server-Header",),
        #            allow_headers=("X-Requested-With", "Content-Type"),
        #            max_age=3600,
       #         )
       #     }

        #)
        runner = web.AppRunner(app)
        await runner.setup()
        self.site = web.TCPSite(runner, '0.0.0.0', 5000)
        await self.bot.wait_until_ready()
        await self.site.start()

    def __unload(self):
        asyncio.ensure_future(self.site.stop())


async def setup(bot):
    wb = Webserver(bot)
    await bot.add_cog(wb)
    bot.loop.create_task(wb.webserver())
                

