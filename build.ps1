pyinstaller --onefile --clean `
    --upx-dir="C:\Program Files\upx-5.0.2-win64" `
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
    .\test.py