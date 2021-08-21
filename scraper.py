"""
This file is a web scraper that gathers restaurant reviews from the website TripAdvisor.

@author micheldearaujo

created at 2021 August 17

"""

# Importing the necessary libraries
import selenium.common.exceptions
from selenium import webdriver
from time import sleep
import pymongo

# Defining the chromedriver path
path = 'C:/Program Files (x86)/chromedriver.exe'
link = 'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d4080412-Reviews-Tio_Armenio_Shopping_rio_mar-Recife_State_of_Pernambuco.html'

# Setting up the MongoDB connection URL
my_mongo_url = "mongodb+srv://m001-student:m001-mongodb-basics@sandbox.fkppj.mongodb.net/test"


class RestaurantReviews:

    def __init__(self):
        # Creating a instance of the MongoDB client
        print("Connecting to the Atlas Cluster")
        self.client = pymongo.MongoClient(my_mongo_url, serverSelectionTimeoutMS=5000)

        # Connecting to the database
        self.db = self.client.restaurantreviews

    def get_reviews(self, path, link):
        nextpos = 13
        # Executing the Chrome webdriver
        driver = webdriver.Chrome(path)
        driver.get(link)
        sleep(3)

        Warning_Button = driver.find_element_by_xpath('//*[@id="_evidon-accept-button"]')
        Warning_Button.click()
        sleep(1)

        # Looping throughout the pages
        paginas = 1
        try:
            while True:

                # Getting restaurant information
                print("Getting the restaurant data")
                restName = driver.find_element_by_xpath('//*[@id="component_45"]/div/div[1]/h1').text
                rating = driver.find_element_by_xpath('//*[@id="component_46"]/div[1]/div/div[1]/div/div[1]/div[1]/span[1]').text
                numberRatings = int(driver.find_element_by_xpath('//*[@id="component_46"]/div[1]/div/div[1]/div/div[1]/div[1]/a').text.split(' ')[0])
                address = driver.find_element_by_xpath('//*[@id="component_45"]/div/div[3]/span[1]/span/a').text

                # Getting the reviews
                print("Getting the reviews data")
                titles = driver.find_elements_by_class_name('noQuotes')
                revs = driver.find_elements_by_class_name('partial_entry')
                dates = driver.find_elements_by_class_name('ratingDate')
                reviewer = driver.find_elements_by_class_name('member_info')

                # Until now we have gathered the data of one page.
                # At this point, we need to insert the data into the MongoDB
                # Using the insert_one statement within a loop

                for record in range(len(reviewer)):
                    self.to_mongodb(
                               restName, rating, numberRatings, address,
                               titles[record].text,
                               revs[record].text,
                               dates[record].text,
                               reviewer[record].text.split('\n')[0]
                               )

                paginas += 1

                print("Changing page...")
                next_page_button = driver.find_element_by_xpath(f'//*[@id="taplc_location_reviews_list_resp_rr_resp_0"]/div/div[{nextpos}]/div/div/a[2]')
                next_page_button.click()
                nextpos = 12
                sleep(2)

        except selenium.common.exceptions.NoSuchElementException as error:
            print("No more pages.")
            driver.quit()
            print(f'{paginas} Were scraped.')


    def to_mongodb(self, restName, rating, numberRatings, address, title, rev, date, reviewer):
        # Inserting the new group of documents to the collection I
        # In this collection every document is a single review
        print("Inserting Document")
        self.db.reviews_I.insert_one(
            {
                "Restaurant Name": restName,
                "Rating": rating,
                "Number of Ratings": numberRatings,
                "Address": address,
                "Review Title": title,
                "Review Date": date,
                "Reviewer Name": reviewer,
                "Review": rev
            }
        )

        # Inserting the new data into the collection I
        # In this collection each document is a different restaurant and the reviews are a array of documents
        # self.db.reviews_II.(
        #     {},
        #     {
        #         "$push": {
        #             "Reviews": {
        #                 "Review Title": title,
        #                 "Review Date": date,
        #                 "Reviewer Name": reviewer,
        #                 "Review": rev
        #                         }
        #                 },
        #         "$set": {
        #             "Restaurant Name": restName,
        #         }
        #     }
        # )

# Executing

if __name__ == '__main__':
    reviews = RestaurantReviews()
    reviews.get_reviews(path, link)

