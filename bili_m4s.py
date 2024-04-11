import time
import requests
from lxml import etree
import json
from moviepy.editor import *
import os
from concurrent.futures import ThreadPoolExecutor
def getLength(address):
    if "av" in address:
        parts = "?aid=" + address.split("av")[1]
    elif "BV" in address:
        parts = "?bvid=BV" + address.split("BV")[1]
    else:
        print("Invalid address")
        return -1
    request = requests.get("https://api.bilibili.com/x/web-interface/view" + parts, headers=head)
    pages = json.loads(request.text)["data"]["pages"]
    print(f"{len(pages)} videos in total")
    #print(len(pages),[x["cid"] for x in pages])
    if "av" in address:
        parts = "?avid=" + address.split("av")[1]
    return [len(pages),[x["cid"] for x in pages],parts,[x["part"] for x in pages]]
head = {
    'Referer': 'https://www.bilibili.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44'
}
def getFileM4s(url, type, path=r"D:/", title=""):
    opener= {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept':'*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Range': 'bytes=0-',
        'Referer': "https://search.bilibili.com/all",#!!!!
        'Origin': 'https://www.bilibili.com',
        'Connection': 'keep-alive'
        }

    response = requests.get(url, stream=True,headers=opener)
    print(f"{path}{title}.{type}")
    with open(f"{path}{title}.{type}", "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
def videoEdit(address, path=r"D:/",title=""):
    response = requests.get(f"https://www.bilibili.com/video/{address}", headers=head)
    tree = etree.HTML(response.content.decode())
    script_text = tree.xpath('/html/head/script[4]/text()')[0][20:]
    if "/" in title:
        title = title.replace("/", " ")
    resultVideo = json.loads(script_text)["data"]["dash"]["video"]
    resultAudio = json.loads(script_text)["data"]["dash"]["audio"]
    print(resultAudio[-1]["baseUrl"])
    getFileM4s(resultAudio[-1]["baseUrl"], "mp3", title=title, path=path)
    getFileM4s(resultVideo[-1]["baseUrl"], "mp4", title=title, path=path)
    print(114)

    video = VideoFileClip(f"{path}{title}.mp4")
    audio = AudioFileClip(f"{path}{title}.mp3")

    video = video.set_audio(audio)
    video.write_videofile(f"{path}{title}(含音频).mp4",logger=None)
    os.remove(f"{path}{title}.mp4")
    os.remove(f"{path}{title}.mp3")
    print(f"{title} finish")
def Start_process(address, length, path=r"D:/", title=None):
    with ThreadPoolExecutor() as t:
        t.submit(videoEdit, address + f"/", path, title[0])
        for i in range(2, length + 1):
            t.submit(videoEdit, address + f"/?p={i}", path, title[i - 1])
address = input("address")
address = address.split('/')[4]
Store_address = input("\n" + "Store at")
attributes = getLength(address)
print(attributes)
if not os.path.exists(Store_address):
    print("Directory does not exist, using default address")
    print(attributes[-1])
    Start_process(address, attributes[0],title=attributes[-1])
else:
    Start_process(address, attributes[0], title=attributes[-1],path=Store_address)

