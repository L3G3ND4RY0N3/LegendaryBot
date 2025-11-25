import typing as T

import discord
from dbmodels.base import SessionLocal
from dbmodels import ReactionRole, Guild
from .dbservice import DatabaseService
from sqlalchemy.orm import Session
from constants.enums import SuccessStatus
from utils import settings
from utils.structs.ReactionRoles import ReactionRolesConfig


logger=settings.logging.getLogger("discord")

db_service = DatabaseService(SessionLocal)


def set_reaction_role(config: ReactionRolesConfig
                        ) -> SuccessStatus:
    """Sets or updates the reaction role for a guild."""
    with db_service.session_scope() as session:
        try:
            reaction_role = get_or_create_for_guild_config(config.guild_id, config.guild_name, session, config.message_id, config.role_id, config.emoji)
        except Exception as e:
            logger.exception(f"Error setting reaction role for guild {config.guild_name}: {e}")
            return SuccessStatus.Fail
        if reaction_role:
            return SuccessStatus.Success
    return SuccessStatus.Fail


def get_reaction_roles_for_message(dcguild: discord.Guild, message_id: int) -> T.List[ReactionRole]:
    """Retrieves the reaction roles for a guild and message."""
    with db_service.session_scope() as session:
        reaction_roles = (session.query(ReactionRole)
                    .join(Guild)
                    .filter(Guild.guild_dc_id == dcguild.id, ReactionRole.message_id == message_id)
                    ).all()

        reaction_roles = T.cast(T.List[ReactionRole], reaction_roles)
        return reaction_roles
    

def get_reaction_role_by_emoji(dcguild: discord.Guild, message_id: int, emoji: str) -> T.Optional[ReactionRole]:
    """Retrieves a specific reaction role for a guild, message and emoji."""
    with db_service.session_scope() as session:
        reaction_role = (session.query(ReactionRole)
                    .join(Guild)
                    .filter(Guild.guild_dc_id == dcguild.id, ReactionRole.message_id == message_id, ReactionRole.emoji == emoji)
                    ).first()

        reaction_role = T.cast(T.Optional[ReactionRole], reaction_role)
        return reaction_role


def get_or_create_for_guild_config(dcguild_id: int,
                                    dcguild_name: str,
                                    session: Session,
                                    message_id: int,
                                    role_id: int,
                                    emoji: str
                                    ) -> ReactionRole:
    """creates all relevant models for the activity updates"""
    guild = db_service.get_or_create(Guild, session=session, guild_dc_id=dcguild_id, name=dcguild_name)
    session.flush()
    reaction_role = db_service.get_or_create(ReactionRole, session=session, guild_id = guild.id, message_id=message_id, role_id=role_id, emoji=emoji)
    session.commit()
    return reaction_role