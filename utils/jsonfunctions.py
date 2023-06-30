import json

def update(filepath: str, id, key, value):
    with open(filepath, "r+") as f:
        data = json.load(f)
        id, key, value = str(id), str(key), str(value)

        if id not in data:
            data[id] = {key: value}

        data[id].update({key: value})

        f.seek(0)

        json.dump(data, f, indent=4)
