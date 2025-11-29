pyinstaller --onefile --clean -i "icon.ico"`
    --upx-dir="F:\Program Files\upx-5.0.2-win64" `
    --exclude-module tkinter `
    --exclude-module asyncio `
    --exclude-module pydoc `
    --exclude-module sqlite3 `
    --exclude-module pandas `
    --exclude-module numpy `
    --exclude-module colorama `
    --exclude-module commonmark `
    --exclude-module markdown `
    --exclude-module pygments `
    .\main.py

    #upx-dir 填写你自己upx.exe的路径