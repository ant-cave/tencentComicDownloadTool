#!/usr/bin/env python3
"""腾讯漫画下载工具 - 支持交互式和非交互式命令行模式"""

import argparse
import requests
import js_lib as jl
import input_lib as il
import output_lib as ol
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich import print
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn


class MainApplication:
    def __init__(self):
        self.output_path = 'download'
        self.lang = 'zh-cn'
        self.langd = {'zh-cn': {
            'input_id_or_name.info': '[yellow]请输入[/yellow][green]标题关键字[/green][yellow]或[/yellow][green]漫画id[/green][yellow]:[/yellow]',
            'input_id_or_name.error.invalid_id': '[red]输入错误 请重新输入。',
            'search.error.invalid_comic': '[red]没有找到该漫画[/red]',
            'search.error.network_not_available': '[red]网络异常[/red]',
            'exit': '[red]程序已退出',
            'error.unkown': '[red]未知错误 请报告[/red]',
        }}
        self.langc = self.langd[self.lang]

    # ═══════════════════════════════════════════
    # 原有交互模式（完全保留，未改动）
    # ═══════════════════════════════════════════

    def start(self):
        while True:
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

                        def download_chapter(chapter_index):
                            try:
                                self.download(meta_data, chapter_index)
                                progress.update(total_task, advance=1)
                            except Exception as e:
                                print(f'[red]章节 {chapter_index + 1} 下载失败: {e}')
                                raise e

                        # 使用4线程线程池下载章节
                        failed_chapters = []
                        with ThreadPoolExecutor(max_workers=4) as executor:
                            futures = {executor.submit(download_chapter, ci): ci for ci in chosen}
                            for future in as_completed(futures):
                                try:
                                    future.result()
                                except Exception:
                                    failed_chapters.append(futures[future])

                    # 下载完成提示
                    success_count = total_chapters - len(failed_chapters)
                    if success_count == total_chapters:
                        print(f'[green]所有 {total_chapters} 个章节下载完成！[/green]')
                    else:
                        print(f'[yellow]下载完成：成功 {success_count} 个章节，失败 {len(failed_chapters)} 个章节[/yellow]')
                        if failed_chapters:
                            print(f'[red]失败的章节：{[ci + 1 for ci in failed_chapters]}[/red]')
                            print('[yellow]是否重试失败的章节？(y/n)')
                            if input('> ').strip().upper().startswith('Y'):
                                print('[yellow]开始重试失败的章节...[/yellow]')
                                retry_success = 0
                                for ci in failed_chapters:
                                    try:
                                        print(f'[yellow]重试章节 {ci + 1}...[/yellow]')
                                        self.download(meta_data, ci)
                                        retry_success += 1
                                        print(f'[green]章节 {ci + 1} 重试成功！[/green]')
                                    except Exception as e:
                                        print(f'[red]章节 {ci + 1} 重试失败: {e}[/red]')
                                if retry_success > 0:
                                    print(f'[green]重试完成：成功 {retry_success}/{len(failed_chapters)} 个章节[/green]')
                                else:
                                    print('[red]所有重试均失败[/red]')

                except KeyboardInterrupt:
                    continue

            except KeyboardInterrupt:
                print(self.langc['exit'])
                return 0

    def download(self, meta_data, index):
        chapter_url = f"https://ac.qq.com/{meta_data['chapters'][index][1]}"
        res = requests.get(chapter_url, timeout=10).text
        chapter_meta = jl.encode(res)
        chapter_name = chapter_meta['chapter']['cTitle']
        pic_list = chapter_meta['picture']
        chapter_path = f"{self.output_path}/{meta_data['comic']['title']}/{index + 1}_{chapter_name}"
        os.makedirs(chapter_path, exist_ok=True)

        total_images = len(pic_list)
        print(f'[cyan]正在下载章节 {index + 1}: {chapter_name} (共 {total_images} 张图片)[/cyan]')

        session = requests.Session()

        def download_image(url, save_path):
            with open(save_path, 'wb') as f:
                f.write(session.get(url, timeout=10).content)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(download_image, pic['url'], f"{chapter_path}/{i + 1:04d}.jpg")
                for i, pic in enumerate(pic_list)
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f'[red]下载失败: {e}')

    def get_index_to_download(self, meta_data):
        print('[yellow]请选择章节: [/yellow][white](如"1,2,4"; "1-9,5-6"; "1,2,5-10")')
        while True:
            input_text = input('> ')
            print('-' * 50)
            try:
                split_result = il.split_list(input_text)
                if max(split_result) >= len(meta_data['chapters']):
                    print(f'[red]章节超出范围（1-{len(meta_data["chapters"])}），请重新选择[/red]')
                    continue
                break
            except Exception:
                print('[red]输入格式错误 请重新选择章节[/red]')

        print(f'[yellow]确定要下载 {len(split_result)} 个章节吗？(y/n)')
        if not input('> ').strip().upper().startswith('Y'):
            print('-' * 50)
            return None
        print('-' * 50)
        return split_result

    def get_comic_content(self):
        print('-' * 50)
        is_id, value = self.input_id_or_name()
        if is_id:
            return self.get_search_result_by_id(value)
        return self.get_search_result_by_name(value)

    def input_id_or_name(self) -> tuple[bool, str]:
        '''
        return:
            (bool,str)
            bool: True 输入的是id, str 返回id值
            bool: False 输入的是名称, str 返回名称值
        '''
        print(self.langc['input_id_or_name.info'])
        while True:
            input_str = input('> ').strip()
            if not input_str:
                continue
            if input_str.isdigit():
                if len(input_str) <= 4:
                    print(self.langc['input_id_or_name.error.invalid_id'])
                    continue
                return (True, input_str)
            return (False, input_str)

    def get_search_result_by_id(self, comic_id: str) -> dict | None:
        try:
            res = requests.get(f'https://ac.qq.com/Comic/comicInfo/id/{comic_id}', timeout=10).text
            chapters = jl.search_chapter_from_comic(res)
            if not chapters:
                print(self.langc['search.error.invalid_comic'])
                return self.get_comic_content()

            example_chapter = chapters[0][1]
            res = requests.get(f'https://ac.qq.com/{example_chapter}', timeout=10).text
            inner_chapter_data = jl.encode(res)

            return {
                'comic': inner_chapter_data['comic'],
                'chapters': chapters,
            }
        except IndexError:
            print(self.langc['search.error.invalid_comic'])
        except ValueError:
            print(self.langc['search.error.invalid_comic'])
        except requests.RequestException:
            print(self.langc['search.error.network_error'])
        except Exception as e:
            print(self.langc['error.unkown'])
            print(e)
        return self.get_comic_content()

    def get_search_result_by_name(self, name) -> dict | None:
        comic_id = self.search_comic_by_name(name)
        if comic_id is None:
            return None
        return self.get_search_result_by_id(comic_id)

    def search_comic_by_name(self, keyword) -> str | None:
        url = f'https://ac.qq.com/Comic/searchList?search={keyword}'
        comic_list_page = requests.get(url, timeout=10)
        comic_list = jl.search_comic(comic_list_page.text)
        if not comic_list:
            print('[red]没有找到该漫画![/red]')
            return None
        ol.print_comic_table(comic_list)

        while True:
            print('[yellow]请输入: 序号')
            input_text = input('>')
            print('-' * 50)
            try:
                return comic_list[int(input_text) - 1][0]
            except IndexError:
                print('[red]序号不正确[/red]')
            except ValueError:
                print('[red]序号格式不正确[/red]')

    def show_comic_info(self, meta_data):
        print('[cyan][bold]动漫数据')
        ol.print_comic_info(meta_data['comic'])
        chapters = meta_data['chapters']
        print('[cyan][bold]章节列表')
        times = 0

        display_count = min(len(chapters), 9)
        for idx in range(display_count):
            print(f"[cyan]{idx + 1}[/cyan] [green]{chapters[idx][0]}[/green]")
        if len(chapters) > 9:
            print(f'[cyan]... 章节过多 共 [yellow]{len(chapters)}[/yellow] 仅显示前9章 ...[/cyan]')

    # ═══════════════════════════════════════════
    # 新增：非交互式命令行 API
    # ═══════════════════════════════════════════

    def search_comic(self, keyword: str) -> list:
        """搜索漫画，返回 [(id, title), ...]"""
        url = f'https://ac.qq.com/Comic/searchList?search={keyword}'
        r = requests.get(url, timeout=10)
        return jl.search_comic(r.text)

    def get_comic_meta(self, comic_id: str) -> dict | None:
        """获取漫画元数据: {comic: {...}, chapters: [(title, url), ...]}"""
        try:
            res = requests.get(f'https://ac.qq.com/Comic/comicInfo/id/{comic_id}', timeout=10).text
            chapters = jl.search_chapter_from_comic(res)
            if not chapters:
                return None
            example_chapter = chapters[0][1]
            res = requests.get(f'https://ac.qq.com/{example_chapter}', timeout=10).text
            inner = jl.encode(res)
            return {'comic': inner['comic'], 'chapters': chapters}
        except Exception as e:
            print(f'[red]获取漫画信息失败: {e}[/red]')
            return None

    def download_chapter(self, meta: dict, index: int):
        """下载指定索引的单个章节（0-based）"""
        chapter_url = f"https://ac.qq.com/{meta['chapters'][index][1]}"
        res = requests.get(chapter_url, timeout=10).text
        chapter_meta = jl.encode(res)
        chapter_name = chapter_meta['chapter']['cTitle']
        pic_list = chapter_meta['picture']
        chapter_path = f"{self.output_path}/{meta['comic']['title']}/{index + 1}_{chapter_name}"
        os.makedirs(chapter_path, exist_ok=True)

        total = len(pic_list)
        print(f'[cyan]下载章节 {index + 1}: {chapter_name} ({total} 张图)[/cyan]')

        session = requests.Session()
        def dl_img(url, save_path):
            with open(save_path, 'wb') as f:
                f.write(session.get(url, timeout=10).content)

        with ThreadPoolExecutor(max_workers=4) as pool:
            futs = [
                pool.submit(dl_img, pic['url'], f"{chapter_path}/{i + 1:04d}.jpg")
                for i, pic in enumerate(pic_list)
            ]
            for f in as_completed(futs):
                try:
                    f.result()
                except Exception as e:
                    print(f'[red]图片下载失败: {e}[/red]')
        print(f'[green]章节 {index + 1} 完成，保存在 {chapter_path}[/green]')

    def download_chapters(self, meta: dict, indices: list[int]):
        """批量下载多个章节"""
        total = len(indices)
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        ) as progress:
            total_task = progress.add_task("总进度", total=total)

            def worker(ci):
                try:
                    self.download_chapter(meta, ci)
                    progress.update(total_task, advance=1)
                except Exception as e:
                    print(f'[red]章节 {ci + 1} 下载失败: {e}[/red]')
                    raise e

            failed = []
            with ThreadPoolExecutor(max_workers=4) as pool:
                futs = {pool.submit(worker, ci): ci for ci in indices}
                for f in as_completed(futs):
                    try:
                        f.result()
                    except Exception:
                        failed.append(futs[f])

            ok = total - len(failed)
            if ok == total:
                print(f'[green]全部 {total} 个章节下载完成！[/green]')
            else:
                print(f'[yellow]完成 {ok}/{total}，失败 {len(failed)} 个章节[/yellow]')


# ═══════════════════════════════════════════
# 命令行入口
# ═══════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='腾讯漫画下载工具 - 不加参数进入交互模式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py -i 545320 -c 1                # 下载非人哉第1章
  python main.py -i 545320 -c 1,3,5-8         # 下载非人哉第1、3、5-8章
  python main.py -s 非人哉 -c 1                # 搜索"非人哉"然后下载第1章
  python main.py -s 非人哉 --list              # 搜索并列出章节
  python main.py -i 545320 -c 1 -o ./manga     # 指定输出目录
  python main.py                                # 交互模式
        """,
    )
    parser.add_argument('-i', '--id', help='漫画ID')
    parser.add_argument('-s', '--search', help='搜索漫画名称')
    parser.add_argument('-c', '--chapters', help='要下载的章节，如 "1" "1,3,5" "1-5" "1,3,5-10"')
    parser.add_argument('--list', action='store_true', help='仅列出章节，不下载')
    parser.add_argument('-o', '--output', default='download', help='下载目录 (默认: download)')

    args = parser.parse_args()

    app = MainApplication()

    # ── 无参数 → 原交互模式 ──
    if not args.id and not args.search:
        app.start()
        return

    # ── 有参数 → 非交互模式 ──
    app.output_path = args.output

    # 1. 确定漫画ID
    comic_id = args.id
    if args.search:
        comics = app.search_comic(args.search)
        if not comics:
            print('[red]没有找到匹配的漫画[/red]')
            sys.exit(1)
        if len(comics) > 1:
            print(f'[yellow]找到多个结果，使用第一个: {comics[0][1]} (ID: {comics[0][0]})[/yellow]')
        comic_id = comics[0][0]
        print(f'[green]漫画: {comics[0][1]} (ID: {comic_id})[/green]')

    if not comic_id:
        print('[red]未指定漫画ID[/red]')
        sys.exit(1)

    # 2. 获取元数据
    meta = app.get_comic_meta(comic_id)
    if meta is None:
        print('[red]获取漫画信息失败[/red]')
        sys.exit(1)

    print(f'[green]漫画: {meta["comic"]["title"]}，共 {len(meta["chapters"])} 章[/green]')

    # 3. --list 仅列出章节
    if args.list:
        print(f'[cyan]章节列表 (共 {len(meta["chapters"])} 章):[/cyan]')
        for idx, ch in enumerate(meta['chapters']):
            print(f'  [{idx + 1}] {ch[0]}')
        return

    # 4. 下载章节
    if not args.chapters:
        print('[red]请使用 -c 指定要下载的章节[/red]')
        sys.exit(1)

    indices = il.split_list(args.chapters)
    if max(indices) >= len(meta['chapters']):
        print(f'[red]章节超出范围 (1-{len(meta["chapters"])})[/red]')
        sys.exit(1)

    print(f'[green]开始下载 {len(indices)} 个章节...[/green]')
    app.download_chapters(meta, indices)


if __name__ == '__main__':
    main()
