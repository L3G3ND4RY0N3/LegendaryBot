import discord
from dbmodels.base import SessionLocal
from dbmodels import Guild, GuildConfig
from .dbservice import DatabaseService
from sqlalchemy.orm import Session, Query
from utils import settings

from constants.enums import GuildChannelTypes


logger=settings.logging.getLogger("discord")

db_service = DatabaseService(SessionLocal)


def _handle_guild_config_update(dcguild: discord.Guild,
                                error_id: int | None = None,
                                welcome_id: int | None = None,
                                boost_id: int | None = None,
                                log_id: int | None = None,
                                activity: bool | None = None) -> None:
    with db_service.session_scope() as session:
        guild_config = get_or_create_for_guild_config(dcguild, session=session)
        if activity is not None:
            guild_config.update_activity(activity=activity)
        
        guild_config.update_channels(error_id=error_id, welcome_id=welcome_id, boost_id=boost_id, log_id=log_id)


def update_channels_guild_config(guild: discord.Guild, channel_name: str, channel_id: int = 0, activity_status: bool = False) -> None:
    """Function to update the channels using the embeds title"""
    if channel_name == GuildChannelTypes.ERROR.value:
        _handle_guild_config_update(guild, error_id=channel_id)
    elif channel_name == GuildChannelTypes.LOG.value:
        _handle_guild_config_update(guild, log_id=channel_id)
    elif channel_name == GuildChannelTypes.WELCOME.value:
        _handle_guild_config_update(guild, welcome_id=channel_id)
    elif channel_name == GuildChannelTypes.BOOST.value:
        _handle_guild_config_update(guild, boost_id=channel_id)
    elif channel_name == GuildChannelTypes.ACTIVITY.value:
        _handle_guild_config_update(guild, activity=activity_status)
    else:
        raise InvalidChannelName()
    

def get_config_channel_id(config: dict[str, int | bool], channel: str) -> int | bool:
    if not config: # if guild has no config yet
        return 0
    for key, val in config.items():
        if channel in key:
            return val
    raise InvalidChannelName()


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
    

def get_guild_config(guild_id: int) -> dict[str, int | bool]:
    with db_service.session_scope() as session:
        guild_query: Query = (session.query(GuildConfig)
                    .join(Guild)
                    .filter(Guild.guild_dc_id == guild_id)
                    )
        config: GuildConfig = guild_query.first()
        if config is not None:
            config = config.to_dict()
        else:
            config = {}
    return config


def get_or_create_for_guild_config(dcguild: discord.Guild, session: Session) -> GuildConfig:
    """creates all relevant models for the activity updates"""
    guild = db_service.get_or_create(Guild, session=session, guild_dc_id=dcguild.id, name=dcguild.name)
    session.flush()
    guild_config = db_service.get_or_create(GuildConfig, session=session, guild_id = guild.id)
    session.commit()
    return guild_config

class InvalidChannelName(Exception):
    pass