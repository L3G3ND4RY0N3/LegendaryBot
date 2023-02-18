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
        conf_embed = discord.Embed(color=discord.Color.blue())
        conf_embed.add_field(name="Slap!", value=f"<@{jura}> kriegt ne heftige Schelle!")
        conf_embed.set_footer(text=f"Verteilt durch {interaction.user}.")
        await interaction.response.send_message(embed=conf_embed)

    #Legendslap!
    @app_commands.command(name="slaplegend", description="Schlage L3G3ND")
    @app_commands.checks.has_permissions(administrator=True)
    async def slaplegend(self, interaction: discord.Interaction):
        legend = 247342650917650434
        conf_embed = discord.Embed(color=discord.Color.blue())
        conf_embed.add_field(name="Slap!", value=f"<@{legend}> kriegt ne heftige Schelle!")
        conf_embed.set_footer(text=f"Verteilt durch {interaction.user}.")
        await interaction.response.send_message(embed=conf_embed)

    #Hug a Person with Mention!
    @app_commands.command(name="hug", description="Give someone a hug!")
    @app_commands.describe(user = "Who do you want to hug?")
    async def hug(self, interaction: discord.Interaction, user: discord.Member):
        conf_embed = discord.Embed(color=discord.Color.green())
        conf_embed.add_field(name="Hugged!", value=f"{interaction.user.mention} gives {user.mention} a hug <3")
        conf_embed.set_footer(text=f"Verteilt durch {interaction.user}.")
        await interaction.response.send_message(embed=conf_embed)

    #Slap a Person with Mention!
    @app_commands.command(name="slap", description="Slap someone!")
    @app_commands.describe(user = "Who do you want to slap?")
    async def slap(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == 247342650917650434:
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!", value=f"{interaction.user.mention}, you lack the permission to slap L3G3ND! Nice try though.")
            conf_embed.set_footer(text=f"Attempted by {interaction.user}.")
        await interaction.response.send_message(embed=conf_embed)


    @slaplegend.error
    async def slaplegend_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!", value=f"{interaction.user}, you do not have the permissions to slap L3G3ND! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Slap(bot))