import os
import json
from pathlib import Path

##################### temp vc paths
temp_vc_fp = "modules/TemporaryVoiceChannel/json/"
temp_vc_json = "modules/TemporaryVoiceChannel/json/tempchannels.json"
temp_creation_vc_json = "modules/TemporaryVoiceChannel/json/tempcreationvc.json"


##################### role paths
join_roles_json = "modules/Autoroles/json/autoroles.json"
LINKED_ROLES_FILE: Path = Path("modules/Linkedroles/json/linkedroles.json")


##################### guild logging
guild_log_json = "tables/guildchannels.json"



#################### wordle
WORDLE_WORDS: Path = Path("utils/Wordle/valid-wordle-words.txt")


#region IMAGES
##################### images
discord_logo = "img/discord_logo.jpg"
discord_logo_name="discord_logo.jpg"



#region ATTACHEMENTS
def attach(filename: str) -> str:
    return f"attachment://{filename}"
#endregion
#endregion

#region CHECKS
def json_exists(path: str) -> bool:
    return os.path.isfile(path)

def create_empty_json(path: str) -> None:
    if not os.path.isfile(path):
        empty_dict = {}
        with open(path, "w") as f:
            json.dump(empty_dict, f, indent=4)
#endregion