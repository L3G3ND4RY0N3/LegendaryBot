import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils import settings, filepaths, guildjsonfunctions
import json

logger=settings.logging.getLogger("discord")

class GuildLogging(commands.Cog, name="Guild Logging"):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info("GuildLogging.py is ready!")

    #region "tasks"
    ####################### tasks
    #######################################################################################
    #loads the guild ids from the json into memory (list)

    @tasks.loop(minutes=1, count=1)
    async def load_guilds_from_json(self):
        guildjsonfunctions.load_json_to_activity_id_list()

    #endregion

async def setup(bot):
    await bot.add_cog(GuildLogging(bot))