import discord
from dbmodels.base import SessionLocal
from dbmodels import Guild, GuildConfig
from .dbservice import DatabaseService
from sqlalchemy.orm import Session
from utils import settings


logger=settings.logging.getLogger("discord")

db_service = DatabaseService(SessionLocal)

ACTIVITY_GUILDS = set()
GUILDS_WITH_CONFIGS = set()


def handle_guild_config_update(dcguild: discord.Guild,
                                error_id: int | None = None,
                                welcome_id: int | None = None,
                                boost_id: int | None = None,
                                log_id: int | None = None,
                                activity: bool | None = None) -> None:
    with db_service.session_scope() as session:
        guild_config = get_or_create_for_guild_config(dcguild, session=session)

        GUILDS_WITH_CONFIGS.add(dcguild.id)
        if activity is not None:
            guild_config.update_activity(activity=activity)
            if activity:
                ACTIVITY_GUILDS.add(dcguild.id)
            else:
                ACTIVITY_GUILDS.remove(dcguild.id)
        
        guild_config.update_channels(error_id=error_id, welcome_id=welcome_id, boost_id=boost_id, log_id=log_id)


def get_all_activity_guilds() -> set[int]:
    with db_service.session_scope() as session:
        guild_query = (session.query(Guild.guild_dc_id)
                    .join(GuildConfig, full=True)
                    .filter(GuildConfig.activity_status is True)
                    )
        guild_ids = set(guild_query.all())
        return guild_ids
    

def get_all_guilds_with_configs() -> set[int]:
    with db_service.session_scope() as session:
        guild_query = (session.query(Guild.guild_dc_id)
                    .join(GuildConfig, full=True)
                    .filter(GuildConfig.guild_id == Guild.id)
                    )
        guild_ids = set(guild_query.all())
        return guild_ids


def get_or_create_for_guild_config(dcguild: discord.Guild, session: Session) -> GuildConfig:
    """creates all relevant models for the activity updates"""
    guild = db_service.get_or_create(Guild, session=session, guild_dc_id=dcguild.id, name=dcguild.name)
    session.flush()
    guild_config = db_service.get_or_create(GuildConfig, session=session, guild_id = guild.id)
    session.commit()
    return guild_config