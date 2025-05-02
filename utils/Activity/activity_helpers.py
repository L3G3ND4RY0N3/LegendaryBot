import datetime as dt
import discord
from ..structs.activity_times_data import SessionManager
from utils.dbhelpers.activity_db_helpers import handle_activity_update
from utils.dbhelpers.guild_config_db_helpers import get_all_activity_guild_ids


# Idea to make it more modular, make a call to a new function update user?
# TODO: add more complex logic to allow for difference in currency calculation -> more models...
def update_all_members_in_voice(users_in_voice: SessionManager, bot: discord.Client) -> int:
    user_count = len(user_ids := set(users_in_voice.sessions.keys())) # copy so that no iteration error happens, when a user leaves a channel while update happens
    activity_guilds = get_all_activity_guild_ids()
    for user_id in user_ids:
        if not (session := users_in_voice.get_session_for_member(user_id)):
            continue
        if not (member := users_in_voice.get_guild_member(bot, user_id)):
            continue
        update_time = dt.datetime.now()
        # if the guild is removed while the users were still in voice, just keep updating their times, in case it gets turned back on!
        if member.guild.id not in activity_guilds:
            session.update_session_data(time=update_time)
            continue
        if member_is_mute(member.voice) or len(member.voice.channel.members) < 2:
            session.update_session_data(time=update_time)
            continue
        duration = update_time - session.start_time
        minutes = int(duration.total_seconds() / 60)
        # Award currency for unmuted time
        currency = minutes*20
        handle_activity_update(member, minutes=minutes, xp=currency)
        session.update_session_data(time=update_time)
    return user_count


def member_is_mute(voice_state: discord.VoiceState) -> bool:
    if voice_state.mute or voice_state.self_mute or voice_state.deaf or voice_state.self_deaf:
        return True
    return False