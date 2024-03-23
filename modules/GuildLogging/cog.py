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
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        channel_id = gjf.get_guild_channel(str(message.guild.id), en.GuildChannelTypes.LOG.value)
        if not channel_id:
            return
        
        channel = message.guild.get_channel(channel_id)      
        embed = emb.log_del_message(message, message.author)
        await channel.send(embed=embed)
    
    #endregion

async def setup(bot):
    await bot.add_cog(GuildLogging(bot))