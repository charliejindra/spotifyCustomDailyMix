import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
import random
from json.decoder import JSONDecodeError
# give your playlist name, and it will get its id
# if not found returns none

def getPlaylistId(playlistName):
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
    

playlistName = "Daily Mix Best"
#get username and scope
username =  "charlessjindra"
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



# remove old songs from daily mix better
oldPlaylist = getPlaylistId(playlistName)
print(oldPlaylist)

if oldPlaylist == "DNE":
    spotifyObj.user_playlist_create("charlessjindra", playlistName, public=True)
    
else:
    oldTracks = spotifyObj.user_playlist_tracks(username, playlist_id=oldPlaylist)["items"]
    #print(json.dumps(oldTracks, indent=4))
    oldTrackIds = []

    for track in oldTracks:
        
        #print(json.dumps(track, indent=4))
        oldTrackIds.append(track["track"]["id"])

    spotifyObj.user_playlist_remove_all_occurrences_of_tracks(username, oldPlaylist, oldTrackIds) 


playlistid = getPlaylistId(playlistName)


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
    trackList.append(familiarSongs[random.randint(0,40)])
    songsLeftToAdd -= 1

## GET SONGS FROM TOP ARTISTS OF USER (top 10 tracks in each artists catalog)
songsLeftToAdd = 30

results = spotifyObj.current_user_top_artists(time_range="short_term", limit=50)

# get artist ids
artistids = []
for item in results["items"]:
    artistids.append(item["id"])

while (songsLeftToAdd != 0):
    
    artist = artistids[random.randint(0,45)]
    songsToChooseFrom = spotifyObj.artist_top_tracks(artist)
    track = songsToChooseFrom["tracks"][random.randint(0,9)]["id"]
    trackList.append(track)
    #print(json.dumps(songsToChooseFrom["tracks"][0], indent=4))
    songsLeftToAdd -= 1

spotifyObj.user_playlist_add_tracks("charlessjindra", playlistid, trackList)