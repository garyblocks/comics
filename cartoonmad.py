#coding:utf-8

import urllib2
import re
import os
import zlib

class cartoonmad:
    def __init__(self, path):
        exists = os.path.exists(path)
        if not exists:
            print("path not valid")
            exit(0)
        # page of comic lists
        self.base_url = 'http://www.cartoonmad.com'
        # local path to store the images
        self.path = path
    
    # get raw content of the cover page of html
    def get_content(self, url):
        # open the page
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request, timeout=20)

            # decompress if compressed
            # check if compressed: print response.info().get('Content-Encoding') 
            #decompressed_data = zlib.decompress(response.read(), 16 + zlib.MAX_WBITS)
            # if decode format is gb2312
            #content = decompressed_data.decode('gb2312','ignore')
            
            content = response.read()
            return content
        except Exception, e:
            print e
            print ("failed to open "+url)
            return None

    # get the list of urls
    def get_episode_url_arr(self,content):
        result = re.findall('<a href=(/comic/[0-9]*?\.html) target=_blank>\xb2\xc4 ',content,re.S)
        # combine the page result with base url
        arr = []
        for item in result:
            page_url = self.base_url + item
            arr.append(page_url)
        return arr

    # get the list of each page
    def get_page_url_arr(self,url):
        num_of_pages = int(url[-11:-8])
        arr = []
        for i in range(num_of_pages):
            page_url = url[:-8]+str(i+1).zfill(3)+".html"
            arr.append(page_url)
        return arr

    def get_image(self,content,p):
        # get url 
        pic_url = re.findall('<img src="(http.*?\.jpg)" border="0"',content,re.S)[0]
        # save the img
        req = urllib2.Request(pic_url)
        req.add_header('User-Agent', 
                'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
        req.add_header('GET', pic_url)
        try:
            print("save pic url:" + pic_url)
            resp = urllib2.urlopen(req, timeout=20)
            data = resp.read()
            file_name = re.findall("[0-9]+", p)[0]+'.jpg'
            fp = open(self.path+'/'+file_name, "wb")
            fp.write(data)
            fp.close
            print("save pic finished.")
        except Exception, e:
            print(e)
            print("save pic: " + pic_url + " failed.")


comic = raw_input('Please copy the category page url here: ').strip()
path = raw_input('Please input where you want to save the comics: ').strip()
# create object
obj = cartoonmad(path)
# get content
content = obj.get_content(comic)
# get episodes
episodes = obj.get_episode_url_arr(content)
for url in episodes:
    # get pages
    pages = obj.get_page_url_arr(url)
    for p in pages:
        page_content = obj.get_content(p)
        obj.get_image(page_content,p)

