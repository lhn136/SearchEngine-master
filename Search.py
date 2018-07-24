import pymongo
from pymongo import MongoClient
import json

def oneWordSearch(db, word, data):
    results = db.find({word.lower():"term"}).sort("rating",pymongo.DESCENDING).limit(10)

    if len(str(results)) == 0:
        return False
    count = 0
    for post in results:
        count +=1
        print str(count)+"."
        print("       URL: "+data[post["docID"]])
        print("       RATING (tf-idf): "+str(post["rating"]))
        print""
    return True

def multiWord(db, words, data):
    commonDocID = {}
    words = set(words.split())
    for word in words:
        print ""
        print "Querying word: " , word

        results = db.find({word.lower():"term"})

        for item in results:
            key = item["docID"]
            values = (item["rating"], 1) 
            
            # if commonDic contains website then increment occurence and update td-idf
            if commonDocID.has_key(key):
                
                incrementOccurence = commonDocID[key][1] + 1
                updateTDIDF = commonDocID[key][0] + item["rating"]
                
                commonDocID[key] = (updateTDIDF, incrementOccurence)

            else: 
                commonDocID[key] = values

            

    if len(commonDocID) == 0:
        return False

    # sort values in dictionary
    # print top values
    # for k,v in sorted(dictionary_input.items(),key=lambda x:(-x[1],x[0].lower()),reverse=False)
    count = 0
    for item in sorted(commonDocID.items(),key = lambda x: (x[1][1],x[1][0]), reverse = True):
        count += 1
        print str(count)+"."
        print("       URL: "+str(data[item[0]]))
        print("       RATING (tf-idf): "+str(item[1][0]))
        print""


        if count == 10:
            break;
    return True

def readingJson():
    json_file = open('./WEBPAGES_RAW/bookkeeping.json')
    json_str = json_file.read()
    json_data = json.loads(json_str)
    json_file.close()
    return json_data

def SearchEngine():
    userInput = ""
    data = readingJson()
    print("")
    print ("      _______________________________________________________________")
    print("")
    print("                      Welcome to our Search Engine")
    print("")
    print("                        ** enter 999 to quit **")
    print("")
    print ("      _______________________________________________________________")
    print("")

    # connecting to the dbs only once
    client = MongoClient('mongodb://localhost:27017')

    db = client.project3v2
    dbConnector = db.posts

    while userInput.strip() != "999":

        result = []
        userInput = str(raw_input("SEARCH: "))

        if userInput.strip() != "999":
            print("SEARCHING FOR \""+str(userInput.lower())+"\" ...")
            print("")
            print"RESULTS FOR \"" + userInput.lower() +"\":"
            print("")

            hasResults = False

            #handle 1 word search
            if len(userInput.split(" ")) == 1:
                hasResults = oneWordSearch(dbConnector, userInput, data)
            #handle multijob
            else:
                hasResults = multiWord(dbConnector, userInput, data)

            if hasResults == False:
                print "No results"

            #handle multie search

            print ("      _______________________________________________________________")
            print("")

        else:
            print("Quitting Search \nShut Down...")
            print("")
            print("")

        # close connection
        client.close()

SearchEngine()