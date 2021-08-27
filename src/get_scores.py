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
#path = 'C:/Program Files (x86)/chromedriver'
links=[]

link = input('Enter the restaurant link: ')

# Setting up the MongoDB connection URL
f = open('/media/michel/dados/Projects/emails.txt', 'r')
passwd = f.read().splitlines()[2]
my_mongo_url = passwd


class RestaurantReviews:

    def __init__(self):
        # Creating a instance of the MongoDB client
        print("Connecting to the Atlas Cluster")
        self.client = pymongo.MongoClient(my_mongo_url, serverSelectionTimeoutMS=5000)

        # Connecting to the database
        self.db = self.client.restaurant_reviews

    def get_reviews(self, path, link):

        driver.get(link)
        sleep(1)

        # Getting restaurant information
        print("Getting the restaurant data")
        rest_name = driver.find_element_by_xpath('//*[@id="component_44"]/div/div[1]/h1').text
        print(f"Restaurant name: {rest_name}")

        scores = driver.find_elements_by_class_name('content')[0].text
        scores = scores.split('\n')

        print("Inserting document to database")
        self.to_mongodb(
            rest_name,
            int(''.join(scores[0].split(' ')[1].split('.'))),
            int(''.join(scores[1].split(' ')[2].split('.'))),
            int(''.join(scores[2].split(' ')[1].split('.'))),
            int(''.join(scores[3].split(' ')[1].split('.'))),
            int(''.join(scores[4].split(' ')[1].split('.')))
                   )



    def to_mongodb(self, rest_name, excellent, very_good, good, bad, terrible):
        # Inserting the new group of documents to the collection I (schema I)
        # In this collection every document is a single review
        print("Inserting Document I")
        self.db.reviews_I.update_many(
            {
                "restaurant_name": rest_name,
            },
            {
                "$set": {
                    "reviews_scores": {
                        "Excellent": excellent,
                        "Very Good": very_good,
                        "Good": good,
                        "Bad": bad,
                        "Terrible": terrible
                    }
                }
            }
        )

        # Inserting the new data into the collection II (schema II)
        # In this collection each document is a different restaurant and the reviews are a array of documents
        print("Inserting Document II")
        self.db.reviews_II.update_many(
            {
                "restaurant_name": rest_name,
            },
            {
                "$set": {
                    "reviews_scores": {
                        "Excellent": excellent,
                        "Very Good": very_good,
                        "Good": good,
                        "Bad": bad,
                        "Terrible": terrible
                    }
                }
            }
        )


# Executing

# Executing the Chrome webdriver


if __name__ == '__main__':
    driver = webdriver.Chrome(path)
    driver.get(links[0])
    sleep(3)

    warning_button = driver.find_element_by_xpath('//*[@id="_evidon-accept-button"]')
    warning_button.click()
    sleep(1)
    for link in links:
        reviews = RestaurantReviews()
        reviews.get_reviews(path, link)

