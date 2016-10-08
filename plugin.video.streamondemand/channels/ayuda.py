# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# streamondemand.- XBMC Plugin
# ayuda - Videos de ayuda y tutoriales para pelisalacarta
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# contribuci?n de jurrabi
#----------------------------------------------------------------------
import re
from core import scrapertools
from core import config
from core import logger
from core.item import Item


CHANNELNAME = "ayuda"

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.channels.ayuda mainlist")
    itemlist = []

    platform_name = config.get_platform()
    cuantos = 0
    if "kodi" in platform_name or platform_name=="xbmceden" or platform_name=="xbmcfrodo" or platform_name=="xbmcgotham":
        itemlist.append( Item(channel=CHANNELNAME, action="force_creation_advancedsettings" , title="Crea file advancedsettings.xml ottimizzato"))
        cuantos = cuantos + 1
        
    if "kodi" in platform_name or "xbmc" in platform_name or "boxee" in platform_name:
        itemlist.append( Item(channel=CHANNELNAME, action="updatebiblio" , title="Cerca nuovi episodi e aggiorna la biblioteca"))
        cuantos = cuantos + 1

    if cuantos>0:
        itemlist.append( Item(channel=CHANNELNAME, action="tutoriales" , title="Vedere video per guide e tutorial"))
    else:
        itemlist.extend(tutoriales(item))

    return itemlist

def tutoriales(item):
    logger.info("streamondemand.channels.ayuda tutoriales")
    itemlist = []

    return playlists(item,"tvalacarta")

def force_creation_advancedsettings(item):
    logger.info("streamondemand.channels.ayuda force_creation_advancedsettings")
    import xbmc, xbmcgui, os

    # ======================================
    # Impostazioni
    # ======================================
    ram = ['512 Mega', '1 Gb', '2 Gb']
    opt = ['20971520','157286400', '157286400']
    advancedsettings = xbmc.translatePath("special://userdata/advancedsettings.xml")
    default = '20971520'
    valore = default

    try:
        dialog = xbmcgui.Dialog()
        risp = dialog.select('Scegli settaggio', [ram[0], ram[1], ram[2]])
        logger.info(str(risp))
        if risp ==0: valore = opt[0]
        if risp ==1: valore = opt[1]
        if risp ==2: valore = opt[2]
        if risp ==-1: valore = default
        file = '''<advancedsettings>
                    <network>
                        <buffermode>1</buffermode>
                        <cachemembuffersize>''' + valore + '''</cachemembuffersize>
                        <readbufferfactor>10</readbufferfactor>
                        <autodetectpingtime>30</autodetectpingtime>
                        <curlclienttimeout>60</curlclienttimeout>
                        <curllowspeedtime>60</curllowspeedtime>
                        <curlretries>2</curlretries>
                        <disableipv6>true</disableipv6>
                    </network>
                    <gui>
                        <algorithmdirtyregions>0</algorithmdirtyregions>
                        <nofliptimeout>0</nofliptimeout>
                    </gui>
                        <playlistasfolders1>false</playlistasfolders1>
                    <audio>
                        <defaultplayer>dvdplayer</defaultplayer>
                    </audio>
                        <imageres>540</imageres>
                        <fanartres>720</fanartres>
                        <splash>false</splash>
                        <handlemounting>0</handlemounting>
                    <samba>
                        <clienttimeout>30</clienttimeout>
                    </samba>
                </advancedsettings>'''
        logger.info(file)
        salva = open(advancedsettings, "w")
        salva.write(file)
        salva.close()
    except:
        pass

    dialog = xbmcgui.Dialog()
    dialog.ok("plugin", "E' stato creato un file advancedsettings.xml","con la configurazione ideale per lo streaming.")

    return []

def updatebiblio(item):
    import library_service
    
    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, action="" , title="Aggiornamenti in corso..."))
    
    return itemlist

# Show all YouTube playlists for the selected channel
def playlists(item,channel_id):
    logger.info("youtube_channel.playlists ")
    itemlist=[]

    item.url = "http://gdata.youtube.com/feeds/api/users/"+channel_id+"/playlists?v=2&start-index=1&max-results=30"

    # Fetch video list from YouTube feed
    data = scrapertools.cache_page( item.url )
    logger.info("data="+data)
    
    # Extract items from feed
    pattern = "<entry(.*?)</entry>"
    matches = re.compile(pattern,re.DOTALL).findall(data)
    
    for entry in matches:
        logger.info("entry="+entry)
        
        # Not the better way to parse XML, but clean and easy
        title = scrapertools.find_single_match(entry,"<titl[^>]+>([^<]+)</title>")
        plot = scrapertools.find_single_match(entry,"<media\:descriptio[^>]+>([^<]+)</media\:description>")
        thumbnail = scrapertools.find_single_match(entry,"<media\:thumbnail url='([^']+)'")
        url = scrapertools.find_single_match(entry,"<content type\='application/atom\+xml\;type\=feed' src='([^']+)'/>")

        # Appends a new item to the xbmc item list
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="videos" , url=url, thumbnail=thumbnail, plot=plot , folder=True) )
    return itemlist

# Show all YouTube videos for the selected playlist
def videos(item):
    logger.info("youtube_channel.videos ")
    itemlist=[]

    # Fetch video list from YouTube feed
    data = scrapertools.cache_page( item.url )
    logger.info("data="+data)
    
    # Extract items from feed
    pattern = "<entry(.*?)</entry>"
    matches = re.compile(pattern,re.DOTALL).findall(data)
    
    for entry in matches:
        logger.info("entry="+entry)
        
        # Not the better way to parse XML, but clean and easy
        title = scrapertools.find_single_match(entry,"<titl[^>]+>([^<]+)</title>")
        plot = scrapertools.find_single_match(entry,"<summa[^>]+>([^<]+)</summa")
        thumbnail = scrapertools.find_single_match(entry,"<media\:thumbnail url='([^']+)'")
        video_id = scrapertools.find_single_match(entry,"http\://www.youtube.com/watch\?v\=([0-9A-Za-z_-]{11})")
        url = video_id

        # Appends a new item to the xbmc item list
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="youtube", url=url, thumbnail=thumbnail, plot=plot , folder=False) )
    return itemlist

