import discord
from discord.ext import commands, tasks
from discord import app_commands
from constants import enums as en
from utils import settings
from utils import guildjsonfunctions as gjf
from utils.embeds import embedbuilder as emb


logger=settings.logging.getLogger("discord")

class GuildLogging(commands.Cog, name="Guild Logging"):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info("GuildLogging.py is ready!")

    #region TASKS
    ####################### tasks #######################################################################################

    #endregion
        
    #region EVENTS
    #region MESSAGE EVENTS
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        channel_id = gjf.get_guild_channel(str(message.guild.id), en.GuildChannelTypes.LOG.value)
        if not channel_id:
            return
        
        channel = message.guild.get_channel(channel_id)      
        embed, file = emb.log_del_message_embed(message, message.author)
        await self.custom_send(channel, embed, file)
    #endregion
        
    #region MEMBER EVENTS
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        channel_id = gjf.get_guild_channel(str(member.guild.id), en.GuildChannelTypes.LOG.value)
        if not channel_id:
            return
        channel = member.guild.get_channel(channel_id)      
        embed, file = emb.log_member_join_embed(member)
        await self.custom_send(channel, embed, file)
    #endregion
    #endregion
            
    @staticmethod
    async def custom_send(channel: discord.TextChannel, embed: discord.Embed, file:discord.File = None) -> None:
        if file:
            await channel.send(embed=embed, file=file)
            return
        else:
            await channel.send(embed=embed)
        return


async def setup(bot):
    await bot.add_cog(GuildLogging(bot))