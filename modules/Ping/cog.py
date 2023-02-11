import discord
from discord.ext import commands

class Ping(commands.Cog, name = "Ping"):
    def __innit__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ping.py is ready!")    

    @commands.command()
    async def ping(self, ctx: commands.Context):
        bot_latency = round(self.bot.latency * 1000)

        await ctx.send(f"Football.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))