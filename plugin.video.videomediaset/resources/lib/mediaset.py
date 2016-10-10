import requests
import re
import math
from bs4 import BeautifulSoup

class Mediaset:

    def _getJson(self,url,params=None):
        r = requests.get(url, params=params)
        if r.status_code == requests.codes.ok:
            try:
                return r.json()
            except:
                return False
        return False

    def _getSoup(self,url,params=None):
        r = requests.get(url, params=params)
        if r.status_code == requests.codes.ok:
            return BeautifulSoup(r.text, "html.parser")
        return False

    def _getText(self,url,params=None):
        r = requests.get(url, params=params)
        if r.status_code == requests.codes.ok:
            return r.text
        return False

    def get_prog_root(self):
        url = "http://www.video.mediaset.it/programma/progr_archivio.json"
        data = self._getJson(url)
        return data["programmi"]["group"]

    def get_url_groupList(self,url):
        if not url.startswith("http"):
            url="http://www.video.mediaset.it"+url
        url=url.replace("archivio-news.shtml","archivio-video.shtml")
        soup=self._getSoup(url)
        container=soup.find("div", class_="main-container")
        subparts=container.find_all('section')
        elements = []
        for subpart in subparts:
            name = subpart.find('h2')
            if name and name.text.strip():
                data=subpart.find('div')
                if data:
                    elements.append({'titolo': name.text.strip(), 
                                    'url': "http://www.video.mediaset.it/%s/%s/%s.shtml" % (data['data-type'],data['data-area'],data['data-box'])})
        return elements

    def get_prog_epList(self,url):
        totres = 0
        count = 0
        page = 1
        arrdata=[]
        maxpage = 200
        while (page < maxpage):
            nurl = "%s?page=%s" % (url,page)
            soup = self._getSoup(nurl)
            videos = soup.find_all('div',class_='box')
            if videos:
                for video in videos:
                    if totres == 0 and video.has_attr('data-maxitem'):
                        totres = float(video['data-maxitem'])
                        maxpage = totres
                        totpage = math.ceil(totres / 2)
                    img = video.find('img')
                    p = video.find('p')
                    arrdata.append({'id': video['data-id'],'titolo':img['alt'].encode('utf-8'),'thumbs':img['data-src'].replace("176x99","640x360"),'desc':p.text.strip().encode('utf-8')});
            page = page + 1

        return arrdata

    def get_prog_seasonList(self,url):
        if not url.startswith("http"):
            url="http://www.video.mediaset.it"+url
        url=url.replace("archivio-news.shtml","archivio-video.shtml")
        soup = self._getSoup(url)
        arrdata = []
        container=soup.find("li", class_="season clearfix")
        if container:
            links = container.find_all("a")
            if links:
                for link in links:
                    if not link.has_attr("class"):
                        arrdata.append({"titolo": link.text.strip().encode('utf-8'), "url": link['href']})
        return arrdata

    def get_global_epList(self,mode,range=0):
        if mode == 0: 
            url = "http://www.video.mediaset.it/bacino/bacinostrip_1.shtml?page=all"
        elif mode == 1:
            url = "http://www.video.mediaset.it/piu_visti/piuvisti-%s.shtml?page=all" % range
        elif mode == 2:
            url = "http://www.video.mediaset.it/bacino/bacinostrip_5.shtml?page=all"

        soup = self._getSoup(url)
        arrdata=[]
        videos = soup.find_all('div',class_='box')
        if videos:
            for video in videos:
                a = video.find('a', {'data-type': 'video'})
                img = a.find('img')
                imgurl = img['data-src']
                res = re.search("([0-9][0-9][0-9][0-9][0-9]+)",imgurl)
                if res:
                    idv = res.group(1)
                else:
                    idv = re.search("([0-9][0-9][0-9][0-9][0-9]+)",a['href']).group(1)
                p = video.find('p', class_='descr')
                arrdata.append({'id': idv,'url':a['href'],'titolo':img['alt'].encode("utf-8"),'tipo':video['class'],'thumbs':imgurl.replace("176x99","640x360"),'desc':p.text.strip().encode("utf-8")})
        return arrdata

    def get_canali_live(self):
        
        url = "http://live1.msf.ticdn.it/Content/HLS/Live/Channel(CH%sHA)/Stream(04)/index.m3u8"
        tmb = "https://raw.githubusercontent.com/aracnoz/videomediaset_logo/master/%s.png"

        arrdata = []

        arrdata.append({'titolo':"Canale 5", 'url':url % ('01'),'desc':"",'thumbs':tmb % ("Canale_5")})
        arrdata.append({'titolo':"Italia 1", 'url':url % ('02'),'desc':"",'thumbs':tmb % ("Italia_1")})
        arrdata.append({'titolo':"Rete 4", 'url':url % ('03'),'desc':"",'thumbs':tmb % ("Rete_4")})
        arrdata.append({'titolo':"La 5", 'url':url % ('04'),'desc':"",'thumbs':tmb % ("La_5")})
        arrdata.append({'titolo':"Italia 2", 'url':url % ('05'),'desc':"",'thumbs':tmb % ("Italia_2")})
        arrdata.append({'titolo':"Iris", 'url':url % ('06'),'desc':"",'thumbs':tmb % ("Iris")})
        arrdata.append({'titolo':"Top Crime", 'url':url % ('07'),'desc':"",'thumbs':tmb % ("Top_Crime")})
        arrdata.append({'titolo':"Premium Extra", 'url':url % ('08'),'desc':"",'thumbs':tmb % ("Premium_Extra")})
        arrdata.append({'titolo':"Mediaset Extra", 'url':url % ('09'),'desc':"",'thumbs':tmb % ("Mediaset_Extra")})
        arrdata.append({'titolo':"TGCOM24", 'url':url % ('10'),'desc':"",'thumbs':tmb % ("TGCOM24")})

        return arrdata

    def get_stream(self, id):

        url = "http://cdnselector.xuniplay.fdnames.com/GetCDN.aspx?streamid=%s&format=json" % (id)

        jsn = self._getJson(url)

        if jsn and jsn["state"]=="OK":

            stream = {"wmv":"","mp4":""}
            for vlist in jsn["videoList"]:
                print "videomediaset: streams %s" % vlist
                if ( vlist.find("/wmv2/") > 0): stream["wmv"] = vlist
                if ( vlist.find("/mp4/") > 0): stream["mp4"] = vlist

            return stream
        return False