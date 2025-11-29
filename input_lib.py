from rich import print
def split_list(text:str):
    index=[]
    output=text.split(',')
    for i in output:
        if '-' in i:
            each=i.split('-')
            if each.__len__()>2:
                raise Exception('格式错误')
            each1=[]
            for i2 in each:
                each1.append(int(i2))
            #each1.reverse()
            each2=each1.copy()
            each2.sort()
            if each1[0]!=each2[0]:
                raise Exception('格式错误')
            else:
                for i2 in range(each1[0],each1[-1]+1):
                    index.append(i2-1)
        elif i.isdigit():
            index.append(int(i)-1)
        else:
            raise Exception('格式错误')
    
    output_tuple=list(set(index))
    output_tuple.sort()

    return output_tuple