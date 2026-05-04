def split_list(text: str):
    index = []
    output = text.split(',')
    for i in output:
        if '-' in i:
            bounds = i.split('-')
            if len(bounds) > 2:
                raise Exception('格式错误')
            start, end = int(bounds[0]), int(bounds[1])
            if start > end:
                raise Exception('格式错误')
            for j in range(start, end + 1):
                index.append(j - 1)
        elif i.isdigit():
            index.append(int(i) - 1)
        else:
            raise Exception('格式错误')

    return sorted(set(index))