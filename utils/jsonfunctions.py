import json

# update json file for join roles and temp voice
def update_autorole(filepath: str, guildid, key, value, retcode):
    with open(filepath, "r+") as f:
        data = json.load(f)
        guildid, key, value = str(guildid), str(key), str(value)

        if guildid in data:
            if key in data[guildid]:
                retcode += 1
                return retcode

        if guildid not in data:
            data[guildid] = {key: value}

        data[guildid].update({key: value})

        f.seek(0)

        json.dump(data, f, indent=4)

        return retcode

# update json for linked roles
def update_linkedrole(filepath: str, guildid, key, value, retcode):
    with open(filepath, "r+") as f:
        with open("modules/Linkedroles/json/linkedroles.json", "r+") as f: 
            data = json.load(f)

            guild_id, role_id , linked_role_id = str(guildid), str(key), str(value)

            if guild_id not in data:
                data[guild_id] = {}
            
            if role_id not in data[guild_id]:
                data[guild_id][role_id] = []

            if linked_role_id in data[guild_id][role_id]:
                retcode += 1
                return retcode

            data[guild_id][role_id].append(linked_role_id)
        
            f.seek(0)
       
            json.dump(data, f, indent=4)

            return retcode
        
# TODO: include enum! 0 = Success, 1 = No links on server, 2 = Role has no links 3 = No links between roles
def remove_update_linkedrole(filepath: str, role, linked_role):
    with open("modules/Linkedroles/json/linkedroles.json", "r+") as f: 
            data = json.load(f)

            guild_id, role_id, linked_role_id = str(role.guild.id), str(role.id), str(linked_role.id)

            if guild_id not in data or not data[guild_id]:
                data[guild_id] = {}
                return 1
                        
            if role_id not in data[guild_id]:
                return 2

            if linked_role_id in data[guild_id][role_id]:
                if len(data[guild_id][role_id]) == 1:
                    #data[guild_id][role_id].clear()
                    data[guild_id].pop(role_id)
                else:
                    data[guild_id][role_id].remove(linked_role_id)

            else:
                return 3
        
            f.seek(0)
            f.truncate()
       
            json.dump(data, f, indent=4)

            return 0