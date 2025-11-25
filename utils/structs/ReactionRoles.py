from dataclasses import dataclass

@dataclass
class ReactionRolesConfig():
    """Configuration for reaction roles in a guild."""
    guild_id: int
    message_id: int | None
    reaction_roles_data: list['ReactionRolesData'] | None


@dataclass
class ReactionRolesData():
    role_id: int | None
    emoji: str | None