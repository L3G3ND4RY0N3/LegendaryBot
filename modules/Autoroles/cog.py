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

        roles = []
        role_ids = auto_role[str(member.guild.id)].keys()
        for key in role_ids:
            roles.append(member.guild.get_role(int(key)))
        
        await member.add_roles(*roles)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        with open("modules/Autoroles/json/autoroles.json", "r+") as f:
            auto_role = json.load(f)

            try:
                auto_role[str(role.guild.id)].pop(str(role.id))

                f.seek(0)
                f.truncate()
                json.dump(auto_role, f, indent=4)

            except KeyError:
                print("Deleted Role was not an autorole")


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


    ####################################################################################################################################
    ##################################################### Add Command ##################################################################
    ####################################################################################################################################

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
        conf_embed.add_field(name="Success!", value=f"{role.mention} has been added as an autorole for this server!")
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
        
        await interaction.response.send_message(embed=conf_embed)


    ####################################################################################################################################
    ################################################### Remove Command #################################################################
    ####################################################################################################################################


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
                await interaction.response.send_message(f"{role} is not assigned as an autorole!", ephemeral=True)          

        conf_embed = discord.Embed(color=discord.Color.red())
        conf_embed.add_field(name="Success!", value=f"The automatic role {role.mention} for this guild/server has been removed.")
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
        
        await interaction.response.send_message(embed=conf_embed)


    ####################################################################################################################################
    ##################################################### List Command #################################################################
    ####################################################################################################################################

    @app_commands.command(name="list_autorole", description="Lists the autoroles for this server, e.g. all roles that are assigned to a joining member!")
    @app_commands.checks.has_permissions(administrator=True)
    async def list_join_role(self, interaction: discord.Interaction):
        with open("modules/Autoroles/json/autoroles.json", "r") as f:
            auto_role = json.load(f)

            if str(interaction.guild.id) not in auto_role or list(auto_role[str(interaction.guild.id)].keys()) == []:
                conf_embed = discord.Embed(color=discord.Color.red())
                conf_embed.add_field(name="No Autroles!", value=f"This server has yet to add autoroles!")
                conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

                await interaction.response.send_message(embed=conf_embed)
            
            roles = []
            role_ids = auto_role[str(interaction.guild.id)].keys()
            for key in role_ids:
                roles.append(interaction.guild.get_role(int(key)))

            mention_list = [r.mention for r in roles]

            mention = ", ".join(mention_list)

            conf_embed = discord.Embed(color=discord.Color.blue())
            conf_embed.add_field(name="Autroles:", value=f"{mention}")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

            await interaction.response.send_message(embed=conf_embed)

    ####################################################################################################################################
    ################################################### Error Handeling ################################################################
    ####################################################################################################################################

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
            conf_embed.add_field(name="Failure!", value=f"{interaction.user.name}, you do not have the permissions to remove autoroles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    @list_join_role.error
    async def list_role_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!", value=f"{interaction.user.name}, you do not have the permissions to list autoroles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Autoroles(bot))