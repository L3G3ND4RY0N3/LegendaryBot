import discord
from discord.ext import commands
from discord import app_commands
import json

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

        with open("modules/Slap/json/jura.json", "r+") as f:
            jura_data = json.load(f)
            if str(interaction.guild.id) not in jura_data:
                jura_data[str(interaction.guild.id)] = 0

            jura_data[str(interaction.guild.id)] = jura_data[str(interaction.guild.id)] + 1
            amount = jura_data[str(interaction.guild.id)]

            f.seek(0)
       
            json.dump(jura_data, f, indent=4)

        conf_embed = discord.Embed(color=discord.Color.blue())
        conf_embed.add_field(name="Slap!", value=f"<@{jura}> kriegt ne heftige Schelle! Das ist bereits die {amount}. Schelle, die er sich verdient hat!")
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

        with open("modules/Slap/json/hugs.json", "r+") as f:
            hug_data = json.load(f)

            if str(interaction.guild.id) not in hug_data:
                hug_data[str(interaction.guild.id)] = {}

            if str(user.id) not in hug_data[str(interaction.guild.id)]:
                hug_data[str(interaction.guild.id)].update({str(user.id): 0})
            hug_data[str(interaction.guild.id)][str(user.id)] = hug_data[str(interaction.guild.id)][str(user.id)] + 1
            amount = hug_data[str(interaction.guild.id)][str(user.id)]
        
            f.seek(0)
       
            json.dump(hug_data, f, indent=4)

        conf_embed = discord.Embed(color=discord.Color.green())
        conf_embed.add_field(name="Hugged!", value=f"{interaction.user.mention} gives {user.mention} a hug <3 This is the {amount}. hug given to {user.name}!")
        conf_embed.set_footer(text=f"Verteilt durch {interaction.user}.")
        await interaction.response.send_message(embed=conf_embed)

    #Pat a Person with Mention!
    @app_commands.command(name="pat", description="Pat someone!")
    @app_commands.describe(user = "Who do you want to pat?")
    async def pat(self, interaction: discord.Interaction, user: discord.Member):

        with open("modules/Slap/json/pats.json", "r+") as f:
            pat_data = json.load(f)

            if str(interaction.guild.id) not in pat_data:
                pat_data[str(interaction.guild.id)] = {}

            if str(user.id) not in pat_data[str(interaction.guild.id)]:
                pat_data[str(interaction.guild.id)].update({str(user.id): 0})
            pat_data[str(interaction.guild.id)][str(user.id)] = pat_data[str(interaction.guild.id)][str(user.id)] + 1
            amount = pat_data[str(interaction.guild.id)][str(user.id)]
        
            f.seek(0)
       
            json.dump(pat_data, f, indent=4)

        conf_embed = discord.Embed(color=discord.Color.green())
        conf_embed.add_field(name="Pat!", value=f"{interaction.user.mention} pats {user.mention} because they like them! <3 This is the {amount}. pat given to {user.name}!")
        conf_embed.set_footer(text=f"Patted by {interaction.user}.")
        await interaction.response.send_message(embed=conf_embed)

    #Slap a Person with Mention!
    @app_commands.command(name="slap", description="Slap someone!")
    @app_commands.describe(user = "Who do you want to slap?")
    async def slap(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == 247342650917650434 and interaction.user.id != 247342650917650434:
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!", value=f"{interaction.user.mention}, you lack the permission to slap L3G3ND! Nice try though.")
            conf_embed.set_footer(text=f"Attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

        with open("modules/Slap/json/slaps.json", "r+") as f:
            slap_data = json.load(f)

            if str(interaction.guild.id) not in slap_data:
                slap_data[str(interaction.guild.id)] = {}

            if str(user.id) not in slap_data[str(interaction.guild.id)]:
                slap_data[str(interaction.guild.id)].update({str(user.id): 0})
            slap_data[str(interaction.guild.id)][str(user.id)] = slap_data[str(interaction.guild.id)][str(user.id)] + 1
            amount = slap_data[str(interaction.guild.id)][str(user.id)]
        
            f.seek(0)
       
            json.dump(slap_data, f, indent=4)
        
        conf_embed = discord.Embed(color=discord.Color.blue())
        conf_embed.add_field(name="Slap!", value=f"{user.mention} was slapped by {interaction.user.mention}! This is the {amount}. slap!")
        conf_embed.set_footer(text=f"Slap issued by {interaction.user}.")
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