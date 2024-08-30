import discord
import utils.settings as settings
import utils.filepaths as fp
import json
from constants import enums as en


logger=settings.logging.getLogger("discord")


#region SETUP EMBEDS
######## embed for the /settings command
def createSettingEmbed(guild: discord.Guild , pageNum=0, inline=False) -> discord.Embed:
    with open(fp.GUILD_LOG_JSON, "r") as f:
        data = json.load(f)
    guild_id = str(guild.id)
    try:
        guild_data = data[guild_id]
    except KeyError as e:
        logger.error(f"Keyerror for key {guild_id} in guild logging setup embedbuilder.")
        logger.exception(f"{e}")
    pageNum = pageNum % len(list(guild_data))
    pageTitle: str = list(guild_data.keys())[pageNum]
    embed=discord.Embed(color=discord.Color.blurple(), title=pageTitle.title())
    status = get_channel_status(pageTitle, guild_data)

    # if not looking at activity page, where no channel is set, get the channel to display in embed, else set channel to 'None'
    if pageTitle != en.GuildChannelTypes.ACTIVITY.value: 
        channel = guild.get_channel(guild_data.get(pageTitle, 0))

    match pageTitle: #will be prone to breaking if I fuck with the json...
        case en.GuildChannelTypes.ERROR.value:
            embed.add_field(name=f"{pageTitle.title()} channel: {status}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will show error messages to you. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(guild_data))}")

        case en.GuildChannelTypes.LOG.value:
            embed.add_field(name=f"{pageTitle.title()} channel: {status}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will log events from the guild like edited/deleted messages. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(guild_data))}")

        case en.GuildChannelTypes.WELCOME.value:
            embed.add_field(name=f"{pageTitle.title()} channel: {status}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will show welcome messages to new joining members. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(guild_data))}")

        case en.GuildChannelTypes.BOOST.value:
            embed.add_field(name=f"{pageTitle.title()} channel: {status}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will send thank you messages to server booster. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(guild_data))}")

        case en.GuildChannelTypes.ACTIVITY.value:
            embed.add_field(name=f"{pageTitle.title()} tracker: {status}", value="", inline=inline)
            embed.add_field(name="Info", value="Activate the activity tracker, tracking the times of members in voice and written messages. Deactivated by default.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(guild_data))}")

    return embed


######### helper for the settings embed builder
def get_channel_status(channel: str, data: dict) -> str:
    status = data.get(channel, 0)
    if status == 0:
        return en.GuildChannelStatus.Inactive.name
    return en.GuildChannelStatus.Active.name

#endregion