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

if __name__ == '__main__':
    main()