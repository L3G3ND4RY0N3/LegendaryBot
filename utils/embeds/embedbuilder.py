import discord
import utils.settings as settings

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