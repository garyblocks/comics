#coding:utf-8

import urllib2
import re
import os
import zlib
import json
import sys

class cartoonmad:
    def __init__(self, path):
        exists = os.path.exists(path)
        if not exists:
            try:
                os.makedirs(path)
                print("folder " + path + " created.\n")
            except Exception, e:
                print e
                print ("failed to create path: " + path +"\n")
                exit(0)
        # page of comic lists
        self.base_url = 'http://www.cartoonmad.com'
        # local path to store the images
        self.path = path
    
    # get raw html content of a url
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

    # get the list of episode urls
    def get_episode_url_arr(self,content):
        result = re.findall('<a href=(/comic/[0-9]*?\.html) target=_blank>\xb2\xc4 ',content,re.S)
        # combine the page result with base url
        arr = []
        for item in result:
            page_url = self.base_url + item
            arr.append(page_url)
        return arr

    # get the list of page urls
    def get_page_url_arr(self,url):
        num_of_pages = int(url[-11:-8])
        arr = []
        for i in range(num_of_pages):
            page_url = url[:-8]+str(i+1).zfill(3)+".html"
            arr.append(page_url)
        return arr
    
    # get the image url
    def get_image_url(self,content,url):
        # get url 
        pic_url = re.findall('<img src="(http.*?\.jpg)" border="0"',content,re.S)[0]
        return pic_url
    
    # get the image
    def get_image(self,pic_url):
        # save the img
        req = urllib2.Request(pic_url)
        req.add_header('User-Agent', 
                'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
        req.add_header('GET', pic_url)
        try:
            #print("save pic url:" + pic_url)
            resp = urllib2.urlopen(req, timeout=20)
            data = resp.read()
            file_name = '-'.join(re.findall("[a-z|0-9]+", pic_url)[:-1])+'.jpg'
            fp = open(self.path+'/'+file_name, "wb")
            fp.write(data)
            fp.close
            return True
        except Exception, e:
            print(e)
            print("save pic: " + pic_url + " failed.")
            return False
    
    # get all urls
    def get_urls(self,comic):
        # get main page content
        content = self.get_content(comic)
        # get episodes
        episodes = self.get_episode_url_arr(content)
        urls = []
        i = 0
        for url in episodes:
            # print a episode marker 
            print '<'+str(i+1).zfill(3)+'> [ ',
            i += 1
            # get pages
            pages = self.get_page_url_arr(url)
            for p in pages:
                sys.stdout.write('* ')
                sys.stdout.flush()
                page_content = self.get_content(p)
                urls.append(self.get_image_url(page_content,p))
            print ']'
        # store data in json file
        data = json.dumps([urls])
        with open(self.path+'/urls.json','w') as fj:
            fj.write(data)
        return urls
        
if __name__ == '__main__':
    comic = raw_input('Please copy the category page url here: ').strip()
    path = raw_input('Please input where you want to save the comics: ').strip()
    # create object
    obj = cartoonmad(path)
    # check if the urls are already downloaded
    if not os.path.exists(obj.path+'/urls.json'):
        # get all urls
        print "collecting urls..."
        urls = obj.get_urls(comic)
        print "All image urls are ready"
        start = 0
    # read json data
    else:
        start = int(raw_input('Start from URLID: ').strip())
        with open(obj.path+'/urls.json') as fj:
            data = fj.readline().strip()
            urls = json.loads(data)
    # save all pictures
    print "start downloading..."
    n = len(urls)
    for i in range(start,n):
        progress = (i+1)/float(n)*100
        sys.stdout.write("Download progress: %d%%   \r" % (progress))
        sys.stdout.flush()
        if not obj.get_image(urls[i]):
            print "\ndownload failed at: (URLID: "+i+") "+urls[i]
    print "download complete."
    os.remove(obj.path+'/urls.json')
