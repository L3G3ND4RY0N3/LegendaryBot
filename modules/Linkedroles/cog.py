import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
from utils import jsonfunctions, settings
from utils.embeds import embedbuilder as emb
from utils.filepaths import LINKED_ROLES_FILE
from utils.structs.LinkedRoles import LinkedRoles
from constants.enums import LRRetCode
from time import sleep


logger=settings.logging.getLogger("discord")

class LinkedRolesBot(commands.Cog, name="Linked Roles"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.file_open = True
        try:
            if not LINKED_ROLES_FILE.exists():
                with open(LINKED_ROLES_FILE, "w") as f:
                    json.dump({}, f)
            else:
                with open(LINKED_ROLES_FILE, "r") as f:
                    data = json.load(f)
                    self.guild_linked_roles: dict[int, LinkedRoles] = {
                        int(guild_id): LinkedRoles(linked_roles_dict)
                        for guild_id, linked_roles_dict in data.items()
                    }
        except IOError:
            logger.error("Could not read or write linkedroles.json file!")
        self.file_open = False

    
    def write_json(self) -> None:
        """writes the serialized dict to the linked roles json file
        """
        while self.file_open:
            sleep(0.0001)
        
        serialized_dict: dict[int: dict[int, list[int]]] = {
            guild_id: lr.serialize() for guild_id, lr in self.guild_linked_roles.items()
            }
        
        self.file_open = True
        with open(LINKED_ROLES_FILE, "w") as f:
            json.dump(serialized_dict, f, indent=4)
        self.file_open = False

    #TODO: write check_all_members and check_all_roles

    def check_all_roles(self):
        for guild in self.bot.guilds:
            if (guild.id not in set(self.guild_linked_roles)
            or not self.guild_linked_roles[guild.id]
            ):
                continue
            guild_roles = set([role.id for role in guild.roles])
            guild_linked_roles = set(self.guild_linked_roles[guild.id]._linked_roles) | set(self.guild_linked_roles[guild.id]._reverse_linked_roles)
            dif = guild_linked_roles - guild_roles
            for role_id in dif:
                self.guild_linked_roles[guild.id].remove_role(role_id)

        self.write_json()
        return
    
    async def check_all_members(self):
        for guild in self.bot.guilds:
            if (guild.id not in set(self.guild_linked_roles)
            or not self.guild_linked_roles[guild.id]
            ):
                continue
            linked_roles = self.guild_linked_roles[guild.id]
            for member in guild.members:
                mem_roles = set(role.id for role in member.roles)
                updated_roleids = linked_roles.get_all_targets_for_reqs(*mem_roles)

                add_role_ids = updated_roleids - mem_roles
                remove_role_ids = mem_roles - updated_roleids

                if not add_role_ids and not remove_role_ids:
                    continue # do nothing if no relevant roles changed

                add_roles = [member.guild.get_role(rid) for rid in add_role_ids]
                remove_roles = [member.guild.get_role(rid) for rid in remove_role_ids]

                if add_role_ids:
                    try:
                        sleep(0.01) # to not trigger rate limit
                        await member.add_roles(*add_roles, atomic=False)
                    # if "forbidden" exception is thrown
                    except discord.errors.Forbidden:
                        logger.info(f"Bot is missing permission to add roles in {member.guild.name}")

                if remove_role_ids:
                    try:
                        sleep(0.01) # to not trigger rate limit
                        await member.remove_roles(*remove_roles, atomic=False)
                    except discord.Forbidden:
                        logger.info(
                            f"Bot is missing permission to manage roles for {member.name} in {member.guild.name}"
                        )
        return


    ###############################################################################################################
    ########################################### Listener (Events) #################################################
    ###############################################################################################################

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info("Linkedroles.py is ready!")
        self.check_all_roles()
        await self.check_all_members()

    # if a role in a guild gets deleted, the bot check if it was an linkedrole and deletes it from the list, else it creates a log entry

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        guild_id = role.guild.id

        if (guild_id not in set(self.guild_linked_roles)
        or not self.guild_linked_roles[guild_id]
        ):
            return
        
        self.guild_linked_roles[guild_id].remove_role(role.id)

        self.write_json()

        return


    # Adds the server to the json file, when the bot joins

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        self.guild_linked_roles[guild.id] = LinkedRoles()
        self.write_json()

    # Removes the server from the json file, when the bot gets yeeted

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if guild.id not in self.guild_linked_roles:
            return
        self.guild_linked_roles.pop(guild.id)
        self.write_json()


    # member update listener, to add linked roles, when a member gets assigned a new role or looses a required role
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        guild_id = before.guild.id

        # if not in server or no linked roles in server -> dont do anything
        if (
            guild_id not in self.guild_linked_roles
            or not self.guild_linked_roles[guild_id]
        ):
            return

        # if no roles added or removed, dont do anything
        if before.roles == after.roles:
            return

        linked_roles = self.guild_linked_roles[guild_id]

        after_roleids = set(r.id for r in after.roles)
        updated_roleids = linked_roles.get_all_targets_for_reqs(*after_roleids)

        add_role_ids = updated_roleids - after_roleids
        remove_role_ids = after_roleids - updated_roleids

        if not add_role_ids and not remove_role_ids:
            return # do nothing if no relevant roles changed

        add_roles = [before.guild.get_role(rid) for rid in add_role_ids]
        remove_roles = [before.guild.get_role(rid) for rid in remove_role_ids]

        if add_role_ids:
            try:
                await after.add_roles(*add_roles, atomic=False)
            # if "forbidden" exception is thrown
            except discord.errors.Forbidden:
                logger.info(f"Bot is missing permission to add roles in {after.guild.name}")

        if remove_role_ids:
            try:
                await after.remove_roles(*remove_roles, atomic=False)
            except discord.Forbidden:
                logger.info(
                    f"Bot is missing permission to manage roles for {after.name} in {after.guild.name}"
                )
            


    ###############################################################################################################
    ############################################## Commands #######################################################
    ###############################################################################################################

    ####################################################################################################################################
    ##################################################### Add Command ##################################################################
    ####################################################################################################################################

    #TODO: prevent circular links! e.g. role : linked_role, linked_role : role

    # Add command, takes a role, that is supposed to be added to a member, when they get another required linked_role
    # Gets stored in a json file with server_id = {role: [linked_role, linked_role2,...]}

    @app_commands.command(name="add_link_to_role", description="Adds role(s) that is automatically assigned when a certain role gets added to a member!")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        role = "Select the role to automatically add/remove",
        required_role="Select the required role"
        )
    async def add_linked_role(
        self, 
        interaction: discord.Interaction, 
        role: discord.Role, 
        required_role: discord.Role
        ):
        if role == required_role:
        
            await interaction.response.send_message(embed=emb.forbidden_embed(f"{required_role.mention} can not be a required role for {role.mention}, no circular logic please!"))
            return
        
        guild_id = role.guild.id
        if guild_id not in self.guild_linked_roles:
            self.guild_linked_roles[guild_id] = LinkedRoles()

        ret_code = self.guild_linked_roles[guild_id].add_link_to_target(role.id, required_role.id)

        if ret_code == LRRetCode.FAIL_CIRCULAR:
            emb.forbidden_embed(f"{required_role.mention} can not be a required role for {role.mention}, no circular logic please!")
        
            await interaction.response.send_message(embed=emb.forbidden_embed(f"{required_role.mention} can not be a required role for {role.mention}, no circular logic please!"))
            return
        
        self.write_json()
        await interaction.response.send_message(embed=emb.success_embed(f"{role.mention} will now be added/removed when a member is assigned/revoked {required_role.mention}!"))

    ####################################################################################################################################
    ################################################### Remove Command #################################################################
    ####################################################################################################################################


    # Remove command, takes a role, that is no longer supposed to be added to a member, when they get another required linked_role
    # Removes the role from the json file with server_id = {role: [linked_role, linked_role2,...]}, if the list of the role is empty, it gets dropped: server:id = {}

    @app_commands.command(name="remove_link_from_role", description="Removes the link from the role to the linked_role")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role = "Select the role to no longer automatically add/remove", required_role="Select the linked (required) role that should no longer be linked")
    async def remove_link_from_role(self, interaction: discord.Interaction, role: discord.Role, required_role: discord.Role):

        guild_id, role_id, required_role_id = role.guild.id, role.id, required_role.id

        if guild_id not in self.guild_linked_roles or not self.guild_linked_roles[guild_id]:
            await interaction.response.send_message(embed=emb.warn_embed(f"This server has no linked roles yet, no link to remove!"))
            return
        
        if role_id not in self.guild_linked_roles[guild_id]:
            await interaction.response.send_message(embed=emb.warn_embed(f"{role.mention} has no links yet!"))
            return

        if required_role_id not in self.guild_linked_roles[guild_id].get(role_id):
            await interaction.response.send_message(embed=emb.warn_embed(f"{role.mention} has no link to {required_role.mention}!"))
            return

        self.guild_linked_roles[guild_id].remove_link_from_target(role_id, required_role_id)
        self.write_json()
            
        await interaction.response.send_message(embed=emb.success_embed(f"{role.mention} will no longer be added/removed when a member is assigned/revoked {required_role.mention}!"))


    ####################################################################################################################################
    ################################################# Remove All Command ###############################################################
    ####################################################################################################################################


    # Remove command, takes a role, that is no longer supposed to be added to a member, when they get another required linked_role
    # Removes the role from the json file with server_id = {role: [linked_role, linked_role2,...]}, if the list of the role is empty, it gets dropped: server:id = {}

    @app_commands.command(name="remove_all_links_from_role", description="Removes the link from the role to the linked_role")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role = "Select the role to no longer automatically add/remove")
    async def remove_all_links_from_role(self, interaction: discord.Interaction, role: discord.Role):
        guild_id, role_id = role.guild.id, role.id

        if guild_id not in self.guild_linked_roles or not self.guild_linked_roles[guild_id]:
            await interaction.response.send_message(embed=emb.warn_embed(f"This server has no linked roles yet, no link to remove!"))
            return
        
        if role_id not in self.guild_linked_roles[guild_id]:
            await interaction.response.send_message(embed=emb.warn_embed(f"{role.mention} has no links yet!"))
            return

        self.guild_linked_roles[guild_id].remove_link_from_target(role_id)
        self.write_json()
            
        await interaction.response.send_message(embed=emb.success_embed(f"{role.mention} is no longer a linked role!"))

    ####################################################################################################################################
    ##################################################### List Command #################################################################
    ####################################################################################################################################


    # list command, that lists all roles with the links

    @app_commands.command(name="list_linked_roles", description="Lists the roles and their links for this server!")
    @app_commands.checks.has_permissions(administrator=True)
    async def list_linked_roles(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id not in self.guild_linked_roles or not self.guild_linked_roles[guild_id]:
            await interaction.response.send_message(embed=emb.warn_embed(f"Server has no linked roles yet!"))
            return

        linked_roles = self.guild_linked_roles[guild_id]
        field = "**Role: Requirements** \n"

        for role_id, links in linked_roles.serialize().items():
            role = interaction.guild.get_role(role_id)
            field += f"{role.mention}"
            field += "**:** "
            for link in links:
                l_r = interaction.guild.get_role(link)
                field += f"{l_r.mention}"
                field += "**,** "
            field += "\n"

        conf_embed = discord.Embed(color=discord.Color.blue())
        conf_embed.add_field(name="`🔗`**Links:**", value=f"{field}")
        conf_embed.set_footer(text=f"Action taken by {interaction.user}.")

        await interaction.response.send_message(embed=conf_embed)

        
    ###############################################################################################################
    ################################################ Errors #######################################################
    ###############################################################################################################



    @add_linked_role.error
    async def linked_role_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌`**Failure!**", value=f"{interaction.user}, you do not have the permissions to add new links to roles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    @remove_link_from_role.error
    async def remove_linked_role_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌`**Failure!**", value=f"{interaction.user.name}, you do not have the permissions to remove linked roles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    @remove_all_links_from_role.error
    async def remove_linked_role_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌`**Failure!**", value=f"{interaction.user.name}, you do not have the permissions to remove linked roles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

    @list_linked_roles.error
    async def list_linked_roles_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            conf_embed = discord.Embed(color=discord.Color.red())
            conf_embed.add_field(name="`❌`**Failure!**", value=f"{interaction.user.name}, you do not have the permissions to list linked roles! You need administrator permissions!")
            conf_embed.set_footer(text=f"Action attempted by {interaction.user}.")
            await interaction.response.send_message(embed=conf_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(LinkedRolesBot(bot))