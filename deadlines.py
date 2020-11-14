import discord
from discord.ext import commands


class Deadlines(commands.Cog):
    def __init__(self):
        pass

    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello!')
