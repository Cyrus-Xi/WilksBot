#WilksBot

A simple Reddit bot that uses PRAW, a popular wrapper for Reddit's API, and regular expressions to appropriately and flexibly parse relevant post- and comment-embedded weightlifting statistics to reply with the Wilks coefficient adjusted statistic. 

For example, if I post a comment saying 

> I totaled 1045 @ a BW of 140 lbs 

WilksBot would reply with this:

> Your total of 1045 at a BW of 140 gives you a Wilks score of 384.45. Congrats!
[Questions/Comments/Suggestions/Likes/Dislikes?](http://www.reddit.com/message/compose/?to=Wilks_bot) Version 1.0 [(Source)](https://github.com/Suryc11/WilksBot)

> Formats: 'total 1200 @ 160', '400/300/500 at 200', 'total[ed] 1500 @ [a] BW [of] 200', '300/200/400 bw[:] 140'.

A number of different input formats are accepted.

The bot is deployed using Heroku.

Sources I used during the course of this include but are not limited to the following:
* https://praw.readthedocs.org/en/v2.1.16/pages/writing_a_bot.html
* http://www.nonbird.com/rbb_article/redditbottutorial.html
* http://amertune.blogspot.com/2014/04/tutorial-create-reddit-bot-with-python.html
* https://github.com/zd9/IMDb-Reddit-Bot/blob/master/bot.py


###TODO

* [ ] Have bot delete its comments when they go below a certain karma score
* [ ] Calculate Wilks not just for a total but for a single lift, too
* [ ] And refactor code for less redundancy.
* [ ] Parse lift numbers given in kilograms too
