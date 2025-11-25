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
    role_id: int | None
    emoji: str | None