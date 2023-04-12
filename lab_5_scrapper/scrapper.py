"""
Crawler implementation
"""
import datetime
import json
import os.path
import re
import shutil
from pathlib import Path
from typing import Pattern, Union

import requests
from bs4 import BeautifulSoup

from core_utils.article.article import Article
from core_utils.article.io import to_raw, to_meta
from core_utils.config_dto import ConfigDTO
from core_utils.constants import ASSETS_PATH, CRAWLER_CONFIG_PATH


class IncorrectSeedURLError(Exception):
    """
    seed URL does not match standard pattern "https?://w?w?w?."
    or does not correspond to the target website
    """


class NumberOfArticlesOutOfRangeError(Exception):
    """
    total number of articles is out of range from 1 to 150
    """


class IncorrectNumberOfArticlesError(Exception):
    """
    total number of articles to parse is not integer
    """


class IncorrectHeadersError(Exception):
    """
    headers are not in a form of dictionary
    """


class IncorrectEncodingError(Exception):
    """
    encoding must be specified as a string
    """


class IncorrectTimeoutError(Exception):
    """
    timeout value must be a positive integer less than 60
    """


class IncorrectVerifyError(Exception):
    """
    verify certificate value must either be True or False
    """


class UnavailableWebsiteError(Exception):
    """
    Website doesn't respond
    """


class NoMetaException(Exception):
    """
    Website doesn't have meta information
    """


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
        self._seed_urls = self.config.seed_urls
        self._num_articles = self.config.total_articles
        self._headers = self.config.headers
        self._encoding = self.config.encoding
        self._timeout = self.config.timeout
        self._should_verify_certificate = self.config.should_verify_certificate

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
            if not isinstance(seed_url, str) or re.match(r'https://.*/', seed_url) is None:
                raise IncorrectSeedURLError

        if (not isinstance(self.config.total_articles, int)
                or isinstance(self.config.total_articles, bool)
                or self.config.total_articles < 0):
            raise IncorrectNumberOfArticlesError
        if self.config.total_articles > 150 or self.config.total_articles < 1:
            raise NumberOfArticlesOutOfRangeError

        if not isinstance(self.config.headers, dict):
            raise IncorrectHeadersError
        if not isinstance(self.config.encoding, str):
            raise IncorrectEncodingError
        if (not isinstance(self.config.timeout, int)
                or self.config.timeout < 0 or self.config.timeout > 60):
            raise IncorrectTimeoutError
        if not isinstance(self.config.headless_mode, bool):
            raise IncorrectVerifyError
        if not(self.config.should_verify_certificate is True
               or self.config.should_verify_certificate is False):
            raise IncorrectVerifyError

    def get_seed_urls(self) -> list[str]:
        """
        Retrieve seed urls
        """
        return self._seed_urls

    def get_num_articles(self) -> int:
        """
        Retrieve total number of articles to scrape
        """
        return self._num_articles

    def get_headers(self) -> dict[str, str]:
        """
        Retrieve headers to use during requesting
        """
        return self._headers

    def get_encoding(self) -> str:
        """
        Retrieve encoding to use during parsing
        """
        return self._encoding

    def get_timeout(self) -> int:
        """
        Retrieve number of seconds to wait for response
        """
        return self._timeout

    def get_verify_certificate(self) -> bool:
        """
        Retrieve whether to verify certificate
        """
        return self._should_verify_certificate

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
    response = requests.get(url=url, headers=headers, timeout=timeout)
    return response


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
        self._seed_urls = config.get_seed_urls()
        self.urls = []

    def _extract_url(self, article_bs: BeautifulSoup) -> str:
        """
        Finds and retrieves URL from HTML
        """
        all_links_bs = article_bs.find_all('a')
        for link_bs in all_links_bs:
            link = link_bs.get('href')
            if link[0:8] == 'https://' and 'news' in link and 'from' in link:
                self.urls.append(link)
        return ''

    def find_articles(self) -> None:
        """
        Finds articles
        """
        for seed_url in self._seed_urls:
            try:
                response = make_request(seed_url, self.config)
                main_bs = BeautifulSoup(response.text, 'lxml')
                self._extract_url(main_bs)
            except UnavailableWebsiteError:
                continue

    def get_search_urls(self) -> list:
        """
        Returns seed_urls param
        """
        return self._seed_urls


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
        body_bs = article_soup.find_all('div', class_='page-content')[0]
        all_paragraphs = body_bs.find_all('p')
        texts = []
        for paragraph in all_paragraphs:
            texts.append(paragraph.text)
        self.article.text = '\n'.join(texts)

    def _fill_article_with_meta_information(self, article_soup: BeautifulSoup) -> None:
        """
        Finds meta information of article
        """
        try:
            self.article.title = article_soup.find('h1').get_text()
            self.article.author = ["NOT FOUND"]
            self.article.topics = list(article_soup.find(class_='fn-rubric-a').get_text())
            date = article_soup.find(class_='fn-rubric-link').get_text()
            self.article.date = self.unify_date_format(date)
        except NoMetaException:
            pass

    def unify_date_format(self, date_str: str) -> datetime.datetime:
        """
        Unifies date format
        """
        " ".join(date_str.split())
        date_str = date_str.strip()
        month_dict = {'января': '1',
                      'февраля': '2',
                      'марта': '3',
                      'апреля': '4',
                      'мая': '5',
                      'июня': '6',
                      'июля': '7',
                      'августа': '8',
                      'сентября': '9',
                      'октября': '10',
                      'ноября': '11',
                      'декабря': '12'}
        if len(date_str) > 5:
            for key, value in month_dict.items():
                if key in date_str:
                    date_str = date_str.replace(key, value)
            res = datetime.datetime.strptime(date_str, '%d %m, %H:%M')
        else:
            res = datetime.datetime.strptime(date_str, '%H:%M')
        return res

    def parse(self) -> Union[Article, bool, list]:
        """
        Parses each article
        """
        response = make_request(self.full_url, self.config)
        main_bs = BeautifulSoup(response.text, 'lxml')
        self._fill_article_with_text(main_bs)
        self._fill_article_with_meta_information(main_bs)
        return self.article


def prepare_environment(base_path: Union[Path, str]) -> None:
    """
    Creates ASSETS_PATH folder if no created and removes existing folder
    """
    if os.path.isdir(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path)


def main() -> None:
    """
    Entrypoint for scrapper module
    """
    configuration = Config(path_to_config=CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(config=configuration)
    crawler.find_articles()
    urls = crawler.urls
    for i, url in enumerate(urls, start=1):
        parser = HTMLParser(full_url=url, article_id=i, config=configuration)
        article = parser.parse()
        if isinstance(article, Article):
            to_raw(article)
            to_meta(article)


if __name__ == "__main__":
    main()
