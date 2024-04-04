import discord
import utils.settings as settings
import utils.filepaths as fp
import json
from constants import enums as en
import datetime as dt

logger=settings.logging.getLogger("discord")


#region BASIC EMBEDS
def forbidden_embed(val: str) -> discord.Embed:
    conf_embed = discord.Embed(color=discord.Color.red())
    conf_embed.add_field(name="`❌` **Failure!**", value=val)
    return conf_embed


def warn_embed(val: str) -> discord.Embed:
    conf_embed = discord.Embed(color=discord.Color.red())
    conf_embed.add_field(name="`⚠️` **Failure!**", value=val)
    return conf_embed


def success_embed(val: str) -> discord.Embed:
    conf_embed = discord.Embed(color=discord.Color.green())
    conf_embed.add_field(name="`✅` **Success!**", value=val)
    return conf_embed
#endregion

#region SETUP EMBEDS
######## embed for the /settings command
def createSettingEmbed(guild: discord.Guild , pageNum=0, inline=False) -> discord.Embed:
    with open(fp.guild_log_json, "r") as f:
        data = json.load(f)
    guild_id = str(guild.id)
    try:
        guild_data = data[guild_id]
    except KeyError as e:
        logger.error(f"Keyerror for key {guild_id} in guild logging setup embedbuilder.")
        logger.exception(f"{e}")
    pageNum = pageNum % len(list(guild_data))
    pageTitle = list(guild_data.keys())[pageNum]
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
        return "Inactive"
    return "Active"

#endregion

#region LOGGING EMBEDS

### embeds for the logging module

#region MESSAGE ACTIONS
def log_del_message_embed(message: discord.Message, member: discord.Member) -> tuple[discord.Embed, discord.File | None]:
    """Creates an Embed for deleted messages

    Args:
        message (discord.Message): The Message that got deleted
        member (discord.Member): The author (member) of the deleted message

    Returns:
        tuple[discord.Embed, discord.File | None]: The created embed that gets send to the log channel of the guild and the file for the discord icon, if the user has no pfp
    """

    embed = discord.Embed(color=discord.Color.red())
    embed.timestamp = dt.datetime.now()
    embed.add_field(name="", value=f"** Message sent by **{member.mention} ** deleted in **{message.channel.mention}")
    embed.add_field(name="", value=message.content, inline=False)
    embed.set_footer(text=f"Author ID: {member.id} | Message ID: {message.id}")
    embed, file = custom_set_author(embed, member)
    return (embed, file)


def log_edit_message_embed(before: discord.Message, after:discord.Message, member: discord.Member) -> tuple[discord.Embed, discord.File | None]:
    """Creates and Embed when a message is edited

    Args:
        message (discord.Message): The edited member
        member (discord.Member): The member that send and edited the message

    Returns:
        tuple[discord.Embed, discord.File | None]: A tuple of the embed and the file of the discord icon, if the user has no pfp
    """
    
    embed = discord.Embed(color=discord.Color.blue())
    embed.timestamp = dt.datetime.now()
    embed.add_field(name="", value=f"** Message edited in **{before.channel.mention} {after.jump_url}")
    embed.add_field(name="Before Edit", value=before.content, inline=False)
    embed.add_field(name="After Edit", value=after.content, inline=False)
    embed.set_footer(text=f"Author ID: {member.id} | Message ID: {after.id}")
    embed, file = custom_set_author(embed, member)
    return (embed, file)
#endregion

#region MEMBER ACTIONS
def log_member_join_embed(member: discord.Member) -> tuple[discord.Embed, discord.File | None]:
    """Creates an embed when a member joins a guild

    Args:
        member (discord.Member): The joining member
    
    Returns:
        tuple[discord.Embed, discord.File | None]: A tuple of the embed and the file of the discord icon, if the user has no pfp
    """
    member_account_age = calc_member_account_age(dt.datetime.now().date(), member.created_at.date())
    embed = discord.Embed(color=discord.Color.green())
    embed.timestamp = dt.datetime.now()
    embed.add_field(name="", value=f"{member.mention} {member.name}")
    embed.add_field(name="Account Age", value=f"{member_account_age}", inline=False)
    embed.set_footer(text=f"Member ID: {member.id}")
    embed, file = custom_set_author(embed, member, "Member Joined")
    return (embed, file)


def log_member_leave_embed(member: discord.Member) -> tuple[discord.Embed, discord.File | None]:
    """Creates an embed when a member leaves a guild

    Args:
        member (discord.Member): The leaving member
    
    Returns:
        tuple[discord.Embed, discord.File | None]: A tuple of the embed and the file of the discord icon, if the user has no pfp
    """

    member_account_age = calc_member_account_age(dt.datetime.now().date(), member.created_at.date())
    member_guild_age = calc_member_account_age(dt.datetime.now().date(), member.joined_at.date())
    embed = discord.Embed(color=discord.Color.red())
    embed.timestamp = dt.datetime.now()
    embed.add_field(name="", value=f"{member.mention} {member.name}")
    embed.add_field(name="Account Age", value=f"{member_account_age}", inline=False)
    embed.add_field(name="Guild Membership", value=f"{member_guild_age}", inline=False)
    embed.set_footer(text=f"Member ID: {member.id}")
    embed, file = custom_set_author(embed, member, "Member Left")
    return (embed, file)
#endregion

#region UTILITIES
# TODO: Auslagern?
def calc_member_account_age(now: dt.date, member_created_at: dt.date) -> str:
    """Calculates the account age of a member

    Args:
        now (dt.date): The current date
        member_created_at (dt.date): The date of creation of the member account

    Returns:
        str: The string representation of the account age
    """
    if not member_created_at:
        return "0 days"
    dif = now - member_created_at
    years = dif.days // 365
    months = (dif.days % 365) // 30
    days = (dif.days % 365) % 30
    return f"{years} years, {months} months, {days} days"
    

def custom_set_author(emb: discord.Embed, member: discord.Member, action: str = None) -> tuple[discord.Embed, discord.File | None]:
    """Modifys an embed by setting an author field and setting a default pfp if the member has none

    Args:
        emb (discord.Embed): The embed that gets modified
        member (discord.Member): The member that iss the author in the embed field
        action (str): The action of the member, default is None

    Returns:
        tuple[discord.Embed, discord.File | None]: The embed and the file for the default pfp, if the member did not have custom pfp
    """
    name_field = action if action else member.name
    if member.avatar:
        emb.set_author(name=f"{name_field}", icon_url=member.avatar.url)
        return (emb, None)
    else:
        file = discord.File(fp.discord_logo, filename=fp.discord_logo_name)
        emb.set_author(name=f"{name_field}", icon_url=fp.attach(fp.discord_logo_name))
        return (emb, file)
#endregion

#endregion
    
