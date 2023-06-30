import discord
from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog, name="Ping"):
    def __init__(self, bot):
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

    @app_commands.command(name="hello", description="The Bot says hello to you")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello {interaction.user.mention}! This is my first slash (/) command.")

    #Slash Command Syntaxin a Cog!
    @app_commands.command(name="say", description="Let the bot say something")
    @app_commands.describe(resp = "What do you want me to say?")
    async def say(self, interaction: discord.Interaction, resp: str):
        await interaction.response.send_message(f"{interaction.user.name} said: `{resp}`")

async def setup(bot):
    await bot.add_cog(Ping(bot))