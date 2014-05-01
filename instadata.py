from __future__ import division
import sys
import os
import re
import ast
from compiler.ast import flatten
import urllib2
import json
from time import time as tm
import numpy

def get_id(username, access_token):
    try:       
        for a in json.loads(urllib2.urlopen('https://api.instagram.com/v1/users/search?q='+username+'&access_token='+access_token).read())['data']:
            if a['username'] == username:
                _id = str(a['id'])
                break
        return _id
    except Exception, e:
        #error = str(e)
        print "invalid username provided..exiting.."
        sys.exit()

def followers_crawler(_id, y, counter, stop_value, access_token, url=None):
    try:
        stop_value = 30
        if counter > stop_value:
            return y
        else:
            data = []
            
        if not url:
            response = urllib2.urlopen('https://api.instagram.com/v1/users/'+_id+'/followed-by?access_token='+access_token)
            t = response.read()
            t = json.loads(t)
            data = t
        else:
            response = urllib2.urlopen(url)
            t = response.read()
            t = json.loads(t)
            
        if t.has_key('pagination'):
            if t['pagination'].has_key('next_url'):
                counter = counter+1
                y.append(followers_crawler(_id, [t], counter, stop_value, access_token, t['pagination']['next_url']))
            else:
                print "done"
        return y, data                
    except:
        print "user is private..terminating.."
    
    

def follows_crawler(_id, y, counter, stop_value, access_token, url=None):
    
    try:
        stop_value = 30
        if counter > stop_value:
            return y
        else:
            data = []
        
        if not url:
            response = urllib2.urlopen('https://api.instagram.com/v1/users/'+_id+'/follows?access_token='+access_token)
            t = response.read()
            t = json.loads(t)
            data = t
        else:
            response = urllib2.urlopen(url)
            t = response.read()
            t = json.loads(t)
            
        if t.has_key('pagination'):
            if t['pagination'].has_key('next_url'):
                counter = counter+1
                y.append(follows_crawler(_id, [t], counter, stop_value, access_token, t['pagination']['next_url']))
            else:
                print "done"

        return y, data
                
    except:
        print "user is private..terminating.."
        


def get_followers(username, type_q, stop_value=None, access_token=None):
    """Returns data of all the users following a particular user."""
    t1 = tm()
    
    print_results = 'no'
    
    followed_by = []

    try:
        if not access_token:
            access_token = '1013808034.cdfd9a8.6dc3da1cfcb64628b5c056381f372cba'

        _id = get_id(username.encode('utf-8'), access_token)
        y, data = followers_crawler(_id, [], 0, stop_value, access_token)
    
        if len(flatten(flatten(y))) > len(data):
            #del data[:]
            for a in flatten(flatten(y)):
                if type_q == 'users_only':
                    followed_by.append([b['username'] for b in a['data']])
                elif type_q == 'user_and_bio':
                    followed_by.append([{'username': b['username'], 'bio': b['bio']} for b in a['data']])
            t2 = tm()
            #del y[:]
        else:
            #del y[:]
            for a in data['data']:
                if type_q == 'users_only':
                    followed_by.append(a['username'])
                elif type_q == 'user_and_bio':
                    followed_by.append({'username': a['username'], 'bio': a['bio']})
            #del data[:]
            t2 = tm()
        
        print "total time spent: "+ str(float(t2-t1)) + " seconds"
        
        if print_results == 'yes':
            print flatten(followed_by)
        else:
            return flatten(followed_by)
    except:
        return followed_by



def get_follows(username, type_q, stop_value=None, access_token=None):
    """Returns data for all the followers for a given user"""
    t1 = tm()
    print_results = 'no'
    follows = []
    try:
        if not access_token:
            access_token = '1013808034.cdfd9a8.6dc3da1cfcb64628b5c056381f372cba'
        
        _id = get_id(username.encode('utf-8'), access_token)
        y, data = follows_crawler(_id, [], 0, stop_value, access_token)
        
        if len(flatten(flatten(y))) > len(data):
            #del data[:]
            for a in flatten(flatten(y)):
                if type_q == 'users_only':
                    follows.append([b['username'] for b in a['data']])
                elif type_q == 'user_and_bio':
                    follows.append([{'username': b['username'], 'bio': b['bio']} for b in a['data']])
            #del y[:]
            t2 = tm()
        else:
            #del y[:]
            for a in data['data']:
                if type_q == 'users_only':
                    follows.append(a['username'])
                elif type_q == 'user_and_bio':
                    follows.append({'username': a['username'], 'bio': a['bio']})
            #del data[:]
            t2 = tm()

        print "total time spent: "+ str(float(t2-t1))  + " seconds."
        
        if print_results == 'yes':
            print flatten(follows)
        else:
            return flatten(follows)
    except:
        return follows


def tokenize_all(bios):
    stopwords = numpy.load('stopwords.bin')
    return filter(lambda x: [g not in stopwords for g in x['bio']],[{'username': a['username'], 'bio': a['bio'].lower().split()} for a in bios])


def classify_followers_semantically(username, stop_value=None, access_token=None):
    """Returns a list of all the followers of a users classified according to their bios"""
    try:
        import string
        from sklearn.neighbors import NearestNeighbors
        from sklearn.feature_extraction.text import CountVectorizer
        
        specials = lambda x: re.sub('[^A-Za-z0-9]+',' ', x)
        non_empty = lambda x: x if x != ' ' else ''
        filter_crap = lambda x: {'username': x['username'], 'bio': map(non_empty, re.sub(r'[^\x00-\x7f]',r' ', re.sub('[^A-Za-z0-9]+', ' ', x['bio'])).encode('utf-8').strip(' \t\n\r').split())}
        non_zero = lambda x: len(x['bio']) > 3
        joiner = lambda x: {'username': x['username'], 'bio': ' '.join(x['bio'])}

        classified = []
        
        followers_data = numpy.array(map(joiner, filter(non_zero, map(filter_crap, get_followers(username, 'user_and_bio')))))
        
        try:
            vectorizer = CountVectorizer(min_df=4)
            
            X = vectorizer.fit_transform(map(str, map(specials, [filter(lambda x: x in string.printable, s) for s in [b['bio'] for b in followers_data]])))
            print "yoohoo"
        except:
            try:
                vectorizer = CountVectorizer(min_df=3)
                X = vectorizer.fit_transform(map(str, map(specials, [filter(lambda x: x in string.printable, s) for s in [b['bio'] for b in followers_data]])))
            except:
                try:
                    vectorizer = CountVectorizer(min_df=2)
                    X = vectorizer.fit_transform(map(str, map(specials, [filter(lambda x: x in string.printable, s) for s in [b['bio'] for b in followers_data]])))
                except:
                    try:
                        vectorizer = CountVectorizer(min_df=1)
                        X = vectorizer.fit_transform(map(str, map(specials, [filter(lambda x: x in string.printable, s) for s in [b['bio'] for b in followers_data]])))
                    except:
                        print "every measure failed..exit"
                        sys.exit()

        if len(X.toarray()) >= 5:
            k = 5
        else:
            k = len(X.toarray())
        
        neighbors = NearestNeighbors(n_neighbors=k, algorithm='ball_tree').fit(X.toarray())
        
        for a, b in zip(X.toarray(), range(0, len(X.toarray()))):
            distances, indices = neighbors.kneighbors(a)
            classified.append({'related': [t['username'] for t in followers_data[flatten(indices)] if t['username'] != followers_data[b]['username'] ], 'username': followers_data[b]['username']})
        
        return classified
    except ImportError, e:
        print "please install scikit-learn from http://scikit-learn.org/ to utilize this method.."


def classify_followings_semantically(username, stop_value=None, access_token=None):
    """Returns a list of all the followings of a users classified according to their bios"""
    try:
        import string
        from sklearn.neighbors import NearestNeighbors
        from sklearn.feature_extraction.text import CountVectorizer

        specials = lambda x: re.sub('[^A-Za-z0-9]+',' ', x)
        non_empty = lambda x: x if x != ' ' else ''
        filter_crap = lambda x: {'username': x['username'], 'bio': map(non_empty, re.sub(r'[^\x00-\x7f]',r' ', re.sub('[^A-Za-z0-9]+', ' ', x['bio'])).encode('utf-8').strip(' \t\n\r').split())}
        non_zero = lambda x: len(x['bio']) > 3
        joiner = lambda x: {'username': x['username'], 'bio': ' '.join(x['bio'])}

        classified = []
        
        follows_data = numpy.array(map(joiner, filter(non_zero, map(filter_crap, get_follows(username, 'user_and_bio')))))
        
        try:
            vectorizer = CountVectorizer(min_df=4)
            X = vectorizer.fit_transform(map(str, map(specials, [filter(lambda x: x in string.printable, s) for s in [b['bio'] for b in follows_data]])))
        except:
            try:
                vectorizer = CountVectorizer(min_df=3)
                X = vectorizer.fit_transform(map(str, map(specials, [filter(lambda x: x in string.printable, s) for s in [b['bio'] for b in follows_data]])))
            except:
                try:
                    vectorizer = CountVectorizer(min_df=2)
                    X = vectorizer.fit_transform(map(str, map(specials, [filter(lambda x: x in string.printable, s) for s in [b['bio'] for b in follows_data]])))
                except:
                    try:
                        vectorizer = CountVectorizer(min_df=1)
                        X = vectorizer.fit_transform(map(str, map(specials, [filter(lambda x: x in string.printable, s) for s in [b['bio'] for b in follows_data]])))
                    except:
                        print "every measure failed..exiting"
                        sys.exit()
        
        if len(X.toarray()) >= 5:
            k = 5
        else:
            k = len(X.toarray())
        
        neighbors = NearestNeighbors(n_neighbors=k, algorithm='brute').fit(X.toarray())
        
        for a, b in zip(X.toarray(), range(0, len(X.toarray()))):
            distances, indices = neighbors.kneighbors(a)
            classified.append({'related': [t['username'] for t in follows_data[flatten(indices)] if t['username'] != follows_data[b]['username'] ], 'username': follows_data[b]['username']})
                        
        return classified
    except ImportError, e:
        print "please install scikit-learn from http://scikit-learn.org/ to utilize this method.."



def clf2(username, stop_value=None, access_token=None):
    try:
        import re
        non_empty = lambda x: x if x != ' ' else ''
        filter_crap = lambda x: {'username': x['username'], 'bio': map(non_empty, re.sub(r'[^\x00-\x7f]',r' ', re.sub('[^A-Za-z0-9]+', ' ', x['bio'])).encode('utf-8').strip(' \t\n\r').split())}
        non_zero = lambda x: len(x['bio']) > 3
        joiner = lambda x: {'username': x['username'], 'bio': ' '.join(x['bio'])}
        
        followers_data = numpy.array(map(joiner, filter(non_zero, map(filter_crap, get_followers(username, 'user_and_bio')))))
        
        return followers_data
        
    except Exception, e:
        print str(e)

#--here we normalize using a z-score        
def normalize(sentiment):
    sentiment -= numpy.mean(sentiment, axis=0)
    sentiment /= numpy.std(sentiment, axis=0)
    return sentiment


def cluster_followers_sentiments(username, stop_value=None, access_token=None):
    """Returns a list of all the followers of a users clustered according to the sentiment reflected in their bios"""
    try:
        from textblob import TextBlob
        from scipy.cluster import vq
        import numpy

        non_empty = lambda x: x if x != ' ' else ''
        filter_crap = lambda x: {'username': x['username'], 'bio': map(non_empty, re.sub(r'[^\x00-\x7f]',r' ', re.sub('[^A-Za-z0-9]+', ' ', x['bio'])).encode('utf-8').strip(' \t\n\r').split())}
        non_zero = lambda x: len(x['bio']) > 3
        joiner = lambda x: {'username': x['username'], 'bio': ' '.join(x['bio'])}
        whiten = lambda obs: obs/numpy.std(obs)

        followers_data = numpy.array(map(joiner, filter(non_zero, map(filter_crap, get_followers(username, 'user_and_bio')))))
        
        grouped = []

        t = [{'username': a['username'],
                'bio': a['bio'],
                'sentiment': [float(a) for a in TextBlob(a['bio']).sentiment]} for a in followers_data]
        
        centers, dist = vq.kmeans(numpy.array([[a['sentiment'][0], a['sentiment'][1]] for a in t]), whiten(numpy.array([[a['sentiment'][0], a['sentiment'][1]] for a in t])), 100)
        code, distance = vq.vq(numpy.array([[a['sentiment'][0], a['sentiment'][1]] for a in t]), centers)
        
        for i in range(0, len(centers)):
            grouped.append({'centroid': {'polarity': list(map(float, centers[i]))[0], 'subjectivity': list(map(float, centers[i]))[1]},
                              'cluster': list(numpy.array([{'polarity': a['sentiment'][0], 'subjectivity': a['sentiment'][1], 'username': a['username']} for a in t])[code==i])})
        
        centers = sorted([list([float(b) for b in a]) for a in centers])
        
        return grouped, centers
                
        return t
    except Exception, e:
        print str(e)


def cluster_followings_sentiments(username, stop_value=None, access_token=None):
    """Returns a list of all the followings of a users clustered according to the sentiment reflected in their bios"""
    try:
        from textblob import TextBlob
        from scipy.cluster import vq
        import numpy
        
        non_empty = lambda x: x if x != ' ' else ''
        filter_crap = lambda x: {'username': x['username'], 'bio': map(non_empty, re.sub(r'[^\x00-\x7f]',r' ', re.sub('[^A-Za-z0-9]+', ' ', x['bio'])).encode('utf-8').strip(' \t\n\r').split())}
        non_zero = lambda x: len(x['bio']) > 3
        joiner = lambda x: {'username': x['username'], 'bio': ' '.join(x['bio'])}
        whiten = lambda obs: obs/numpy.std(obs)
        
        follows_data = numpy.array(map(joiner, filter(non_zero, map(filter_crap, get_follows(username, 'user_and_bio')))))
 
        grouped = []
        
        t = [{'username': a['username'],
                'bio': a['bio'],
                'sentiment': [float(a) for a in TextBlob(a['bio']).sentiment]} for a in follows_data]
        
        centers, dist = vq.kmeans(numpy.array([[a['sentiment'][0], a['sentiment'][1]] for a in t]), whiten(numpy.array([[a['sentiment'][0], a['sentiment'][1]] for a in t])), 100)
        code, distance = vq.vq(numpy.array([[a['sentiment'][0], a['sentiment'][1]] for a in t]), centers)
        
        for i in range(0, len(centers)):
            grouped.append({'centroid': {'polarity': list(map(float, centers[i]))[0], 'subjectivity': list(map(float, centers[i]))[1]},
                              'cluster': list(numpy.array([{'polarity': a['sentiment'][0], 'subjectivity': a['sentiment'][1], 'username': a['username']} for a in t])[code==i])})
        
        centers = sorted([list([float(b) for b in a]) for a in centers])
        
        return grouped, centers
    except Exception, e:
        print str(e)



        
        
