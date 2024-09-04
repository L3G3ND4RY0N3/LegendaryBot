import discord
from dataclasses import dataclass
import datetime as dt


@dataclass
class SessionData():
    """A dataclass that stores the ids for the guild and channel and the relevant time of a members voice state"""
    guild_id: int = None
    voice_channel_id: int = None
    start_time: dt.datetime = None


    def update_session_data(self, guild_id: int | None = None, channel_id: int | None = None, time: dt.datetime | None = None) -> None:
        """Updates the session data, if guild, voice channel changes or time gets updated"""
        if guild_id:
            self.guild_id = guild_id
        if channel_id:
            self.voice_channel_id = channel_id
        if time:
            self.start_time = time


# TODO: Consider that a user can be in multiple voice channels at once by using multiple devices
class SessionManager():
    """A very simple session manager that keeps track of a members session in a voicechannel"""
    def __init__(self):
        self.sessions: dict[int, SessionData] = {}


    def add_session(self, member_id: int, guild_id: int, channel_id: int) -> None:
        """Adds the session of a member, if the member has already a session ongoing, skip"""
        time = dt.datetime.now()
        # TODO: find a satisfying fix to allow a member to be in multiple channels at once (uuid?)
        if member_id in self.sessions.keys():
            return
        self.sessions[member_id] = SessionData(guild_id=guild_id, voice_channel_id=channel_id, start_time=time)


    def get_session_for_member(self, member_id: int) -> SessionData | None:
        """Returns the SessionData for a member or None if not found"""
        return self.sessions.get(member_id, None)


    def remove_session(self, member_id) -> SessionData | None:
        return self.sessions.pop(member_id, None)


    def update_session(self, member_id: int, guild_id: int | None = None, channel_id: int| None = None, time: dt.datetime | None = None) -> None:
        """Updates the session, if a member joins, leaves or switches voice channels"""
        if member_id not in self.sessions.keys():
            # TODO: Check if this could lead to issues with race conditions (e.g. member gets updated at the same time he leaves the channel)
            # self.add_session(member_id, guild_id, channel_id)
            return
        self.sessions[member_id].update_session_data(guild_id=guild_id, channel_id=channel_id, time=time)


    def get_guild_member(self, client: discord.Client, member_id: int) -> discord.Member | None:
        """recreates the guild member for the given member_id from the session"""
        member_session = self.sessions.get(member_id, None)
        if not member_session:
            return None
        guild = client.get_guild(member_session.guild_id)
        # remove the session if neither the guild nor the member exists
        if not guild:
            self.remove_session(member_id)
            return None
        member = guild.get_member(member_id)
        if not member:
            self.remove_session(member_id)
            return None
        return member

        