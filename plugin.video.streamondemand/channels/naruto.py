# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para Naruto
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#  By Zanzibar82
# ------------------------------------------------------------

import re
import urlparse

import xbmc

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "naruto"
__category__ = "A"
__type__ = "generic"
__title__ = "naruto"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://manganimenod.altervista.org/"
home = "http://manganimenod.altervista.org/episodi.php?a=NARUTO1"

def isGeneric():
    return True

# -----------------------------------------------------------------
def mainlist(item):
    itemlist = []

    patron = '<div class="ep"><a href="(.*?)"><.*?title="(.*?)">'

    for scrapedurl, scrapedtitle in scrapedAll(home, patron):
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=host + scrapedurl,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 thumbnail="http://i46.tinypic.com/14njw2f.png",
                 fanart="http://www.animenewsnetwork.com/thumbnails/crop900x350/video/category/62/key_art_naruto.jpg"))

    return itemlist

# =================================================================
# Funzioni di servizio
# =================================================================

# -----------------------------------------------------------------

def scrapedAll(url="", patron=""):

    data = scrapertools.cache_page(url)
    if DEBUG: logger.info("data:" + data)
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    return matches
# =================================================================


