import discord
from discord.ext import commands
from discord import app_commands

class Slap(commands.Cog, name="Slaps"):
    def __innit__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        print("Slap.py is ready!")    

    #Juraslap!
    @app_commands.command(name="slapjura", description="Gib Jura eine Schelle, weil er das verdient hat!")
    async def slapjura(self, interaction: discord.Interaction):
        jura = 768786872184078357
        await interaction.response.send_message(f"{interaction.user.mention} gibt <@{jura}> eine krasse Schelle!")

    #Legendslap!
    @app_commands.command(name="slaplegend", description="Schlage L3G3ND")
    async def slaplegend(self, interaction: discord.Interaction):
        legend = 247342650917650434
        await interaction.response.send_message(f"{interaction.user.mention} gibt <@{legend}> eine krasse Schelle!")

    #Hug a Person with Mention!
    @app_commands.command(name="hug", description="Give someone a hug!")
    @app_commands.describe(user = "Who do you want to hug?")
    async def hug(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.send_message(f"{interaction.user.mention} gives {user.mention} a hug <3")

async def setup(bot):
    await bot.add_cog(Slap(bot))