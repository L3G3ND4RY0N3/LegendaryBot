import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import create_reaction_role_setup_embed
from utils.views.ReactionRoleSetupView import ReactionRoleSetupSetupView
from utils import settings
from utils.structs import RoleMemberMapping
from utils.dbhelpers.reaction_roles_db_helpers import get_reaction_role_by_emoji

logger=settings.logging.getLogger("discord")

class ReactionRoles(commands.Cog, name="ReactionRoles"):
    def __init__(self, bot: discord.Client):
        self.bot = bot

#region events
####################### events #######################################################################################
    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!") 

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        mapping = await self.check_payload_guild(payload)
        if mapping:
            try:
                await mapping.member.add_roles(mapping.role, reason="Reaction Role Added")
            except discord.Forbidden:
                logger.warning(f"Failed to add role {mapping.role.name} to user {mapping.member.display_name} in guild {mapping.member.guild.name} via reaction role due to missing permissions.")
                return
            logger.info(f"Added role {mapping.role.name} to user {mapping.member.display_name} in guild {mapping.member.guild.name} via reaction role.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        mapping = await self.check_payload_guild(payload)
        if mapping:
            try:
                await mapping.member.remove_roles(mapping.role, reason="Reaction Role Removed")
            except discord.Forbidden:
                logger.warning(f"Failed to remove role {mapping.role.name} from user {mapping.member.display_name} in guild {mapping.member.guild.name} via reaction role due to missing permissions.")
                return
            logger.info(f"Removed role {mapping.role.name} from user {mapping.member.display_name} in guild {mapping.member.guild.name} via reaction role.")
#endregion

#region commands
################################ commands #######################################################################################
    @app_commands.command(name="reaction_roles_setup", description="Set up reaction roles for this guild.")
    @app_commands.describe(channel="The channel where the reaction roles message will be sent.")
    @app_commands.checks.has_permissions(administrator=True)
    async def reaction_roples_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = create_reaction_role_setup_embed(interaction.guild)
        await interaction.response.send_message(embed=embed, view=ReactionRoleSetupSetupView(self.bot, interaction.guild.id, interaction.guild.roles, channel))

#endregion

#region helpers
################################ helpers #######################################################################################
    async def check_payload_guild(self, payload: discord.RawReactionActionEvent) -> RoleMemberMapping | None:
        if payload.guild_id is None:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        
        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return
        
        channel = guild.get_channel(payload.channel_id)
        if channel is None:
            return
        
        try:
            message = await channel.fetch_message(payload.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return
        
        config = get_reaction_role_by_emoji(guild, message.id, str(payload.emoji))
        if config is None:
            return
        
        role = guild.get_role(config.role_id) if config.role_id else None
        if role is None:
            return
        return RoleMemberMapping(role=role, member=member)
#endregion

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))