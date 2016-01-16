import collections
from abc import ABCMeta, abstractmethod

import requests
from bs4 import BeautifulSoup

from aggregator import exceptions


Article = collections.namedtuple('Article', ['source', 'title', 'url', 'author',
                                             'date_published'])

InvalidArticle = collections.namedtuple('InvalidArticle', ['source', 'exception'])


def make_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


class Aggregator(metaclass=ABCMeta):

    base_url = ''
    source = ''
    EXCLUDE_IF_IN_TITLE = []

    def __init__(self):
        self.articles = None

    def extract(self):
        return list(article for article in self.articles if article is not None)

    @abstractmethod
    def crawl(self, tag):
        pass

    def get_author(self, tag):
        return self._get_text_or_raise_exception(tag,
                    exceptions.AuthorNotFoundException)

    @abstractmethod
    def get_date_published(self, tag):
        pass

    def get_title(self, tag):
        title = self._get_text_or_raise_exception(tag,
                    exceptions.TitleNotFoundException)
        return (title if not any(exclude in title
                for exclude in self.__class__.EXCLUDE_IF_IN_TITLE) else None)


    @abstractmethod
    def get_url(self, tag):
        pass

    def _get_text_or_raise_exception(self, tag, exception):
        try:
            return tag.text.strip()
        except AttributeError as e:
            raise exception
