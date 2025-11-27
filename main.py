import requests
import json
import js_lib as jl
import input_lib as il
import output_lib as ol

from rich import print

class MainApplication:
    def __init__(self):
        pass

    def start(self):
        
        print('[yellow]请输入[/yellow][green]标题关键字[/green][yellow]或[/yellow][green]漫画id[/green][yellow]:[/yellow]')
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
        come_back=result
        if come_back==None:
            self.start()
        come_back=self.choose_chapter_to_download(result)
        
        if come_back==None:
            self.start()
    
    def show_comic_info_by_id(self, comic_id):
        url = 'https://ac.qq.com/ComicView/index/id/'+str(comic_id)+'/cid/'
        comic_url='https://ac.qq.com/Comic/comicInfo/id/'


        try:

            res = requests.get(comic_url+str(comic_id)).text
            chapters=jl.search_chapter_from_comic(res)

            example_chapter=chapters[0][1]

            res = requests.get('https://ac.qq.com/'+str(example_chapter)).text

            meta_data=jl.encode(res)
            print('[cyan][bold]动漫数据')
            ol.print_comic_info(meta_data['comic'])
            print('[cyan][bold]章节列表')
            if  len(chapters)>10:
                __times=0
                for i in chapters[:9]:
                    __times+=1
                    print(f"[cyan]{__times}[/cyan] [green]{i[0]}[/green]")
                print('[cyan]... 章节过多 仅显示前9章 ...[/cyan]')

            else:
                for i in chapters:
                    print(f"[cyan]{i[0]}.[/cyan] {i[1]}")
            print('[bold][cyan]共有'+str(len(chapters))+'章')
            return meta_data
        except IndexError:
            print('[red]漫画信息不正确![/red]')
        except ValueError:
            print('[red]漫画信息不正确![/red]')
        except requests.RequestException:
            print('[red]连接错误 请检查网络')
        except Exception as e:
            print('[red]未知错误 请报告以下信息')
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
    
    def choose_chapter_to_download(self,meta_data,content):
        print('[yellow]请选择章节:')
        input_text=input('> ')
        print('-'*50)
        try:
            splited=il.split_list(input_text)
        except Exception as e:
            print('[red]输入格式错误 请重新选择章节')
            return self.choose_chapter_to_download(meta_data)

        if len(splited)>len(meta_data['chapter_list']):
            print('[red]章节超出范围 请重新选择章节[/red]')
            return self.choose_chapter_to_download(meta_data)
        
        print('[yellow]确定要下载'+str(splited.__len__())+'个章节吗？(y/n)')

        if 'Y' not in input('> ').capitalize():
            print('-'*50)
            return None
        print('-'*50)
        print(splited)

        if len(splited)>5:
            print('[yellow]章节较多，下载可能需要较长时间，请耐心等待...[/yellow]')






main=MainApplication()
main.start()