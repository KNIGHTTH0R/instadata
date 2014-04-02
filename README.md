insta-data
==========

A short module to get followers and followings data for a given instagram user.


Introduction
============

Instadata basically collects (and processes) the data for a network of a user. Using instadata, you can (as of this point) collect the following data types for users:

* usernames for all the followers/followings of a given instagram user
* processed bios for all the followers/followings of a given instagram user (for nlp purposes)


Basic Usage
===========

#####To get data for all the users followed by a given user:

######get_follows(*username, type_q, stop_value=None, access_token=None*)

-- username: Valid username of the target user (required)

-- *type_q*: Type of data required, which can be either ```'users_only'``` (to get all the usernames) or ```'bio_only'``` (to get all the usernames and their corresponding bio texts as ```[{'username': username, 'bio': bio_text}]```). (required)

-- stop_value: This is an optional parameter to specify how many records you want to retrieve. Not specifying it by default retrieves all the available data.

-- *access_token* : If you want to provide your own instagram access_token for getting access to data of users that are private to public but visible to you. The module uses a default instagram access token, which is only able to access public profiles.

    from instadata import get_follows
    follows = get_follows(username='username', type_q='users_only')

-- **Returns**: *a [list] of all the usernames/bios of users followed by the target user*  




#####To get all the users (usernames only) following a particular user:

######get_followers(*username, type_q, stop_value=None, access_token=None*)

-- *username*: Valid username of the target user (required)

-- *type_q*: Type of data required, which can be either ```'users_only'``` (to get all the usernames) or ```'bio_only'``` (to get all the usernames and their corresponding bio texts as ```[{'username': username, 'bio': bio_text}]```). (required)

-- *stop_value*: This is an optional parameter to specify how many records you want to retrieve. Not specifying it by default retrieves all the available data.

-- *access_token*: If you want to provide your own instagram access_token for getting access to data of users that are private to public but visible to you. The module uses a default instagram access token, which is only able to access public profiles.

    from instadata import get_followedby
    followedby = get_followedby(username='username', type_q='users_only')

-- **Returns**: *a [list] of all the usernames/bios of users following the target user*  




Advanced Usage:
===============

Instadata can be used in multiple ways to extract the semantic, sentiment-based and many other dimensions of the users' followers and followings. As of now, Instadata suports following key classification, grouping and clustering techniques:


#####To get all the followers of a user classified (interconnected) with each other based on the semantic relationship of their instagram bios.

######classify_followers_semantically(*username*, *stop_value=None*, *access_token=None*):

-- *username*: Valid username of the target user (required)

-- *stop_value*: This is an optional parameter to specify how many records you want to retrieve. Not specifying it by default retrieves all the available data.

-- *access_token*: If you want to provide your own instagram *access_token* for getting access to data of users that are private to public but visible to you. The module uses a default instagram access token, which is only able to access public profiles.

    from instadata import classify_followers_semantically
    semantic_grouping = classify_followers_semantically('username')
    
-- **Returns**: *a list containing all the followers and their semantically related neighbors from within the followers of the target user* 


#####To get all the followings of a user classified (interconnected) with each other based on the semantic relationship of their instagram bios.

######classify_followings_semantically(*username*, *stop_value=None*, *access_token=None*):

-- *username*: Valid username of the target user (required)

-- *stop_value*: This is an optional parameter to specify how many records you want to retrieve. Not specifying it by default retrieves all the available data.

-- *access_token*: If you want to provide your own instagram *access_token* for getting access to data of users that are private to public but visible to you. The module uses a default instagram access token, which is only able to access public profiles.

    from instadata import classify_followings_semantically
    semantic_grouping = classify_followings_semantically('username')
    
-- **Returns**: *a list containing all the following users and their semantically related neighbors from within the followings of the target user* 




#####To get all the followers of a user clustered into groups based on the sentiment reflected in their bios.

######cluster_followers_sentiments(*username*, *stop_value=None*, *access_token=None*):

-- *username*: Valid username of the target user (required)

-- *stop_value*: This is an optional parameter to specify how many records you want to retrieve. Not specifying it by default retrieves all the available data.

-- *access_token*: If you want to provide your own instagram *access_token* for getting access to data of users that are private to public but visible to you. The module uses a default instagram access token, which is only able to access public profiles.

    from instadata import cluster_followers_sentiments
    sentiment_clusters, centroids = cluster_followers_sentiments('username')
    
-- **Returns**: *clusters and centroids associated with each sentiment based clusters found within the user's followers data* 


#####To get all the followings of a user clustered into groups based on the sentiment reflected in their bios.

######cluster_followings_sentiments(*username*, *stop_value=None*, *access_token=None*):

-- *username*: Valid username of the target user (required)

-- *stop_value*: This is an optional parameter to specify how many records you want to retrieve. Not specifying it by default retrieves all the available data.

-- *access_token*: If you want to provide your own instagram *access_token* for getting access to data of users that are private to public but visible to you. The module uses a default instagram access token, which is only able to access public profiles.

    from instadata import cluster_followings_sentiments
    sentiment_clusters, centroids = cluster_followings_sentiments('username')
    
-- **Returns**: *clusters and centroids associated with each sentiment based clusters found within the user's followings data* 