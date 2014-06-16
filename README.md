WilksBot
========

A simple Reddit bot that uses regular expressions to appropriately and flexibly parse Reddit post- and comment-embedded weightlifting statistics to reply with the Wilks coefficient adjusted statistic. 

For example, if I post a comment saying "I totaled 1045 @ a BW of 140 lbs," Wilks_bot would reply with this:

"""
Your total of 1045 at a BW of 140 gives you a Wilks score of 384.45. Congrats!
Questions/Comments/Suggestions? Message me! Version 1.0 (Source)

Formats: 'total 1200 @ 160', '400/300/500 at 200', 'total[ed] 1500 @ [a] BW [of] 200', '300/200/400 bw[:] 140'.
"""

A number of different formats are accepted.


TODO: Have bot delete its comments when they go below a certain karma score. Calculate Wilks not just for a total but for
a single lift, too.
