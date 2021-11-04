import os
import random
import tweepy

# Twitter auth tokens
try:
    consumer_key = os.environ['xkN0usRya9qHAZa60ktOrvjGe']
    consumer_secret = os.environ['DZrKPRDhW5E4rGtrbj7Wcxm6ix5vWcBHgK2KO5TF9r1CasaeDQ']
    access_token = os.environ['1322976554922725384-lh41c7fEN3lzuzFzP5EwgqzVOEzmww']
    access_token_secret = os.environ['pwG8h6EquDCKJRcyQ59oCo8B3yV7p5Bs8G5MURJW0YFYs']

except KeyError:
    raise RuntimeError('Auth token credentials not found in environment variables')

# Initialize
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)

# Searchable tokens
search_tokens = [
    '@spooncentral',
    '#spoonie',
    '#spoonielife',
    '#chronicpain',
    '#chronicillness',
    '#chronicillnesswarrior',
    '#reliefnews',
    '#spoonies',
    '#EhlersDanlos',
    '#lupus',
    '#fibromyalgia',
    '#fibro',
    '#auotoimmunedisease',
    '#mcas'
]

# Scramble the list of tokens to use a different order to search every time
random.shuffle(search_tokens)

# Accounts to not re-tweet from
never_share_accounts = ['@joinwana']

for tweet in tweepy.Cursor(api.search,
                           q=f'{" OR ".join(search_tokens)} -filter:retweets AND -filter:replies',
                           result_type='recent',
                           lang='en',
                           tweet_mode='extended').items(1):
    print('\nTweet found for retweet:\n')
    print(tweet)

    # Skip re-tweeting from banned users
    if tweet.user.screen_name in never_share_accounts:
        print('Avoiding spam user: ', tweet.user.screen_name)
        break

    # Re-tweet
    tweet.retweet()

print('\nDone')
