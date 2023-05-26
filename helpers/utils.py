import os.path
from typing import Dict, List


def split_dict_by_keys(target: Dict, max_count: int = 500) -> List[Dict]:
    result = []
    dict_keys = list(target.keys())

    for i in range(0, len(dict_keys), max_count):
        sub_dict = {
            key: target[key]
            for key in dict_keys[i:i + max_count]
        }
        result.append(sub_dict)

    return result


def get_path(path: str) -> str:
    path = os.path.abspath(os.path.join(os.getcwd(), path))
    dirname = os.path.dirname(path) if os.path.isfile(path) or '.' in os.path.basename(path) else path
    os.makedirs(dirname, exist_ok=True)
    return path
