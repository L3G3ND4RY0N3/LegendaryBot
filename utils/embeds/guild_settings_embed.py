import discord
import utils.settings as settings
from constants import enums as en
from utils.dbhelpers.guild_config_db_helpers import get_config_channel_id, get_guild_config


logger=settings.logging.getLogger("discord")


#region SETUP EMBEDS
######## embed for the /settings command
def createSettingEmbed(guild: discord.Guild , pageNum=0, inline=False) -> discord.Embed:
    config = get_guild_config(guild.id)
    maxPage = len(en.GuildChannelTypes)
    pageNum = pageNum % maxPage
    pageTitle: str = list(en.GuildChannelTypes)[pageNum].value
    embed=discord.Embed(color=discord.Color.blurple(), title=pageTitle.title())
    channel_id = get_config_channel_id(config, pageTitle)

    # if not looking at activity page, where no channel is set, get the channel to display in embed, else set channel to 'None'
    if pageTitle != en.GuildChannelTypes.ACTIVITY.value: 
        channel = guild.get_channel(channel_id)

    match pageTitle: # will be prone to breaking if I fuck with the columns of the db model...
        case en.GuildChannelTypes.ERROR.value:
            embed.add_field(name=f"{pageTitle.title()} channel status: {en.GuildChannelStatus.Active.name if channel_id else en.GuildChannelStatus.Inactive.name}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will show error messages to you. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {maxPage}")

        case en.GuildChannelTypes.LOG.value:
            embed.add_field(name=f"{pageTitle.title()} channel status: {en.GuildChannelStatus.Active.name if channel_id else en.GuildChannelStatus.Inactive.name}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will log events from the guild like edited/deleted messages. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {maxPage}")

        case en.GuildChannelTypes.WELCOME.value:
            embed.add_field(name=f"{pageTitle.title()} channel status: {en.GuildChannelStatus.Active.name if channel_id else en.GuildChannelStatus.Inactive.name}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will show welcome messages to new joining members. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {maxPage}")

        case en.GuildChannelTypes.BOOST.value:
            embed.add_field(name=f"{pageTitle.title()} channel status: {en.GuildChannelStatus.Active.name if channel_id else en.GuildChannelStatus.Inactive.name}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will send thank you messages to server booster. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {maxPage}")

        case en.GuildChannelTypes.ACTIVITY.value:
            embed.add_field(name=f"{pageTitle.title()} tracker status: {en.GuildChannelStatus.Active.name if channel_id else en.GuildChannelStatus.Inactive.name}", value="", inline=inline)
            embed.add_field(name="Info", value="Activate the activity tracker, tracking the times of members in voice and written messages. Deactivated by default.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {maxPage}")

    return embed


######### helper for the settings embed builder
def get_channel_status(channel: str, data: dict) -> str:
    status = data.get(channel, 0)
    if status == 0:
        return en.GuildChannelStatus.Inactive.name
    return en.GuildChannelStatus.Active.name

#endregion