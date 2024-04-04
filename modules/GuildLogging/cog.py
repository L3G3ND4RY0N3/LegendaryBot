from typing import Optional, Tuple
import discord
from discord.ext import commands, tasks
from discord import app_commands
from constants import enums as en
from utils import settings
from utils import guildjsonfunctions as gjf
from utils.embeds import embedbuilder as emb


logger=settings.logging.getLogger("discord")

class GuildLogging(commands.Cog, name="Guild Logging"):
    def __init__(self, bot: discord.Client):
        self.bot = bot


    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info("GuildLogging.py is ready!")

    #region TASKS
    ####################### tasks #######################################################################################

    #endregion
        
    #region EVENTS
    #region MESSAGE EVENTS

    # also fires if messages isnt cached when deleted
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        await self.log_event_from_message(message.guild, emb.log_del_message_embed(message, message.author))

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        await self.log_event_from_message(after.guild, emb.log_edit_message_embed(before, after, after.author))

    #endregion
        
    #region MEMBER EVENTS
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await self.log_event_from_member(member.guild, emb.log_member_join_embed(member))


    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:
        guild = self.bot.get_guild(payload.guild_id)
        await self.log_event_from_member(guild, emb.log_member_leave_embed(payload.user))
    #endregion

    #region CLASS METHODS
    @classmethod
    async def log_event(cls, channel: discord.TextChannel, embed: discord.Embed, file: Optional[discord.File] = None) -> None:
        await cls.custom_send(channel, embed, file)
    

    @classmethod
    async def log_event_from_member(cls, guild: discord.Guild, embed_file_tuple: Tuple[discord.Embed, Optional[discord.File]]) -> None:
        channel_id = gjf.get_guild_channel(str(guild.id), en.GuildChannelTypes.LOG.value)
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        await cls.log_event(channel, embed_file_tuple[0], embed_file_tuple[1])


    @classmethod
    async def log_event_from_message(cls, guild: discord.Guild, embed_file_tuple: Tuple[discord.Embed, Optional[discord.File]]) -> None:
        channel_id = gjf.get_guild_channel(str(guild.id), en.GuildChannelTypes.LOG.value)
        if not channel_id:
            return
        channel = guild.get_channel(channel_id)
        await cls.log_event(channel, embed_file_tuple[0], embed_file_tuple[1])
    #endregion

    #region STATIC METHODS        
    @staticmethod
    async def custom_send(log_channel: discord.TextChannel, embed: discord.Embed, file:discord.File = None) -> None:
        if file:
            await log_channel.send(embed=embed, file=file)
            return
        else:
            await log_channel.send(embed=embed)
        return
    #endregion
    

async def setup(bot):
    await bot.add_cog(GuildLogging(bot))