import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time


class PythonOrgSearch(unittest.TestCase):

    def get_soup(self, url):
        """
        Given the url of a page, this function returns the soup object.
        Parameters:
            url: the link to get soup object for
        Returns:
            soup: soup object
        """
        driver = webdriver.Chrome("./chromedriver")
        driver.get(url)
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        driver.close()
        return soup

    def test_search_in_python_org(self):

        self.options = webdriver.ChromeOptions()
        options = self.options

        reviews_dict = {'text': [], 'date': [], 'name': [], 'profile_link': [], 'helpful_votes': [],
                        'reviews_count': [], 'hearts': [], 'idea_lists': []}
        url_prefix = 'https://www.amazon.com'
        total_reviews_count = 0
        start = time.time()

        for i in range(1, 2):
            samsung_url = 'https://www.amazon.com/product-reviews/B08C35KLKK/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=all_stars&reviewerType=all_reviews&pageNumber=' + str(
                i) + '#reviews-filter-bar'
            iphone_url = 'https://www.amazon.com/product-reviews/B01NAW98VS/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=all_stars&reviewerType=all_reviews&pageNumber=' + str(
                i) + '#reviews-filter-bar'
            soup = self.get_soup(samsung_url)

            # find review blocks
            review_block = soup.findAll("div", attrs={'class': 'a-section celwidget'})
            print('Get total ' + str(len(review_block)) + ' in ' + str(i) + ' page')
            total_reviews_count += len(review_block)

            for j in review_block:
                text = j.find("span", attrs={'data-hook': 'review-body'}).text.replace('\n', '').strip()
                length = len(text.split())

                if (length > 50):

                    date = j.find('span', attrs={'data-hook': 'review-date'}).text
                    name = j.find('span', attrs={'class': 'a-profile-name'}).text
                    profile_link = j.find('a').attrs['href']
                    reviews_dict['text'].append(text)
                    reviews_dict['date'].append(date.split('on')[1])  # remove the first part "Reviewed in the United States on" and only keep date
                    reviews_dict['name'].append(name)
                    hyperLink = url_prefix + profile_link
                    reviews_dict['profile_link'].append(hyperLink)

                    soup1 = self.get_soup(hyperLink)

                    temp = soup1.find_all("span", attrs={'class': 'a-size-large a-color-base'})
                    reviews_dict['helpful_votes'].append(temp[0].text)
                    reviews_dict['reviews_count'].append(temp[1].text)
                    reviews_dict['hearts'].append(temp[2].text)

                    temp = soup1.find_all("span", attrs={'class': 'a-size-base'})
                    reviews_dict['idea_lists'].append(temp[-1].text[1:])

        elapse = time.time() - start

        df = pd.DataFrame(reviews_dict)
        df.to_csv('test_review.csv')

        print("Finished scraping " + str(total_reviews_count) + " reviews in " + str(elapse) + " secs")


if __name__ == "__main__":
    unittest.main()
