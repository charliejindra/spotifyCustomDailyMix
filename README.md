# spotifyCustomDailyMix

this program creates a custom daily mix for you which contains:

- 5 songs you've been listening to recently
- some clusters of:
    - 1 song from an artist you've listened to recently
    - 2 songs from related artists

the program is designed to be run on a machine consistently ( i use a raspberry pi ),
so it will refresh this daily mix for you every 24 hours. this isn't absolutely necessary,
although it is very cool.

it also will eventually email an email of your choice the daily mix logic so you know when
your daily mix is hot n ready. this is another optional feature that has to be configured
with a password.txt file of your own to login to your own email ( you know what if you want
to use this feature then contact me at charlessjindra@gmail.com and i'll help you )

hope you enjoy! in the future i will hopefully make this more featured and dev friendly.

# - backlog -

- flask app
- improved song selection
    - record songs and how many times theyve been selected in the past
    - select songs that have been selected in the past less
    - pick songs from three lists potentially: "this is" playlist, then top songs, then all artist's songs
- improved artist curation
    - track related artist selection history
    - recognize when related artist enters top artist list and do ?? with it
    
