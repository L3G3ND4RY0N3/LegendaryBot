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

    #adds the autorole to new members, so far only one role per server. 
    #TODO add more roles!
    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open("modules/Autoroles/json/autoroles.json", "r") as f:
            auto_role = json.load(f)

        roles = []
        role_ids = auto_role[str(member.guild.id)].keys()
        for key in role_ids:
            roles.append(member.guild.get_role(int(key)))

        #join_role = discord.utils.get(member.guild.roles, name=auto_role[str(member.guild.id)])
        
        await member.add_roles(*roles)

    #Commando to add new autorole with normal prefix eg. $joinrole "roleidhere" (lame)
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


    #Slash Command um eine neue Autorole hinzuzufügen :D
    @app_commands.command(name="add_autorole", description="Adds a role that is automatically assigned to a new member!")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role = "Select the role")
    async def add_join_role(self, interaction: discord.Interaction, role: discord.Role):
        with open("modules/Autoroles/json/autoroles.json", "r+") as f:
            auto_role = json.load(f)

            if str(role.guild.id) not in auto_role:
                auto_role[str(role.guild.id)] = {}

            auto_role[str(role.guild.id)].update({str(role.id): str(role.name)})
        
            f.seek(0)
       
            json.dump(auto_role, f, indent=4)

        conf_embed = discord.Embed(color=discord.Color.green())
        conf_embed.add_field(name="Success!", value=f"The automatic role for this guild/server has been set to {role.mention}.")
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
        
        await interaction.response.send_message(embed=conf_embed)


    #Slash Command to remove an Autorole :D
    @app_commands.command(name="remove_autorole", description="Removes the autorole that is automatically assigned to a new member!")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role = "Select the role to remove")
    async def remove_join_role(self, interaction: discord.Interaction, role: discord.Role):
        with open("modules/Autoroles/json/autoroles.json", "r+") as f:
            auto_role = json.load(f)

            try:
                auto_role[str(role.guild.id)].pop(str(role.id))

                f.seek(0)
                f.truncate()
                json.dump(auto_role, f, indent=4)

            except KeyError:
                await interaction.response.send_message("Rolle wurde nicht gefunden", ephemeral=True)          

        conf_embed = discord.Embed(color=discord.Color.red())
        conf_embed.add_field(name="Success!", value=f"The automatic role {role.mention} for this guild/server has been removed.")
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
        
        await interaction.response.send_message(embed=conf_embed)


    @add_join_role.error
    async def join_role_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!!", value=f"{interaction.user}, you do not have the permissions to add new autoroles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    @remove_join_role.error
    async def remove_role_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Success!", value=f"{interaction.user.name}, you do not have the permissions to aremove autoroles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Autoroles(bot))