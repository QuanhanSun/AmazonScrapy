import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import time
from faker import Factory

from tqdm import tqdm

fc = Factory.create()


class AmazonScrapy(object):
    def __init__(self, url_prefix, target_url, page, path, csv_name, account_url_prefix, rank_url_prefix):
        self.url_prefix = url_prefix
        self.target_url = target_url
        self.page = page
        self.path = path
        self.csv_name = csv_name
        self.total_reviews = 0
        self.account_url_prefix = account_url_prefix
        self.rank_url_prefix = rank_url_prefix

    def get_soup(self, url):
        headers = {'User-Agent': fc.user_agent(),
                   'Accept-Language': 'en-US, en;q=0.5'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')
        return soup

    def get_result(self):
        result = {
            'text': [],
            'date': [],
            'name': [],
            'profile_link': [],
            'helpful_votes': [],
            'reviews_count': [],
            'hearts': [],
            'idea_lists': [],
            'rank': []
        }
        start_time = time.time()

        for i in tqdm(range(1, self.page + 1)):
            review_page_url = self.target_url.format(i)
            review_page_soup = self.get_soup(review_page_url)

            review_block = review_page_soup.find_all('div', attrs={'class': 'a-section celwidget'})
            print('Get {} reviews in {} page'.format(len(review_block), i))
            self.total_reviews += len(review_block)

            for j in review_block:
                try:
                    text = j.find('span', attrs={'data-hook': 'review-body'}).text.replace('\n', '').strip()
                except Exception as e:
                    print(e)
                    # print(j)
                    # print(j.find('div', attrs={'class': 'a-row a-spacing-small review-data'}))
                    text = ''
                length = len(text.split())

                if length > 50:
                    date = j.find('span', attrs={'data-hook': 'review-date'}).text
                    name = j.find('span', attrs={'class': 'a-profile-name'}).text
                    profile_link = j.find('a').attrs['href']
                    result['text'].append(text)
                    # remove the first part "Reviewed in the United States on" and only keep date
                    result['date'].append(date.split('on')[1])
                    result['name'].append(name)
                    hyperlink = self.url_prefix + profile_link
                    result['profile_link'].append(hyperlink)

                    # get profile soup to find insights
                    account_id = hyperlink[48:76]
                    account_url = self.account_url_prefix.format(account_id)
                    headers = {'User-Agent': fc.user_agent(),
                               'Accept-Language': 'en-US, en;q=0.5',
                               'referer': 'https://www.amazon.com/gp/profile/amzn1.account.{}/ref=cm_cr_arp_d_gw_btm?ie=UTF8'.format(account_id)}
                    profile_json = requests.get(account_url, headers=headers).json()
                    votes = profile_json['helpfulVotes']['helpfulVotesData']['count']
                    count = profile_json['reviews']['reviewsCountData']['count']
                    hearts = profile_json['ideaList']['ideaListHeartsData']['count']
                    ideas = profile_json['ideaList']['ideaListData']['count']

                    rank_url = self.rank_url_prefix.format(account_id)
                    headers = {'User-Agent': fc.user_agent(),
                               'Accept-Language': 'en-US, en;q=0.5',
                               'refer': "referer: https://www.amazon.com/gp/profile/amzn1.account.{}/ref=cm_cr_arp_d_gw_btm?ie=UTF8".format(account_id)}
                    rank_json = requests.get(rank_url, headers=headers).json()
                    rank = rank_json['topReviewerInfo']['rank']

                    result['helpful_votes'].append(votes)
                    result['reviews_count'].append(count)
                    result['hearts'].append(hearts)
                    result['idea_lists'].append(ideas)
                    result['rank'].append(rank)

        elapse = time.time() - start_time

        df = pd.DataFrame(result)
        df.to_csv(self.csv_name, encoding="utf-8-sig")

        print("Finishing scrapying {} reviews in {} secs {} reviews length lager than 50".format(self.total_reviews,
                                                                                                 elapse, len(df)))


if __name__ == '__main__':
    url_prefix = 'https://www.amazon.com'
    samsung_url = 'https://www.amazon.com/product-reviews/B08C35KLKK/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=all_stars&reviewerType=all_reviews&pageNumber={}#reviews-filter-bar'
    iphone_url = 'https://www.amazon.com/product-reviews/B01NAW98VS/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=all_stars&reviewerType=all_reviews&pageNumber={}#reviews-filter-bar'
    account_url_prefix = 'https://www.amazon.com/hz/gamification/api/contributor/dashboard/amzn1.account.{}'
    rank_url_prefix = 'https://www.amazon.com/profilewidget/bio/amzn1.account.{}?view=visitor'
    path = './chromedriver'
    HEADERS = {'User-Agent':
                   'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
               'Accept-Language': 'en-US, en;q=0.5'}

    # samsung_scrapy = AmazonScrapy(url_prefix, samsung_url, 10, path, 'samsung_result.csv')
    # samsung_scrapy.get_result()

    iphone_scrapy = AmazonScrapy(url_prefix, iphone_url, 30, path, 'iphone7_result.csv', account_url_prefix,
                                 rank_url_prefix)
    iphone_scrapy.get_result()
