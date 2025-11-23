import typing as T

import discord
from dbmodels.base import SessionLocal
from dbmodels import WelcomeMessage, Guild
from .dbservice import DatabaseService
from sqlalchemy.orm import Session
from utils import settings


logger=settings.logging.getLogger("discord")

db_service = DatabaseService(SessionLocal)

def set_welcome_message(guild: discord.Guild, message: str, member_id: int) -> str | None:
    """Sets or updates the welcome message for a guild."""
    with db_service.session_scope() as session:
        try:
            welcome_message = get_or_create_for_guild_config(guild, session, message)
        except Exception as e:
            logger.exception(f"Error setting welcome message for guild {guild.id}: {e}")
            return None
        return welcome_message.message.replace("{member}", f"<@{member_id}>").replace("{guild}", guild.name)


def get_welcome_message(guild: discord.Guild, member: discord.Member) -> str:
    """Retrieves the welcome message for a guild."""
    with db_service.session_scope() as session:
        welcome_message = (session.query(WelcomeMessage)
                    .join(Guild)
                    .filter(Guild.guild_dc_id == guild.id)
                    ).first()

        welcome_message = T.cast(WelcomeMessage, welcome_message)
        if welcome_message:
            return welcome_message.message.replace("{member}", f"<@{member.id}>").replace("{guild}", guild.name)
        else:
            return f"Welcome to {guild.name}, <@{member.id}>!"


def get_or_create_for_guild_config(dcguild: discord.Guild, session: Session, message: str) -> WelcomeMessage:
    """creates all relevant models for the activity updates"""
    guild = db_service.get_or_create(Guild, session=session, guild_dc_id=dcguild.id, name=dcguild.name)
    session.flush()
    welcome_message = db_service.get_or_create(WelcomeMessage, session=session, guild_id = guild.id, message=message)
    session.commit()
    return welcome_message