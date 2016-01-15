import datetime

from aggregator import exceptions
from aggregator.base import Aggregator, Article, InvalidArticle, make_soup
from aggregator.utils.calendar import code_to_month

class FourFourTwo(Aggregator):

    base_url = 'http://www.fourfourtwo.com/features'
    source = 'FourFourTwo'

    def extract(self):
        soup = make_soup(FourFourTwo.base_url)
        divs =  soup.find('div', {'class': 'content-wrapper'})
        divs = divs.find('div', {'class': 'view-content'})
        divs = iter(divs.findChildren(recursive=False))
        articles = (self.crawl(div) for div in divs)
        return list(articles)

    def crawl(self, tag):
        try:
            anchor = tag.find('div', {'class': 'title'}).find('a')
            url = self.get_url(anchor)
            title = self.get_title(anchor)
            date_published = self.get_date_published(tag)
            author = self.get_author(make_soup(url))
            return Article(FourFourTwo.source, title, url, author, date_published)
        except (exceptions.WebCrawlException, AttributeError) as e:
            return InvalidArticle(FourFourTwo.source, e)

    def get_author(self, tag):
        try:
            author = tag.find('p', {'class': 'authorName'})
            return author.text.strip()
        except AttributeError as e:
            raise exceptions.AuthorNotFoundException
        

    def get_date_published(self, tag):
        try:
            date_published = tag.find('div', {'class': 'created'})
            date_published = date_published.text.strip().split()
            date_published[1] = code_to_month[date_published[1][:3].lower()]
            date_published.reverse()
            date_published = datetime.datetime(*map(int, date_published)).date()
            return date_published
        except (IndexError, AttributeError, ValueError):
            raise exceptions.DatePublishedNotFoundException

    def get_title(self, tag):
        try:
            return tag.text.strip()
        except AttributeError as e:
            raise exceptions.TitleNotFoundException

    def get_url(self, tag):
        try:
            url = tag['href']
            url = url.split('/')[-1]
            url = FourFourTwo.base_url + '/' + url
            return url
        except (KeyError, IndexError, AttributeError, ValueError, TypeError):
            raise exceptions.UrlNotFoundException

if __name__ == '__main__':
    fourfourtwo = FourFourTwo()
    print(fourfourtwo.extract())