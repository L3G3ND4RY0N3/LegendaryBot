import typing as T
import discord
import utils.settings as settings
from utils.structs.ReactionRoles import ReactionRolesData

logger=settings.logging.getLogger("discord")


def create_reaction_role_setup_embed(guild: discord.Guild, reaction_role_data: T.List[ReactionRolesData] | None = None) -> discord.Embed:
    embed = discord.Embed(
        title="Reaction Roles Setup",
        description="React to the message with the corresponding emoji to get the role!",
        color=discord.Color.blue()
    )
    if reaction_role_data:
        embed = add_fields(guild, embed, reaction_role_data)
    embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else "")
    embed.set_footer(text="LegendaryBot Reaction Roles Setup")
    return embed


def create_reaction_role_embed(guild: discord.Guild, reaction_role_data: T.List[ReactionRolesData]) -> discord.Embed:
    embed = discord.Embed(
        title="Reaction Roles",
        description="React to the message with the corresponding emoji to get the role!",
        color=discord.Color.blue()
    )
    if reaction_role_data:
        embed = add_fields(guild, embed, reaction_role_data)
    embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else "")
    embed.set_footer(text="LegendaryBot Reaction Roles")
    return embed


def add_fields(guild: discord.Guild, embed: discord.Embed, reaction_role_data: T.List[ReactionRolesData]) -> discord.Embed:
    for data in reaction_role_data:
        if data.role_id:
            role = guild.get_role(data.role_id)
        if role and data.emoji:
            embed.add_field(name=f"{data.emoji} -> {role.name}", value=f"Assign yourself the **{role.mention}** role by reacting with {data.emoji}", inline=False)
        elif data.emoji:
            embed.add_field(name=f"{data.emoji} -> Role not found", value=f"The role associated with {data.emoji} was not found. It might have been deleted.", inline=False)
        elif role:
            embed.add_field(name=f"Role: {role.name}", value=f"The emoji associated with the **{role.mention}** role was not found.", inline=False)
    return embed
