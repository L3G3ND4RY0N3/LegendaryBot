import json
from utils import filepaths as fp
from utils import settings
from constants import enums as en

logger=settings.logging.getLogger("discord")


# set allowed channels, as they are in the JSON file:
allowed_channels = [en.GuildChannelTypes.ERROR.value, en.GuildChannelTypes.LOG.value, en.GuildChannelTypes.WELCOME.value, en.GuildChannelTypes.BOOST.value]

#region common functions
def is_valid_channel(channel: str) -> bool:
    if channel in allowed_channels:
        return True
    return False


# loading the json into a dict
def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)
    

def save_json(path: str, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    
def update_channel(data: dict, guild_id: str, channel: str, channel_id: int) -> None:
    try:
        data[guild_id][channel] = channel_id
    except KeyError as e:
        logger.error(f"Key error for {guild_id} or {channel}")
        logger.exception(f"{e}")

#endregion

#region "Properties"
#Property
##### set to store the server ids with setups for quick access
ids: set = set()


#Loading the Property
##### loads the guild ids from the json into memory (list)
def load_json_to_guild_id_list():
    data = load_json(fp.guild_log_json)
        
    for key in data:
        ids.add(int(key))


#Property set of INTS
##### set with guild ids with active activity tracker
activity_ids: set = set()


#Loading the Property
##### loads the guild ids from the json into memory (list)
def load_json_to_activity_id_list():
    data = load_json(fp.guild_log_json)
    
    for key in data:
        try:
            if data[key][en.GuildChannelTypes.ACTIVITY.value] != 0:
                activity_ids.add(int(key))
        except KeyError as e:
            logger.error(f"Key error for {key} or activity tracker!")
            logger.exception(f"{e}")
            continue

#endregion
            
#region "Functions"
            
#region "Init Functions"
######## called when a guild is joined or the /guild_setup command is called
def initialise_guild_setup(guild_id: str) -> None:
    try:
        data = load_json(fp.guild_log_json)

        #if guild is already registered return, as this is just the basic setup with no modification intentions
        if guild_id in data:
            return
        #else add the guild with basic settings
        data[guild_id] = {en.GuildChannelTypes.ERROR.value: 0, en.GuildChannelTypes.LOG.value: 0, en.GuildChannelTypes.WELCOME.value: 0, en.GuildChannelTypes.BOOST.value : 0, en.GuildChannelTypes.ACTIVITY.value: 0}
        save_json(fp.guild_log_json, data)
        return
    
    except Exception as e:
        logger.error(f"An error occured while trying to add a guild setup: {e}")
        logger.exception(f"{e}")


####### called when the bot is removed from a guild
def remove_guild_setup(guild_id: str) -> int:
    try:
        data = load_json(fp.guild_log_json)

        if guild_id not in data: #if guild had no setup in json return
            return -1

        #else remove the guild from the json
        data.pop(guild_id)
        save_json(fp.guild_log_json, data)
        return 0
    except Exception as e:
        logger.error(f"An error occured while trying to remove a guild setup: {e}")
        logger.exception(f"{e}")
        return -1
#endregion


####### check channel status to disable buttons, returns a negative returncode, when operation fails
def check_guild_channel_status(guild_id: str, channel: str, path=fp.guild_log_json) -> int:
    data = load_json(path)
    #if the guild is not in the data send an error code
    if guild_id not in data: 
        return -1
    # if channel is zero, the return zero e.g. meaning "Not Active"
    if data[guild_id][channel] == 0:
        return 0
    # else return 1, e.g. "Active"
    else:
        return 1


####### called to update the json for a specific channel
def update_guild_channel(guild_id: str, channel_id: int, channel: str, path=fp.guild_log_json) -> int:
    if not is_valid_channel(channel):
        logger.error(f"Invalid channel: {channel}")
        return -1
    try:
        data = load_json(path)
        #if the guild is not in the data send an error code
        if guild_id not in data: 
            return -1
        #else modify the specific channel
        update_channel(data, guild_id, channel, channel_id)
        save_json(path, data)    
        return 0

    except Exception as e:
        logger.error(f"An error occured: {e}")
        logger.exception(f"{e}")
        return -1


# functiong ONLY for activating the activity feature!
def update_activity_tracker(guild_id: str, status: int, path=fp.guild_log_json) -> int:
    if status not in [0, 1]:
        logger.error(f"Invalid status: {status}")
        return -1
    data = load_json(path)
    try:
        #if the guild is not in the data send an error code
        if guild_id not in data:
            return -1
        #else modify the Activity channel specifically
        update_channel(data, guild_id, en.GuildChannelTypes.ACTIVITY.value, status)
        activity_ids.add(guild_id)
        save_json(path, data)
        return 0
            
    except Exception as e:
        logger.error(f"An error occured: {e}")
        logger.exception(f"{e}")
        return -1
    

# gets the channel id for the requested channel type of the guild or 0 if guild not found or not enabled for that channel
# TODO: return data form check function
def get_guild_channel(guild_id: str, channel: str, path=fp.guild_log_json) -> int|None:
    """Checks the status of the specified channel in the json for the guild and returns thhe channel id, if found, if not None

    Args:
        guild_id (str): The id of the guild as a string for the json
        channel (str): The channel type, as the enum requires (value)
        path (str, optional): The file path of the json. Defaults to fp.guild_log_json.

    Returns:
        int: The channel id
    """
    if check_guild_channel_status(guild_id, channel) != 1:
        return None
    data = load_json(path)

    return data[guild_id][channel]

#endregion