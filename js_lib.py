def get_nonce(res:str):
    import execjs
    import time
    for i in range(5):
        try:
            nonce=res[res.index('window["n'):]

            nonce=nonce[:nonce.index(';')]

            res=res.replace(nonce,'')

            nonce=res[res.index('window["n'):]

            nonce=nonce[:nonce.index(';')]

            nonce=nonce[nonce.index('=')+1:]

            nonce=execjs.eval(nonce)
            return nonce
        except:
            time.sleep(0.1)

    raise Exception('nonce error')
    return None

def get_data(res:str):
    
    data=res[res.index('var DATA = ')+12:]
    data=data[:data.index(',')-1]
    return data
def encode(res:str):

    nonce=get_nonce(res)
    data=get_data(res)
    def Base():
        _keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        
        def decode(c):
            a = ""
            b = d = h = f = g = e = 0
            import re
            c = re.sub(r'[^A-Za-z0-9\+\/\=]', "", c)  # Note: Python doesn't have g flag, so we use sub with no count
            while e < len(c):
                b = _keyStr.index(c[e])
                e += 1
                d = _keyStr.index(c[e])
                e += 1
                f = _keyStr.index(c[e])
                e += 1
                g = _keyStr.index(c[e])
                e += 1
                b = b << 2 | d >> 4
                d = (d & 15) << 4 | f >> 2
                h = (f & 3) << 6 | g
                a += chr(b)
                if f != 64:
                    a += chr(d)
                if g != 64:
                    a += chr(h)
            return utf8_decode(a)
        
        def utf8_decode(c):
            a = ""
            b = 0
            d = c1 = c2 = 0
            while b < len(c):
                d = ord(c[b])
                if d < 128:
                    a += chr(d)
                    b += 1
                elif 191 < d and d < 224:
                    c2 = ord(c[b + 1])
                    a += chr((d & 31) << 6 | c2 & 63)
                    b += 2
                else:
                    c2 = ord(c[b + 1])
                    c3 = ord(c[b + 2])
                    a += chr((d & 15) << 12 | (c2 & 63) << 6 | c3 & 63)
                    b += 3
            return a
        
        return decode

    import json
    W={'DATA':data,'nonce':nonce}
    

    B = Base()
    T = list(W['DA' + 'TA'])  # split('') equivalent in Python is list()
    N = W['n' + 'onc' + 'e']
    # Better regex implementation:
    import re
    N = re.findall(r'\d+[a-zA-Z]+', N)
    len_var = len(N)
    while len_var > 0:
        len_var -= 1
        locate = int(re.search(r'\d+', N[len_var]).group()) & 255
        str_val = re.sub(r'\d+', '', N[len_var])
        T = T[:locate] + T[locate + len(str_val):]  # splice equivalent
    T = ''.join(T)
    _v = json.loads(B(T))  # JSON.parse equivalent - using json.loads instead of eval

    return _v




import re

def minify_html(html):
    """
    简单高效地最小化 HTML 代码。
    去除注释、多余空白和标签间空格。
    """
    # 1. 移除 HTML 注释（<!-- ... -->），但保留条件注释（如 IE 注释）
    html = re.sub(r'<!--(?![if|endif]).*?-->', '', html, flags=re.DOTALL | re.IGNORECASE)

    # 2. 合并多个空白字符为一个空格
    html = re.sub(r'[ \t\n\r]+', ' ', html)

    # 3. 去除标签内部的空格（如 <div > → <div>）
    html = re.sub(r'\s+>', '>', html)
    html = re.sub(r'<(\w+)', r'<\1', html)  # 去除左尖括号后的空格

    # 4. 去除属性等号两边的空格：<img src =" xxx" -> <img src="xxx">
    html = re.sub(r'\s*=\s*', '=', html)

    # 5. 再次清理标签间的空格（合并连续空格）
    html = re.sub(r'(?<=>)\s+(?=<)', '', html)  # 去除标签之间的空格

    # 6. 清理首尾空白
    return html.strip()

def search_comic(res:str):
    import re
    return re.findall(r'<a\s+href="/Comic/comicInfo/id/(\d+)"\s+title="([^"]+)"\s+class="mod_book_cover db"\s+target="_blank">',res)

def search_chapter(res:str):
    import re
    return re.findall(r'<a\s+href="/ComicView/index/id/(\d+)/cid/(\d+)"\s+title="([^"]+)">',minify_html(res))