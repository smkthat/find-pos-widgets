def split_dict_by_keys(target: dict, max_count: int = 500) -> list[dict]:
    result = []
    dict_keys = list(target.keys())

    for i in range(0, len(dict_keys), max_count):
        sub_dict = {
            key: target[key]
            for key in dict_keys[i:i + max_count]
        }
        result.append(sub_dict)

    return result
