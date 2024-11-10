from dbmodels import Activity, Guild, Member, User
from dbmodels.base import SessionLocal
from .dbservice import DatabaseService
import discord
from sqlite3 import Row
from typing import Iterable
from utils import settings


logger=settings.logging.getLogger("discord")

db_service = DatabaseService(SessionLocal)


def migrate_db_data(bot: discord.Client, old_data: Iterable[Row]) -> bool:
    with db_service.session_scope() as session:
        try:
            for row in old_data:
                user_id, xp, message_count, voice_minutes = row
                dcuser = discord.Client.get_user(bot, user_id)
                if dcuser is None:
                    continue
                user = db_service.get_or_create(User, session=session, user_id=dcuser.id, name=dcuser.global_name)
                guild = db_service.get_or_create(Guild, session=session, name="Terste´s Kinderzimmer", guild_dc_id=618043172047552520) #Id for Terste DC
                session.flush()
                member = db_service.get_or_create(Member, session=session, 
                                                user_id=user.id, 
                                                guild_id=guild.id, 
                                                server_name=guild.name
                                                )
                session.flush()
                # get or create activity, ensure that existing ones will just be updated
                activity = db_service.get_or_create(Activity,
                                                    session=session, 
                                                    member_id=member.id
                                                    )
                # update activity
                activity.update_member_activity(minutes=voice_minutes, messages=message_count, xp=xp)
        except Exception as e:
            logger.exception(f"{e}")
            session.rollback()
            return False
        
        session.commit()
        return True