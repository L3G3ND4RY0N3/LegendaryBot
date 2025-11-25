import discord
from dataclasses import dataclass

@dataclass
class ReactionRolesConfig():
    """Configuration for reaction roles in a guild."""
    guild_id: int
    guild_name: str
    message_id: int
    role_id: int | None
    emoji: str | None


@dataclass
class ReactionRolesData():
    """Simple Map of role_id to emoji for Reaction Role."""
    role_id: int | None
    emoji: str | None


@dataclass
class RoleMemberMapping():
    """Map a Member to a Role."""
    role: discord.Role | None
    member: discord.Member | None