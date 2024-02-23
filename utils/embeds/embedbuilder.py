import discord
import utils.settings as settings
import utils.filepaths as fp
import json

logger=settings.logging.getLogger("discord")

def forbidden_embed(val):
    conf_embed = discord.Embed(color=discord.Color.red())
    conf_embed.add_field(name="`❌` **Failure!**", value=val)
    return conf_embed


def warn_embed(val):
    conf_embed = discord.Embed(color=discord.Color.red())
    conf_embed.add_field(name="`⚠️` **Failure!**", value=val)
    return conf_embed


def success_embed(val):
    conf_embed = discord.Embed(color=discord.Color.green())
    conf_embed.add_field(name="`✅` **Success!**", value=val)
    return conf_embed


######## embed for the /settings command
def createSettingEmbed(guild: discord.Guild , pageNum=0, inline=False):
    with open(fp.guild_log_json, "r") as f:
        data = json.load(f)
    guild_id = str(guild.id)
    try:
        guild_data = data[guild_id]
    except KeyError as e:
        logger.error(f"Keyerror for key {guild_id} in guild logging setup embedbuilder.")
    pageNum = pageNum % len(list(guild_data))
    pageTitle = list(guild_data.keys())[pageNum]
    embed=discord.Embed(color=discord.Color.blurple(), title=pageTitle)
    status = get_channel_status(pageTitle, guild_data)
    if pageTitle != "activity":
        channel = guild.get_channel(guild_data.get(pageTitle, 0))
    match pageTitle: #will be prone to breaking if I fuck with the json...
        case "error":
            embed.add_field(name=f"{pageTitle.title()} channel: {status}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will show error messages to you. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(guild_data))}")
        case "log":
            embed.add_field(name=f"{pageTitle.title()} channel: {status}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will log events from the guild like edited/deleted messages. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(guild_data))}")
        case "welcome":
            embed.add_field(name=f"{pageTitle.title()} channel: {status}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will show error messages to you. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(guild_data))}")
        case "boost":
            embed.add_field(name=f"{pageTitle.title()} channel: {status}", value="", inline=inline)
            if channel is not None:
                embed.add_field(name="Current channel:", value=f"{channel.mention}")
            embed.add_field(name="Info", value="Set a channel where the bot will send thank you messages to server booster. The default is none.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(guild_data))}")
        case "activity":
            embed.add_field(name=f"{pageTitle.title()} tracker: {status}", value="", inline=inline)
            embed.add_field(name="Info", value="Activate the activity tracker, tracking the times of members in voice and written messages. Deactivated by default.", inline=inline)
            embed.set_footer(text=f"Page {pageNum+1} of {len(list(guild_data))}")
    return embed


######### helper for the settings embed builder
def get_channel_status(channel: str, data: dict):
    status = data.get(channel, 0)
    if status == 0:
        return "Inactive"
    return "Active"