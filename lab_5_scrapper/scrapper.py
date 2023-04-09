"""
Crawler implementation
"""
import json
import os.path
import re
from typing import Pattern, Union
from core_utils.config_dto import ConfigDTO
from core_utils.constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import datetime
from core_utils.article.article import Article
from core_utils.article.io import to_raw
import shutil


class IncorrectSeedURLError(Exception):
    """
    seed URL does not match standard pattern "https?://w?w?w?." or does not correspond to the target website
    """
    pass


class NumberOfArticlesOutOfRangeError(Exception):
    """
    total number of articles is out of range from 1 to 150
    """
    pass


class IncorrectNumberOfArticlesError(Exception):
    """
    total number of articles to parse is not integer
    """
    pass


class IncorrectHeadersError(Exception):
    """
    headers are not in a form of dictionary
    """
    pass


class IncorrectEncodingError(Exception):
    """
    encoding must be specified as a string
    """
    pass


class IncorrectTimeoutError(Exception):
    """
    timeout value must be a positive integer less than 60
    """
    pass


class IncorrectVerifyError(Exception):
    """
    verify certificate value must either be True or False
    """
    pass


class Config:
    """
    Unpacks and validates configurations
    """

    def __init__(self, path_to_config: Path) -> None:
        """
        Initializes an instance of the Config class
        """
        self.path_to_config = path_to_config
        self.config = self._extract_config_content()
        self._validate_config_content()

    def _extract_config_content(self) -> ConfigDTO:
        """
        Returns config values
        """
        with open(self.path_to_config, 'r', encoding='utf-8') as f:
            config_content = json.load(f)
            seed_urls = config_content['seed_urls']
            total_articles_to_find_and_parse = config_content['total_articles_to_find_and_parse']
            headers = config_content['headers']
            encoding = config_content['encoding']
            timeout = config_content['timeout']
            should_verify_certificate = config_content['should_verify_certificate']
            headless_mode = config_content['headless_mode']
        config = ConfigDTO(seed_urls=seed_urls,
                           total_articles_to_find_and_parse=total_articles_to_find_and_parse,
                           headers=headers,
                           encoding=encoding,
                           timeout=timeout,
                           should_verify_certificate=should_verify_certificate,
                           headless_mode=headless_mode)
        return config

    def _validate_config_content(self) -> None:
        """
        Ensure configuration parameters
        are not corrupt
        """
        if not isinstance(self.config.seed_urls, list):
            raise IncorrectSeedURLError
        for seed_url in self.config.seed_urls:
            if not isinstance(seed_url, str):
                raise IncorrectSeedURLError
            response = requests.get(seed_url)
            if re.match(r'https://.*/', seed_url) is None:
                # or not response.status_code == 200:
                raise IncorrectSeedURLError

        if not type(self.config.total_articles) == int or self.config.total_articles < 0:
            raise IncorrectNumberOfArticlesError
        if self.config.total_articles > 150 or self.config.total_articles < 1:
            raise NumberOfArticlesOutOfRangeError

        if not isinstance(self.config.headers, dict):
            raise IncorrectHeadersError
        if not isinstance(self.config.encoding, str):
            raise IncorrectEncodingError
        if not isinstance(self.config.timeout, int) or self.config.timeout < 0 or self.config.timeout > 60:
            raise IncorrectTimeoutError
        if not isinstance(self.config.headless_mode, bool):
            raise IncorrectVerifyError
        if not(self.config.should_verify_certificate is True or self.config.should_verify_certificate is False):
            raise IncorrectVerifyError

    def get_seed_urls(self) -> list[str]:
        """
        Retrieve seed urls
        """
        return self.config.seed_urls

    def get_num_articles(self) -> int:
        """
        Retrieve total number of articles to scrape
        """
        return self.config.total_articles

    def get_headers(self) -> dict[str, str]:
        """
        Retrieve headers to use during requesting
        """
        return self.config.headers

    def get_encoding(self) -> str:
        """
        Retrieve encoding to use during parsing
        """
        return self.config.encoding

    def get_timeout(self) -> int:
        """
        Retrieve number of seconds to wait for response
        """
        return self.config.timeout

    def get_verify_certificate(self) -> bool:
        """
        Retrieve whether to verify certificate
        """
        return self.config.should_verify_certificate

    def get_headless_mode(self) -> bool:
        """
        Retrieve whether to use headless mode
        """
        return self.config.headless_mode


def make_request(url: str, config: Config) -> requests.models.Response:
    """
    Delivers a response from a request
    with given configuration
    """
    headers = config.get_headers()
    timeout = config.get_timeout()
    return requests.get(url=url, headers=headers, timeout=timeout)


class Crawler:
    """
    Crawler implementation
    """

    url_pattern: Union[Pattern, str]

    def __init__(self, config: Config) -> None:
        """
        Initializes an instance of the Crawler class
        """
        self.config = config
        self.seed_urls = config.get_seed_urls()
        self.urls = []

    def _extract_url(self, article_bs: BeautifulSoup) -> str:
        """
        Finds and retrieves URL from HTML
        """
        all_links_bs = article_bs.find_all('a')
        for link_bs in all_links_bs:
            link = link_bs.get('href')
            if link is None:
                continue
            elif link[0:8] == 'https://' and 'news' in link and 'from' in link:
                return link
        return ''

    def find_articles(self) -> None:
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = make_request(seed_url, self.config)
            main_bs = BeautifulSoup(response.text, 'lxml')
            link = self._extract_url(main_bs)
            if link:
                self.urls.append(link)

    def get_search_urls(self) -> list:
        """
        Returns seed_urls param
        """
        return self.seed_urls
        #return self.urls




class HTMLParser:
    """
    ArticleParser implementation
    """

    def __init__(self, full_url: str, article_id: int, config: Config) -> None:
        """
        Initializes an instance of the HTMLParser class
        """
        self.full_url = full_url
        self.article_id = article_id
        self.config = config
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup: BeautifulSoup) -> None:
        """
        Finds text of article
        """
        gff=article_soup.find_all('div', class_='page-content')
        body_bs = gff[0]
        all_paragraphs = str(body_bs.find_all('p'))
        self.article.text = all_paragraphs

    def _fill_article_with_meta_information(self, article_soup: BeautifulSoup) -> None:
        """
        Finds meta information of article
        """
        pass

    def unify_date_format(self, date_str: str) -> datetime.datetime:
        """
        Unifies date format
        """
        pass

    def parse(self) -> Union[Article, bool, list]:
        """
        Parses each article
        """
        response = make_request(self.full_url, self.config)
        main_bs = BeautifulSoup(response.text, 'lxml')
        self._fill_article_with_text(main_bs)
        return self.article

def prepare_environment(base_path: Union[Path, str]) -> None:
    """
    Creates ASSETS_PATH folder if no created and removes existing folder
    """
    if os.path.isdir(ASSETS_PATH):
        shutil.rmtree(ASSETS_PATH)
    os.makedirs(ASSETS_PATH)


def main() -> None:
    """
    Entrypoint for scrapper module
    """
    configuration = Config(path_to_config=CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(config=configuration)
    crawler.find_articles()
    urls = crawler.urls
    for i in range(len(urls)):
        parser = HTMLParser(full_url=urls[i], article_id=i, config=configuration)
        article = parser.parse()
        to_raw(article)


if __name__ == "__main__":
    main()
