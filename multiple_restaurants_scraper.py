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
path = '/usr/local/bin/chromedriver'
link = 'https://www.tripadvisor.com.br/Restaurants-g304560-Recife_State_of_Pernambuco.html'

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

        warning_button = driver.find_element_by_xpath('//*[@id="_evidon-accept-button"]')
        warning_button.click()
        sleep(1)

        # Looping through each page of restaurants listed in the "Best" Section (30 restaurants per page)
        while True:
            try:
                # Looping through each restaurant of each page
                for rest_number in range(1, 31):

                    # Selecting one restaurant from the list
                    print("Selecting the restaurant")
                    window_before = driver.window_handles[0]
                    rest_button = driver.find_element_by_xpath(f'//*[@id="component_2"]/div/div[{rest_number}]/span/div[1]/div[2]/div[1]/div/span/a')
                    rest_button.click()
                    sleep(3)
                    print("Restaurant selected!")
                    # Switching window
                    window_after = driver.window_handles[1]
                    driver.switch_to_window(window_after)

                    # Looping throughout all this restaurant page
                    pages = 1
                    try:
                        while True:

                            # Getting restaurant information
                            print("Getting the restaurant data")
                            rest_name = driver.find_element_by_xpath('//*[@id="component_44"]/div/div[1]/h1').text
                            rating = driver.find_element_by_xpath('//*[@id="component_45"]/div[2]/div/div[1]/div/div[1]/div[1]/span[1]').text
                            number_ratings = driver.find_element_by_xpath('//*[@id="component_45"]/div[2]/div/div[1]/div/div[1]/div[1]/a').text.split(' ')[0]

                            # Getting the reviews
                            print("Getting the reviews data")
                            titles = driver.find_elements_by_class_name('noQuotes')
                            revs = driver.find_elements_by_class_name('partial_entry')
                            dates = driver.find_elements_by_class_name('ratingDate')
                            reviewer = driver.find_elements_by_class_name('member_info')

                            # Until now we have gathered the data of one page.
                            # At this point, we need to insert the data into the MongoDB
                            # Using the insert_one statement within a loop
                            print("Inserting document to database")
                            for record in range(len(reviewer)):
                                self.to_mongodb(
                                           rest_name, rating, number_ratings,
                                           titles[record].text,
                                           revs[record].text,
                                           dates[record].text,
                                           reviewer[record].text.split('\n')[0]
                                           )

                            pages += 1

                            print("Going to next reviews page")
                            next_page_button = driver.find_element_by_xpath(f'//*[@id="taplc_location_reviews_list_resp_rr_resp_0"]/div/div[{nextpos}]/div/div/a[2]')
                            next_page_button.click()
                            nextpos = 12
                            sleep(2)

                    except selenium.common.exceptions.NoSuchElementException:
                        print("No more pages of this restaurant.")
                        print(f'{pages} pages were scraped.')

                    driver.close()
                    driver.switch_to_window(window_before)

                print("Going to the next restaurants page")
                next_page = driver.find_element_by_xpath('//*[@id="EATERY_LIST_CONTENTS"]/div[2]/div/a')
                next_page.click()

            except selenium.common.exceptions.NoSuchElementException:
                print("No more restaurants to extract data from.")

    def to_mongodb(self, rest_name, rating, number_ratings, title, rev, date, reviewer):
        # Inserting the new group of documents to the collection I (schema I)
        # In this collection every document is a single review
        print("Inserting Document")
        self.db.reviews_I.insert_one(
            {
                "restaurant_name": rest_name,
                "rating": rating,
                "number_of_ratings": number_ratings,
                "review_title": title,
                "review_date": date,
                "reviewer_Name": reviewer,
                "review": rev
            }
        )

        # Inserting the new data into the collection II (schema II)
        # In this collection each document is a different restaurant and the reviews are a array of documents
        self.db.reviews_II.update_one(
            {
                "restaurant_name": rest_name
            },
            {
                "$push": {
                    "reviews": {
                        "review_title": title,
                        "review_date": date,
                        "reviewer_name": reviewer,
                        "review": rev
                                }
                        },
                "$set": {
                    "restaurant_name": rest_name,
                    "number_of_reviews": number_ratings,
                    "rating": rating
                }
            },
            upsert=True
        )

        # Inserting the new data into the collection III (schema III)
        # In this collection each document is a different restaurant and the reviews are a array of documents
        # Inserting or updating the restaurant date
        self.db.reviews_III.update_one(
            {
                "restaurant_name": rest_name
            },
            {
                "$set": {
                    "restaurant_name": rest_name,
                    "rating": rating,
                    "number_of_ratings": number_ratings
                }
            },
            upsert=True
        )

        # Inserting the new review to the reviews documents
        self.db.reviews_III.insert_one(
            {
                "restaurant_id": 'id',
                "restaurant_name": rest_name,
                "review_title": title,
                "review_date": date,
                "reviewer_name": reviewer,
                "review": rev
            }
        )


# Executing


if __name__ == '__main__':
    reviews = RestaurantReviews()
    reviews.get_reviews(path, link)

