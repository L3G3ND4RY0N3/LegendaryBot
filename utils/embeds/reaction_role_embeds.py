import typing as T
import discord
import utils.settings as settings
from utils.structs.ReactionRoles import ReactionRolesData

logger=settings.logging.getLogger("discord")


def reaction_role_embed(guild: discord.Guild, reaction_role_data: T.List[ReactionRolesData] | None = None) -> discord.Embed:
    embed = discord.Embed(
        title="Reaction Roles Setup",
        description="React to the message with the corresponding emoji to get the role!",
        color=discord.Color.blue()
    )
    if reaction_role_data:
        for data in reaction_role_data:
            if data.role_id and data.emoji:
                role = guild.get_role(data.role_id)
                embed.add_field(name=f"{data.emoji} - {role.name}", value=f"Assign yourself the **{role.name}** role by reacting with {data.emoji}", inline=False)
            elif data.emoji:
                embed.add_field(name=f"{data.emoji} - Role not found", value=f"The role associated with {data.emoji} was not found. It might have been deleted.", inline=False)
            elif data.role_id:
                embed.add_field(name=f"Role: {role.name}", value=f"The emoji associated with the **{role.name}** role was not found.", inline=False)
    embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else "")
    embed.set_footer(text="LegendaryBot Reaction Roles")
    return embed
