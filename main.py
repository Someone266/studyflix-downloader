import requests
from bs4 import BeautifulSoup
import json
import os
import subprocess
import sys
import os.path

def get_video_src(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Save the HTML content to a file for debugging
        #with open('page.html', 'w', encoding='utf-8') as file:
            #file.write(response.text)
        
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the video element with the attribute 'data-player-container'
        video_tag = soup.find('div', attrs={'data-player': True})
        # video_tag = soup.find('div', class_=""
        
        
        if video_tag:
            # Get the source URL inside the video element
            src_url = video_tag.get('up-data')
            # print(src_url)
            src = json.loads(src_url)
            src = src.get('video', {}).get('stream_urls', [])
            if src:
                return src[0]  # Assuming there's only one stream URL
            else:
                return "Stream URL not found in the JSON data."
        else:
            return "Video element with attribute 'data-player-container' not found."
    else:
        return "Failed to retrieve the HTML content."

def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

def getTitle(url):
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Save the HTML content to a file for debugging
        #with open('page.html', 'w', encoding='utf-8') as file:
            #file.write(response.text)
        
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', class_="h2")
        title = title.text
        return title
        
# Example usage:

if not sys.argv[1]:
    print("No URL provided")
    exit()
    
url = sys.argv[1]
if not url.startswith("https://studyflix.de"):
    print("Invalid URL")
    exit()
# url = "https://studyflix.de/lernplan/KpD7o8a0/atombindungen-5691"
video_src = get_video_src(url)
video_src = video_src.replace(".m3u8", "_hls.m3u8")
print("Video source URL:", video_src)

title = getTitle(url)
print("Downloading: " + title + "")
if os.path.isfile(title + ".mp4"):
    print("Video already downloaded!")
    exit()


#ydl_opts = {'outtmpl' : 'video.mp4',}
#with YoutubeDL(ydl_opts) as ydl:    
#    ydl.download(video_src)
#wget.download(video_src)
#m3u8_To_MP4.multithread_download(video_src)
print("Downloading video...")
subprocess.run(['ffmpeg -hide_banner -v error -i "' + video_src + '" -c copy tmpvideo.mp4'])

print("Downloading audio...")
subprocess.run(['ffmpeg -hide_banner -v error -i "' + video_src + '" -map 0:1 -codec:a libmp3lame -b:a 96k audio.mp3'])
# ffmpeg -i "https://ducsmxsiuk0zw.cloudfront.net/video_2276/7561/7561_hls.m3u8" -map 0:1 -codec:a libmp3lame -b:a 96k test.mp3
print("Converting video...")
subprocess.run(['ffmpeg -hide_banner -v error -i tmpvideo.mp4 -i audio.mp3 -c:v copy -c:a aac "' + title + '.mp4"'])
# ffmpeg -i "https://ducsmxsiuk0zw.cloudfront.net/video_2276/7561/7561_hls.m3u8" -c copy file.mp4
os.remove("audio.mp3")
os.remove("tmpvideo.mp4")


print("Finished! Saved video as " + title + ".mp4")