from enum import Enum


#region Guild Logging 
class GuildChannelStatus(Enum):
    Active = 1
    Inactive = 0
    GuildNotSet = -1


class GuildChannelTypes(Enum):
    ERROR = "error"
    LOG = "log"
    WELCOME = "welcome"
    BOOST = "boost"
    ACTIVITY = "activity"
#endregion


class VoiceChannelStatus(Enum):
    NotInOwnVoice = "NotInOwnVoice"
    AloneInVoice = "AloneInVoice"
    InOwnVoice = "InOwnVoice"