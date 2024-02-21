import json
from utils import filepaths as fp
from utils import settings

logger=settings.logging.getLogger("discord")


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
            if data[key]["activity tracker"] != 0:
                activity_ids.append(int(key))
        except KeyError as e:
            logger.error(f"Key error for {key} or activity tracker!")
            continue

#endregion
            

#region "Functions"
            
######## called when a guild is joined or the /guild_setup command is called
def initialise_guild_setup(guild_id: str):
    retcode = 0
    with open(fp.guild_log_json, "r+") as f:
        data = json.load(f)

        if guild_id in data: #if guild is already registered return, as this is just the basic setup with no modification intentions
            retcode -1
            return retcode

        else: #else add the guild with basic settings
            data[guild_id] = {"error channel": 0, "log channel": 0, "welcome channel": 0, "boost channel" : 0, "activity tracker": 0}
        
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


####### called to update the json for a specific channel
def update_guild_channel(guild_id: str, channel_id: int, channel: str):
    retcode = 0
    with open(fp.guild_log_json, "r+") as f:
        data = json.load(f)

        if guild_id not in data: #if the guild is not in the data send an error code
            retcode = -1
            return retcode

        else: #else modify the specific channel
            try:
                data[str(guild_id)][channel] = channel_id
            except KeyError:
                logger.error(f"Key error for {guild_id} or {channel}!")
        
        f.seek(0)
        json.dump(data, f, indent=4)
    return retcode

#endregion