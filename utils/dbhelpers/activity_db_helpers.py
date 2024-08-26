import discord
from dbmodels.base import SessionLocal
from dbmodels import Activity, Member, User
from .dbservice import DatabaseService


db_service = DatabaseService(SessionLocal)

def handle_activity_update(dcuser: discord.User, minutes: int = 0, messages: int = 0, xp: int = 0) -> dict | None:
    with db_service.session_scope() as session:
        user = db_service.get_or_create(User, user_id=dcuser.id, name=dcuser.global_name)
        session.add(user)
        member = db_service.get_or_create(Member, user_id=user.id)
        session.add(member)
        activity = db_service.get_or_create(Activity, member_id=member.id)
        
        if activity:
            activity.update_member_activity(minutes, messages, xp)
