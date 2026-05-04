from rich.console import Console
from rich.table import Table


def print_comic_table(data, title="漫画列表", headers=None):
    """
    使用 rich 美化打印漫画列表表格。

    :param data: 漫画数据列表，格式为 [(id, title), ...]
    :param title: 表格标题（字符串）
    :param headers: 列标题 [序号列名, 标题列名, ID列名]，可选，默认 ['序号', '标题', 'ID']
    """
    if headers is None:
        headers = ["序号", "标题", "ID"]

    console = Console()

    table = Table(
        title=title,
        show_header=True,
        header_style="bold white",
        show_lines=False,
        box=None
    )

    table.add_column(headers[0], style="cyan", justify="right", no_wrap=True, width=4)
    table.add_column(headers[1], style="green", justify="left", overflow="fold", width=40)
    table.add_column(headers[2], style="green", justify="right", no_wrap=True, width=12)

    for idx, (comic_id, title_name) in enumerate(data):
        table.add_row(str(idx + 1), title_name, comic_id)

    console.print(table)


def print_comic_info(data):
    console = Console()
    table = Table(show_header=False, box=None, width=60)
    table.add_column("", style="cyan", width=15)
    table.add_column("", style="white", width=45)

    mapping = {
        'id': '动漫id',
        'title': '标题',
        'collect': '收藏数',
        'isJapanComic': '日本动漫',
        'isLightNovel': '轻小说',
        'isLightComic': '轻漫画',
        'isFinish': '已完结',
        'isRoastable': '可吐槽',
    }

    for key, label in mapping.items():
        if key not in data:
            continue
        value = data[key]
        if isinstance(value, bool):
            value_str = "[green]是[/green]" if value else "[red]否[/red]"
        else:
            value_str = f'[green]{value}[/green]'
        table.add_row(label, value_str)

    console.print(table)