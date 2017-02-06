# -*- coding: utf-8 -*-
#------------------------------------------------------------
# fusionse - XBMC Plugin
# Canal para ver un vídeo conociendo su URL
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

from core import config
from core import logger
from core import servertools
from core.item import Item


DEBUG = config.get_setting("debug")


def mainlist(item):
    logger.info("[tengourl.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=item.channel, action="search", title="Incolla il Link del video"))

    return itemlist

# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item,texto):
    logger.info("[tengourl.py] search texto="+texto)

    if not texto.startswith("http://"):
        texto = "http://"+texto

    itemlist = []

    itemlist = servertools.find_video_items(data=texto)
    for item in itemlist:
        item.channel="tengourl"
        item.action="play"

    if len(itemlist)==0:
        itemlist.append( Item(channel=item.channel, action="search", title="Non c'è uno stream compatibile per questo Link"))
    
    return itemlist
