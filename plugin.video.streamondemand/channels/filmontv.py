# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Canal para filmontv
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------

import re

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "filmontv"
__category__ = "F"
__type__ = "generic"
__title__ = "filmontv.tv (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.comingsoon.it"

TIMEOUT_TOTAL = 60


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.filmontv mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR red]IN ONDA ADESSO[/COLOR]",
                     action="tvoggi",
                     url="%s/filmtv/" % host,
                     thumbnail="http://a2.mzstatic.com/eu/r30/Purple/v4/3d/63/6b/3d636b8d-0001-dc5c-a0b0-42bdf738b1b4/icon_256.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Mattina[/COLOR]",
                     action="tvoggi",
                     url="%s/filmtv/?range=mt" % host,
                     thumbnail="http://www.creattor.com/files/23/787/morning-pleasure-icons-screenshots-17.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Pomeriggio[/COLOR]",
                     action="tvoggi",
                     url="%s/filmtv/?range=pm" % host,
                     thumbnail="http://icons.iconarchive.com/icons/custom-icon-design/weather/256/Sunny-icon.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Preserale[/COLOR]",
                     action="tvoggi",
                     url="%s/filmtv/?range=pr" % host,
                     thumbnail="https://s.evbuc.com/https_proxy?url=http%3A%2F%2Ftriumphbar.com%2Fimages%2Fhappyhour_icon.png&sig=ADR2i7_K2FSfbQ6b3dy12Xjgkq9NCEdkKg"),
                Item(channel=__channel__,
                     title="[COLOR azure]Prima serata[/COLOR]",
                     action="tvoggi",
                     url="%s/filmtv/?range=ps" % host,
                     thumbnail="http://icons.iconarchive.com/icons/icons-land/vista-people/256/Occupations-Pizza-Deliveryman-Male-Light-icon.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Seconda serata[/COLOR]",
                     action="tvoggi",
                     url="%s/filmtv/?range=ss" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Notte[/COLOR]",
                     action="tvoggi",
                     url="%s/filmtv/?range=nt" % host,
                     thumbnail="http://icons.iconarchive.com/icons/oxygen-icons.org/oxygen/256/Status-weather-clear-night-icon.png")]

    return itemlist


def tvoggi(item):
    logger.info("streamondemand.filmontv tvoggi")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="col-xs-5 box-immagine">[^<]+<img src="([^"]+)[^<]+<[^<]+<[^<]+<[^<]+<[^<]+<.*?titolo">(.*?)<[^<]+<[^<]+<[^<]+<[^>]+><br />(.*?)<[^<]+</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedtitle, scrapedtv in matches:
        scrapedurl = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        if (DEBUG): logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="do_search",
                 extra=scrapedtitle + '{}' + 'movie',
                 title=scrapedtitle + "[COLOR yellow]   " + scrapedtv + "[/COLOR]",
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 folder=True), tipo="movie"))

    return itemlist


# Esta es la función que realmente realiza la búsqueda

def do_search(item):
    from channels import buscador
    return buscador.do_search(item)
