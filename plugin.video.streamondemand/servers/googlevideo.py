# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para Google Video
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
# modify by DrZ3r0

import json
import re
import urllib
import urllib2

from core import logger
from core import scrapertools
from core import servertools

itag_map = {'5': '240', '6': '270', '17': '144', '18': '360', '22': '720', '34': '360', '35': '480',
            '36': '240', '37': '1080', '38': '3072', '43': '360', '44': '480', '45': '720', '46': '1080',
            '82': '360 [3D]', '83': '480 [3D]', '84': '720 [3D]', '85': '1080p [3D]', '100': '360 [3D]',
            '101': '480 [3D]', '102': '720 [3D]', '92': '240', '93': '360', '94': '480', '95': '720',
            '96': '1080', '132': '240', '151': '72', '133': '240', '134': '360', '135': '480',
            '136': '720', '137': '1080', '138': '2160', '160': '144', '264': '1440',
            '298': '720', '299': '1080', '266': '2160', '167': '360', '168': '480', '169': '720',
            '170': '1080', '218': '480', '219': '480', '242': '240', '243': '360', '244': '480',
            '245': '480', '246': '480', '247': '720', '248': '1080', '271': '1440', '272': '2160',
            '302': '2160', '303': '1080', '308': '1440', '313': '2160', '315': '2160', '59': '480'}


# Returns an array of possible video url's from the page_url
def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[googlevideo.py] get_video_url(page_url='%s')" % page_url)

    data, video_urls = _parse_google(page_url)

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0'}
    if data is not None:
        res_headers = dict(scrapertools.get_headers_from_response(page_url))
        if 'set-cookie' in res_headers:
            headers['Cookie'] = res_headers['set-cookie']
    headers = urllib.urlencode(headers)

    if not video_urls:
        video_urls.append(['Unknown Quality', page_url])

    for video_url in video_urls:
        if ('redirector.' in video_url[1]) or ('googleusercontent' in video_url[1]):
            video_url[1] = urllib2.urlopen(video_url[1]).geturl()

        if 'plugin://' not in video_url[1]:
            video_url[1] += '|' + headers

    for video_url in video_urls:
        logger.info("[googlevideo.py] %s - %s" % (video_url[0], video_url[1]))

    return video_urls


# Encuentra v�deos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos = r"""(https?://(?:redirector\.)?googlevideo.com/[^"']+)(?:",\s*"label":\s*([0-9]+),)?"""
    logger.info("[googlevideo.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        titulo = "[googlevideo]"
        url = match.group(1)

        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'googlevideo'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    patronvideos = r'(https?://(?:lh.\.)?googleusercontent.com/[^=]+=m(\d+))'
    logger.info("[googlevideo.py] find_videos #" + patronvideos + "#")
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        titulo = "[googlevideo]"
        url = match.group(1)

        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'googlevideo'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    patronvideos = r'.google.com/file/d/([a-zA-Z0-9_-]+)'
    logger.info("[googlevideo.py] find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for media_id in matches:
        titulo = "[googlevideo]"
        # redir = "http://api.getlinkdrive.com/getlink?url="
        url = 'https://drive.google.com/file/d/%s/view' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'googlevideo'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    patronvideos = r'.google.com/open\?\id=([a-zA-Z0-9_-]+)'
    logger.info("[googledrive.py] find_videos #" + patronvideos + "#")

    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    for media_id in matches:
        titulo = "[googlevideo]"
        # redir = "http://api.getlinkdrive.com/getlink?url="
        url = 'https://drive.google.com/file/d/%s/view' % media_id
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'googlevideo'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve


def _parse_google(link):
    sources = []
    response = None
    if re.match('https?://get[.]', link):
        if link.endswith('/'): link = link[:-1]
        vid_id = link.split('/')[-1]
        response = scrapertools.cache_page(link)
        sources = _parse_gget(vid_id, response)
    elif re.match('https?://plus[.]', link):
        response = scrapertools.cache_page(link)
        sources = _parse_gplus(response)
    elif 'drive.google' in link or 'docs.google' in link:
        response = scrapertools.cache_page(link)
        sources = _parse_gdocs(response)
    return response, sources


def _parse_gplus(html):
    sources = []
    match = re.search('<c-wiz.+?track:impression,click".*?jsdata\s*=\s*".*?(http[^"]+)"', html, re.DOTALL)
    if match:
        source = match.group(1).replace('&amp;', '&').split(';')[0]
        resolved = servertools.findvideos(data=source, skip=True)
        if resolved:
            resolved, ok, msg = servertools.resolve_video_urls_for_playing(url=resolved[0][1], server=resolved[0][2])
            if ok:
                sources.append(['Unknown Quality', resolved[0][1]])
    return sources


def _parse_gget(vid_id, html):
    sources = []
    match = re.search('.+return\s+(\[\[.*?)\s*}}', html, re.DOTALL)
    if match:
        try:
            js = _parse_json(match.group(1))
            for top_item in js:
                if isinstance(top_item, list):
                    for item in top_item:
                        if isinstance(item, list):
                            for item2 in item:
                                if isinstance(item2, list):
                                    for item3 in item2:
                                        if vid_id in str(item3):
                                            sources = _extract_video(item2)
                                            if sources:
                                                return sources
        except Exception as e:
            pass
    return sources


def _parse_gdocs(html):
    urls = []
    for match in re.finditer('\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]', html):
        key, value = match.groups()
        if key == 'fmt_stream_map':
            items = value.split(',')
            for item in items:
                _source_itag, source_url = item.split('|')
                if isinstance(source_url, unicode):
                    source_url = source_url.encode('utf-8')

                source_url = source_url.decode('unicode_escape')
                quality = itag_map.get(_source_itag, 'Unknown Quality [%s]' % _source_itag)
                source_url = urllib2.unquote(source_url)
                urls.append([quality, source_url])
            return urls

    return urls


def _parse_json(html):
    if html:
        try:
            if not isinstance(html, unicode):
                if html.startswith('\xef\xbb\xbf'):
                    html = html[3:]
                elif html.startswith('\xfe\xff'):
                    html = html[2:]
            js_data = json.loads(html)
            if js_data is None:
                return {}
            else:
                return js_data
        except ValueError:
            return {}
    else:
        return {}


def _extract_video(item):
    sources = []
    for e in item:
        if isinstance(e, dict):
            for key in e:
                for item2 in e[key]:
                    if isinstance(item2, list):
                        for item3 in item2:
                            if isinstance(item3, list):
                                for item4 in item3:
                                    if isinstance(item4, unicode):
                                        item4 = item4.encode('utf-8')

                                    if isinstance(item4, basestring):
                                        item4 = urllib2.unquote(item4).decode('unicode_escape')
                                        for match in re.finditer('url=(?P<link>[^&]+).*?&itag=(?P<itag>[^&]+)', item4):
                                            link = match.group('link')
                                            itag = match.group('itag')
                                            quality = itag_map.get(itag, 'Unknown Quality [%s]' % itag)
                                            sources.append([quality, link])
                                        if sources:
                                            return sources
    return sources
