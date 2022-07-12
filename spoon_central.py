import logging
import os
import random
import tweepy
from profanity_check import predict_prob
from tenacity import retry, stop_after_attempt, wait_fixed

def build_search_query(search_tokens):
    """Returns a search query used to find tweets using the given search tokens."""
    concatenated_tokens = ' OR '.join(search_tokens)
    filters = '-filter:retweets AND -filter:replies'
    return f'{concatenated_tokens} {filters}'

def pick_random_result_type():
    """Picks and returns a random result type from ['recent', 'popular', 'mixed']."""
    available_result_types = ['recent', 'popular', 'mixed']
    return random.choice(available_result_types)

def is_offensive(check_str, probability_threshold=0.50):
    """Returns true if the given string is offensive, false otherwise."""
    return predict_prob([check_str])[0] > probability_threshold

@retry(stop=stop_after_attempt(3), wait=wait_fixed(60))
def retweet(twitter_api, search_tokens, skip_retweet_accounts):
    """Uses the given search tokens to find tweets and retweet the given number of tweets."""
    # Scramble the list of tokens to use a different search each time
    random.shuffle(search_tokens)
    # Look at the first 10 results to find a tweet
    candidate_count = 10
    is_suitable_tweet_found = False
    for tweet in tweepy.Cursor(
            twitter_api.search_tweets,
            q=build_search_query(search_tokens),
            result_type=pick_random_result_type(),
            lang='en',
            tweet_mode='extended').items(candidate_count):
        logging.info(f'Candidate tweet:\n{tweet}')
        # Skip if it has already been retweeted
        if twitter_api.get_status(tweet.id).retweeted:
            logging.warning(f'Detected an already retweeted tweet: {tweet.full_text}')
            continue
        # Skip retweeting from banned users
        if tweet.user.screen_name in skip_retweet_accounts:
            logging.warning(f'Detected a spam user: {tweet.user.screen_name}. Skipping.')
            continue
        # Skip retweeting if the tweet is offensive
        if is_offensive(tweet.full_text):
            logging.warning(f'Detected an offensive tweet: {tweet.full_text}. Skipping.')
            continue
        # Tweet looks okay, retweet!
        logging.info(f'Retweeting: {tweet.full_text}')
        tweet.retweet()
        # Done
        logging.info(f'Retweet successful.')
        is_suitable_tweet_found = True
        break

    if not is_suitable_tweet_found:
        # No suitable tweets were found at this point
        logging.error('Failed to find a suitable tweet to retweet.')

def main():
    """Main function."""
    logging.getLogger().setLevel(logging.INFO)

    # Retrieve environment variables
    try:
        CONSUMER_KEY = os.environ['CONSUMER_KEY']
        CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
        ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
        ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
        COMMA_SEPARATED_SEARCH_TOKENS = os.environ['COMMA_SEPARATED_SEARCH_TOKENS']
        COMMA_SEPARATED_SKIP_RETWEET_ACCOUNTS = os.environ['COMMA_SEPARATED_SKIP_RETWEET_ACCOUNTS']
    except KeyError:
        raise RuntimeError('Missing a required field in the environment variables.')

    # Initialize Twitter API
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # Tokens used to find tweets
    search_tokens = list(map(str.strip, COMMA_SEPARATED_SEARCH_TOKENS.split(',')))
    # Accounts to not retweet from
    skip_retweet_accounts = set(map(str.strip, COMMA_SEPARATED_SKIP_RETWEET_ACCOUNTS.split(',')))

    # Find posts and retweet
    retweet(
        twitter_api=api,
        search_tokens=search_tokens,
        skip_retweet_accounts=skip_retweet_accounts)

    logging.info('Done.')


if __name__ == '__main__':
    main()
