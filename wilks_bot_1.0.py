#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import praw  # Reddit API wrapper
import re
import time
import os  # For environment variables



# Most recent.
# Split main up into 2 functions (from version3). May make
# even more modular. Now have to flesh out the documentation,
# reply text (give more information about the bot, etc.),
# and make sure lines aren't too long. Make prettier basically.
# Also, do a little more testing.
#
# Fixing regex to handle more cases, e.g., bw of 140 and just
# a total, no individual lifts.
#
# Sources:
# https://praw.readthedocs.org/en/v2.1.16/pages/writing_a_bot.html
# http://www.nonbird.com/rbb_article/redditbottutorial.html
# http://amertune.blogspot.com/2014/04/tutorial-create-reddit-bot-with-python.html

submission_already_done = []  # List of submission IDs already checked
comment_already_done = []  # Comment IDs already checked

# If wilk/wilks is already in post/comment, then don't need Wilks calculated.
wilk_words = ['wilk', 'wilks']

### Regular expressions.
# With colon and without colon cases are separate, because while
# can handle together, can't do so without capturing the colon
# since no repeating modifiers inside a lookbehind/lookahead.
# Same issue with the "of" bit. And \s is whitespace.
wilks_pattern = re.compile(r"""     # Either explicit lifts or total
     \d{2,3}/\d{2,3}/\d{2,3}        # E.g.: 350/250/450
    |(?<=totaled\s)\d{3,4}          # E.g.: totaled 1000
    |(?<=total:)\s?\d{3,4}          # E.g.: total:1000
    |(?<=total\s)\d{3,4}            # E.g.: total 1000
    |(?<=total\sis\s)\d{3,4}        # E.g.: total is 1000
    |(?<=total\sof\s)\d{3,4}        # E.g.: total of 1000
                           """, re.X | re.I)  # Verbose and case-insensitive

BW_pattern = re.compile(r"""
     (?<=at\s)\d{2,3}                  # E.g.: at 140
    |(?<=@)\s?\d{2,3}                  # E.g.: ... @ 140
    |(?<=bw\s)\d{2,3}                  # E.g.: BW 140
    |(?<=bw:)\s?\d{2,3}                # E.g.: BW:140
    |(?<=bw\sof\s)\d{2,3}              # E.g.: at a bw of 140
    |(?<=bodyweight:)\s?\d{2,3}        # E.g.: bodyweight: 140
    |(?<=bodyweight\s)\d{2,3}          # E.g.: Bodyweight 140
    |(?<=bodyweight\sof\s)\d{2,3}      # E.g.: ... bodyweight of 140
                        """, re.X | re.I)  # Verbose and case-insensitive

comment_string = """
\n\n\n------------------------\n\n
^^[Questions/Comments/Suggestions? Message me!](http://www.reddit.com/message/compose/?to=Wilks_bot)
^^Version^^1.0^^[(Source)](https://github.com/Suryc11/WilksBot)\n
 """

extra_string = """
Formats: 'total 1200 @ 160', '400/300/500 at 200', 'total[ed] 1500 @ [a] BW [of] 200', '300/200/400 bw[:] 140'.
"""

# Make text "subscripted" using Reddit's formatting.
comment_end_string = comment_string + extra_string.replace(' ', ' ^^')

### Login
#with open('wilks_login.txt', 'r') as infile:
    #login_lines = infile.readlines()

# Add github link to user_agent description later.
user_agent = ("Wilks_bot, a Wilks score calculator, 1.6 by /u/Tyrion314")
r = praw.Reddit(user_agent=user_agent)  # Represents session with reddit
USERNAME = os.environ['REDDIT_USER']
PASSWORD = os.environ['REDDIT_PASS']

trying = True
while trying:
    try:
        r.login(USERNAME, PASSWORD)
        print "Success! Logged in"
        trying = False
    except praw.errors.InvalidUserPass:
        print "ERROR: Wrong username or password"
        #print USERNAME, PASSWORD
        exit()
    except Exception as e:
        print "ERROR: {}".format(e)
        time.sleep(10)


# Handles either an explicit total or individual lifts.
def calculate_wilks(data):
    lifts_string = data.split()[0]
    BW_string = data.split()[1]
    if len(lifts_string) == 3 or len(lifts_string) == 4:  # Just the total
        total = float(lifts_string)
    else:
        lifts = lifts_string.split('/')  # Get individual lifts
        clean_lifts = [float(lift) for lift in lifts]
        total = sum(clean_lifts)  # Yay Python
    BW = float(BW_string)
    total_kg = total / 2.20462262185
    x = BW / 2.20462262185
    # Now time for the nitty-gritty calculation.
    # Formula from Wikipedia page: http://en.wikipedia.org/wiki/Wilks_score
    a = -216.0475144
    b = 16.2606339
    c = -0.002388645
    d = -0.00113732
    e = 7.01863E-06
    f = -1.291E-08
    coefficient = 500.0 / (a + b * x + c * pow(x, 2) + d * pow(x, 3)
                         + e * pow(x, 4) + f * pow(x, 5))
    wilks = coefficient * total_kg
    return round(wilks, 2)


def reply_to_submission(submission):
    if submission.id not in submission_already_done and submission:
        #print submission.id, submission.title
        # Get list of all authors of top-level/root comments.
        #real_comments = [comment for comment in submission.comments if comment.author is not None]
        #print real_comments
        root_comment_authors = [(comment.author.name).encode('utf-8') for comment in submission.comments if
                                comment.author is not None and comment.is_root]
        print root_comment_authors
        #for author in root_comment_authors:
            #print author
        # True if this bot has made a top-level comment.
        already_replied_submission = any(USERNAME == author for author in root_comment_authors)
        #print already_replied_submission
        if not already_replied_submission:
            # Include title, because may need to calculate Wilks there.
            print "At this submission: {}".format(submission.title)
            op_text = submission.title.lower() + ' ' + submission.selftext.lower()
            print op_text
            # has_wilks is True if 'wilk' or 'wilks' shows up anywhere.
            # Case-insensitive. If True, then don't need to calculate.
            has_wilks = any(word in op_text for word in wilk_words)
            if submission.id not in submission_already_done and not has_wilks:
                wilks_match = wilks_pattern.search(op_text)
                if wilks_match:  # Will be true if found pattern
                    BW_match = BW_pattern.search(op_text)
                    if BW_match:
                        # Take out whitespace and concatenate data.
                        raw_data = (wilks_match.group().strip()
                                    + ' ' + BW_match.group().strip())
                        wilks = calculate_wilks(raw_data)
                        if len(wilks_match.group().strip()) < 5:  # Just total given
                            submission.add_comment("""Your total of {} at a BW of {}
                                gives you a Wilks score of {}. Congrats!
                                {}""".format(
                                wilks_match.group(), BW_match.group(), wilks, comment_end_string))
                        else:
                            submission.add_comment("""Your lifts of {} at a BW of {}
                                give you a Wilks score of {}. Congrats!
                                {}""".format(
                                wilks_match.group(), BW_match.group(), wilks, comment_end_string))
                        print "Replied to {}".format(submission.title)
        submission_already_done.append(submission.id)


def reply_to_comments(submission):
    # Now look at submission's comments.
    # Flatten comment forest because don't care about comment's place.

    flat_comments = praw.helpers.flatten_tree(submission.comments)
    # Use Pythonic filtering list comprehension to get only existent and
    # non-bot-authored comments.
    valid_comments = [comment for comment in flat_comments if comment.author is not None]
    valid_comments = [comment for comment in valid_comments if str(comment.author).encode('utf-8') != USERNAME]
    valid_comments = [comment for comment in valid_comments if comment.id not in comment_already_done]

    #for valid_comment in valid_comments:
        #print "Valid comment: {} by {}".format(valid_comment.body, valid_comment.author)
    # For each comment, see if matches.
    for comment in valid_comments:
        # Must check that the bot hasn't already replied.
        replies_authors = [str(comment.author.name).encode('utf-8') for comment in comment.replies]
        #print replies_authors

        already_replied_comment = any(USERNAME == author for author in replies_authors)
        #print already_replied_comment
        if not already_replied_comment:
            comment_text = comment.body.lower()
            #print comment_text
            has_wilks = any(word in comment_text for word in wilk_words)
            #print has_wilks
            #print comment.score
            # Make sure comment is not a troll and worth replying to.
            if comment.score > 0 and not has_wilks:
                wilks_match = wilks_pattern.search(comment_text)
                #print wilks_match
                if wilks_match:  # Will be true if found pattern
                    BW_match = BW_pattern.search(comment_text)
                    #print BW_match
                    if BW_match:
                        raw_data = (wilks_match.group().strip()
                                    + ' ' + BW_match.group().strip())
                        wilks = calculate_wilks(raw_data)
                        if len(wilks_match.group().strip()) < 5:  # Just total given
                            comment.reply("""Your total of {} at a BW of {}
                                gives you a Wilks score of {}. Congrats! {}""".format(
                                wilks_match.group(), BW_match.group(), wilks, comment_end_string))
                        else:
                            comment.reply("""Your lifts of {} at a BW of {}
                                give you a Wilks score of {}. Congrats! {}""".format(
                                wilks_match.group(), BW_match.group(), wilks, comment_end_string))
                        print "Replied to a comment in {}".format(submission.title)
        comment_already_done.append(comment.id)
        print "yay done with comment"


def main():
    while True:
        multi_reddits = r.get_subreddit('bottest+powerlifting+weightroom')
        try:
            for submission in multi_reddits.get_hot(limit=10):
                print "Doing submission stuff."
                reply_to_submission(submission)
                print "Doing comment stuff."
                reply_to_comments(submission)
            time.sleep(7200)
        except KeyboardInterrupt:
            break
        except praw.errors.APIException as e:
            print "ERROR: ", e
            print "Sleeping 1 minute"
            time.sleep(60)
        # Shouldn't happen since PRAW controls the rate automatically, but just in case
        except praw.errors.RateLimitExceeded as e:
            print "ERROR: Rate Limit Exceeded: {}".format(e)
            time.sleep(60)
        except Exception as e: # In reality you don't want to just catch everything like this, but this is toy code.
            print "ERROR: ", e
            print "Lazily handling error, exiting"
            break

if __name__ == "__main__":
    main()
