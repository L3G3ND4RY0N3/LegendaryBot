import discord
from discord.ext import commands

class Ping(commands.Cog, name="Ping"):
    def __innit__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        print("Ping.py is ready!")    

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Ping {ctx.author.mention}!")

    @commands.command()
    async def hi(self, ctx):
        await ctx.send(f"Hello there {ctx.author.mention}")

async def setup(bot):
    await bot.add_cog(Ping(bot))