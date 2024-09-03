import discord
from dataclasses import dataclass
import datetime


@dataclass
class StartTime():
    guild_id: int = None
    start_time: datetime.datetime = None
    voice_channel: discord.VoiceChannel = None


# TODO: Consider that a user can be in multiple voice channels at once by using multiple devices
class UserStartTime():
    def __init__(self):
        self.times: dict[int, StartTime] = {}