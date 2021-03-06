# Dependencies
import sys
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import (consumer_key, consumer_secret,
                    access_token, access_token_secret)

# Setup Tweepy API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser(),
                 wait_on_rate_limit=False, wait_on_rate_limit_notify=False)

# Initialize Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# "Real Person" Filters
min_tweets = 5
max_tweets = 10000
max_followers = 2500
max_following = 2500
lang = "en"


# Function to search today's most recent tweets
def searchToday():

    # Grab today's date
    today = dt.datetime.now()

    # Create variable for holding the oldest tweet
    oldest_tweet = None

    # List to hold average compound values for each movie
    compound_list = []

    # Create list of dictionaries
    sentiment = []

    # List of some tweets
    tweet_text_list = []

    # Instantiate tweet count
    tweet_count = 1

    try:

        # Paginate 10 times (Total of 1000 Tweets)
        for x in range(10):

            # Get all tweets from home feed (for each page specified)
            public_tweets = api.search(search_term,
                                       count=100,
                                       lang='en',
                                       result_type="recent",
                                       max_id=oldest_tweet)

            # Loop through all tweets
            for tweet in public_tweets['statuses']:

                # Use filters to check if user meets conditions
                if (tweet["user"]["followers_count"] < max_followers and
                        tweet["user"]["statuses_count"] > min_tweets and
                        tweet["user"]["statuses_count"] < max_tweets and
                        tweet["user"]["friends_count"] < max_following and
                        tweet["user"]["lang"] == lang):

                    # Grab tweet data
                    tweet_text = tweet['text']

                    # Append a few tweets to tweet list
                    tweet_text_list.append(tweet_text)

                    # Run Vader Analysis on each tweet
                    results = analyzer.polarity_scores(tweet_text)
                    compound = results["compound"]

                    # Append compound values to list
                    compound_list.append(compound)

                    # Create dictionary holding tweet data
                    tweet_dict = {'Search_term': search_term, 'Date': today, 'Compound': compound,
                                  'Tweets Ago': tweet_count}

                    # Increment tweet_count
                    tweet_count += 1

                    # Append tweet data to sentiment list
                    sentiment.append(tweet_dict)

                    # Reassign the the oldest tweet (i.e. the max_id)
                    oldest_tweet = int(tweet["id_str"])

                    # Subtract 1 so the previous oldest isn't included
                    # in the new search
                    oldest_tweet = oldest_tweet - 1

    except RateLimitError:
        print("You have exceeded Twitter's rate limit. Come back in 15 minutes and try again.")
        sys.exit(1)
    except Exception as e:
        print(e)

    # Store average
    tweet_analysis = {"Search": search_term,
                      "Search Date": today,
                      "Compound": np.mean(compound_list).round(3),
                      "Tweet Count": len(compound_list)}

    # Create dataframe
    sentiment_df = pd.DataFrame(sentiment)

    return tweet_text_list, tweet_analysis, sentiment_df


# Function to search a specified date's most recent tweets
def searchDate(until_date):

    # Create variable for holding the oldest tweet
    oldest_tweet = None

    # List to hold average compound values for each movie
    compound_list = []

    # Create list of dictionaries
    sentiment = []

    # List of some tweets
    tweet_text_list = []

    # Instantiate tweet count
    tweet_count = 1

    try:

        # Paginate 10 times (Total of 1000 Tweets)
        for x in range(10):

            # Get all tweets from home feed (for each page specified)
            public_tweets = api.search(search_term,
                                       count=100,
                                       lang='en',
                                       until=until_date,
                                       max_id=oldest_tweet)

            # Loop through all tweets
            for tweet in public_tweets['statuses']:

                # Use filters to check if user meets conditions
                if (tweet["user"]["followers_count"] < max_followers and
                    tweet["user"]["statuses_count"] > min_tweets and
                    tweet["user"]["statuses_count"] < max_tweets and
                    tweet["user"]["friends_count"] < max_following and
                        tweet["user"]["lang"] == lang):

                    # Grab tweet data
                    tweet_text = tweet['text']

                    # Append a few tweets to tweet list
                    tweet_text_list.append(tweet_text)

                    # Run Vader Analysis on each tweet
                    results = analyzer.polarity_scores(tweet_text)
                    compound = results["compound"]

                    # Append compound values to list
                    compound_list.append(compound)

                    # Create dictionary holding tweet data
                    tweet_dict = {'Search_term': search_term, 'Date': user_date,
                                  'Compound': compound, 'Tweets Ago': tweet_count}

                    # Increment tweet_count
                    tweet_count += 1

                    # Append tweet data to sentiment list
                    sentiment.append(tweet_dict)

                    # Reassign the the oldest tweet (i.e. the max_id)
                    oldest_tweet = int(tweet["id_str"])

                    # Subtract 1 so the previous oldest isn't included
                    # in the new search
                    oldest_tweet = oldest_tweet - 1

    except RateLimitError:
        print("You have exceeded Twitter's rate limit. Come back in 15 minutes and try again.")
        sys.exit(1)
    except Exception as e:
        print(e)

    # Store average
    tweet_analysis = {"Search": search_term,
                      "Search Date": user_date,
                      "Compound": np.mean(compound_list).round(3),
                      "Tweet Count": len(compound_list)}

    # Create dataframe
    sentiment_df = pd.DataFrame(sentiment)

    return tweet_text_list, tweet_analysis, sentiment_df


# Function to plot vader sentiment analysis and return image path
def plotSentiment(sentiment_df, search_term):

    # Set axes
    tweets_ago = np.arange(1, len(sentiment_df)+1)
    target = sentiment_df['Compound']

    # Set figure size
    plt.figure(figsize=(10, 7))

    # Plot
    target_plot, = plt.plot(tweets_ago, target, marker='o', ms=7.5, color='steelblue',
                            alpha=0.8, lw=0.5, label=f"{search_term}")

    # Set limits
    plt.xlim(len(sentiment_df)+6, -5)
    plt.ylim(-1.05, 1.05)

    # Set axes background color
    ax = plt.gca()
    ax.set_facecolor('whitesmoke')

    # Insert grid lines and set behind plot elements
    ax.grid(color='white')
    ax.set_axisbelow(True)

    # Specify max number of ticks in x-axis
    plt.locator_params(axis='y', numticks=1)

    # Labels
    plt.title(f"Sentiment Analysis of '{search_term}' Tweets", fontsize=20)
    plt.xlabel('Tweets Ago', fontsize=18)
    plt.ylabel('Tweet Polarity', fontsize=18)

    # Legend
    # plt.legend(handles=[target_plot], title='Tweets', loc=1, bbox_to_anchor=(1.15, 1))

    # Format datetime for saving image
    # today = dt.now().strftime('%Y%m%d')

    # Show graph
    plt.show()


'''
Below implements user input to conduct twitter extraction and analyses.
'''

# Potential response lists
yes_list = ["yes", "y", "yep", "yeah", "yea", "sure",
            "ya", "yah", "ye", "affirmative", "absolutely"]
no_list = ["no", "n", "na", "nah", "nope", "never", "no way", "nein"]

# Instantiate run again while loop
run_again = True

while run_again:

    # Target user
    search_term = input("What do you want to search for on Twitter? ")

    # Search until date
    search_date = input("Do you want to specify a date? Yes or no. ").lower()

    # Conditional to check user input
    if search_date in no_list:

        # Print search text
        print(f"Awesome! One sec. Let's do a search for tweets that contain '{search_term}'.\n")

        # Run analysis and grab tweets and analysis
        tweet_text_list, tweet_analysis, sentiment_df = searchToday()

        # Print some tweets
        print("Here are some tweets:")
        for i, tweet in enumerate(tweet_text_list[:10]):
            print(f"{i+1}) {tweet}")

        # Print analysis
        print(f"\nHere is the analysis for today's tweets:")
        print(f"What you searched for: '{tweet_analysis['Search']}'")
        print(f"Average compound sentiment value: {tweet_analysis['Compound']}")
        print(f"Number of filtered analyzed tweets (out of 1000): "
              f"{tweet_analysis['Tweet Count']}\n")

        # Run plot function
        plotSentiment(sentiment_df, search_term)

        # Instantiate run again while loop
        ask_another = True

        while ask_another:
            # Ask to run again
            run_again_input = input("Do you want to run another analysis? ").lower()

            if run_again_input in no_list:
                print("\nThank you for using twitter sentiment analyzer! Have a good one.")
                ask_another = False
                run_again = False
            elif run_again_input in yes_list:
                ask_another = False
            elif (run_again_input not in no_list) and (run_again_input not in yes_list):
                print("Yes or no question. Try again.\n")

    elif search_date in yes_list:

        while search_date:

            # Specify date
            user_date = input("Try a date. Please use the format, YYYY-MM-DD. ")

            try:
                # Check to see if date format is correct
                object_date = dt.datetime.strptime(user_date, "%Y-%m-%d")

                # Today's date
                today = dt.datetime.now()

                # Days between today's date and entered date
                days_between = (today - object_date).days

                if today < object_date:
                    print("Umm...I can't see into the future!\n")
                elif days_between > 7:
                    print("You can only search up to 7 days in the past.\n")
                else:
                    # Change back to string date
                    user_date = dt.datetime.strftime(object_date, "%Y-%m-%d")

                    # Add one day to specify true date
                    object_date = object_date + dt.timedelta(days=1)

                    # Grab date for twitter search api
                    until_date = dt.datetime.strftime(object_date, "%Y-%m-%d")

                    if user_date:
                        break

            except ValueError:
                print("That's not a valid date. Please check your formatting.\n")
            except Exception as e:
                print(e)

        print(f"Awesome! One sec. Let's do a search for tweets that contain '{search_term}' "
              f"for the date {user_date}.\n")

        # Run search by date function
        tweet_text_list, tweet_analysis, sentiment_df = searchDate(until_date)

        # Print some tweets
        print("Here are some tweets:")
        for i, tweet in enumerate(tweet_text_list[:10]):
            print(f"{i+1}) {tweet}")

        # Print analysis
        print(f"\nHere is the analysis for {user_date}'s tweets:")
        print(f"What you searched for: '{tweet_analysis['Search']}'")
        print(f"Average compound sentiment value: {tweet_analysis['Compound']}")
        print(f"Number of filtered analyzed tweets (out of 1000): "
              f"{tweet_analysis['Tweet Count']}\n")

        # Run plot function
        plotSentiment(sentiment_df, search_term)

        # Instantiate run again while loop
        ask_another = True

        while ask_another:
            # Ask to run again
            run_again_input = input("Do you want to run another analysis? ").lower()

            if run_again_input in no_list:
                print("\nThank you for using twitter sentiment analyzer! Have a good one.")
                ask_another = False
                run_again = False
            elif run_again_input in yes_list:
                ask_another = False
            elif (run_again_input not in no_list) and (run_again_input not in yes_list):
                print("Yes or no question. Try again.\n")

    elif (search_date not in no_list) and (search_date not in yes_list):
        print("It was a yes or no question. Try again.")
    else:
        print("Sorry, too many problems. Imma dip out :)")
        run_again = False
