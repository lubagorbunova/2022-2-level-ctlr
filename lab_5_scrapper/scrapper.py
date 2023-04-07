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
        pass

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
        return ConfigDTO(seed_urls=seed_urls,
                         total_articles_to_find_and_parse=total_articles_to_find_and_parse,
                         headers=headers,
                         encoding=encoding,
                         timeout=timeout,
                         should_verify_certificate=should_verify_certificate,
                         headless_mode=headless_mode)

    def _validate_config_content(self) -> None:
        """
        Ensure configuration parameters
        are not corrupt
        """
        for seed_url in ConfigDTO.seed_urls:
            response = requests.get(seed_url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'})
            if not re.match(r'https?://.*/', seed_url) or not response.status_code == 520:
                raise IncorrectSeedURLError
        if ConfigDTO.total_articles_to_find_and_parse > 150 or ConfigDTO.total_articles_to_find_and_parse < 1:
            raise NumberOfArticlesOutOfRangeError
        if not isinstance(ConfigDTO.total_articles_to_find_and_parse, int):
            raise IncorrectNumberOfArticlesError
        if not isinstance(ConfigDTO.headers, dict):
            raise IncorrectHeadersError
        if not isinstance(ConfigDTO.encoding, str):
            raise IncorrectEncodingError
        if not isinstance(ConfigDTO.timeout, int) or ConfigDTO.timeout<0 or ConfigDTO.timeout>60:
            raise IncorrectTimeoutError
        if not(ConfigDTO.verify_certificate is True or ConfigDTO.verify_certificate is False):
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
        return self.config.verify_certificate

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
        pass

    def find_articles(self) -> None:
        """
        Finds articles
        """
        pass

    def get_search_urls(self) -> list:
        """
        Returns seed_urls param
        """
        pass


class HTMLParser:
    """
    ArticleParser implementation
    """

    def __init__(self, full_url: str, article_id: int, config: Config) -> None:
        """
        Initializes an instance of the HTMLParser class
        """
        pass

    def _fill_article_with_text(self, article_soup: BeautifulSoup) -> None:
        """
        Finds text of article
        """
        pass

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
        pass


def prepare_environment(base_path: Union[Path, str]) -> None:
    """
    Creates ASSETS_PATH folder if no created and removes existing folder
    """
    if os.path.isdir(ASSETS_PATH):
        for file_name in os.listdir(ASSETS_PATH):
            file = ASSETS_PATH + file_name
            if os.path.isfile(file):
                os.remove(file)
    else:
        os.mkdir(path=ASSETS_PATH)


def main() -> None:
    """
    Entrypoint for scrapper module
    """
    configuration = Config(path_to_config=CRAWLER_CONFIG_PATH)
    crawler = Crawler(config=configuration)
    pass


if __name__ == "__main__":
    main()
