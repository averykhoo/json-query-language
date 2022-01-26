import math
import re


def match_jql(jql: dict | list | str | int | float | bool | None | tuple | type(Ellipsis),
              json_obj: dict | list | str | int | float | bool | None,
              *,
              relative_tolerance: float | int = 1e-15,
              ) -> bool:
    # sanity checks (non-recursive)
    if not isinstance(jql, (dict, list, str, int, float, bool, type(None), tuple, type(...))):
        raise TypeError(jql)
    if not isinstance(json_obj, (dict, list, str, int, float, bool, type(None))):
        raise TypeError(json_obj)
    if not isinstance(relative_tolerance, (int, float)):
        raise TypeError(relative_tolerance)
    if not 0 <= relative_tolerance < 1:
        raise ValueError(relative_tolerance)

    # lazy convenience method to curry in the relative tolerance
    # it would be much better to build an internal stack of [(jql, json_obj), ...]
    # because this laziness will exhaust the recursion limit twice as fast
    # todo: don't use recursion
    def _match(_jql, _json_obj):
        return match_jql(jql, json_obj, relative_tolerance=relative_tolerance)

    # start matching
    match jql, json_obj:

        # (special case) Ellipsis matches anything
        case e, _ if e is Ellipsis:
            print(f'matching Ellipsis: {json_obj}')
            return True

        # (special case) recursively expand tuple of match options
        case (*_, ), _:
            print(f'checking jql options: {jql} -> {json_obj}')
            for sub_jql in jql:
                if _match(sub_jql, json_obj):
                    return True
            return False

        # None matches None
        case None, None:
            print('matching None -> None')
            return True

        # exact match for boolean values
        # note that bool must be checked before int because bool is a subclass of int
        case bool(_), bool(_):
            print(f'checking bool match: {jql} -> {json_obj}')
            return jql == json_obj

        # boolean values cannot match non-boolean values
        # this prevents bool from matching ints
        case (bool(_), _) | (_, bool(_)):
            print('non-bool value in bool match')
            return False

        # approximate float match
        # this is to account for possible floating point errors in a json parser
        # 64-bit doubles have about 16 decimal digits of precision, but 32-bit floats have only 7
        # it is reasonable for a json parser to be unable to handle 128-bit quad precision
        # this is why the default is 1e-15, which should (probably?) be within what any parser can handle
        # on a 32-bit pc, maybe set this to 1e-5 or 1e-6
        case float(_), float(_):
            print(f'checking fuzzy float match: {jql} -> {json_obj}')
            if math.isnan(jql) and math.isnan(json_obj):
                return True
            return jql == json_obj or math.isclose(jql, json_obj, rel_tol=relative_tolerance)

        # numerically equivalent floats / ints
        case float(_) | int(_), float(_) | int(_):
            print(f'checking numeric match: {jql} -> {json_obj}')
            return jql == json_obj

        # exact string match
        case str(_), str(_):
            print(f'checking string match: {jql} -> {json_obj}')
            return jql == json_obj

        # regex match
        # todo: which is the most appropriate? re.match / re.search / re.fullmatch
        case p, str(_) if isinstance(p, re.Pattern):
            print(f'checking regex match: {jql} -> {json_obj}')
            if p.fullmatch(json_obj) is None:
                return False

        # check if jql dict is a subtree of json dict
        case dict(_), dict(_):
            print(f'checking subtree: {jql}, {json_obj}')

            # fast exist on empty dict
            if not jql:
                print('empty dict')
                return True

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
                        if other_key not in jql and _match(value, json_obj[other_key]):
                            break
                    else:
                        return False
                    continue

                # handle keys which are primitives
                elif not _match(value, json_obj[key]):
                    return False

            # no failed matches
            return True

        # jql dict specifies objects by index in a list
        case dict(_), list(_):
            print(f'checking list elems: {jql} -> {json_obj}')

            # fast exit on empty dict
            if not jql:
                print('empty dict')
                return True

            # fast exit if any keys are invalid
            if any(not isinstance(key, int) for key in jql if key is not Ellipsis):
                return False

            # fast exit if any keys are missing
            if any(not -len(json_obj) <= key < len(json_obj) for key in jql if key is not Ellipsis):
                return False

            # check each key and value in jql matches a corresponding list element
            for key, value in jql.items():
                # handle ellipsis
                if key is Ellipsis:
                    for i, elem in enumerate(json_obj):
                        if i not in jql and (i - len(json_obj)) not in jql and _match(value, elem):
                            break
                    else:
                        return False
                    continue

                # keys must be ints which specify valid positions in the list
                if not isinstance(key, int):
                    return False
                if not -len(json_obj) <= key < len(json_obj):
                    return False

                # recursively check element matches
                if not _match(value, json_obj[key]):
                    return False

            # no failed matches
            return True

        # special case for empty list jql, which can only match an empty list
        case [], list(_):
            return not json_obj

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
    print(match_jql(True, None))
