import discord
from dbmodels.base import SessionLocal
from dbmodels import Activity, Guild, Member, User
from .dbservice import DatabaseService
from.general_helpers import get_valid_attributes
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from utils import settings


logger=settings.logging.getLogger("discord")


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
        _,_,_, activity = get_or_create_for_activity(dcuser, session)
        
        if activity:
            activity.update_member_activity(minutes, messages, xp)


#region LEADERBOARD
def handle_guild_leaderboard(dcuser: discord.Member, sort_by: str = 'xp', limit: int = 10):
    try:
        if sort_by not in get_valid_attributes(Activity):
            raise ValueError(f"Invalid sorting attribute: {sort_by}")
    except ValueError as e:
        logger.exception(f"{e}")
        return
    guild_id = dcuser.guild.id
    with db_service.session_scope() as session:
        activity_query = (session.query(Activity)
                          .join(Member).join(Guild)
                          .filter(Guild.guild_dc_id == guild_id)
                          .order_by(desc(getattr(Activity, sort_by)))
                          .limit(limit)
                          )
        activities = activity_query.all()

        activity_dict_list = list[dict]
        for activity in activities:
            activity_dict_list.append(activity.to_dict())

#endregion

#region DEBUG
# TODO: Error handling when user is type discord.User?
def handle_stats_command(dcuser: discord.Member) -> dict:
    with db_service.session_scope() as session:
        _, _, _, activity = get_or_create_for_activity(dcuser, session)
        return activity.to_dict()

def display_test(dcuser: discord.User | discord.Member) -> str:
    with db_service.session_scope() as session:
        user, guild, member, activity = get_or_create_for_activity(dcuser, session)
        return f"{user.name} with id: {member.id} in guild: {member.guild.guild_dc_id} = {guild.name} and msg_count: {activity.message_count}"
#endregion

#region GENEREAL USE
# TODO: consider Named Tuple returns
def get_or_create_for_activity(dcuser: discord.User | discord.Member, session: Session) -> tuple[User, Guild, Member, Activity]:
    user = db_service.get_or_create(User, user_id=dcuser.id, name=dcuser.global_name, session=session)
    guild = db_service.get_or_create(Guild, guild_dc_id=dcuser.guild.id, name=dcuser.guild.name, session=session)
    session.flush()
    member = db_service.get_or_create(Member, user=user, guild=guild, server_name=guild.name, session=session)
    session.flush()
    activity = db_service.get_or_create(Activity, member=member, session=session)
    return user, guild, member, activity
#endregion