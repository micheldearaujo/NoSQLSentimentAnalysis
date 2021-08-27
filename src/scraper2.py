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
links =['https://www.tripadvisor.com.br/Restaurant_Review-g304560-d4080412-Reviews-Tio_Armenio_Shopping_rio_mar-Recife_State_of_Pernambuco.html', ###
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d10477057-Reviews-Prima_Deli_Restaurante_e_Pizzaria-Recife_State_of_Pernambuco.html',
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d3699478-Reviews-Buca_Trattoria-Recife_State_of_Pernambuco.html',
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d3195441-Reviews-Dom_Ferreira_Forneria-Recife_State_of_Pernambuco.html',
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d6006139-Reviews-Villa_Foria-Recife_State_of_Pernambuco.html',
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d4525760-Reviews-Papacapim-Recife_State_of_Pernambuco.html',
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d4052348-Reviews-Cozinhando_Escondidinho-Recife_State_of_Pernambuco.html',
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d2359781-Reviews-Recanto_Lusitano-Recife_State_of_Pernambuco.html',
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d3405616-Reviews-Steakhouse_Sal_e_Brasa_Recife-Recife_State_of_Pernambuco.html,'
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d3959336-Reviews-The_Fifties_Recife-Recife_State_of_Pernambuco.html',
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d1886702-Reviews-Guaiamum_Gigante-Recife_State_of_Pernambuco.html',
        'https://www.tripadvisor.com.br/Restaurant_Review-g304560-d6692537-Reviews-Outback_Steakhouse_Shopping_Recife-Recife_State_of_Pernambuco.html']
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

        # Executing the Chrome webdriver
        driver = webdriver.Chrome(path)
        driver.get(link)
        sleep(3)

        warning_button = driver.find_element_by_xpath('//*[@id="_evidon-accept-button"]')
        warning_button.click()
        sleep(1)

        # Setting a variable in the "Next" button that starts in 13 in the first page and then changes to 12 in the following pages
        nextpos = 13

        # Looping throughout all this restaurant page
        pages = 1
        # try:

        try:

            while True:
                # Getting restaurant information
                print("Getting the restaurant data")
                rest_name = driver.find_element_by_xpath('//*[@id="component_44"]/div/div[1]/h1').text
                print(f"Restaurant name: {rest_name}")
                rating = driver.find_element_by_xpath('//*[@id="component_45"]/div/div/div[1]/div/div[1]/div[1]/span[1]').text
                number_ratings = driver.find_element_by_xpath('//*[@id="component_45"]/div/div/div[1]/div/div[1]/div[1]/a').text.split(' ')[0]

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
                               rest_name,
                                float('.'.join(rating.split(','))),     # Transforming the string into float
                                int(''.join((number_ratings.split(' ')[0].split('.')))),    # Transforming the string into a int
                               titles[record].text,
                               revs[record].text,
                               dates[record].text,
                               reviewer[record].text.split('\n')[0]     # Getting only reviewer name. The 1 index is how much reviews this person has given in the website
                               )

                pages += 1

                print("Going to next reviews page")
                next_page_button = driver.find_element_by_xpath(f'//*[@id="taplc_location_reviews_list_resp_rr_resp_0"]/div/div[{nextpos}]/div/div/a[2]')
                next_page_button.click()
                nextpos = 12
                sleep(2)

        except:
            print("No more pages of this restaurant.")
            print(f'{pages} pages were scraped.')
            driver.quit()


    def to_mongodb(self, rest_name, rating, number_ratings, title, rev, date, reviewer):
        # Inserting the new group of documents to the collection I (schema I)
        # In this collection every document is a single review
        print("Inserting Document I")
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
        print("Inserting Document II")
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
        print("Inserting Document III")
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
    for link in links:
        reviews = RestaurantReviews()
        reviews.get_reviews(path, link)

