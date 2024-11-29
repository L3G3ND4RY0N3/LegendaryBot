import discord
import utils.settings as settings
from utils.embeds.embedbuilder import custom_set_author, calc_member_account_age, EmbedFileTuple
import datetime as dt


logger=settings.logging.getLogger("discord")


#region LOGGING EMBEDS

### embeds for the logging module

#region MESSAGE ACTIONS
def log_del_message_embed(message: discord.Message, member: discord.Member) -> EmbedFileTuple:
    """Creates an Embed for deleted messages"""
    embed = discord.Embed(color=discord.Color.red())
    embed.timestamp = dt.datetime.now()
    embed.add_field(name="", value=f"** Message sent by **{member.mention} ** deleted in **{message.channel.mention}")
    embed.add_field(name="", value=message.content, inline=False)
    if len(message.attachments) == 1:
        embed.set_image(url=message.attachments[0].url)
    embed.set_footer(text=f"Author ID: {member.id} | Message ID: {message.id}")
    return custom_set_author(embed, member)


def log_edit_message_embed(before: discord.Message, after:discord.Message, member: discord.Member) -> EmbedFileTuple:
    """Creates and Embed when a message is edited"""
    embed = discord.Embed(color=discord.Color.blue())
    embed.timestamp = dt.datetime.now()
    embed.add_field(name="", value=f"** Message edited in **{before.channel.mention} {after.jump_url}")
    embed.add_field(name="Before Edit", value=before.content, inline=False)
    embed.add_field(name="After Edit", value=after.content, inline=False)
    embed.set_footer(text=f"Author ID: {member.id} | Message ID: {after.id}")
    return custom_set_author(embed, member)
#endregion

#region MEMBER ACTIONS
def log_member_join_embed(member: discord.Member) -> EmbedFileTuple:
    """Creates an embed when a member joins a guild"""
    member_account_age = calc_member_account_age(dt.datetime.now().date(), member.created_at.date())
    embed = discord.Embed(color=discord.Color.green())
    embed.timestamp = dt.datetime.now()
    embed.add_field(name="", value=f"{member.mention} {member.name}")
    embed.add_field(name="Account Age", value=f"{member_account_age}", inline=False)
    embed.set_footer(text=f"Member ID: {member.id}")
    return custom_set_author(embed, member, "Member Joined")


def log_member_leave_embed(member: discord.Member) -> EmbedFileTuple:
    """Creates an embed when a member leaves a guild"""
    member_account_age = calc_member_account_age(dt.datetime.now().date(), member.created_at.date())
    member_guild_age = calc_member_account_age(dt.datetime.now().date(), member.joined_at.date())
    embed = discord.Embed(color=discord.Color.red())
    embed.timestamp = dt.datetime.now()
    embed.add_field(name="", value=f"{member.mention} {member.name}")
    embed.add_field(name="Account Age", value=f"{member_account_age}", inline=False)
    embed.add_field(name="Guild Membership", value=f"{member_guild_age}", inline=False)
    embed.set_footer(text=f"Member ID: {member.id}")
    return custom_set_author(embed, member, "Member Left")
#endregion