from constants.enums import GuildChannelTypes
import discord
from discord.ext import commands
from utils.dbhelpers.guild_config_db_helpers import get_config_channel_id, get_guild_config
from utils import settings

logger=settings.logging.getLogger("discord")

class GuildWelcome(commands.Cog, name="GuildWelcome"):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        channel_id = get_config_channel_id(get_guild_config(member.guild.id), GuildChannelTypes.WELCOME.value)
        welcome_channel = member.guild.get_channel(channel_id)
        if not welcome_channel:
            return
        await welcome_channel.send(f"Welcome to the guild, <@{member.id}>!")

async def setup(bot):
    await bot.add_cog(GuildWelcome(bot))