import json
from utils import filepaths as fp
from utils import settings

logger=settings.logging.getLogger("discord")


# set allowed channels, as they are in the JSON file:
allowed_channels = ["error", "log", "welcome", "boost"]


#region "Properties"
#Property
##### list to store the server ids with setups for quick access
ids = []


#Loading the Property
##### loads the guild ids from the json into memory (list)
def load_json_to_guild_id_list():
    with open(fp.guild_log_json, "r") as f:
        data = json.load(f)
        
    for key in data:
        ids.append(int(key))


#Property
##### list with guilds with active activity tracker
activity_ids = []


#Loading the Property
##### loads the guild ids from the json into memory (list)
def load_json_to_activity_id_list():
    with open(fp.guild_log_json, "r") as f:
        data = json.load(f)
    
    for key in data:
        try:
            if data[key]["activity"] != 0:
                activity_ids.append(int(key))
        except KeyError as e:
            logger.error(f"Key error for {key} or activity tracker!")
            logger.exception(f"{e}")
            continue

#endregion
            

#region "Functions"
            
#region "Init Functions"
######## called when a guild is joined or the /guild_setup command is called
def initialise_guild_setup(guild_id: str):
    retcode = 0
    with open(fp.guild_log_json, "r+") as f:
        data = json.load(f)

        if guild_id in data: #if guild is already registered return, as this is just the basic setup with no modification intentions
            retcode -1
            return retcode

        else: #else add the guild with basic settings
            data[guild_id] = {"error": 0, "log": 0, "welcome": 0, "boost" : 0, "activity": 0}
        
        f.seek(0)
        json.dump(data, f, indent=4)
    return retcode


####### called when the bot is removed from a guild
def remove_guild_setup(guild_id: str):
    retcode = 0
    with open(fp.guild_log_json, "r+") as f:
        data = json.load(f)

        if guild_id not in data: #if guild had no setup in json return
            retcode -1
            return retcode

        else: #else remove the guild from the json
            data.pop(guild_id)
        
        f.truncate()
        f.seek(0)
        json.dump(data, f, indent=4)
    return retcode
#endregion


####### check channel status to disable buttons, returns a negative returncode, when operation fails
def check_guild_channel_status(guild_id: str, channel: str) -> int:
    with open(fp.guild_log_json, "r") as f:
        data = json.load(f)
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
def update_guild_channel(guild_id: str, channel_id: int, channel: str) -> int:
    if channel.lower() not in allowed_channels:
        return -1
    with open(fp.guild_log_json, "r+") as f:
        data = json.load(f)
        #if the guild is not in the data send an error code
        if guild_id not in data: 
            return -1
        #else modify the specific channel
        else: 
            try:
                data[guild_id][channel] = channel_id
            except KeyError as e:
                logger.error(f"Key error for {guild_id} or {channel}!")
                logger.exception(f"{e}")
                return -1
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=4)
    return 0


# functiong ONLY for activating the activity feature!
def update_activity_tracker(guild_id: str, status: int) -> int:
    if status not in [0, 1]:
        return -1
    with open(fp.guild_log_json, "r+") as f:
        data = json.load(f)
        #if the guild is not in the data send an error code
        if guild_id not in data: 
            return -1
        #else modify the specific channel
        else: 
            try:
                if status == 1:
                # hard coded activity
                    data[guild_id]["activity"] = 1
                else:
                    data[guild_id]["activity"] = 0
            except KeyError as e:
                logger.error(f"Key error for {guild_id} or activity!")
                logger.exception(f"{e}")
                return -1
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=4)
    return 0

#endregion