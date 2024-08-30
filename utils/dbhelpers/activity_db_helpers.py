import discord
from dbmodels.base import SessionLocal
from dbmodels import Activity, Guild, Member, User
from .dbservice import DatabaseService


db_service = DatabaseService(SessionLocal)

def handle_activity_update(dcuser: discord.User | discord.Member, minutes: int = 0, messages: int = 0, xp: int = 0) -> None:
    """handles all activity updates

    Args:
        dcuser (discord.User | discord.Member): A discord user or member
        minutes (int, optional): Minutes in VOice to add to activity. Defaults to 0.
        messages (int, optional): Message count to add. Defaults to 0.
        xp (int, optional): Xp to add. Defaults to 0.
    """
    with db_service.session_scope() as session:
        user = db_service.get_or_create(User, user_id=dcuser.id, name=dcuser.global_name, session=session)
        guild = db_service.get_or_create(Guild, guild_dc_id=dcuser.guild.id, name=dcuser.guild.name, session=session)
        session.flush()
        member = db_service.get_or_create(Member, user=user, guild=guild, server_name=guild.name, session=session)
        session.flush() # call to send the member to the db so activity can access it!
        activity = db_service.get_or_create(Activity, member=member, session=session)
        
        if activity:
            activity.update_member_activity(minutes, messages, xp)
