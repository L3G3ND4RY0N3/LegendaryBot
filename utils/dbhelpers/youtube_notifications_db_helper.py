from dataclasses import dataclass
from dbmodels.base import SessionLocal
from dbmodels import YouTubeNotification
from .dbservice import DatabaseService
from sqlalchemy.orm import Session
from utils import settings


logger=settings.logging.getLogger("discord")
db_service = DatabaseService(SessionLocal)


@dataclass
class YouTubeNotificationConfig:
    discord_channel_id: int
    youtube_channel_id: str
    last_video_id: str | None
    custom_message: str | None
    role_id: int | None
    enabled: bool


def handle_yt_notificatin_update(
        channel_id: int,
        youtube_channel_id: int,
        custom_message: str | None,
        role_id: int | None,
        last_video_id: str | None,
        enabled: bool = True
        ) -> None:
    with db_service.session_scope() as session:
        yt_config = get_or_create_for_yt(channel_id=channel_id,
                            youtube_channel_id=youtube_channel_id,
                            session=session,
                            custom_message=custom_message,
                            role_id=role_id,
                            enabled=enabled)
        
        if last_video_id:
            yt_config.last_video_id = last_video_id
        

def get_all_Youtube_Notifications(only_enabled: bool = False) -> list[YouTubeNotificationConfig]:
    with db_service.session_scope() as session:
        notifications = session.query(YouTubeNotification).all()
        config_list = []
        for note in notifications:
            if not note.enabled and only_enabled:
                continue
            config = YouTubeNotificationConfig(
                discord_channel_id = note.discord_channel_id,
                youtube_channel_id = note.youtube_channel_id,
                last_video_id = note.last_video_id,
                custom_message = note.custom_message,
                role_id = note.role_id,
                enabled=note.enabled
            )
            config_list.append(config)
        return config_list
    

def get_or_create_for_yt(
        channel_id: int,
        youtube_channel_id: int,
        session: Session,
        custom_message: str | None,
        role_id: int | None,
        enabled: bool = True) -> YouTubeNotification:
    yt_notification = db_service.get_or_create(
        YouTubeNotification,
        discord_channel_id = channel_id,
        youtube_channel_id = youtube_channel_id,
        custom_message = custom_message,
        role_id = role_id,
        enabled = enabled,
        session=session)
    session.flush()
    return yt_notification
