from constants import enums as en
import discord
from discord.ext import commands
from utils import settings
from utils import guildjsonfunctions as GJF
from utils.embeds.embedbuilder import EmbedFileTuple
from utils.embeds.guild_logging_embeds import log_del_message_embed, log_edit_message_embed, log_member_join_embed, log_member_leave_embed


logger=settings.logging.getLogger("discord")

class GuildLogging(commands.Cog, name="GuildLogging"):
    def __init__(self, bot: discord.Client):
        self.bot = bot


    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")

    #region TASKS
    ####################### tasks #######################################################################################

    #endregion
        
    #region EVENTS
    #region MESSAGE EVENTS

    # also fires if messages isnt cached when deleted
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        await self.log_event_from_message(message.guild, log_del_message_embed(message, message.author))

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.author.bot or before.content == after.content:
            return
        await self.log_event_from_message(after.guild, log_edit_message_embed(before, after, after.author))

    #endregion
        
    #region MEMBER EVENTS
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await self.log_event_from_member(member.guild, log_member_join_embed(member))


    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:
        guild = self.bot.get_guild(payload.guild_id)
        await self.log_event_from_member(guild, log_member_leave_embed(payload.user))
    #endregion

    #region CLASS METHODS
    @classmethod
    async def log_event(cls, channel: discord.TextChannel, embed: discord.Embed, file: discord.File | None = None) -> None:
        await cls.custom_send(channel, embed, file)
    

    @classmethod
    async def log_event_from_member(cls, guild: discord.Guild, embed_file_tuple: EmbedFileTuple) -> None:
        channel_id = GJF.get_guild_channel(str(guild.id), en.GuildChannelTypes.LOG.value)
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if not channel:
            return
        await cls.log_event(channel, embed_file_tuple.embed, embed_file_tuple.file)


    @classmethod
    async def log_event_from_message(cls, guild: discord.Guild, embed_file_tuple: EmbedFileTuple) -> None:
        channel_id = GJF.get_guild_channel(str(guild.id), en.GuildChannelTypes.LOG.value)
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        if not channel:
            return
        await cls.log_event(channel, embed_file_tuple.embed, embed_file_tuple.file)
    #endregion

    #region STATIC METHODS        
    @staticmethod
    async def custom_send(log_channel: discord.TextChannel, embed: discord.Embed, file: discord.File | None = None) -> None:
        await log_channel.send(embed=embed, file=file)
    #endregion
    

async def setup(bot):
    await bot.add_cog(GuildLogging(bot))