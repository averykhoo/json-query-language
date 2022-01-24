def match_jql(jql, json_obj) -> bool:
    match jql, json_obj:
        case {}, {**anything}:
            return True

        # if only this worked
        case {key_1: value_1, **data_1}, {key_2: value_2, **data_2} if key_1 == key_2:
            return match_jql(value_1, value_2) and match_jql(data_1, data_2)



if __name__ == '__main__':
    print(match_jql({'a':1}, {1:'a'}))