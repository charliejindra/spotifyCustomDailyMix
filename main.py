import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
import random
import smtplib,ssl
from json.decoder import JSONDecodeError
import time

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# give your playlist name, and it will get its id
# if not found returns none
def getUserPlaylistId(playlistName):
    playlists = spotifyObj.user_playlists(username, limit=50)["items"]
    playlistFound = False
    for playlist in playlists:
        if(playlist["name"] == playlistName):
            playlistFound = True
            playlistid = playlist["id"]
            break
    if playlistFound:
        return playlistid
    else:
        return "DNE"

# get playlist from pool of all playlists
# right now specifically for getting a "this is" playlist
def getFromAllPlaylists(playlistName):
    playlist = spotifyObj.search(q=playlistName, type='playlist', limit=1)
    #print("results for {}".format(playlistName))
    #print(json.dumps(playlist, indent=4))
    playlistFound = False
    
    #change playlist name to look normal
    playlistName = playlistName.replace('+', ' ')
    playlistName = playlistName.replace('"', '')

    if(len(playlist["playlists"]["items"]) > 0):
        if(playlist["playlists"]["items"][0]["name"] == playlistName):
                playlistFound = True
                playlistid = playlist["playlists"]["items"][0]["id"]
        if(playlistFound):
            return playlistid
        else:
            return "DNE"
    else:
        return "DNE"
    
def getArtistFromId():
    return True
#function for sending email
def send_email(subject, msg, rcvemail):
    sender_email = "michelvsace@gmail.com"
    receiver_email = rcvemail

    passW = open("password.txt", 'r')
    password = passW.readline()
    passW.close()

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = """\
    get a better email"""
    html = msg

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def containsThisTrack(trackId, tList):
    for track in tList:
        if track == trackId:
            return True
    return False

while True:
    
    
    playlistName = "Daily Mix Best"
    #get username and scope
    username =  sys.argv[1]
    # sys.argv[1]
    scope = 'user-modify-playback-state user-top-read playlist-modify-public user-read-currently-playing playlist-read-collaborative'

    #erase cache and prompt for user permission
    try:
        token = util.prompt_for_user_token(username, scope)
    except:
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope)

    #print('well we got past the stupid junk')
    #set up spotify object
    spotifyObj = spotipy.Spotify(auth=token)

    #get email to use for email feature
    try:
        emailFile = open("email/{}".format(username), "r")
        email = emailFile.read()
    except:
        emailFile = open("email/{}".format(username), "w+")
        email = input("Please enter an email you would like to be notified on when your daily mix is ready:")
        emailFile.write(email)

    # remove old songs from daily mix better
    oldPlaylist = getUserPlaylistId(playlistName)
    #print(oldPlaylist)

    if oldPlaylist == "DNE":
        spotifyObj.user_playlist_create(username, playlistName, public=True)
        
    else:
        oldTracks = spotifyObj.user_playlist_tracks(username, playlist_id=oldPlaylist)["items"]
        #print(json.dumps(oldTracks, indent=4))
        oldTrackIds = []

        for track in oldTracks:
            #print(json.dumps(track, indent=4))
            oldTrackIds.append(track["track"]["id"])

        spotifyObj.user_playlist_remove_all_occurrences_of_tracks(username, oldPlaylist, oldTrackIds) 


    playlistid = getUserPlaylistId(playlistName)


    # #rint(playlistid)


    ## GET SONGS FROM TOP SONGS OF USER
    songsLeftToAdd = 5
    trackList = []
    familiarSongs = []
    songsJson = spotifyObj.current_user_top_tracks(time_range='medium_term', limit=40)["items"]
    i = 0

    print(len(songsJson))

    for song in songsJson:
        familiarSongs.append(song["id"])

    while songsLeftToAdd != 0:
        potentialSong = familiarSongs[random.randint(0,len(familiarSongs)-1)]
        if not containsThisTrack(potentialSong, trackList):
            trackList.append(familiarSongs[random.randint(0,len(familiarSongs)-1)])
            songsLeftToAdd -= 1

    ## GET SONGS FROM TOP ARTISTS OF USER (top 10 tracks in each artists catalog)
    songsLeftToAdd = 30

    results = spotifyObj.current_user_top_artists(time_range="short_term", limit=50)

    # get artist ids
    artistids = []
    for item in results["items"]:
        artistids.append(item["id"])

    while songsLeftToAdd != 0:
        artist = artistids[random.randint(0,45)]
        songsToChooseFrom = spotifyObj.artist_top_tracks(artist)
        track = songsToChooseFrom["tracks"][random.randint(0,9)]["id"]
        while containsThisTrack(track, trackList):
            track = songsToChooseFrom["tracks"][random.randint(0,9)]["id"]
        trackList.append(track)
        #print(json.dumps(songsToChooseFrom["tracks"][0], indent=4))
        songsLeftToAdd -= 1

        relatedArtists = spotifyObj.artist_related_artists(artist)["artists"]
        #print(json.dumps(relatedArtists, indent=4))
        relatedArtistIds = []
        for artist in relatedArtists:
            relatedArtistIds.append(artist["id"])
        counter = 2

        while counter != 0:
            #print(len(relatedArtistIds))
            artistIdUsing = relatedArtistIds[random.randint(0, len(relatedArtistIds)-1)]

            # Try to get the This Is playlist from the artist.

            artistUsingDict = spotifyObj.artist(artistIdUsing)
            
            artistUsing = artistUsingDict["name"]
            artistUsing = json.dumps(artistUsing).replace(' ', '+')

            thisIsPlaylist = getFromAllPlaylists("This+Is+" + artistUsing)

            #print(json.dumps(thisIsPlaylist, indent=4))
            getFromThisIs = True if (thisIsPlaylist == "This is " + artistUsing) else False
            #print(getFromThisIs)

            if(getFromThisIs):
                # this is playlist path
                songsToChooseFrom = spotifyObj.playlist(thisIsPlaylist, fields="tracks")["tracks"]
                #print(json.dumps(songsToChooseFrom, indent=4))
                #print("there they are")

                
                #print(json.dumps(songsToChooseFrom, indent=4))
                
                #print("length of songs to choose from: " + str(len(songsToChooseFrom)))
                track = songsToChooseFrom["items"][random.randint(0,len(songsToChooseFrom)-1)]["track"]["id"]
                #print(json.dumps(track, indent=4))
                
                while containsThisTrack(track, trackList):
                    track = songsToChooseFrom["items"][random.randint(0,len(songsToChooseFrom)-1)]["track"]["id"]
                trackList.append(track)
                songsLeftToAdd -= 1
                counter -= 1
            else:
                # top tracks path
                songsToChooseFrom = spotifyObj.artist_top_tracks(artistIdUsing)
                track = songsToChooseFrom["tracks"][random.randint(0,len(songsToChooseFrom["tracks"])-1)]["id"]
                while containsThisTrack(track, trackList):
                    track = songsToChooseFrom["tracks"][random.randint(0,len(songsToChooseFrom["tracks"])-1)]["id"]
                trackList.append(track)
                songsLeftToAdd -= 1
                counter -= 1

    spotifyObj.user_playlist_add_tracks(username, playlistid, trackList)

    print("now we wait")

    playlistSongs = spotifyObj.user_playlist_tracks(username, playlistid, limit=100)

    songListBuilder = playlistSongs["items"][0:5]
    songsPrettified = []
    #print(json.dumps(songListBuilder, indent=4))
    for song in songListBuilder:
        songsPrettified.append(song["track"]["name"] + " - " + song["track"]["artists"][0]["name"])

    songsYouLike = "<ul>"
    for song in songsPrettified:
        songsYouLike += "<li>" + song + "</li>"
    songsYouLike += "</ul>"

    songListBuilder = playlistSongs["items"][5:len(playlistSongs["items"])]
    songsPrettified = []
    print (len(songListBuilder))
    for song in songListBuilder:
        #if the song number is divisible by three (an artist you know)
        if songListBuilder.index(song) % 3 == 0:
            songsPrettified.append(song["track"]["artists"][0]["name"])

    songsWithInfluences = "<ul>"
    for art in songsPrettified:
        songsWithInfluences += "<li>" + art + "</li>"
    songsWithInfluences += "</ul>"
    
    playlistUrl = "https://open.spotify.com/playlist/{}".format(playlistid)

    msgBuilder = """\
    <html>
    <body>
        <h2>Today's Daily Mix</h2>
        <b>Here's some songs you already love:</b>
        {}
        <b>Here's some artists you listen to, followed up with songs fellow listeners liked:</b>
        {}
        <i>Here's a link to your playlist - </i>{}
    </body>
    </html>
    """.format(songsYouLike, songsWithInfluences, playlistUrl)

    send_email("Your Custom Daily Mix is Here", msgBuilder, email)

    # 24 hours boyo
    time.sleep(86400)