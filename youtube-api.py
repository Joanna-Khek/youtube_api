import os
from dotenv import load_dotenv
import pandas as pd

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


def get_channel_stats(youtube, channel_ids):
    
    all_data = []
    
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_ids
    )
    
    response = request.execute()
    
    for item in response["items"]:
        data = {'channelName': item["snippet"]["title"],
                'publishedDate': item["snippet"]["publishedAt"],
                'subscribers': item["statistics"]["subscriberCount"],
                'views': item["statistics"]["viewCount"],
                'totalVideos': item["statistics"]["videoCount"],
                'playlistId': item["contentDetails"]['relatedPlaylists']['uploads']
        }
        
        all_data.append(data)
        
    return(pd.DataFrame(all_data))

def get_video_ids(youtube, playlist_id):
    
    video_ids = []
    
    request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults = 50
            )
    
    response = request.execute()
    
    for item in response['items']:
        video_ids.append(item["contentDetails"]['videoId'])
            
    next_page_token = response.get('nextPageToken')
    while next_page_token is not None:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults = 50,
            pageToken = next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_ids.append(item["contentDetails"]['videoId'])
            
        next_page_token = response.get('nextPageToken')
        
    return video_ids
    
def get_video_details(youtube, video_ids):
    
    all_video_info = []
    
    for ids in video_ids:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=ids
        )
        response = request.execute()
        
        for video in response["items"]:
            stats_to_keep = {'snippet':  ['title', 'description', 'publishedAt', 'tags'],
                             'statistics': ['viewCount', 'likeCount', 'favoriteCount', 'commentCount'],
                             'contentDetails': ['duration', 'definition', 'caption']}
            
            video_info = {}
            video_info["video_id"] = video["id"]
            
            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        video_info[v] = video[k][v]
                    except:
                        video_info[v] = None
                    
            all_video_info.append(video_info)
            
    return pd.DataFrame(all_video_info)

def main():
    # Load Environments
    api_service_name = "youtube"
    api_version = "v3"
    load_dotenv()
    
    # Set Configurations
    API_KEY = os.getenv("API_KEY")
    channel_ids = 'UCuJyaxv7V-HK4_qQzNK_BXQ'
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=API_KEY)

    # Get Channel Statistics
    channel_stats = get_channel_stats(youtube, channel_ids)
    playlist_id = channel_stats.playlistId.values[0]
    
    # Get Video Information
    video_ids = get_video_ids(youtube, playlist_id)
    all_video_info = get_video_details(youtube, video_ids)
    
    all_video_info.to_csv("data.csv")

if __name__ == "__main__":
    main()