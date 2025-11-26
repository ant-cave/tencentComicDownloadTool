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

    # 添加列（注意顺序）
    table.add_column(headers[0], style="cyan", justify="right", no_wrap=True)
    table.add_column(headers[1], style="green", justify="left", overflow="fold")
    table.add_column(headers[2], style="green", justify="right", no_wrap=True)

    # 添加数据行
    for idx, (comic_id, title_name) in enumerate(data):
        table.add_row(str(idx + 1), str(title_name), str(comic_id))

    # 输出
    console.print(table)