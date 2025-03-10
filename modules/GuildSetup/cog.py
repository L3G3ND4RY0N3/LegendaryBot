import discord
from discord.ext import commands
from discord import app_commands
from utils import settings
from utils.embeds.guild_settings_embed import createSettingEmbed
from utils.views import guildsetupview as gsv
from utils.dbhelpers.guild_config_db_helpers import get_guild_config, _handle_guild_config_update

logger=settings.logging.getLogger("discord")


class GuildSetup(commands.Cog, name="GuildSetup"):
    def __init__(self, bot: discord.Client):
        self.bot = bot


    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        # if a system channel exist, send a small welcome message
        if guild.system_channel is not None:
            conf_embed = discord.Embed(color=discord.Color.blurple())
            conf_embed.add_field(name="`❤` **Hello!**", value=f"Hi, {guild.name}. To set up my functions like logging, welcome greetings and economy, please use the /setup command.")
            await guild.system_channel.send(embed=conf_embed)
    
    ################################ commands
    ###########################################################################################
        
    @app_commands.command(name="guild_setup", description="calls the setup menu for the guild")
    @app_commands.checks.has_permissions(administrator=True)
    async def guild_setup(self, ctx: discord.Interaction):
        guild_id = ctx.guild.id
        currentPage = 0
        if not get_guild_config(guild_id):
            _handle_guild_config_update(ctx.guild)
        
        embed = createSettingEmbed(ctx.guild, pageNum=currentPage)
        channel = embed.fields[0].name.split(" ")[0].lower()
        await ctx.response.send_message(embed=embed, view=gsv.GuildSetupView(self.bot, currentPage, channel, guild_id))


async def setup(bot):
    await bot.add_cog(GuildSetup(bot))