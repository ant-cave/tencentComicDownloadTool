import requests
import json
import js_lib as jl
import output_lib as ol

print('请输入 关键字|漫画id：')
keyword = input('>')

comic_list_page=requests.get('https://ac.qq.com/Comic/searchList?search='+keyword)
comic_list=jl.search_comic(comic_list_page.text)

ol.print_comic_table(comic_list)

while 1:
    comic_id = input('输入漫画id或序号：')

    if comic_id.isdigit():
        if int(comic_id)>=100000:
            #是id
            pass
        else:
            #是序号
            comic_id = comic_list[int(comic_id)-1][0]
        break
    else:
        print('输入错误')

url = 'https://ac.qq.com/ComicView/index/id/'+str(comic_id)+'/cid/'
for i in range(10):
    res = requests.get(url+str(i)).text
    if '该漫画不存在' not in res:
        break

with open('output.json','w+',encoding='utf-8') as f:
    f.write(json.dumps(jl.encode(res),ensure_ascii=False,indent=4))
    #f.write(json.dumps(jl.find_chapter(res),indent=4))

print('done!')