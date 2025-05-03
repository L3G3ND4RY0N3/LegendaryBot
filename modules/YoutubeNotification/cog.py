import discord
from discord.ext import commands, tasks
from discord import app_commands
import feedparser
from utils import settings
#from utils.customwrappers import is_owner
from utils.dbhelpers.youtube_notifications_db_helper import get_all_Youtube_Notifications, handle_yt_notificatin_update
from utils.embeds.embedbuilder import success_embed

logger=settings.logging.getLogger("discord")

DISCORD_CHANNEL_ID = 1156877414606049323 # general Legendary.Dev
YOUTUBE_CHANNEL_ID = "UCq8Z8IO_3SG5Q-55fnb2gLA" # Tersti Channel ID
YOUTUBE_RSS_URL = f'https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}' # Tersti RSS URL
NEWS_ROLE_ID = 1243703921340317696

class YoutubeNotification(commands.Cog, name="YoutubeNotification"):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.latest_video_id = None
        self.check_youtube.start()
    

    @commands.Cog.listener() #ansatt bot.event!
    async def on_ready(self):
        logger.info(f"{self.__cog_name__}.py is ready!")

#region TASKS
    @tasks.loop(minutes=10)
    async def check_youtube(self):

        yt_configs = get_all_Youtube_Notifications(only_enabled=True)

        for config in yt_configs:
            yt_rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={config.youtube_channel_id}'
            feed = feedparser.parse(yt_rss_url)
            if not feed.entries:
                return

            latest_entry = feed.entries[0]
            video_id = latest_entry.yt_videoid
            video_link = latest_entry.link

            if video_id != config.last_video_id:
                config.last_video_id = video_id  # Update stored ID to avoid reposting
                channel = self.bot.get_channel(config.discord_channel_id)
                if channel:
                    role_mention = f"<@&{config.role_id}>" if config.role_id else ""
                    if not config.custom_message:
                        message = f"Hey {role_mention}! New upload on YouTube! \n {video_link}"
                    else:
                        message = f"{role_mention} {config.custom_message} \n {video_link}"
                    await channel.send(message)
                handle_yt_notificatin_update(config.discord_channel_id, config.youtube_channel_id, config.custom_message, config.role_id,config.last_video_id, config.enabled)


    @check_youtube.before_loop
    async def before_check_youtube_task(self):
        logger.info("Check youtube loop is waiting for the bot to load...") 
        await self.bot.wait_until_ready()
#endregion

#region COMMANDS
    @app_commands.command(name="youtube_notification", description="Add a new youtube notification")
    @app_commands.checks.has_permissions(administrator=True)
    async def update_youtube_notification(self,
                                        ctx: discord.Interaction,
                                        discord_channel: discord.TextChannel,
                                        youtube_channel_id: str,
                                        role: discord.Role | None,
                                        enabled: bool = True,
                                        custom_message: str | None = None
                                        ) -> None:
        role_id = role.id if role else None

        handle_yt_notificatin_update(channel_id=discord_channel.id,
                                    youtube_channel_id=youtube_channel_id,
                                    custom_message=custom_message,
                                    enabled=enabled,
                                    role_id=role_id,
                                    last_video_id=None)
        
        await ctx.response.send_message(embed=success_embed("Successfully added Youtube Notification!"))


async def setup(bot):
    await bot.add_cog(YoutubeNotification(bot))