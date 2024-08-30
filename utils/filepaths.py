import os
import json
from pathlib import Path

##################### temp vc paths
TEMP_VC_FP = Path("modules/TemporaryVoiceChannel/json/")
TEMP_VC_JSON = Path("modules/TemporaryVoiceChannel/json/tempchannels.json")
TEMP_CREATION_VC_JSON = Path("modules/TemporaryVoiceChannel/json/tempcreationvc.json")


##################### role paths
JOIN_ROLES_JSON = Path("modules/Autoroles/json/autoroles.json")
LINKED_ROLES_FILE = Path("modules/Linkedroles/json/linkedroles.json")


##################### guild logging
GUILD_LOG_JSON = Path("tables/guildchannels.json")



#################### wordle
WORDLE_WORDS = Path("utils/Wordle/valid-wordle-words.txt")
WORDLE_ANSWER_WORDS = Path("utils/Wordle/wordle_answers.txt")


#region IMAGES
##################### images
DISCORD_LOGO_IMG = Path("img/discord_logo.jpg")
DISCORD_LOGO_NAME = "discord_logo.jpg"



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
        with open(path, "w") as f:
            json.dump({}, f, indent=4)
#endregion