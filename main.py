import requests
import json
import js_lib as jl
import output_lib as ol

from rich import print

class MainApplication:
    def __init__(self):
        pass

    def start(self):
        
        print('[yellow]请输入:[/yellow] [green]标题关键字[/green]|[green]漫画id[/green]')
        input_text=input('> ')
        print('-'*50)

        result=None
        if input_text.isdigit():
            if int(input_text)<9000:
                print('[red]漫画id格式不正确[/red]')
                self.start()
            else:
                comic_id=input_text
                result=self.show_comic_info_by_id(comic_id)
        else:
            result=self.choose_comic(input_text)
        
        if result==None:
            self.start()
    
    def show_comic_info_by_id(self, comic_id):
        url = 'https://ac.qq.com/ComicView/index/id/'+str(comic_id)+'/cid/'
        comic_url='https://ac.qq.com/Comic/comicInfo/id/'


        try:

            res = requests.get(comic_url+str(comic_id)).text

            example_chapter=jl.search_chapter_from_comic(res)[0][1]

            res = requests.get('https://ac.qq.com/'+str(example_chapter)).text

            meta_data=jl.encode(res)
            print('[cyan][bold]动漫数据')
            ol.print_comic_info(meta_data['comic'])
            return meta_data
        except IndexError:
            print('[red]漫画信息不正确![/red]')
        except ValueError:
            print('[red]漫画信息不正确![/red]')
        except requests.RequestException:
            print('[red]连接错误 请检查网络')
        except Exception as e:
            print('[red]未知错误 请报告以下信息')
            print('[red]'+e.with_traceback())
            print(e)

        return None
    
    def choose_comic(self,keyword):
        comic_list_page=requests.get('https://ac.qq.com/Comic/searchList?search='+keyword)
        comic_list=jl.search_comic(comic_list_page.text)
        if comic_list.__len__()==0:
            print('[red]没有找到该漫画![/red]')
            return None
        ol.print_comic_table(comic_list)

        while 1:
            print('[yellow]请输入: 序号')
            input_text=input('>')
            print('-'*50)
            try:
                comic_id = comic_list[int(input_text)-1][0]
                break
            except IndexError:
                print('[red]序号不正确')
            except ValueError:
                print('[red]序号格式不正确')
        return self.show_comic_info_by_id(comic_id)



main=MainApplication()
main.start()