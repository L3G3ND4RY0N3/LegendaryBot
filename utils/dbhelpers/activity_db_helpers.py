from typing import Tuple
from constants.enums import ActivityStats
import discord
from dbmodels.base import SessionLocal
from dbmodels import Activity, Guild, Member, User
from .dbservice import DatabaseService
from.general_helpers import get_valid_attributes
from sqlalchemy import func, desc, Row
from sqlalchemy.orm import aliased, Session
from utils import settings


logger=settings.logging.getLogger("discord")


db_service = DatabaseService(SessionLocal)

def handle_activity_update(dcuser: discord.Member, minutes: int | None = None, messages: int| None = None, xp: int| None = None) -> None:
    """handles all activity database updates

    Args:
        dcuser (discord.Member): A discord member
        minutes (int, optional): Minutes in VOice to add to activity. Defaults to 0.
        messages (int, optional): Message count to add. Defaults to 0.
        xp (int, optional): Xp to add. Defaults to 0.
    """
    with db_service.session_scope() as session:
        _,_,_, activity = get_or_create_for_activity(dcuser, session)
        
        if activity:
            activity.update_member_activity(minutes=minutes, messages=messages, xp=xp)


#region LEADERBOARD
def handle_leaderboard_command(dcuser: discord.Member, sort_by: str = ActivityStats.XP, limit: int = 10, guild_only: bool = True) -> str:
    """handles the leaderboard command"""
    try:
        if sort_by not in get_valid_attributes(Activity):
            raise ValueError(f"Invalid sorting attribute: {sort_by}")
    except ValueError as e:
        logger.exception(f"{e}")
        return
    if guild_only:
        return get_guild_leaderboard(dcuser, sort_by, limit)
    else:
        return get_global_leaderboard(sort_by, limit)


def get_guild_leaderboard(dcuser: discord.Member, sort_by: str = ActivityStats.XP, limit: int = 10) -> str:
    """queries the guild for the top ten activities"""
    guild_id = dcuser.guild.id
    with db_service.session_scope() as session:
        activity_query = (session.query(Activity)
                        .join(Member, full=True).join(Guild, full=True)
                        .filter(Guild.guild_dc_id == guild_id)
                        .order_by(desc(getattr(Activity, sort_by)))
                        .limit(limit)
                        )
        activities = activity_query.all()
        # create table
        if activities:
            return format_leaderboard_table(activities)
        # To handle guild without activities (yet)
        return ""
    

def get_global_leaderboard(sort_by: str = 'xp', limit: int = 10) -> str:
    """queries all activities for the top ten users"""
    with db_service.session_scope() as session:
        total_xp = func.sum(Activity.xp).label('total_xp')
        total_messages = func.sum(Activity.message_count).label('total_messages')
        total_voice_minutes = func.sum(Activity.minutes_in_voice).label('total_voice_minutes')

        # Map the sort_by options to the corresponding aggregates
        aggregates = {
            'xp': total_xp,
            'message_count': total_messages,
            'minutes_in_voice': total_voice_minutes
    }
        activity_query = (
        session.query(
            User,
            total_xp,
            total_messages,
            total_voice_minutes
        )
        .join(Member.user)
        .join(Activity, full=True)
        .group_by(User.id)
        .order_by(desc(aggregates[sort_by]))
        .limit(limit)
        )
        activities = activity_query.all()
        # create table
        return format_leaderboard_table(activities)
#endregion

# TODO: Rank Command
#region RANK COMMAND
def get_user_stats_with_position(dcuser: discord.Member) -> str:
    with db_service.session_scope() as session:
        _, guild, _, _ = get_or_create_for_activity(dcuser, session)
        # Aliases for subqueries
        MemberAlias1 = aliased(Member)
        MemberAlias2 = aliased(Member)
        MemberAlias3 = aliased(Member)
        ActivityAlias1 = aliased(Activity)
        ActivityAlias2 = aliased(Activity)
        ActivityAlias3 = aliased(Activity)

        # Subquery for XP position
        xp_position_subquery = (
            session.query(func.count(MemberAlias1.id) + 1)
            .join(ActivityAlias1, MemberAlias1.id == ActivityAlias1.member_id)
            .filter(
                MemberAlias1.user_id == User.id,
                guild.id == MemberAlias1.guild_id,
                ActivityAlias1.xp > func.sum(Activity.xp).label('user_xp')
            )
        ).as_scalar()

        # Subquery for VC Minutes position
        vc_minutes_position_subquery = (
            session.query(func.count(MemberAlias2.id) + 1)
            .join(ActivityAlias2, MemberAlias2.id == ActivityAlias2.member_id)
            .filter(
                MemberAlias2.user_id == User.id,
                guild.id == MemberAlias2.guild_id,
                ActivityAlias2.minutes_in_voice > func.sum(Activity.minutes_in_voice).label('user_minutes')
            )
        ).as_scalar()

        # Subquery for Message Count position
        msg_count_position_subquery = (
            session.query(func.count(MemberAlias3.id) + 1)
            .join(ActivityAlias3, MemberAlias3.id == ActivityAlias3.member_id)
            .filter(
                MemberAlias3.user_id == User.id,
                guild.id == MemberAlias3.guild_id,
                ActivityAlias3.message_count > func.sum(Activity.message_count).label('user_messages')
            )
        ).as_scalar()

        # Main query to get the user stats and positions
        query = (
            session.query(
                func.sum(Activity.xp).label('total_xp'),
                func.sum(Activity.minutes_in_voice).label('total_minutes'),
                func.sum(Activity.message_count).label('total_messages'),
                User,
                xp_position_subquery.label("xp_position"),
                vc_minutes_position_subquery.label("vc_minutes_position"),
                msg_count_position_subquery.label("msg_count_position"),
            )
            .join(Member, Member.user_id == User.id)
            .join(Activity, Activity.member_id == Member.id)
            .join(Guild, Guild.id == Member.guild_id)
            .filter(User.user_id == dcuser.id, Guild.guild_dc_id == dcuser.guild.id)
            .group_by(User.id)
        )

        # Execute the query and fetch the result
        result = query.one_or_none()
        ret_str = format_member_rank(result)
    return ret_str


def format_member_rank(position_tuple: Row[tuple[int, int, int, User, int, int, int]]):
    xp, minutes, message_count, user, xp_pos, minutes_pos, message_pos = position_tuple
    return f"{user.name}, You have {xp} xp, {xp_pos}. Pos., {message_count} messages, {message_pos}. Pos., You have {minutes} minutes in voice, {minutes_pos}. Pos."
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
        return f"{activity.member.user.name} with id: {member.id} in guild: {member.guild.guild_dc_id} = {guild.name} and msg_count: {activity.message_count}"
#endregion

#region GENEREAL USE
# TODO: consider Named Tuple returns
def get_or_create_for_activity(dcuser: discord.Member, session: Session) -> tuple[User, Guild, Member, Activity]:
    """creates all relevant models for the activity updates"""
    user = db_service.get_or_create(User, user_id=dcuser.id, name=dcuser.global_name, session=session)
    session.flush()
    guild = db_service.get_or_create(Guild, guild_dc_id=dcuser.guild.id, name=dcuser.guild.name, session=session)
    session.flush()
    member = db_service.get_or_create(Member, user_id=user.id, guild_id=guild.id, server_name=guild.name, session=session)
    session.flush()
    activity = db_service.get_or_create(Activity, member_id=member.id, session=session)
    return user, guild, member, activity


# TODO: broaden to also allow for use for general leaderboard
# TODO: Add abbreviations for powers of 10 to not destroy table alignement
def format_leaderboard_table(activities: list[Activity] | list[Row[Tuple[Member, int, int, int]]]) -> str:
    """Creates and formats a table for the guild activity leaderboard"""
    # spacing is for alignment
    header = ["Pos.", "    Member", "Messages", "VC Minutes", "    Exp"]
    rows = []
    if isinstance(activities[0], Row):
        for idx, row in enumerate(activities, start=1):
            user, total_xp, total_messages, total_voice_minutes = row
            rows.append(
                f"{idx:<4} | {user.name:>10} | {total_messages:>8} | {total_voice_minutes:>10}| {total_xp:>7} "
            )
    else:
        for idx, activity in enumerate(activities, start=1):
            rows.append(f"{idx:<4} | {activity.member.user.name:>10} | {activity.message_count:>8} | {activity.minutes_in_voice:>10} | {activity.xp:>7}")

    table = f"{' | '.join(header)}\n"
    table += "-" * len(table) + "\n"
    table += "\n".join(rows)

    return table
#endregion