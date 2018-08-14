import requests


cookies_text = """
Cookie: authtoken6=1; bgcolor=bg-default; word=select-m; __gads=ID=7653011dc03125da:T=1525384324:S=ALNI_MYaBrrnT0nZCv4cMAQHb61oY1xdCA; __utmz=204782609.1529880809.78.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); book18limit_651533=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_555894=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_641150=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_631319=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_574036=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_572991=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_617159=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_556130=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_495519=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_530210=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_644802=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_640554=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_630086=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_607871=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_645528=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; book18limit_522949=1362a390f19919863d5ed7b50bcbf274e05e8019s%3A1%3A%221%22%3B; __utmc=204782609; authToken=03m9jd049o2qsnbf3hvr6mnlt0; PORF_TOKEN=fda6ee9b9ba3582e55f8733389abed33903c7fd5s%3A40%3A%228eb49ec01c502cd6dbfffc40ae5499c0845c3717%22%3B; url=https%3A%2F%2Fwww.popo.tw%2Fbooks%2F530210; authtoken1=Z3Vhbmd5dTAwNw%3D%3D; authtoken2=OTM2NzZhYTRlOTYxYmQ2YjBhMGRiZDI0ZWFmNzRkOGU%3D; authtoken3=1393556966; authtoken4=3103586858; authtoken5=1533420218; __utma=204782609.1180877328.1527183640.1533411626.1533420276.137; __utmb=204782609.7.10.1533420276
"""

def get_cookies(cookies_text):
    cookies_text = cookies_text.replace('Cookie:', '')
    attrs = [attr.strip().split('=') for attr in cookies_text.split(';')]
    cookies = {item[0]: item[1] for item in attrs}
    return cookies



url_content = 'https://www.popo.tw/books/654599/articles'
url_page = 'https://www.popo.tw/books/654599/articles/7493810'
referer = 'https://www.popo.tw/books/654599/articles'
headers = {
    'referer': referer,
    'Connection': 'keep-alive',
    'Host': 'www.popo.tw',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}
cookies = get_cookies(cookies_text)
web_page = requests.get(url_page, cookies=cookies, headers=headers, timeout=120)
# web_page = requests.get(url_page)
print(web_page.text)
