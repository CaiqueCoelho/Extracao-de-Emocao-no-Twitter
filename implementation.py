import re
import tweepy
import csv
import sys
import emoji
from tweepy import OAuthHandler
from textblob import TextBlob
from mtranslate import translate

 

tweetsPositives = []
tweetsNegatives = []
dictPositive = {}
dictNegatives = {}

class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''

    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'JkfuUkynd4WfxXLbSukFok7qJ'
        consumer_secret = 'fauEtTf9t7aLBY2oweFUgCkhOt54lPH51tJXsmCWFSQGSIVM3S'
        access_token = '2220145722-63yNKOyb0vEd5beJ7LDcutsMpNSiikfvWiAVvV9'
        access_token_secret = '1ekPldTcxHwdnouSamYtmZczBMxCtOnT94kSTTv9ntcz2'
 
        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def getWordNegatives(self):

        for tweet in tweetsNegatives:
            words = tweet.split()

            for word in words:
                existe = False
                if(word in dictNegatives):
                    existe = True      

                if(not existe):
                    dictNegatives[word] = 1
                if(existe):
                    count = dictNegatives[word]
                    count += 1
                    dictNegatives[word] = count

    def getWordPositives(self):

        for tweet in tweetsPositives:
            words = tweet.split()

            for word in words:
                existe = False
                if(word in dictPositive):
                    existe = True      

                if(not existe):
                    dictPositive[word] = 1
                if(existe):
                    count = dictPositive[word]
                    count += 1
                    dictPositive[word] = count

    def give_emoji_free_text(self, text):
        allchars = [str for str in text]
        emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
        clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
    
        return clean_text
 
    def clean_tweet(self, tweet):

        #Removing á and é from text, why? Study this in future

        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''

        text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())

        '''
        emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F1F2-\U0001F1F4"  # Macau flag
        u"\U0001F1E6-\U0001F1FF"  # flags
        u"\U0001F600-\U0001F64F"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U0001F1F2"
        u"\U0001F1F4"
        u"\U0001F620"
        u"\u200d"
        u"\u2640-\u2642"
        "]+", flags=re.UNICODE)

        text = emoji_pattern.sub(r'', text)
        '''
        

        text = self.give_emoji_free_text(text)
        

        return text
 
    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text

        traducao = TextBlob(self.clean_tweet(tweet))

        origin = traducao

        #print(traducao)

        try:
            #Service unvalible in 29/09/2018 at 2pm
            #if traducao.detect_language() != 'en':
            #traducao = TextBlob(str(traducao.translate(to='en')))
            traducao = TextBlob(translate(str(origin), "en"))
            print()
            print(origin)
        
        except:
            print()
            print("WARNING: TRANSLATION ERROR OR TRANSLATION EXCEPTION")

        #print("AAAA")

        # set sentiment
        if traducao.sentiment.polarity > 0:
            tweetsPositives.append(origin)
            return 'positive'
        elif traducao.sentiment.polarity == 0:
            return 'neutral'
        else:
            tweetsNegatives.append(origin)
            return 'negative'
 
    def get_tweets(self, query, count, tweet_mode, include_entities, truncated):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []
 
        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q = query, count = count, tweet_mode = 'extended')
 
            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}
 
                # saving text of tweet
                #parsed_tweet['text'] = tweet.text

                if(hasattr(tweet, 'retweeted_status')):

                    parsed_tweet['text'] = tweet.retweeted_status.full_text
                    parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.retweeted_status.full_text)
                else:
                    parsed_tweet['text'] = tweet.full_text

                    # saving sentiment of tweet
                    parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.full_text)
     
                    # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
 
            # return parsed tweets
            return tweets
 
        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))
 
def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    tweets = api.get_tweets(query = 'Bolsonaro', count = 100, tweet_mode='extended', include_entities=True, truncated=False)
 
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    # percentage of neutral tweets
    print("Neutral tweets percentage: {} %".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)))
 
    api.getWordPositives()
    api.getWordNegatives()

    print(dictPositive)

    with open('positive_words_bolsonaro.csv', 'w') as f:  # Just use 'w' mode in 3.x
        for key in dictPositive.keys():
            f.write("%s,%s\n"%(key,dictPositive[key]))


    with open('negative_words_bolsonaro.csv', 'w') as f:  # Just use 'w' mode in 3.x
        for key in dictNegatives.keys():
            f.write("%s,%s\n"%(key,dictNegatives[key]))

    # printing first 5 positive tweets
    print("\n\nPositive tweets:")
    for tweet in ptweets[:100]:
        print(tweet['text'])
 
    # printing first 5 negative tweets
    print("\n\nNegative tweets:")
    for tweet in ntweets[:100]:
        print(tweet['text'])

    f.close()
 
if __name__ == "__main__":

    #sys.stdout=open("out_candidate.txt","w")

    # calling main function
    main()
