import discord
from discord.ext import commands
from discord import app_commands
import json
from utils import jsonfunctions, settings
from typing import List


logger=settings.logging.getLogger("discord")

class Linkedroles(commands.Cog, name="Linked Roles"):
    def __init__(self, bot):
        self.bot = bot

    ###############################################################################################################
    ########################################### Listener (Events) #################################################
    ###############################################################################################################

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info("Linkedroles.py is ready!")

    # if a role in a guild gets deleted, the bot check if it was an linkedrole and deletes it from the list, else it creates a log entry

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        with open("modules/Linkedroles/json/linkedroles.json", "r+") as f: 
            data = json.load(f)
  
            guild_id, role_id= str(role.guild.id), str(role.id)

            if guild_id not in data or not data[guild_id]:
                data[guild_id] = {}
                logger.info(f"{role.guild.name} did not have any linked roles yet!")
                return

            if role_id in list(data[guild_id].keys()):
                data[guild_id].pop(role_id)
                logger.info(f"Removed {role.name} in {role.guild.name} and purged links from json")

            linked_roles_lists = list(data[guild_id].values())

            for l_r_list in linked_roles_lists:
                if role_id in l_r_list:
                    l_r_list.remove(role_id)
                    logger.info(f"Removed {role.name} as required (linked) role in {role.guild.name}")

            for key in list(data[guild_id].keys()):
                if data[guild_id][key] == []:
                    data[guild_id].pop(key)
  
            f.seek(0)
            f.truncate()
       
            json.dump(data, f, indent=4)

            return


    # Adds the server to the json file, when the bot joins

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        with open("modules/Linkedroles/json/linkedroles.json", "r+") as f:
            data = json.load(f)
        
            data[str(guild.id)] = {}

            f.seek(0)
                        
            json.dump(data, f, indent=4)

    # Removes the server from the json file, when the bot gets yeeted

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        with open("modules/Linkedroles/json/linkedroles.json", "r") as f:
            data = json.load(f)
        
        data.pop(str(guild.id))

        with open("modules/Linkedroles/json/linkedroles.json", "w") as f:
            json.dump(data, f, indent=4)


    # member update listener, to add linked roles, when a member gets assigned a new role or looses a required role
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        with open("modules/Linkedroles/json/linkedroles.json", "r") as f:
            data = json.load(f)

        guild = str(before.guild.id)

        # if no no server, dont do jack
        if guild not in data:
            return
        
        # if no linked roles in server, its time to stop
        if data[guild] == {}:
            return
        
        old_roles = before.roles
        new_roles = after.roles
        
        # if no roles added or removed, dont do anything
        if old_roles == new_roles:
            return
        
        # if roles where added
        if len(new_roles) > len(old_roles):
            added_roles = []
            
            for role in new_roles:
                if role not in old_roles:
                    added_roles.append(role)

            added_roles_ids = [str(role.id) for role in added_roles]
            
            required_role_list = list(data[guild].values())

            # iterate over added_roles and check in which list of required roles they reside 
            for added_role_id in added_roles_ids:
                #checks if the added role is in any of the roles requirements list
                if any(added_role_id in sl for sl in required_role_list):
                    # role ids to add
                    add = [r for r, lr in data[guild].items() if added_role_id in lr]
                    # list of roles to add to member
                    add_r = []
                    for r in add:
                        nr = before.guild.get_role(int(r))
                        add_r.append(nr)
                    # try adding the role
                    try:
                        await after.add_roles(*add_r)
                    except discord.errors.Forbidden:
                        logger.info(f"Bot is missing permission to add roles in {after.guild.name}")
                        # grab all text channels
                        channels = after.guild.text_channels
                        # bot as member of guild
                        botmem = after.guild.me
                        
                        #find channel to complain to
                        for channel in channels:
                            if channel.permissions_for(botmem).send_messages:
                                if after.top_role >= botmem.top_role:
                                    try:
                                        await channel.send(f"{after.mention} top role is higher the my role, unable to add {nr.mention}!")
                                        return
                                    except discord.errors.Forbidden:
                                        logger.info(f"Bot is missing permission to send messages in {after.guild.name}")
                                        return

                                try:
                                    await channel.send(f"I am missing permission to add/remove roles for {after.mention}!")
                                    return
                                except discord.errors.Forbidden:
                                    logger.info(f"Bot is missing permission to send messages in {after.guild.name}")
                                    return
                            else:
                                logger.info(f"Bot is unable to send messages in {after.guild.name}")

        # if roles were removed
        else:
            removed_roles = []

            for role in old_roles:
                if role not in new_roles:
                    removed_roles.append(role)

            removed_roles_ids = [str(role.id) for role in removed_roles]

            remaining_roles_ids = [str(role.id) for role in after.roles]

            required_role_list = list(data[guild].values())

            for removed_roles_id in removed_roles_ids:
                #checks if the removed role is in any of the roles requirements list
                if any(removed_roles_id in sl for sl in required_role_list):
                    # role ids to remove
                    remove = [r for r, lr in data[guild].items() if removed_roles_id in lr]
                    # roles to remove
                    remove_r = []
                    for r in remove:
                        nr = before.guild.get_role(int(r))
                        remove_r.append(nr)
                    # try removing the role
                    try:
                        await after.remove_roles(*remove_r)
                    except discord.errors.Forbidden:
                        logger.info(f"Bot is missing permission to manage roles for {after.name} in {after.guild.name}")
                        # grab all text channels
                        channels = after.guild.text_channels
                        # bot as member of guild
                        botmem = after.guild.me

                        # find channel to complain
                        for channel in channels:
                            if channel.permissions_for(botmem).send_messages:
                                if after.top_role >= botmem.top_role:
                                    try:
                                        await channel.send(f"{after.mention} top role is higher the my role, unable to remove {nr.mention}!")
                                        return
                                    except discord.errors.Forbidden:
                                        logger.info(f"Bot is missing permission to send messages in {after.guild.name}")
                                        return

                                try:
                                    await channel.send(f"I am missing permission to add/remove roles for {after.mention}!")
                                    return
                                except discord.errors.Forbidden:
                                    logger.info(f"Bot is missing permission to send messages in {after.guild.name}")
                                    return
                            else:
                                logger.info(f"Bot is unable to send messages in {after.guild.name}")

            # readding roles if member still has some required roles left TODO: fix, to many api calls?!
            for remaining_role_id in remaining_roles_ids:
                if any(remaining_role_id in sl for sl in required_role_list):
                    add = [r for r, lr in data[guild].items() if remaining_role_id in lr]
                    add_r = []
                    for r in add:
                        nr = before.guild.get_role(int(r))
                        add_r.append(nr)
                    # try readding the role
                    try:
                        await after.add_roles(*add_r)
                    except discord.errors.Forbidden:
                        logger.info(f"Bot is missing permission to add roles in {after.guild.name}")
            


    ###############################################################################################################
    ############################################## Commands #######################################################
    ###############################################################################################################

    ####################################################################################################################################
    ##################################################### Add Command ##################################################################
    ####################################################################################################################################

    # Add command, takes a role, that is supposed to be added to a member, when they get another required linked_role
    # Gets stored in a json file with server_id = {role: [linked_role, linked_role2,...]}

    @app_commands.command(name="add_link_to_role", description="Adds role(s) that is automatically assigned when a certain role gets added to a member!")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role = "Select the role to automatically add/remove", linked_role="Select the linked (required) role")
    async def add_linked_role(self, interaction: discord.Interaction, role: discord.Role, linked_role: discord.Role):
        if role == linked_role:
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="FORBIDDEN!", value=f"{linked_role.mention} can not be a required role for {role.mention}, no circular logic please!")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
        
            await interaction.response.send_message(embed=conf_embed)
            return

        retcode = 0
        retcode = jsonfunctions.update_linkedrole("modules/Autoroles/json/autoroles.json",role.guild.id, role.id, linked_role.id, retcode)

        if retcode > 0:
            conf_embed = discord.Embed(color=discord.Color.yellow())
            conf_embed.add_field(name="MISTAKE!", value=f"{linked_role.mention} is already a required role for {role.mention} for this server!")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
        
            await interaction.response.send_message(embed=conf_embed)
            return

        conf_embed = discord.Embed(color=discord.Color.green())
        conf_embed.add_field(name="Success!", value=f"{role.mention} will now be added/removed when a member is assigned/revoked {linked_role.mention}!")
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
        
        await interaction.response.send_message(embed=conf_embed)

    ####################################################################################################################################
    ################################################### Remove Command #################################################################
    ####################################################################################################################################


    # Remove command, takes a role, that is no longer supposed to be added to a member, when they get another required linked_role
    # Removes the role from the json file with server_id = {role: [linked_role, linked_role2,...]}, if the list of the role is empty, it gets dropped: server:id = {}

    @app_commands.command(name="remove_link_from_role", description="Removes the link from the role to the linked_role")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role = "Select the role to no longer automatically add/remove", linked_role="Select the linked (required) role that should no longer be linked")
    async def remove_linked_role(self, interaction: discord.Interaction, role: discord.Role, linked_role: discord.Role):
        with open("modules/Linkedroles/json/linkedroles.json", "r+") as f: 
            data = json.load(f)

            guild_id, role_id, linked_role_id = str(role.guild.id), str(role.id), str(linked_role.id)

            if guild_id not in data or not data[guild_id]:
                data[guild_id] = {}

                conf_embed = discord.Embed(color=discord.Color.yellow())
                conf_embed.add_field(name="No linked Roles on server!", value=f"This server has no linked roles yet, no link to remove!")
                conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
            
                await interaction.response.send_message(embed=conf_embed)
                return
            
            if role_id not in data[guild_id]:
                conf_embed = discord.Embed(color=discord.Color.yellow())
                conf_embed.add_field(name=f"Not a linked Role!", value=f"{role.mention} has no links yet!")
                conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
            
                await interaction.response.send_message(embed=conf_embed)
                return    

            if linked_role_id in data[guild_id][role_id]:
                if len(data[guild_id][role_id]) == 1:
                    #data[guild_id][role_id].clear()
                    data[guild_id].pop(role_id)
                else:
                    data[guild_id][role_id].remove(linked_role_id)

            else:
                conf_embed = discord.Embed(color=discord.Color.yellow())
                conf_embed.add_field(name=f"No link between roles!", value=f"{role.mention} has no link to {linked_role.mention}!")
                conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
            
                await interaction.response.send_message(embed=conf_embed)
                return 
        
            f.seek(0)
            f.truncate()
       
            json.dump(data, f, indent=4)

            conf_embed = discord.Embed(color=discord.Color.green())
            conf_embed.add_field(name="Link removed!", value=f"{role.mention} will no longer be added/removed when a member is assigned/revoked {linked_role.mention}!")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")
            
            await interaction.response.send_message(embed=conf_embed)

    ####################################################################################################################################
    ##################################################### List Command #################################################################
    ####################################################################################################################################


    # list command, that lists all roles with the links

    @app_commands.command(name="list_linked_roles", description="Lists the roles and their links for this server!")
    @app_commands.checks.has_permissions(administrator=True)
    async def list_linked_roles(self, interaction: discord.Interaction):
        with open("modules/Linkedroles/json/linkedroles.json", "r") as f:
            data = json.load(f)

            guild_id = str(interaction.guild.id)

            if guild_id not in data or list(data[guild_id].keys()) == []:
                conf_embed = discord.Embed(color=discord.Color.red())
                conf_embed.add_field(name="No links between roles!", value=f"This server has yet to add links to roles!")
                conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

                await interaction.response.send_message(embed=conf_embed)

            field = "**Role: Requirements** \n"

            for role_id, links in data[guild_id].items():
                role = interaction.guild.get_role(int(role_id))
                field += f"{role.mention}"
                field += "**:** "
                for link in links:
                    l_r = interaction.guild.get_role(int(link))
                    field += f"{l_r.mention}"
                    field += "**,** "
                field += "\n"


            #mention = ", ".join(mention_role_list)

            conf_embed = discord.Embed(color=discord.Color.blue())
            conf_embed.add_field(name="Links:", value=f"{field}")
            conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

            await interaction.response.send_message(embed=conf_embed)

        
    ###############################################################################################################
    ################################################ Errors #######################################################
    ###############################################################################################################



    @add_linked_role.error
    async def linked_role_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!!", value=f"{interaction.user}, you do not have the permissions to add new links to roles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    @remove_linked_role.error
    async def remove_linked_role_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!", value=f"{interaction.user.name}, you do not have the permissions to remove linked roles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    @list_linked_roles.error
    async def list_linked_roles_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="Failure!", value=f"{interaction.user.name}, you do not have the permissions to list linked roles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Linkedroles(bot))