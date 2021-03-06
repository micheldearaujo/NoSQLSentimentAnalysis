<div>

# Improving restaurants performance using Sentiment Analysis


<p align="center">
<img width="692" height="401" src="images/unplash_markus_winkler.jpg">

</div>

<div>

## Introduction

In this project, we will build a NoSQL database that stores reviews of restaurants scraped from the web and will be the base for
querying data to create a Machine Learning classifier that tries to predict the overall rating of a restaurant based on the
sentiment analysis of its reviews. In the figure bellow you can see the overview of the project workflow.


<p align="center">
<img width="471" height="233" src="images/projectFlowChart.png">

</div>


<div>

### Sentiment Analysis

Sentiment analysis, also known as opinion mining, is a natural language processing technique used to determine whether
a text is positive, negative or neutral. It is also possible to find other sentiments, like anger and sadness.
Therefore, this process has become crucial when business want to know better how their products are performing.

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
lead us in a collection with a number of documents that goes from a hundred thousands to millions.
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

However, as the size of this dataset will be only a small sample of the whole restaurants in Brazil, it will be kept simple and choose the schema I for simplicity.

Please refer to the [multiple_restaurants_scraper.py](https://github.com/micheldearaujo/NoSQLSentimentAnalysis/blob/main/src/multiple_restaurants_scraper.py) to view the code in depth.

Later after gathering 30745 reviews of 40 restaurants we realized that was forgotten valuable information, the reviews score. So we went back and scraped the missing data and completed the schema, as can be seen bellow.

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

In the next section we will start explore this data using Python.

## Answering some basic questions - Exploratory Data Analysis

What kind of answers can we get from this dataset? Here are some basic questions to make:

### 1. How many reviews each restaurant has?

When building a Machine Learning model, it is essential to have a balanced dataset. This will ensure that our model is not biased. We can answer this question
using the following MongoDB query:

    [
        {"$group": {"_id": "$restaurant_name",
                            "Reviews": {"$sum": 1}}},
        {"$sort": {"Reviews": -1}},
        {"$limit": 20}
    ]

The following result is showed to us:

    [
    { _id: 'Coco Bambu Recife', Reviews: 5605 },
    { _id: 'Camarada Camar??o - Shopping Recife', Reviews: 2592 },
    { _id: 'Chica Pitanga', Reviews: 2587 },
    { _id: 'Camarada Camarao - RioMar Recife', Reviews: 2111 },
    { _id: 'Barga??o', Reviews: 1765 },
    { _id: 'Outback Steakhouse - Shopping RioMar Recife', Reviews: 1331 },
    { _id: 'Bode Do N??', Reviews: 1177 },
    { _id: 'Churrascaria Ponteio', Reviews: 979 },
    { _id: 'Churrascaria Sal e Brasa Recife', Reviews: 846 },
    { _id: 'Parraxaxa - Boa Viagem', Reviews: 833 },
    { _id: 'Guaiamum Gigante', Reviews: 786 },
    { _id: 'Parraxax??', Reviews: 767 },
    { _id: 'Ilha dos Navegantes', Reviews: 703 },
    { _id: 'Spettus Steak House', Reviews: 656 },
    { _id: '??a Va', Reviews: 611 },
    { _id: 'Pobre Juan - Recife', Reviews: 570 },
    { _id: 'Ilha Camar??es', Reviews: 567 },
    { _id: 'Dom Ferreira Forneria', Reviews: 546 },
    { _id: 'Castelus Restaurante', Reviews: 512 },
    { _id: 'Mingus', Reviews: 410 }
    ]

We conclude that there is a huge gap between the biggest and the smallest number of reviews. The restaurant with most reviewed is the Coco Bambu Recife,
with 5605 reviews, against the Mingus restaurant, holding only 410 reviews.


### 2. How is the overall rating distributed?

This question has a similar importance as the last one. The overall rating is our target variable, so it would be great if the rating values were well
distributed. For answering this question we need to create a grouping statement in the "rating" variable, and count the occurrences.

    [
        {"$group": {"_id": "$rating",
                    "Frequency": {"$sum": 1}}},
    ]

The output:

    [
        { _id: 4.5, Frequency: 16515 },                                                                                        
        { _id: 4, Frequency: 3260 },
        { _id: 5, Frequency: 10971 }
    ]  

This is not the most well distributed variable ever. The "4.0" rating is quite unpopular, and the majority of the reviews are gathered in the "4.5" and "5.0".


### 3. Who are the top 10 most interactive reviewers?

This is not a key-question to our problem, but it would be nice to know who are the most interactive users.
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

We see that some users are quite active in TripAdvisor. The first one, 'enriqueolivierjr' has 33 reviews out of 40 restaurants in our database.
This query shows us that there is a group of users that uses to go to restaurants with a high frequency.


A simple dashboard using MongoDB charts summarises very well those answers:

[Click here to see the MongoDB charts Dashboard.](https://charts.mongodb.com/charts-m001-sfvgg/public/dashboards/4fafe90c-6c6a-4fc9-87ae-924cfe81d4c7)

Moreover, it is also possible to ask questions related to the content of the reviews:

4. What are the most common words in the reviews titles?
5. What are the most common words in the reviews text?
6. How the reviews scores affects the overall rating of the restaurant?
7. How the sentiment of reviews affects the overall rating?

Both questions 6 and 7 can be answered using Machine Learning methods, such as Random Forest and Logistic Regression. To answer the questions 4 
and 5 we will need Natural Language processing tools to extract the sentiment of each review and then compare to the overall rating.

For the in-depth code, see the [Exploratory Notebook](https://github.com/micheldearaujo/NoSQLSentimentAnalysis/blob/main/src/Exploratory_Analysis.ipynb).

### 4. What are the most common words in the reviews titles?
In order to answer that question it will be necessary to concatenate all the reviews titles in one string and then 
perform a Term Frequency count in those words. There are two ways of answering that question:
#### Using a Word Cloud

<p align="center">
<img width="400" height="200" src="images/wordcloud1.png">

and

#### Using a bar plot

<p align="center">
<img width="892" height="501" src="images/words_bar1.png">

Great! This word cloud shows us that the majority of the reviews titles relates to the rating of the restaurant. Being "Excellent" the title most 
attributed to the user experience. Then comes "Good", "Best", "Wonderful". The other group of titles relates to the type of meal that users were 
having, like "Lunch" and "Dinner". It is also possible to create a bar plot to show the exact frequency of the words. For that, we have to count 
the frequency of each word, also known as Term Frequency.

### 5. What are the most common words in the reviews text?

First, what looks like the sentiment polarity distribution? The sentiment analyzer from TextBlob results a value from -1 to 1 to a sentence.
-1 stands for very negative sentiments, 0 to neutral and +1 to very positive sentiments.

<p align="center">
<img width="892" height="501" src="images/sent_dist.png">

The reviews sentiments follows a normal distribution centered at the 0.5! This means that in average, the review sentiments are just positive, with 
a smaller number of extremely positive reviews and slightly positive. We have a peak of neutral sentiments at 0, and some residual slightly negative 
sentiments. This is an interesting result, it seems that the majority of peoples experiences with restaurants are pleasant. Also, the there is a peak in the reviews with sentiment polarity close to 0 positively. This tells us that a lot of the reviews does not carry any complement of complaining about the user experience. This reviews are probably just describing the experience in a neutral form.

<p align="center">
<img width="400" height="220" src="images/wordcloud_neg.png">

Well, if you know some portuguese you will realize that the majority of those words are not actually negative. There is some word has appears with low frequency with negative meaning, such as "bad", "therefore", "because".
As we saw that the amount of negative reviews is quite low, the "positive" word cloud problably will not be that much different from the general word cloud that we have already made. So, let's continue with the negative sentiments and make a bar plot with the frequencies.

<p align="center">
<img width="892" height="501" src="images/words_bar2.png">

## Creating a Machine Learning model to predict the restaurant rating

Let's end this notebook here and let the Machine Learning model section to a separated notebook. See the [Rating Predictor](https://github.com/micheldearaujo/NoSQLSentimentAnalysis/blob/main/src/Rating%20Predictor.ipynb).