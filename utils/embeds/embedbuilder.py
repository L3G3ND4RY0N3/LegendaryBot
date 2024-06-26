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
    
