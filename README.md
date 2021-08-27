<div>

# NoSQL Sentiment Analysis with Python and MongoDB
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

However, as the size of this dataset will be only a small smaple of the whole restaurants in Brazil, it will be kept simple and choose the schema I for simplicity.

Please refer to the [multiple_restaurants_scraper.py](https://github.com/micheldearaujo/NoSQLSentimentAnalysis/blob/main/multiple_restaurants_scraper.py) to view the code in depth.

Later after gathering 30745 reviews of 40 restaurants it was realized that was forgotten a important information, the reviews score. So it was went back and scraped the missing data and completed the schema, as can be seen bellow.

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

This amount of information can provide some insights about the food market in Brazil.

## Exploratory Data Analysis

What kind of answers can we get from this dataset? Here are some basic questions to make:

### 1. How many reviews each restaurant has?


    [
        {"$group": {"_id": "$restaurant_name",
                            "Reviews": {"$sum": 1}}},
        {"$sort": {"Reviews": -1}},
        {"$limit": 20}
    ]

The answer is: 

    [
    { _id: 'Coco Bambu Recife', Reviews: 5605 },
    { _id: 'Camarada Camarão - Shopping Recife', Reviews: 2592 },
    { _id: 'Chica Pitanga', Reviews: 2587 },
    { _id: 'Camarada Camarao - RioMar Recife', Reviews: 2111 },
    { _id: 'Bargaço', Reviews: 1765 },
    { _id: 'Outback Steakhouse - Shopping RioMar Recife', Reviews: 1331 },
    { _id: 'Bode Do Nô', Reviews: 1177 },
    { _id: 'Churrascaria Ponteio', Reviews: 979 },
    { _id: 'Churrascaria Sal e Brasa Recife', Reviews: 846 },
    { _id: 'Parraxaxa - Boa Viagem', Reviews: 833 },
    { _id: 'Guaiamum Gigante', Reviews: 786 },
    { _id: 'Parraxaxá', Reviews: 767 },
    { _id: 'Ilha dos Navegantes', Reviews: 703 },
    { _id: 'Spettus Steak House', Reviews: 656 },
    { _id: 'Ça Va', Reviews: 611 },
    { _id: 'Pobre Juan - Recife', Reviews: 570 },
    { _id: 'Ilha Camarões', Reviews: 567 },
    { _id: 'Dom Ferreira Forneria', Reviews: 546 },
    { _id: 'Castelus Restaurante', Reviews: 512 },
    { _id: 'Mingus', Reviews: 410 }
    ]


### 2. How is the overall rating distributed?

    [
        {"$group": {"_id": "$rating",
                    "Frequency": {"$sum": 1}}},
    ]

And the result is:

    [
        { _id: 4.5, Frequency: 16515 },                                                                                        
        { _id: 4, Frequency: 3260 },
        { _id: 5, Frequency: 10971 }
    ]  

### 3. Who are the top 10 most interactive reviewers?

This question can be answered with a simple aggregation pipeline using the $group, $sort and $limit:

    [
        {"$group": {"_id": "$reviewer_Name",
                            "Reviews": {"$sum": 1}}},
        {"$sort": {"Reviews":-1}},
        {"$limit": 10}
    ]

Returns:

    [
        { _id: 'enriqueolivierjr', Reviews: 33 },
        { _id: 'marciapir', Reviews: 30 },
        { _id: 'Lucia T', Reviews: 23 },
        { _id: 'Aalexei', Reviews: 20 },
        { _id: 'Heloisan', Reviews: 20 },
        { _id: 'yonnat', Reviews: 19 },
        { _id: 'ARTHUR M', Reviews: 19 },
        { _id: 'brunosvasconcelos', Reviews: 17 },
        { _id: 'solangeluna8', Reviews: 17 },
        { _id: 'Gabriela C', Reviews: 17 }                                                                                    
    ]

A simple dashboard using MongoDB charts summarises very well those answers:

[Click here to see the MongoDB chats Dashbord.](https://charts.mongodb.com/charts-m001-sfvgg/public/dashboards/4fafe90c-6c6a-4fc9-87ae-924cfe81d4c7)

Moreover, it is also possible to ask questions related to the content of the reviews:

4. What are the most common words in the reviews titles?
5. What are the most common words in the reviews text?
6. How the reviews scores affects the overall rating of the restaurant?
7. How the sentiment of reviews affects the overall rating?

Both this questions can be answered using Machine Learning methods, such as Random Forest and Logist Regression. To answer the fifth question we will need some Natural Language processing tools to extract the sentiment of each review and then compare to the overall rating.



