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
    # todo: don't use recursion, use a stack
    def _match(_jql, _json_obj):
        return match_jql(jql, json_obj, relative_tolerance=relative_tolerance)

    # start matching
    match jql, json_obj:

        # (special case) Ellipsis matches anything
        case e, _ if e is Ellipsis:
            print(f'matching Ellipsis: {json_obj}')
            return True

        # (special case) recursively expand tuple of match options
        case tuple(_), _:
            print(f'checking jql options: {jql} -> {json_obj}')
            for sub_jql in jql:
                if _match(sub_jql, json_obj):
                    return True
            return False  # note that an empty tuple will always fail to match

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
        # todo: refactor this out into a separate function
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
        # todo: refactor this out into a separate function
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
            return len(json_obj) == 0

        # simple list matching: every element must match
        case list(_), list(_) if Ellipsis not in jql:
            print(f'checking simple list: {jql} -> {json_obj}')
            if all(elem is not Ellipsis for elem in jql):
                if len(jql) != len(json_obj):
                    return False
                for elem, other_elem in zip(jql, json_obj):
                    if not _match(elem, other_elem):
                        return False
                return True

        # list fuzzy match for a list
        # todo: refactor this out into a separate function
        case list(_), list(_):
            print(f'checking list fuzzy match: {jql} -> {json_obj}')

            # start from the right side and match every non-Ellipsis element
            query_right_idx = len(jql) - 1
            object_right_idx = len(json_obj) - 1
            while jql[query_right_idx] is not Ellipsis:
                if not _match(jql[query_right_idx], json_obj[object_right_idx]):
                    return False
                query_right_idx -= 1
                object_right_idx -= 1

            # the right query pointer is now at the rightmost Ellipsis
            # if this is the 0th item in the jql, then that is a successful wildcard match
            if query_right_idx == 0:
                return True

            # otherwise, we need to start matching from the left side of the jql
            query_left_idx = 0
            object_left_idx = 0
            while True:

                # if the left and right query pointers meet, it's a successful wildcard match
                if query_left_idx == query_right_idx:
                    assert jql[query_left_idx] is Ellipsis
                    return True

                # if the left query pointer is not an Ellipsis, check if it matches and keep going
                if jql[query_left_idx] is not Ellipsis:
                    if not _match(jql[query_left_idx], json_obj[object_left_idx]):
                        return False
                    query_left_idx += 1
                    object_left_idx += 1
                    continue

                # advance the left query pointer until it is not an Ellipsis
                # and remember to check if the left and right query pointers meet
                # but this should only happen if the jql contains multiple Ellipsis-es next to each other
                # which is not particularly useful, but not an error either, so we'll handle it appropriately
                while jql[query_left_idx] is Ellipsis:
                    query_left_idx += 1
                    if query_left_idx == query_right_idx:
                        assert jql[query_left_idx] is Ellipsis
                        return True

                # now we advance the left object pointer until it matches the left query element
                # and remember to check if the left and right object pointers meet
                # note that the right object pointer is always at the rightmost unmatched element
                while object_left_idx <= object_right_idx:
                    # if there's a successful match, advance the left query pointer and object pointer
                    # and continue matching the remainder of the jql
                    if _match(jql[query_left_idx], json_obj[object_left_idx]):
                        query_left_idx += 1
                        object_left_idx += 1
                        break
                    # otherwise, advance the left object pointer and try again
                    object_left_idx += 1

                # if there is no matching element, then this match is not possible
                else:
                    return False

                # continue matching the remainder of the jql
                continue

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
