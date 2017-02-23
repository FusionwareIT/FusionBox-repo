# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Canal para ver un vídeo conociendo su URL
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item


DEBUG = config.get_setting("debug")


def mainlist(item):
    logger.info("[tengourl.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=item.channel, action="search", title="Inserire l'URL [Link a server / download]"))
    itemlist.append( Item(channel=item.channel, action="search", title="Inserire l'URL [Link diretto al video]"))
    itemlist.append( Item(channel=item.channel, action="search", title="Inserire l'URL [Ricerca link in un URL]"))

    return itemlist

# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item,texto):
    logger.info("[tengourl.py] search texto="+texto)

    if not texto.startswith("http://"):
        texto = "http://"+texto

    itemlist = []

    if "servidor" in item.title:
        itemlist = servertools.find_video_items(data=texto)
        for item in itemlist:
            item.channel="tengourl"
            item.action="play"
    elif "directo" in item.title:
        itemlist.append( Item(channel=item.channel, action="play", url=texto, server="directo", title="Ver enlace directo"))
    else:
        data = scrapertools.downloadpage(texto)
        itemlist = servertools.find_video_items(data=data)
        for item in itemlist:
            item.channel="tengourl"
            item.action="play"

    if len(itemlist)==0:
        itemlist.append( Item(channel=item.channel, action="search", title="Non c'è uno stream compatibile per questa URL"))
    
    return itemlist
