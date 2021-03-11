"""
resource: https://github.com/ryantuck/fix-roam
Update all Roam UIDs to enable re-importing exported notes.
"""
import json
import random
import string


def generate_uid():
    """
    Generates a 9-digit UID that adheres to Roam's UID namespace.
    """
    namespace = string.ascii_uppercase + string.ascii_lowercase + \
        string.digits + "-_"
    return "".join(random.choice(namespace) for _ in range(9))


def find_uids(data, uid_map):
    """
    Recursively find all UIDs for blocks and
    update UID_MAP to map them to new values.
    """
    if isinstance(data, list):
        return [find_uids(x, uid_map) for x in data]
    if isinstance(data, dict):
        if "uid" in data:
            existing_uid = data["uid"]
            if existing_uid in uid_map:
                new_uid = uid_map[existing_uid]
            else:
                new_uid = generate_uid()
                uid_map[existing_uid] = new_uid
        return {k: find_uids(v, uid_map) for k, v in data.items()}
    return data


def fix_roam(blacklist, json_content):
    """
    Read Roam JSON export and return a valid Roam JSON file with updated UIDs.
    """
    uid_map = dict()

    # read in graph
    graph = json.loads(json_content)

    # traverse the entire graph and populate UID_MAP, mapping old to new UIDs
    _ = find_uids(graph, uid_map)
    assert set(uid_map.keys()) & set(uid_map.values()) == set()

    # filter to notes that Roam will actually accept
    valid_notes = [note for note in graph if not note["title"] in blacklist]

    # create JSON string blob, swap out old UIDs with new values
    # NOTE: it'd be nice if this were more efficient
    body = json.dumps(valid_notes, indent=2, ensure_ascii=False)
    for existing_uid, new_uid in uid_map.items():
        body = body.replace(existing_uid, new_uid)
    return body
