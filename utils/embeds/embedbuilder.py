from dataclasses import dataclass
import discord
import utils.settings as settings
import utils.filepaths as fp
import datetime as dt

logger=settings.logging.getLogger("discord")

@dataclass
class EmbedFileTuple():
    """dataclass to store a tuple of an embed and its associated file"""
    embed: discord.Embed
    file: discord.File | None = None


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
    

def custom_set_author(emb: discord.Embed, member: discord.Member, action: str | None = None) -> EmbedFileTuple:
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
        return EmbedFileTuple(embed=emb)
    else:
        file = discord.File(fp.DISCORD_LOGO_IMG, filename=fp.DISCORD_LOGO_NAME)
        emb.set_author(name=f"{name_field}", icon_url=fp.attach(fp.DISCORD_LOGO_NAME))
        return EmbedFileTuple(embed=emb, file=file)
#endregion

#endregion
    
