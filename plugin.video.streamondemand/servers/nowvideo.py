# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para nowvideo
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
# Credits:
# Unwise and main algorithm taken from Eldorado url resolver
# https://github.com/Eldorados/script.module.urlresolver/blob/master/lib/urlresolver/plugins/nowvideo.py

import re

from core import logger
from core import scrapertools

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:20.0) Gecko/20100101 Firefox/20.0"


def test_video_exists(page_url):
    logger.info("[nowvideo.py] test_video_exists(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)

    if "The file is being converted" in data:
        return False, "Il file è in conversione"

    if "no longer exists" in data:
        return False, "Il file è stato rimosso"

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[nowvideo.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    video_id = scrapertools.get_match(page_url, "http://www.nowvideo.../video/([a-z0-9]+)")

    if premium:
        # Lee la página de login
        login_url = "http://www.nowvideo.eu/login.php"
        data = scrapertools.cache_page(login_url)

        # Hace el login
        login_url = "http://www.nowvideo.eu/login.php?return="
        post = "user=" + user + "&pass=" + password + "&register=Login"
        headers = [["User-Agent", USER_AGENT], ["Referer", "http://www.nowvideo.eu/login.php"]]
        data = scrapertools.cache_page(login_url, post=post, headers=headers)

        # Descarga la página del vídeo 
        data = scrapertools.cache_page(page_url)
        logger.debug("data:" + data)

        # URL a invocar: http://www.nowvideo.eu/api/player.api.php?user=aaa&file=rxnwy9ku2nwx7&pass=bbb&cid=1&cid2=undefined&key=83%2E46%2E246%2E226%2Dc7e707c6e20a730c563e349d2333e788&cid3=undefined
        # En la página:
        '''
        flashvars.domain="http://www.nowvideo.eu";
        flashvars.file="rxnwy9ku2nwx7";
        flashvars.filekey="83.46.246.226-c7e707c6e20a730c563e349d2333e788";
        flashvars.advURL="0";
        flashvars.autoplay="false";
        flashvars.cid="1";
        flashvars.user="aaa";
        flashvars.key="bbb";
        flashvars.type="1";
        '''
        flashvar_file = scrapertools.get_match(data, 'flashvars.file="([^"]+)"')
        flashvar_filekey = scrapertools.get_match(data, 'flashvars.filekey=([^;]+);')
        flashvar_filekey = scrapertools.get_match(data, 'var ' + flashvar_filekey + '="([^"]+)"')
        flashvar_user = scrapertools.get_match(data, 'flashvars.user="([^"]+)"')
        flashvar_key = scrapertools.get_match(data, 'flashvars.key="([^"]+)"')
        flashvar_type = scrapertools.get_match(data, 'flashvars.type="([^"]+)"')

        # http://www.nowvideo.eu/api/player.api.php?user=aaa&file=rxnwy9ku2nwx7&pass=bbb&cid=1&cid2=undefined&key=83%2E46%2E246%2E226%2Dc7e707c6e20a730c563e349d2333e788&cid3=undefined
        url = "http://www.nowvideo.eu/api/player.api.php?user=" + flashvar_user + "&file=" + flashvar_file + "&pass=" + flashvar_key + "&cid=1&cid2=undefined&key=" + flashvar_filekey.replace(
            ".", "%2E").replace("-", "%2D") + "&cid3=undefined"
        data = scrapertools.cache_page(url)
        logger.info("data=" + data)

        location = scrapertools.get_match(data, 'url=([^\&]+)&')
        location += "?client=FLASH"

        video_urls.append([scrapertools.get_filename_from_url(location)[-4:] + " [premium][nowvideo]", location])
    else:
        # http://www.nowvideo.sx/video/xuntu4pfq0qye
        url = page_url.replace("http://www.nowvideo.sx/video/", "http://embed.nowvideo.sx/embed/?v=")
        data = scrapertools.cache_page(url)
        logger.debug("data=" + data)

        videourl = scrapertools.find_single_match(data, '<source src="([^"]+)"')
        if not videourl:
            data = scrapertools.cache_page(page_url)
            stepkey = scrapertools.find_single_match(data, '<input type="hidden" name="stepkey" value="([^"]+)"')
            if stepkey != "":
                # stepkey=6cd619a0cea72a1cb45a56167c296716&submit=submit
                # <form method="post" action="">
                # <input type="hidden" name="stepkey" value="6cd619a0cea72a1cb45a56167c296716"><Br>
                # <button type="submit" name="submit" class="btn" value="submit">Continue to the video</button>
                data = scrapertools.cache_page(page_url, post="stepkey=" + stepkey + "&submit=submit")
            videourl = scrapertools.find_single_match(data, '<source src="([^"]+)"')
            if not videourl:
                flashvar_filekey = scrapertools.get_match(data, 'flashvars.filekey=([^;]+);')
                filekey = scrapertools.get_match(data, 'var ' + flashvar_filekey + '="([^"]+)"')

                '''
                data = unwise.unwise_process(data)
                logger.debug("data="+data)

                filekey = unwise.resolve_var(data, "flashvars.filekey")
                '''
                logger.debug("filekey=" + filekey)

                # get stream url from api
                url = 'http://www.nowvideo.sx/api/player.api.php?key=%s&file=%s' % (filekey, video_id)
                data = scrapertools.cache_page(url).replace("flv&", "flv?")
                videourl = re.sub(r"^url=", "", data)
                logger.debug("data=" + videourl)
                '''
                location = scrapertools.get_match(data,'url=(.+?)&title')

                mobile="http://www.nowvideo.at/mobile/video.php?id="+ video_id+"&download=2"
                data = scrapertools.cache_page(mobile)
                location = scrapertools.get_match(data,'<source src="([^"]+)" type="video/flv">')
                video_urls.append( [ "[nowvideo]",location ] )
                '''

        video_urls.append([scrapertools.get_filename_from_url(videourl)[-4:] + " [nowvideo]", videourl])

    for video_url in video_urls:
        logger.info("[nowvideo.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls


def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = ['player3k.info/nowvideo/\?id\=([a-z0-9]+)',
                    'nowvideo.../(?:video/|embed\.php\?\S*v=)([A-Za-z0-9]+)',
                    'nowvideo..../(?:video/|embed\.php\?\S*v=)([A-Za-z0-9]+)',
                    '0stream\.to/video/([A-Za-z0-9]+)'
                    ]

    for patron in patronvideos:
        logger.info("[nowvideo.py] find_videos #" + patron + "#")
        matches = re.compile(patron, re.DOTALL).findall(data)

        for match in matches:
            titulo = "[nowvideo]"
            url = "http://www.nowvideo.sx/video/%s" % match
            if url not in encontrados:
                logger.info("  url=" + url)
                devuelve.append([titulo, url, 'nowvideo'])
                encontrados.add(url)
            else:
                logger.info("  url duplicada=" + url)

    return devuelve
