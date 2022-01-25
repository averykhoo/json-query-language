import math
import re


def match_jql(jql, json_obj) -> bool:
    # sanity checks (non-recursive)
    if not isinstance(jql, (dict, list, str, int, float, type(None), tuple)):
        raise TypeError(jql)
    if not isinstance(json_obj, (dict, list, str, int, float, type(None))):
        raise TypeError(json_obj)

    # start matching
    match jql, json_obj:

        # recursively expand tuple of match options
        case (*_, ), _:
            print(f'checking jql options: {jql} -> {json_obj}')
            return any(match_jql(sub_jql, json_obj) for sub_jql in jql)

        # approximate float match
        case float(_), float(_):
            print(f'checking fuzzy float match: {jql} -> {json_obj}')
            if math.isnan(jql) and math.isnan(json_obj):
                return True
            return jql == json_obj or abs(jql - json_obj) < 1e-15

        # equal numbers
        case float(_), int(_):
            print(f'checking float/int match: {jql} -> {json_obj}')
            return jql == json_obj
        case int(_), float(_):
            print(f'checking int/float match: {jql} -> {json_obj}')
            return jql == json_obj
        case int(_), int(_):
            print(f'checking int match: {jql} -> {json_obj}')
            return jql == json_obj

        # exact string match
        case str(_), str(_):
            print(f'checking string match: {jql} -> {json_obj}')
            return jql == json_obj

        # regex match
        # todo: match or search or fullmatch
        case p, str(_) if isinstance(p, re.Pattern):
            print(f'checking regex match: {jql} -> {json_obj}')
            if p.fullmatch(json_obj) is None:
                return False

        # check if jql dict is a subtree of json dict
        case dict(_), dict(_):
            print(f'checking subtree: {jql}, {json_obj}')

            # fast exit if jql has more keys
            if len(jql) > len(json_obj):
                return False

            # fast exist if any keys are missing
            if any(key not in json_obj for key in jql if key is not Ellipsis):
                return False

            # check each key and value
            for key, value in jql.items():

                # handle ..., which must not overlap with other jql keys
                if key is Ellipsis:
                    for other_key in json_obj:
                        if other_key not in jql and match_jql(value, json_obj[other_key]):
                            break
                    else:
                        return False
                    continue

                # handle keys which are primitives
                else:
                    if not match_jql(value, json_obj[key]):
                        return False

            # no failed matches
            return True

        # jql specifies objects in a list
        case dict(_), list(_):
            print(f'checking list elems: {jql} -> {json_obj}')
            for key, value in jql.items():
                # handle ellipsis
                # todo: handle negative keys too!
                if key is Ellipsis:
                    for i, elem in enumerate(json_obj):
                        if i not in jql and match_jql(value, elem):
                            break
                    else:
                        return False
                    continue

                if not isinstance(key, int):
                    return False
                if key >= len(json_obj):
                    return False
                if not match_jql(value, json_obj[key]):
                    return False
            return True

        # list fuzzy match for a list
        case list(_), list(_):
            print(f'checking list: {jql} -> {json_obj}')
            raise NotImplementedError  # todo

        # this should never happen
        case x, y if x == y:
            print(f'exact: {jql} -> {json_obj}')
            raise RuntimeError(f'unexpected types: {type(jql)}, {type(json_obj)}')

        # non-match
        case _:
            print(f'non-match: {jql} -> {json_obj}')
            return False


if __name__ == '__main__':
    print(match_jql({1: 1, 3: (12, 1, 2, 3), ...: 2}, {1: 1, 2: 2, 3.0: 3.0, 4: 4}))
