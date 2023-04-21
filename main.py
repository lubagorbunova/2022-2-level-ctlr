import os.path

import requests
from bs4 import BeautifulSoup
from core_utils.article.article import Article


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
    print(main_bs)
    title_bs = main_bs.find_all('h1', class_='page_fullnews exis-photo')
    title_bs = main_bs.find_all('h1')
    print(title_bs, type(title_bs))

    body_bs = main_bs.find_all('div', class_='page-content')[0]
    all_paragraphs = body_bs.find_all('p')
    print(len(all_paragraphs))


class EmptyDirectoryError(Exception):
    """
    a directory is empty
    """

class InconsistentDatasetError(Exception):
    """
     IDs contain slips, number of meta and raw files is not equal, files are empty
    """

class CorpusManager:
    def __init__(self, path_to_raw_txt_data):
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._storage = {}
        self._validate_dataset()
        self._scan_dataset()

    def _validate_dataset(self) -> None:
        """
        a dataset validation
        """
        files_list = os.listdir(self.path_to_raw_txt_data)
        max_number = int(len(files_list)/2)
        for i in range(max_number):
            meta_filename = str(i+1)+'_meta.json'
            raw_filename = str(i+1) + '_raw.txt'
            if meta_filename not in files_list or raw_filename not in files_list:
                raise InconsistentDatasetError
        if not os.path.isdir(self.path_to_raw_txt_data):
            raise NotADirectoryError
        if not os.path.exists(self.path_to_raw_txt_data):
            raise FileNotFoundError
        if len(files_list) == 0:
            raise EmptyDirectoryError

    def _scan_dataset(self) -> None:
        """
        create a storage(dict) with number as a key and an Article as a value
        """
        files_list = os.listdir(self.path_to_raw_txt_data)
        max_number = int(len(files_list) / 2)
        for i in range(max_number):
            article = Article(url=None, article_id=i)
            self._storage[i+1] = article

    def get_articles(self):
        return self._storage


def main_pipeline():
    # initialize CorpusManager with ASSETS_PATH
    # validate: path exists, leads to a directory, numeration is from 1 to n without splits,
    # there are as many raw files as meta files
    # and scan: create a storage(dict) with number as a key and an Article as a value
    corpus_manager = CorpusManager('D:\hse\CTLR LABS\/2022-2-level-ctlr\/tmp\/articles')
    articles = corpus_manager.get_articles()
    print(articles)

if __name__ == '__main__':
    main_pipeline()
