from enum import Enum


#region Guild Logging 
class GuildChannelStatus(Enum):
    Active = 1
    Inactive = 0
    GuildNotSet = -1


class GuildChannelTypes(Enum):
    """Only add or remove entrys when updating the guild model for guild config!"""
    ERROR = "error"
    LOG = "log"
    WELCOME = "welcome"
    BOOST = "boost"
    ACTIVITY = "activity"
#endregion

#region VOICE
class VoiceChannelStatus(Enum):
    NotInOwnVoice = "NotInOwnVoice"
    AloneInVoice = "AloneInVoice"
    InOwnVoice = "InOwnVoice"
#endregion

class ActivityStats(Enum):
    XP = "xp"
    MESSAGES = "message_count"
    VOICEMINUTES = "minutes_in_voice"

#region LINKED Roles
class LRRetCode(Enum):
    SUCCESS = 0
    FAIL_CIRCULAR = 1
#endregion