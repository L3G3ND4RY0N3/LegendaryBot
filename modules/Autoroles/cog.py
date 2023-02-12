import discord
from discord.ext import commands
from discord import app_commands
import json

class Autoroles(commands.Cog, name="Autoroles"):
    def __innit__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        print("Autoroles.py is ready!")    

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open("modules/Autoroles/json/autoroles.json", "r") as f:
            auto_role = json.load(f)

        join_role = discord.utils.get(member.guild.roles, name=auto_role[str(member.guild.id)])
        
        await member.add_roles(join_role)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def joinrole(self, ctx, role: discord.Role):
        with open("modules/Autoroles/json/autoroles.json", "r") as f:
            auto_role = json.load(f)

        auto_role[str(ctx.guild.id)] = str(role.name)

        with open("modules/Autoroles/json/autoroles.json", "w") as f:
            json.dump(auto_role, f, indent=4)

        conf_embed = discord.Embed(color=discord.Color.green())
        conf_embed.add_field(name="Success!", value=f"The automatic role for this guild/server has been set to {role.mention}.")
        conf_embed.set_footer(text=f"Action taken by {ctx.author.name}.")
        
        await ctx.send(embed=conf_embed)

    @app_commands.command(name="add_autorole", description="Adds a role that is automatically assigned to a new member!")
    @app_commands.describe(role = "Select the role")
    async def add_join_role(self, interaction: discord.Interaction, role: discord.Role):
        with open("modules/Autoroles/json/autoroles.json", "r") as f:
            auto_role = json.load(f)

        auto_role[str(role.guild.id)] = str(role.name)

        with open("modules/Autoroles/json/autoroles.json", "w") as f:
            json.dump(auto_role, f, indent=4)

        conf_embed = discord.Embed(color=discord.Color.green())
        conf_embed.add_field(name="Success!", value=f"The automatic role for this guild/server has been set to {role.mention}.")
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
        
        await interaction.response.send_message(embed=conf_embed)

async def setup(bot):
    await bot.add_cog(Autoroles(bot))