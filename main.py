import requests
import json
import js_lib as jl
import input_lib as il
import output_lib as ol
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


from rich import print
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn

class MainApplication:
    def __init__(self):
        self.output_path='download'
        self.console = Console()
        self.lang = 'zh-cn'
        self.langd={'zh-cn':
            {
            'input_id_or_name.info':'[yellow]请输入[/yellow][green]标题关键字[/green][yellow]或[/yellow][green]漫画id[/green][yellow]:[/yellow]',
            'input_id_or_name.error.invalid_id':'[red]输入错误 请重新输入。',
            'search.error.invalid_comic':'[red]没有找到该漫画[/red]',
            'search.error.network_not_available':'[red]网络异常[/red]',
            'exit':'[red]程序已退出',
            'error.unkown':'[red]未知错误 请报告[/red]',
        }}
        self.langc=self.langd[self.lang]
    
    def start(self):
        while 1:
            try:
                meta_data=self.get_comic_content()
                try:
                    self.show_comic_info(meta_data)
                    chosen=self.get_index_to_download(meta_data)
                    if not chosen:
                        continue
                    
                    # 使用4线程线程池同时下载4个章节，并显示总进度
                    total_chapters = len(chosen)
                    
                    with Progress(
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                        TimeRemainingColumn(),
                    ) as progress:
                        
                        # 创建一个总进度条任务
                        total_task = progress.add_task(f"总进度", total=total_chapters)
                        
                        # 下载章节的函数
                        def download_chapter(chapter_index):
                            try:
                                self.download(meta_data, chapter_index)
                                # 更新总进度条
                                progress.update(total_task, advance=1)
                            except Exception as e:
                                print(f'[red]章节 {chapter_index+1} 下载失败: {e}')
                                raise e
                        
                        # 使用4线程线程池下载章节
                        failed_chapters = []
                        with ThreadPoolExecutor(max_workers=4) as executor:
                            # 提交所有章节下载任务
                            futures = {executor.submit(download_chapter, chapter_index): chapter_index for chapter_index in chosen}
                            
                            # 等待所有任务完成
                            for future in as_completed(futures):
                                try:
                                    future.result()
                                except Exception as e:
                                    chapter_index = futures[future]
                                    failed_chapters.append(chapter_index)
                    
                    # 下载完成提示
                    success_count = total_chapters - len(failed_chapters)
                    if success_count == total_chapters:
                        print(f'[green]所有 {total_chapters} 个章节下载完成！[/green]')
                    else:
                        print(f'[yellow]下载完成：成功 {success_count} 个章节，失败 {len(failed_chapters)} 个章节[/yellow]')
                        if failed_chapters:
                            print(f'[red]失败的章节：{failed_chapters}[/red]')
                            
                            # 询问是否重试失败的章节
                            print('[yellow]是否重试失败的章节？(y/n)')
                            if 'Y' in input('> ').capitalize():
                                print('[yellow]开始重试失败的章节...[/yellow]')
                                
                                # 单线程重试失败的章节
                                retry_success = 0
                                for chapter_index in failed_chapters:
                                    try:
                                        print(f'[yellow]重试章节 {chapter_index+1}...[/yellow]')
                                        self.download(meta_data, chapter_index)
                                        retry_success += 1
                                        print(f'[green]章节 {chapter_index+1} 重试成功！[/green]')
                                    except Exception as e:
                                        print(f'[red]章节 {chapter_index+1} 重试失败: {e}[/red]')
                                
                                if retry_success > 0:
                                    print(f'[green]重试完成：成功 {retry_success}/{len(failed_chapters)} 个章节[/green]')
                                else:
                                    print('[red]所有重试均失败[/red]')
                                    
                except KeyboardInterrupt:
                    continue
                
            except KeyboardInterrupt:
                print(self.langc['exit'])
                return 0

    def download(self,meta_data,index):
            res=requests.get('https://ac.qq.com/'+meta_data['chapters'][index][1]).text
            chapter_meta=jl.encode(res)
            chapter_name=chapter_meta['chapter']['cTitle']
            pic_list=chapter_meta['picture']
            chapter_path=self.output_path+'/'+meta_data['comic']['title']+'/'+str(index+1)+'_'+chapter_name
            try:
                os.makedirs(chapter_path)
            except FileExistsError:
                pass
            
            # 使用4线程线程池下载图片，并显示一个总进度条
            total_images = len(pic_list)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
            ) as progress:
                
                # 创建一个总进度条任务
                total_task = progress.add_task('第'+str(index+1)+'章 '+meta_data['comic']['title']+'\t', total=total_images)
                
                # 下载图片的函数，带进度更新
                def download_image(pic_item):
                    file_path = chapter_path+'/'+str(pic_item['pid'])+'.jpg'
                    with open(file_path, 'wb+') as f:
                        f.write(requests.get(pic_item['url']).content)
                    # 更新总进度条
                    progress.update(total_task, advance=1)
                    return file_path
                
                # 使用4线程线程池下载图片
                with ThreadPoolExecutor(max_workers=4) as executor:
                    # 提交所有任务
                    futures = [executor.submit(download_image, pic_item) for pic_item in pic_list]
                    
                    # 等待所有任务完成
                    for future in as_completed(futures):
                        try:
                            file_path = future.result()
                        except Exception as e:
                            print(f'[red]下载失败: {e}')
    def get_index_to_download(self,meta_data):
        
        print('[yellow]请选择章节: [/yellow][white](如"1,2,4"; "1-9,5-6"; "1,2,5-10")')
        splited=[]
        while 1:
            input_text=input('> ')
            print('-'*50)
            try:
                splited=il.split_list(input_text)
                if max(splited)>len(meta_data['chapters']):
                    print('[red]章节超出范围 请重新选择章节[/red]')
                    continue
                break

            except Exception as e:
                print('[red]输入格式错误 请重新选择章节')


        
        print('[yellow]确定要下载'+str(splited.__len__())+'个章节吗？(y/n)')

        if 'Y' not in input('> ').capitalize():
            print('-'*50)
            return None
        print('-'*50)
        return splited
    
    
    def get_comic_content(self):
        print('-'*50)
        result=self.input_id_or_name()
        if result[0]:
            content=self.get_search_result_by_id(result[1])
        else:
            print('是名称'+str(result[1]))
            content=self.get_search_result_by_name(result[1])
        
        return content
    def input_id_or_name(self)->tuple[bool,str]:
        
        '''
        return:
            (bool,str)
            bool: True输入的是id str返回id值
            bool: False输入的是名称 str返回名称值
        '''
        
        print(self.langc['input_id_or_name.info'])
        input_str=''
        while 1:
            input_str = input('> ')
            if input_str:
                break
        
        if input_str.isdigit(): # 输入的是id
            if input_str.__len__()<=4:
                print(self.langc['input_id_or_name.error.invalid_id'])
                return self.input_id_or_name()
            else:
                return (True, input_str)
        else: # 输入的是名称
            return (False, input_str)
    
    def get_search_result_by_id(self, id:str)->dict|None:
        
        #self.console.clear()
        
        url = 'https://ac.qq.com/ComicView/index/id/'+str(id)+'/cid/'
        comic_url='https://ac.qq.com/Comic/comicInfo/id/'


        try:

            res = requests.get(comic_url+str(id)).text
            chapters=jl.search_chapter_from_comic(res)

            example_chapter=chapters[0][1]

            res = requests.get('https://ac.qq.com/'+str(example_chapter)).text

            inner_chapter_data=jl.encode(res)
            
            meta_data={
                'comic':inner_chapter_data['comic'],
                'chapters':chapters
            }

            return meta_data
        except IndexError:
            print(self.langc['search.error.invalid_comic'])
            return self.get_comic_content()
            
        except ValueError:
            print(self.langc['search.error.invalid_comic'])
            return self.get_comic_content()

            

        except requests.RequestException:
            print(self.langc['search.error.network_error'])
            return self.get_comic_content()

            
        except Exception as e:
            print(self.langc['error.unkown'])
            print(e)
            return self.get_comic_content()

    
    def get_search_result_by_name(self,name)->dict|None:
        tmp=self.search_comic_by_name(name)
        if tmp==None:
            return None
        elif type(tmp)==str:
            return self.get_search_result_by_id(tmp)
    
    def search_comic_by_name(self,keyword)->None|str:
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
                return comic_id
            except IndexError:
                print('[red]序号不正确')
            except ValueError:
                print('[red]序号格式不正确')
        return None
    def show_comic_info(self,meta_data):
        #self.console.clear()
        print('[cyan][bold]动漫数据')
        ol.print_comic_info(meta_data['comic'])
        chapters=meta_data['chapters']
        print('[cyan][bold]章节列表')
        __times=0
        
        if  len(chapters)>10:
            for i in chapters[:9]:
                __times+=1
                print(f"[cyan]{__times}[/cyan] [green]{i[0]}[/green]")
            print('[cyan]... 章节过多 共[yellow]'+str(len(chapters))+'[/yellow][cyan] 仅显示前9章 ...[/cyan]')
        else:
            for i in chapters:
                __times+=1
                
                print(f"[cyan]{__times}[/cyan] [green]{i[0]}.[/green]")

main=MainApplication()
main.start()
