import discord
from discord.ext import commands, tasks
from discord import app_commands, ButtonStyle
from utils import settings, filepaths, guildjsonfunctions 
from utils.embeds import embedbuilder as emb
from discord.ui import View, Button
import json

logger=settings.logging.getLogger("discord")


class GuildSetup(commands.Cog, name="Guild Setup"):
    def __init__(self, bot):
        self.bot = bot
        self.load_guilds_from_json.start()


    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info("GuildLogging.py is ready!")


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        guildjsonfunctions.initialise_guild_setup(str(guild.id))
        # if a system channel exist, send a small welcome message
        if guild.system_channel is not None:
            conf_embed = discord.Embed(color=discord.Color.blurple())
            conf_embed.add_field(name="`❤` **Hello!**", value=f"Hi, {guild.name}. To set up my functions like logging and economy, please use the /setup command.")
            await guild.system_channel.send(embed=conf_embed)

    #region "tasks"
    ####################### tasks
    #######################################################################################
    #loads the guild ids from the json into memory (list)

    @tasks.loop(minutes=1, count=1)
    async def load_guilds_from_json(self):
        guildjsonfunctions.load_json_to_guild_id_list()

    
    @load_guilds_from_json.before_loop
    async def before_load_guilds_from_json(self):
        logger.info("load_guilds_from_json loop is waiting for the bot to load...") 
        await self.bot.wait_until_ready()


    @load_guilds_from_json.after_loop
    async def after_load_guilds_from_json(self):
        logger.info(f"Finished load_guilds_from_json loop!")
        logger.info("Ending loading gulds from json loop!")

    #endregion
        

    
    ################################ commands
    ###########################################################################################
        
    @app_commands.command(name="guild_setup", description="calls the setup menu for the guild")
    @app_commands.checks.has_permissions(administrator=True)
    async def guild_setup(self, ctx:discord.Interaction):
        guild_id = ctx.guild.id

        if guild_id not in guildjsonfunctions.ids:
            conf_embed = emb.warn_embed("That did not work!")
        
            await ctx.response.send_message(embed=conf_embed)
            return
        
        retcode = guildjsonfunctions.initialise_guild_setup(str(guild_id))

        if retcode < 0:
            conf_embed = emb.warn_embed("That did not work!")
        
            await ctx.response.send_message(embed=conf_embed)
            return
        
        currentPage = 0

        async def next_callback(interaction: discord.Interaction):
            nonlocal currentPage, sent_msg
            currentPage += 1
            await interaction.response.edit_message(embed=emb.createSettingEmbed(ctx.guild, pageNum=currentPage), view=myview)

        async def prev_callback(interaction: discord.Interaction):
            nonlocal currentPage, sent_msg
            currentPage -= 1
            await interaction.response.edit_message(embed=emb.createSettingEmbed(ctx.guild, pageNum=currentPage), view=myview)

        async def quit_callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content="Hope this helped!", embed=None, view=None)

        nextButton = Button(label=">", style=ButtonStyle.blurple)
        nextButton.callback = next_callback
        prevButton = Button(label="<", style=ButtonStyle.blurple)
        prevButton.callback = prev_callback
        quitbutton = Button(label="x", style=ButtonStyle.red)
        quitbutton.callback = quit_callback

        myview = View(timeout=180)
        myview.add_item(prevButton)
        myview.add_item(nextButton)
        myview.add_item(quitbutton)
        
        sent_msg = await ctx.response.send_message(embed=emb.createSettingEmbed(ctx.guild, currentPage, False), view=myview)


async def setup(bot):
    await bot.add_cog(GuildSetup(bot))