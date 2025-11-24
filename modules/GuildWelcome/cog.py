from constants.enums import GuildChannelTypes
import discord
from discord.ext import commands
from discord import app_commands
from utils.dbhelpers.guild_config_db_helpers import get_config_channel_id, get_guild_config
from utils.dbhelpers.welcome_message_helper import get_welcome_message, set_welcome_message
from utils import settings
from utils.embeds.embedbuilder import success_embed, warn_embed

logger=settings.logging.getLogger("discord")

class GuildWelcome(commands.Cog, name="GuildWelcome"):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    #region Evenets
    ####################### events #######################################################################################
    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        channel_id = get_config_channel_id(get_guild_config(member.guild.id), GuildChannelTypes.WELCOME.value)
        welcome_channel = member.guild.get_channel(channel_id)
        if not welcome_channel:
            return
        welcome_message = get_welcome_message(member.guild, member)
        await welcome_channel.send(welcome_message)

    #endregion


    #region Commands
    ################################ commands #######################################################################################
    @app_commands.command(name="set_welcome_message", description="set a custom welcome message for new members.")
    @app_commands.describe(new_message="Use \'{member}\' to mention the new member and \'{guild}\' to mention the guild name.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_welcome_message(self, ctx: discord.Interaction, new_message: str) -> None:
        welcome_message = set_welcome_message(ctx.guild, new_message, ctx.user.id)
        if welcome_message is None:
            embed = warn_embed("There was an error setting the welcome message. Please try again later.")
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        embed = success_embed(f"Current welcome message:\n{welcome_message}\n\nTo set a new welcome message, use the /set_welcome_message command.")
        await ctx.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="show_welcome_message", description="show the custom welcome message for new members for the guild")
    @app_commands.checks.has_permissions(administrator=True)
    async def show_welcome_message(self, ctx: discord.Interaction) -> None:
        welcome_message = get_welcome_message(ctx.guild, ctx.user)
        embed = success_embed(f"Current welcome message:\n{welcome_message}\n\nTo set a new welcome message, use the /set_welcome_message command.")
        await ctx.response.send_message(embed=embed, ephemeral=True)
    #endregion

async def setup(bot):
    await bot.add_cog(GuildWelcome(bot))