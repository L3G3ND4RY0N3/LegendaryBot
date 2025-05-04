import aiohttp
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from discord import app_commands
import feedparser
from utils import settings
#from utils.customwrappers import is_owner
from utils.dbhelpers.youtube_notifications_db_helper import get_all_Youtube_Notifications, handle_yt_notificatin_update
from utils.embeds.embedbuilder import success_embed, warn_embed
from utils.customwrappers import is_owner
import os

load_dotenv()

logger=settings.logging.getLogger("discord")

YT_DATA_API_KEY = os.getenv('YT_DATA_API_KEY', "")
YT_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

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
    @app_commands.describe(role = "The role to be pinged",
                            discord_channel = "The channel in which to post the announcement",
                            youtube_channel_id = "The ID of the youtube channel",
                            custom_message = "The message to be displayed along the announcement",
                            enabled = "To toogle the status")
    async def update_youtube_notification(self,
                                        ctx: discord.Interaction,
                                        discord_channel: discord.TextChannel,
                                        youtube_channel_id: str,
                                        role: discord.Role | None,
                                        enabled: bool = True,
                                        custom_message: str | None = None
                                        ) -> None:
        role_id = role.id if role else None

        try:
            handle_yt_notificatin_update(channel_id=discord_channel.id,
                                        youtube_channel_id=youtube_channel_id,
                                        custom_message=custom_message,
                                        enabled=enabled,
                                        role_id=role_id,
                                        last_video_id=None)
        except Exception as e:
            logger.exception(f"{e}")
            logger.error(f"Failed to add a youtube notification for channel id {youtube_channel_id} in guild {discord_channel.guild.name}")

            await ctx.response.send_message(embed=warn_embed("There was an error in adding a youtube notification"))
        
        await ctx.response.send_message(embed=success_embed(f"Successfully added Youtube Notification in {discord_channel.mention}!"))


    @is_owner()
    @app_commands.command(name="youtube_notification_by_yt_name", description="Add a new youtube notification")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role = "The role to be pinged",
                            discord_channel = "The channel in which to post the announcement",
                            youtube_channel_name = "The name of the youtube channel",
                            custom_message = "The message to be displayed along the announcement",
                            enabled = "To toogle the status")
    async def update_youtube_notification_by_yt_name(self,
                                        ctx: discord.Interaction,
                                        discord_channel: discord.TextChannel,
                                        youtube_channel_name: str,
                                        role: discord.Role | None,
                                        enabled: bool = True,
                                        custom_message: str | None = None
                                        ) -> None:
        role_id = role.id if role else None

        youtube_channel_id = await self.get_yt_channelid_from_name(yt_channel_name = youtube_channel_name)

        if youtube_channel_id:
            handle_yt_notificatin_update(channel_id=discord_channel.id,
                                        youtube_channel_id=youtube_channel_id,
                                        custom_message=custom_message,
                                        enabled=enabled,
                                        role_id=role_id,
                                        last_video_id=None)
            
            await ctx.response.send_message(embed=success_embed(f"Successfully added Youtube Notification for {youtube_channel_name} in {discord_channel.mention}!"))
        
        else:
            await ctx.response.send_message(embed=warn_embed(f"Youtube Channel Id for the channel {youtube_channel_name} could not be found!"))

#endregion

#region UTILITY

    async def get_yt_channelid_from_name(self, yt_channel_name: str) -> str | None:
        """Gets the YouTube Channel ID from a channel name."""
        params = {
            "part": "snippet",
            "q": yt_channel_name,
            "type": "channel",
            "key": YT_DATA_API_KEY,
            "maxResults": 1
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(YT_SEARCH_URL, params=params) as response:
                data = await response.json()

                if "items" in data and data["items"]:
                    channel_id = data["items"][0]["snippet"]["channelId"]
                    return channel_id
                else:
                    return None
                
    
    async def verify_youtube_channel_id(channel_id: str, api_key: str) -> bool:
        """To verify a youtube id for the command"""
        params = {
            "part": "snippet",
            "id": channel_id,
            "key": api_key
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(YT_SEARCH_URL, params=params) as response:
                data = await response.json()
                return bool(data.get("items"))

#endregion

async def setup(bot):
    await bot.add_cog(YoutubeNotification(bot))