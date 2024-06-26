import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils import settings, guildjsonfunctions 
from utils.embeds import embedbuilder as emb
from utils.embeds.guild_settings_embed import createSettingEmbed
from utils.views import guildsetupview as gsv
from utils import filepaths as fp

logger=settings.logging.getLogger("discord")


class GuildSetup(commands.Cog, name="GuildSetup"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.load_guilds_from_json.start()


    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")
        fp.create_empty_json(fp.guild_log_json)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        guildjsonfunctions.initialise_guild_setup(str(guild.id))
        # if a system channel exist, send a small welcome message
        if guild.system_channel is not None:
            conf_embed = discord.Embed(color=discord.Color.blurple())
            conf_embed.add_field(name="`❤` **Hello!**", value=f"Hi, {guild.name}. To set up my functions like logging, welcome greetings and economy, please use the /setup command.")
            await guild.system_channel.send(embed=conf_embed)

    #region "tasks"
    ####################### tasks
    #######################################################################################
    #loads the guild ids from the json into memory (set)

    @tasks.loop(minutes=1, count=1)
    async def load_guilds_from_json(self) -> None:
        guildjsonfunctions.load_json_to_guild_id_list()
        guildjsonfunctions.load_json_to_activity_id_list()

    
    @load_guilds_from_json.before_loop
    async def before_load_guilds_from_json(self) -> None:
        logger.info("load_guilds_from_json loop is waiting for the bot to load...") 
        await self.bot.wait_until_ready()


    @load_guilds_from_json.after_loop
    async def after_load_guilds_from_json(self) -> None:
        logger.info(f"Finished load_guilds_from_json loop!")
        logger.info("Ending loading gulds from json loop!")

    #endregion
    
    ################################ commands
    ###########################################################################################
        
    @app_commands.command(name="guild_setup", description="calls the setup menu for the guild")
    @app_commands.checks.has_permissions(administrator=True)
    async def guild_setup(self, ctx:discord.Interaction):
        guild_id = ctx.guild.id

        retcode = 0
        if guild_id not in guildjsonfunctions.ids:
            guildjsonfunctions.initialise_guild_setup(str(guild_id))
            guildjsonfunctions.ids.add(guild_id)
        
        if retcode < 0:
            conf_embed = emb.warn_embed("That did not work!")
        
            await ctx.response.send_message(embed=conf_embed)
            return
        
        currentPage = 0
        
        embed = createSettingEmbed(ctx.guild, pageNum=currentPage)
        channel = embed.fields[0].name.split(" ")[0].lower()
        sent_msg = await ctx.response.send_message(embed=embed, view=gsv.GuildSetupView(ctx, self.bot, currentPage, channel))


async def setup(bot):
    await bot.add_cog(GuildSetup(bot))