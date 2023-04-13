import requests
from bs4 import BeautifulSoup


def main():
    URL = 'https://primamedia.ru/news/'
    response = requests.get(URL, headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'})

    print(response.status_code)
    response.raise_for_status()
    response.encoding = 'utf-8'
    #print(response.text)

    #запись в файл
    f = open('index.html', 'w', encoding='utf-8')
    f.write(str(response.status_code))
    f.write(response.text)
    f.close()

    main_bs = BeautifulSoup(response.text, 'lxml')
    title_bs = main_bs.title
    print(title_bs.text)
    print(title_bs.name)
    print(title_bs.attr)

    all_links_bs = main_bs.find_all('a')
    print(len(all_links_bs))

    all_links = []
    for link_bs in all_links_bs:
        link = link_bs.get('href')
        if link is None:
            print(link_bs)
            continue
        elif link[0:8] == 'https://' and 'news' in link and 'from' in link:
            all_links.append(link_bs['href'])
    print(all_links)
    print(len(all_links))

    '''
    1. get a request to an article page
    2. create a BeautifulSoup instance on top of the response
    3. find the title + all the article text
    '''

def main_new():
    url = 'https://primamedia.ru/news/1484630/?from=19'
    response = requests.get(url, headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'})
    print(response.status_code)

    main_bs = BeautifulSoup(response.text, 'lxml')
    date1 = main_bs.find(class_='fcfv')
    date = date1.get_text()
    print(type(date1))
    import datetime
    " ".join(date.split())
    date = date.strip()
    date = date.replace('апреля', '04')
    print(date)
    date_time = datetime.datetime.strptime(date, '%d %m, %H:%M')
    print(date_time, type(date_time))


    #print(main_bs)
    #title_bs = main_bs.find_all('h1', class_='page_fullnews exis-photo')
    #title_bs = main_bs.find_all('h1')
    #print(title_bs, type(title_bs))

    #body_bs = main_bs.find_all('div', class_='page-content')[0]
    #all_paragraphs = body_bs.find_all('p')
    #print(len(all_paragraphs))

if __name__ == '__main__':
    main_new()
