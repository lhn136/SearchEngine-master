import json
import sys
from bs4 import BeautifulSoup
import re
import pymongo
import math
from pymongo import MongoClient


index = {}
count = 0 #debug

def readingJson():
    json_file = open('../WEBPAGES_RAW/bookkeeping.json')
    json_str = json_file.read()
    json_data = json.loads(json_str)
    json_file.close()
    return json_data

def tokenizefile(filepath):

    '''Read a file with BS, and exclude scripts from being read'''
    soup = BeautifulSoup(open('../WEBPAGES_RAW/'+filepath),'html.parser')

    for script in soup(['style', 'script']): # remove all script and style from being parse
        script.extract()

    return readwords(soup.get_text())


def readwords(words):
    '''empty dictionary to store word occurences'''
    dictionary = dict()


    # this processedline removes unwanted symbols
    processedline = re.sub('[^a-zA-Z0-9 \n\r]', ' ', words).split()

    for word in (processedline):
        word = word.lower()
        if dictionary.has_key(word):
            # this adds onto the existing key satisfy by the condition statement above
            dictionary[word] += 1
        else:
            # this reads adds a new key into the dictionary and setting it at 1
            dictionary.update({word:1})

    return dictionary


def updateMongo():
    ''' create an inverted index for each word (refer to the paper)'''
    json_data = readingJson()           # loads in all file path from book keep from json
    global index
    global count

    for key in json_data.keys():        # for each key = directory
        # print "Processing file path", key
        count += 1                      # increment document counter

        wordDict = (tokenizefile(key))  # dictionaries of words : frequencies

        # if index.has_key():
        for word in wordDict: # tokenize dictionary for the supplied file path for key
            if index.has_key(word):
                # if not in dict, create sub dict and update mongodo with sub dict
                index[word].update({str(key):wordDict[word]})
            else:
                index[word] = {str(key):wordDict[word]}

        # if count == 5:
        #     return (index)

    return (index)


def pushtoMongo(file):
    # create connection to db
    client = MongoClient('mongodb://localhost:27017')
    db = client.project3v2
    posts = db.posts

    # for key in file.keys():
    #
    #     # we can find idf here by getting the length of each keys, take log of that
    #     # then find tf inside of the inner for loop
    #
    #
    #     for item in file[key]: # this is another dictionary
    #
    #         # inside here, tf is file[key][item]
    #         # multiply that by the idf found in the outside loop
    #         # the result will be tf-idf to be stored
    #
    #         post_id = posts.insert({ key :"term" , # this is the term
    #                                  'docID': item, # directory of the term
    #                                  'tf': file[key][item], # instead of storing tf, store tf-idf just calculated
    #                                  } )

    for term in file.keys():


        # we can find idf here by getting the length of each keys, take log of that
        # then find tf inside of the inner for loop
        tobeLogged = (float(count)) / len(file[term])
        # print tobeLogged, count, len(file[term]), math.log(count / len(file[term]))
        idf = math.log( tobeLogged ) # can be different base



        for docID in file[term]: # this is another dictionary


            tf = 1 + float(math.log(file[term][docID]))

            rating = float(idf * tf)
            # inside here, tf is file[key][item]
            # multiply that by the idf found in the outside loop
            # the result will be tf-idf to be stored

            #
            post_id = posts.insert({ term :"term" , # this is the term
                                     'docID': docID, # directory of the term
                                     'tf': tf, # instead of storing tf, store tf-idf just calculated
                                     'idf': idf,
                                     'rating': rating, # rating is tf-idf
                                     } )
            # print "term", term
            # print "docID", docID
            # print "tf", tf
            # print "idf", idf
            # print "rating", rating
            # print ""





print "Starting program to parse files and create database..."
post = updateMongo()

print ""
print ("Documents Read: " ,  count)
print ""
print ("Unique Words:" , len (index) )
print ("Unique Words:" , len (post) )
print ""

print "Pushing to the dbs now!!"
pushtoMongo(post)
print "Done pushing!! Data will all be in local dbs"
