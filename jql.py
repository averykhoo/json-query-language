import json
import math
import re


def match_jql(jql, json_obj) -> bool:
    # test that the json_obj is really json
    json.dumps(json_obj)  # todo: do something less stupid, or at least only check once

    match jql, json_obj:

        # tuple of match options
        case (*_, ), _:
            print(f'checking jql options: {jql} -> {json_obj}')
            return any(match_jql(sub_jql, json_obj) for sub_jql in jql)

        case float(_), float(_):
            print(f'checking fuzzy float match: {jql} -> {json_obj}')
            if math.isnan(jql) and math.isnan(json_obj):
                return True
            return jql == json_obj or abs(jql - json_obj) < 1e-15

        case int(_), int(_):
            print(f'checking int match: {jql} -> {json_obj}')
            return jql == json_obj

        case str(_), str(_):
            print(f'checking string match: {jql} -> {json_obj}')
            return jql == json_obj

        case p, str(_) if isinstance(p, re.Pattern):
            print(f'checking regex match: {jql} -> {json_obj}')
            if __name__ == '__main__':
                return jql.match(json_obj) is not None

        # jql is a subtree of json_obj
        case {**__}, {**__}:
            print(f'checking subtree: {jql}, {json_obj}')
            raise NotImplementedError  # todo

        # jql specifies objects in a list
        case {**__}, [*_]:
            print(f'checking list elems: {jql} -> {json_obj}')
            for key in jql.keys():
                if key is Ellipsis:
                    raise NotImplementedError  # todo
                if not isinstance(key, int):
                    return False
                if not 0 <= key < len(json_obj):
                    return False
            raise NotImplementedError

        # list fuzzy match for a list
        case [*data_1], [*data_2]:
            print(f'checking list: {jql} -> {json_obj}')
            raise NotImplementedError

        # this should never happen
        case (x, y) if x == y:
            print(f'exact: {jql} -> {json_obj}')
            raise RuntimeError(f'unexpected types: {type(jql)}, {type(json_obj)}')

        # non-match
        case _:
            print(f'non-match: {jql} -> {json_obj}')
            return False


if __name__ == '__main__':
    print(match_jql((1, 2, float('inf'), re.compile('1+')), '11'))
