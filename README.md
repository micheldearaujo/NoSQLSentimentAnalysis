<div>

# NoSQL Sentiment Analysis
Hi there! This is a sentiment analysis project. Its objective is trying to predict the overall rating of restaurants based on the reviews given by its clients on [Tripadvisor](https://www.tripadvisor.com.br/) website.

</div>
<hr>

<div>

## Introduction

In this project will be built a NoSQL database that stores reviews of restaurants scraped from the web and will be the base for querying data to create a Machine Learning classifier that tries to predict the overall rating of a restaurant based on the sentiment analysis of its reviews. In the figure bellow you can see the overview of the project workflow.


<p align="center">
<img width="471" height="233" src="images/projectFlowChart.png">

</div>
<hr>

<div>

### Sentiment Analysis

Sentiment analysis, also known as opinion mining, is a natural language processing technique used to determine whether a text is positive, negative or neutral. It also possible to find other sentiments, like anger and sadness. Therefore, this process has become crucial when business want to know better how their products are performing.

#### Why is it important?

Sentiment analysis allows businesses to understand the sentiment of their customers towards their brand. Using text from social media posts, blogs and reviews, the business owners can make better decisions about their product.

## The database design

This is a public dataset that will be collected from the [Tripadvisor](https://www.tripadvisor.com.br/)
website, whose has tons of information about restaurants, trips, places to stay and more.
The data will be scraped using the Python programming language and Selenium library.

During this process the data is stored in a [MongoDB](https://www.mongodb.com/) database, using their free cloud service, Atlas.
When designing a NoSQL database, the first (and only) thing to have in mind is its performance. A MongoDB
database must be design considering the types of queries that will be made in the future. Therefore,
in order to create a most effective database as possible, we need to study what kind of queries we will perform later on.
Among many schemas design for a Document-based database, there is five basics types of relationships,
like *One to One, One to Few, One to Many, One to Squillions and Many to Many*.

As best practices for MongoDB users, each of those relationships has an appropriate way of using:

<ol>
<li> One to One: Use Key-Value paris </li>
<li> One to Few: Prefer Embedding </li>
<li> One to Many: Prefer Referencing </li>
<li> One to Squillions: Inverse Referencing </li>
<li> Many to Many: Multiple Referencing</li>
</ol>

Therefore, we have to decide how are we going to query this data in the future. In this dataset we do not
have too much information about the restaurant, besides the restaurant name, the rating and number of ratings.
The most important field to query is the review title and the review text, and later on the sentiments of the review.

The easiest way to store this data is the form of schema 1, where all the data is within only one document with no arrays. One document
holds the restaurant information and only one review. Therefore, there will be one document for each review given to each restaurant.

Schema I - One to One:

    {
        "_id": ObjectID(),
        "Restaurant Name": restName,
        "Rating": rating,
        "Number of Ratings": numberRatings,
        "Review Title": title,
        "Review Date": date,
        "Reviewer Name": reviewer,
        "Review": rev,
        "Sentiments": sentimentResult
    }

As there will be thousands of restaurants and each restaurant have hundreds of reviews, this schema will
lead us in a collection with a number of documents that goesfrom a hundred thousands to millions.
We also will be able to query for each restaurant isolated, reviewer and sentiments.

The second schema uses arrays to store the reviews. In this schema, each document will represent one
restaurant and all the reviews of each restaurant will be stored in an array of documents.

Schema II - One to Few:

    {
        "_id": ObjectID(),
        "Restaurant Name": restName,
        "Number of Reviews": numberRatings
        "Reviews": [{
            "Review Title": title,
            "Review Date": date,
            "Reviewer Name": reviewer,
            "Review": rev,
            "Sentiments": sentimentResult
                    }, ...]
    }

This schema leads to a considerably small number of documents, as there will many documents as there are
many restaurants. However, this is an embedded schema, and as we saw before, embedding is recommended
only to One to Few schemas. As the time passes, there will be more and more reviews for the restaurants, and
at some point in time it will be no more a One to Few but a One to Many.

This leads us to choose a schema appropriated to the One to Many relationship.

Schema III - One to Many:

Restaurant documents:

    {
        "_id": ObjectID(),
        "restaurant_name": restname,
        "rating": rating,
        "number_of_reviews": numberofratings
    }

Review documents:

    {
        "_id": ObjectID(),
        "restaurant_id": restaurant_ID,
        "review_title": title,
        "review_date": date,
        "reviewer_name": reviewer,
        "review": rev,
        "sentiments": [sentiment result]
    }

For this particular problem, schema 3 is (probably) the best option, as it is easy to query as a One to One relationship
and does not suffer from duplicated records of the restaurant data. Besides, it corrects the problem of the schema 2
by not having to large arrays sizes.

However, as the size of this dataset will be only a small smaple of the whole restaurants in Brazil, I will keep simple and choose the schema I for simplicity.

Please refer to the [multiple_restaurants_scraper.py](https://github.com/micheldearaujo/NoSQLSentimentAnalysis/blob/main/multiple_restaurants_scraper.py) to view the code in depth.

Later after gathering 30745 reviews of 40 restaurants I realized that I forgot a important information, the reviews score. So I went back and scraped the missing data and completed the schema, as you can see bellow.

    {
        "_id": ObjectID(),
        "restaurant_name": restName,
        "rating": rating,
        "number_of_ratings": numberRatings,
        "review_title": title,
        "review_date": date,
        "reviewer_name": reviewer,
        "review": rev,
        "reviews_scores": {
            "Excellent": int(),
            "Very Good": int(),
            "Good": int(),
            "Bad": int(),
            "Terrible": int()
        }
        "sentiments": sentimentResult
    }


</div>
<hr>

This amount of information can provides us with some insights about the food market in Brazil.

## Exploratory Data Analysis

What kind of answers can we get from this dataset? Here are some basic questions to make:

1. How many reviews each restaurant has?

There two basic types of questions to make about this dataset: How the reviews scores affect the overall rating of the restaurant and how the sentiment of reviews affects the overall rating.
Both this questions can be answered using Machine Learning methods, such as Random Forest and Logist Regression. To answer the second question we will need some Natural Language processing tools to extract the sentiment of each review and then compare to the overall rating.
This task seems to be complex and can take quite some time!

