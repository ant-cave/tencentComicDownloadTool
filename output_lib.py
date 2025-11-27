from rich.console import Console
from rich.table import Table

def print_comic_table(data, title="漫画列表", headers=None):
    """
    使用 rich 美化打印漫画列表表格。

    :param data: 漫画数据列表，格式为 [(id, title), ...]
    :param title: 表格标题（字符串）
    :param headers: 列标题 [序号列名, 标题列名, ID列名]，可选，默认 ['序号', '标题', 'ID']
    """
    # 设置默认列名
    if headers is None:
        headers = ["序号", "标题", "ID"]

    console = Console()

    # 创建表格
    table = Table(
        title=title,
        show_header=True,
        header_style="bold white",
        show_lines=False,
        box=None  # 可改为 rich.box.SIMPLE 等增加边框
    )

    # 添加列（注意顺序）- 统一设置列宽
    table.add_column(headers[0], style="cyan", justify="right", no_wrap=True, width=4)
    table.add_column(headers[1], style="green", justify="left", overflow="fold", width=40)
    table.add_column(headers[2], style="green", justify="right", no_wrap=True, width=12)

    # 添加数据行
    for idx, (comic_id, title_name) in enumerate(data):
        table.add_row(str(idx + 1), str(title_name), str(comic_id))

    # 输出
    console.print(table)

def print_comic_info(data):
    console = Console()
    table = Table(show_header=False, box=None, width=60)  # 设置表格总宽度
    table.add_column("", style="cyan", width=15)  # 第一列宽度
    table.add_column("", style="white", width=45)  # 第二列宽度

    # 中文名映射 + 哪些字段要特殊处理（布尔转红/绿）
    mapping = {
        'id': ('动漫id', None),
        'title': ('标题', None),
        'collect': ('收藏数', None),
        'isJapanComic': ('日本动漫', None),
        'isLightNovel': ('轻小说', None),
        'isLightComic': ('轻漫画', None),
        'isFinish': ('已完结', None),
        'isRoastable': ('可吐槽', None),
        # eId 不在这里 → 直接过滤掉
    }

    for key, (label, _) in mapping.items():
        if key not in data:
            continue
        value = data[key]
        # 如果是布尔值：是→红色，否→绿色；其他照常转字符串
        if isinstance(value, bool):
            value_str = "[green]是[/green]" if value else "[red]否[/red]"
        else:
            value_str = str('[green]'+str(value)+'[/green]')
        table.add_row(label, value_str)

    console.print(table)