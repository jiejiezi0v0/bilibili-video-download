import time
import requests
from lxml import etree
import json
from moviepy.editor import *
import os
from concurrent.futures import ThreadPoolExecutor

head = {
    'Referer': 'https://www.bilibili.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44'
}


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



def getFileFlv(Cid,Parts,title,path=r"D:/"):
    flv=[]
    header={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Referer': "https://search.bilibili.com/all"}
    def getFlvAddress():
        for cid in Cid:
            request=requests.get(f"https://api.bilibili.com/x/player/playurl{Parts}&cid={cid}&qn=120&fourk=1",headers=header)
            #print(request.content.decode())
            #print(f"https://api.bilibili.com/x/player/playurl{Parts}&cid={cid}&qn=120&fourk=1")
            flv.append(json.loads(request.text)["data"]["durl"][0]["url"])
    getFlvAddress()
    with ThreadPoolExecutor() as t:
        for i in range(0,len(flv)):
            if "/" in title:
                t.submit(Download, flv[i], "mp4", path, title.replace("/"," "), {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Referer': "https://search.bilibili.com/all"})
            else:
                t.submit(Download, flv[i], "mp4", path, title, {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0',
                    'Referer': "https://search.bilibili.com/all"})


def Download(Address,type,path,title,header):
    response = requests.get(Address, headers=header,stream=True)
    with open(f"{path}{title}.{type}", "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    print(f"{title}.{type} download complete")
    time.sleep(0.5)



def Start_process(path=r"D:/", title=[],Cid=None, Parts=None):
    for t in title:
        getFileFlv(Cid,Parts,t,path)

def main():
    address = input("address")
    address = address.split('/')[4]
    attributes = getLength(address)
    print(attributes)
    Start_process(title=attributes[-1], Cid=attributes[1], Parts=attributes[-2])



if __name__ == '__main__':
    main()
