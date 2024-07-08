import discord
from discord.ext import commands, tasks
from discord import app_commands
from itertools import cycle
from utils import settings
from utils.customwrappers import is_owner
from utils.embeds.embedbuilder import success_embed, warn_embed

logger=settings.logging.getLogger("discord")

class StatusChanger(commands.Cog, name="StatusChanger"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.bot_status = cycle(["Slapping Juratyp", "Preparing next Slap", "Searching for new Targets"])
        self.change_status.start()

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!") 

#region TASKS

    #Status Zyklus
    @tasks.loop(seconds = 5)
    async def change_status(self) -> None:
        await self.bot.change_presence(activity=discord.Game(next(self.bot_status)))

    
    @change_status.before_loop
    async def before_change_status_task(self):
        logger.info("Change status task is waiting for the bot to load...") 
        await self.bot.wait_until_ready()

#endregion

#region COMMANDS

    @app_commands.command(name="change_bot_status", description="Change the status of the bot")
    @is_owner()
    async def change_bot_status(self, interaction: discord.Interaction):
        #TODO: allow changing the status
        await interaction.response.send_message(embed=success_embed("Successfully changed bot status!"))

#endregion

async def setup(bot):
    await bot.add_cog(StatusChanger(bot))