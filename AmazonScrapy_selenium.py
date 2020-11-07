from selenium import webdriver
from bs4 import BeautifulSoup

import pandas as pd
import threading
import time
from faker import Factory

from tqdm import tqdm

fc = Factory.create()

ua = fc.user_agent()
print(ua)

class AmazonScrapy(threading.Thread):
    def __init__(self, url_prefix, target_url, start_page, end_page, path, csv_name, headless=True):
        threading.Thread.__init__(self)
        self.url_prefix = url_prefix
        self.target_url = target_url
        self.start_page = start_page
        self.end_page = end_page
        self.path = path
        self.csv_name = csv_name
        self.total_reviews = 0
        self.headless = headless

    def get_soup(self, url):
        opt = webdriver.ChromeOptions()

        opt.add_argument(f'user-agent={ua}')

        if self.headless:
            opt.add_argument("--headless")

        driver = webdriver.Chrome(self.path, options=opt)
        driver.get(url)
        time.sleep(3)  # make sure web page is fully loaded
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        driver.close()
        return soup

    def get_result(self):
        result = {
            'text': [],
            '# think helpful': [],
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

        for i in tqdm(range(self.start_page, self.end_page + 1)):
            review_page_url = self.target_url.format(i)
            review_page_soup = self.get_soup(review_page_url)

            review_block = review_page_soup.find_all('div', attrs={'class': 'a-section celwidget'})
            print('Get {} reviews in {} page'.format(len(review_block), i))
            self.total_reviews += len(review_block)

            for j in review_block:
                text = j.find('span', attrs={'data-hook': 'review-body'}).text.replace('\n', '').strip()
                length = len(text.split())
                nums = int(
                    j.find('span', attrs={'data-hook': 'helpful-vote-statement'}).text.replace(',', '').split()[0])

                if length > 50 and nums > 10:
                    date = j.find('span', attrs={'data-hook': 'review-date'}).text
                    name = j.find('span', attrs={'class': 'a-profile-name'}).text
                    profile_link = j.find('a').attrs['href']
                    result['# think helpful'].append(nums)
                    result['text'].append(text)
                    # remove the first part "Reviewed in the United States on" and only keep date
                    result['date'].append(date.split('on')[1])
                    result['name'].append(name)
                    hyperlink = self.url_prefix + profile_link
                    result['profile_link'].append(hyperlink)

                    # get profile soup to find insights
                    profile_soup = self.get_soup(hyperlink)
                    votes = profile_soup.find_all("span", attrs={'class': 'a-size-large a-color-base'})[0].text
                    count = profile_soup.find_all("span", attrs={'class': 'a-size-large a-color-base'})[1].text
                    hearts = profile_soup.find_all("span", attrs={'class': 'a-size-large a-color-base'})[2].text
                    ideas = profile_soup.find_all("span", attrs={'class': 'a-size-large a-color-base'})[3].text
                    rank = profile_soup.find_all("span", attrs={'class': 'a-size-base'})[-1].text

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

    def run(self):
        self.get_result()


if __name__ == '__main__':
    url_prefix = 'https://www.amazon.com'
    samsung_url = 'https://www.amazon.com/product-reviews/B08C35KLKK/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=all_stars&reviewerType=all_reviews&pageNumber={}#reviews-filter-bar'
    iphone_url = 'https://www.amazon.com/product-reviews/B01NAW98VS/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=all_stars&reviewerType=all_reviews&pageNumber={}#reviews-filter-bar'
    path = './chromedriver'

    # samsung_scrapy = AmazonScrapy(url_prefix, samsung_url, 10, path, 'samsung_result.csv')
    # samsung_scrapy.get_result()

    iphone_scrapy1 = AmazonScrapy(url_prefix, iphone_url, 1, 2, path, 'iphone7_result_1.csv')
    # iphone_scrapy2 = AmazonScrapy(url_prefix, iphone_url, 11, 20, path, 'iphone7_result_2.csv')

    iphone_scrapy1.start()
    time.sleep(5)
    # iphone_scrapy2.start()

    iphone_scrapy1.join()
    # iphone_scrapy2.join()
