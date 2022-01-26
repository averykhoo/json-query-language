import math
import re


def match_jql(jql: dict | list | str | int | float | bool | None | tuple | type(Ellipsis),
              json_obj: dict | list | str | int | float | bool | None,
              *,
              float_approx: float | int = 1e-15,
              ) -> bool:
    # sanity checks (non-recursive)
    if not isinstance(jql, (dict, list, str, int, float, bool, type(None), tuple, type(...))):
        raise TypeError(jql)
    if not isinstance(json_obj, (dict, list, str, int, float, bool, type(None))):
        raise TypeError(json_obj)
    if not isinstance(float_approx, (int, float)):
        raise TypeError(float_approx)
    if not 0 <= float_approx < 1:
        raise ValueError(float_approx)

    # start matching
    match jql, json_obj:

        # Ellipsis matches anything
        case e, _ if e is Ellipsis:
            print(f'matching Ellipsis: {json_obj}')
            return True

        # None matches None
        case None, None:
            print('matching None -> None')
            return True

        # recursively expand tuple of match options
        case (*_, ), _:
            print(f'checking jql options: {jql} -> {json_obj}')
            return any(match_jql(sub_jql, json_obj) for sub_jql in jql)  # todo: handle empty tuple!

        # exact match for boolean values
        case bool(_), bool(_):
            print(f'checking bool match: {jql} -> {json_obj}')
            return jql == json_obj
        case bool(_), _:
            return False
        case _, bool(_):
            return False

        # approximate float match
        case float(_), float(_):
            print(f'checking fuzzy float match: {jql} -> {json_obj}')
            if math.isnan(jql) and math.isnan(json_obj):
                return True
            return jql == json_obj or abs(jql - json_obj) <= float_approx

        # numerically equivalent
        case float(_), int(_):
            print(f'checking float -> int match: {jql} -> {json_obj}')
            return jql == json_obj
        case int(_), float(_):
            print(f'checking int -> float match: {jql} -> {json_obj}')
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
            
            # todo: fast exist on empty dict!

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
                elif not match_jql(value, json_obj[key]):
                    return False

            # no failed matches
            return True

        # jql specifies objects in a list
        case dict(_), list(_):
            print(f'checking list elems: {jql} -> {json_obj}')
            
            # todo: fast exit on empty dict!

            # fast exit if any keys are invalid
            if any(not isinstance(key, int) for key in jql if key is not Ellipsis):
                return False

            # fast exit if any keys are missing
            if any(not -len(json_obj) <= key < len(json_obj) for key in jql if key is not Ellipsis):
                return False

            for key, value in jql.items():
                # handle ellipsis
                if key is Ellipsis:
                    for i, elem in enumerate(json_obj):
                        if i not in jql and (i - len(json_obj)) not in jql and match_jql(value, elem):
                            break
                    else:
                        return False
                    continue

                if not isinstance(key, int):
                    return False
                if not -len(json_obj) <= key < len(json_obj):
                    return False
                if not match_jql(value, json_obj[key]):
                    return False
            return True

        # list fuzzy match for a list
        case list(_), list(_):
            # todo:fast exit on empty list!
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
    print(match_jql(None, 1))
