# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# streamondemand - XBMC Plugin
# ayuda - Videos de ayuda y tutoriales para streamondemand
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# contribucion de jurrabi
# ----------------------------------------------------------------------

import os
import xbmc
import xbmcgui

from channels import youtube_channel
from core import config
from core import logger
from core.item import Item
from platformcode import platformtools
from core import scrapertools

# =======================================================
# Impostazioni
# --------------------------------------------------------
ram = ['512 Mega', '1 Gb', '2 Gb', 'più di 2 Gb']
opt = ['20971520', '52428800', '157286400', '209715200']
# =======================================================



def mainlist(item):
    logger.info("streamondemand.channels.ayuda mainlist")

    itemlist = []

    cuantos = 0
    if config.is_xbmc():
        itemlist.append(Item(channel=item.channel, action="",
                             title="[COLOR azure]Cache impostata su ram da [/COLOR] [COLOR orange]" + Leggi_Parametro() + "[/COLOR]",plot="\n\nIl file advancedsettings.xml è impostato \n per una ram pari a [COLOR orange]"+ Leggi_Parametro()+"[/COLOR]", folder=False))
        itemlist.append(Item(channel=item.channel, action="force_creation_advancedsettings",
                             title="Crea advancedsettings.xml ottimizzato",plot="\n\n\nImpostazione cache per [COLOR orange] Kodi 16[/COLOR]" ))
        itemlist.append(Item(channel=item.channel, action="force_creation_advancedsettings_17",
                             title="Crea advancedsettings.xml ottimizzato Kodi 17",plot="\n\n\nNuova impostazione cache per [COLOR orange] Kodi 17 [/COLOR]  "))
        cuantos += cuantos


    #if cuantos > 0:
        #itemlist.append(Item(channel=item.channel, action="tutoriales", title="Consulta i video tutorial"))
    #else:
        ##itemlist.extend(tutoriales(item))

    return itemlist


def tutoriales(item):
    playlists = youtube_channel.playlists(item, "tvalacarta")

    itemlist = []

    for playlist in playlists:
        if playlist.title == "Tutorial di streamondemand":
            itemlist = youtube_channel.videos(playlist)

    return itemlist


def force_creation_advancedsettings(item):
    # Ruta del advancedsettings
    advancedsettings = xbmc.translatePath("special://userdata/advancedsettings.xml")
    itemlist = []

    try:
        risp = platformtools.dialog_select('Scegli settaggio cache', [ram[0], ram[1], ram[2], ram[3]])
        logger.info(str(risp))
        if risp == 0:
            valore = opt[0]
            testo = "\n[COLOR orange]Cache Impostata per 512 Mega di RAM[/COLOR]"
        if risp == 1:
            valore = opt[1]
            testo = "\n[COLOR orange]Cache Impostata per 1 Gb di RAM[/COLOR]"
        if risp == 2:
            valore = opt[2]
            testo = "\n[COLOR orange]Cache Impostata per 2 Gb di RAM[/COLOR]"
        if risp == 3:
            valore = opt[3]
            testo = "\n[COLOR orange]Cache Impostata a superiore di 2 Gb di RAM[/COLOR]"
        if risp < 0:
            return itemlist

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

    platformtools.dialog_ok("plugin", "E' stato creato un file advancedsettings.xml","con la configurazione ideale per lo streaming.", testo)

    return itemlist

def force_creation_advancedsettings_17(item):
    # Ruta del advancedsettings
    advancedsettings = xbmc.translatePath("special://userdata/advancedsettings.xml")
    itemlist=[]
    try:
        risp = platformtools.dialog_select('Scegli settaggio cache', [ram[0], ram[1], ram[2], ram[3]])
        logger.info(str(risp))

        if risp == 0:
            valore = opt[0]
            testo = "\n[COLOR orange]Cache Impostata per 512 Mega di RAM[/COLOR]"
        if risp == 1:
            valore = opt[1]
            testo = "\n[COLOR orange]Cache Impostata per 1 Gb di RAM[/COLOR]"
        if risp == 2:
            valore = opt[2]
            testo = "\n[COLOR orange]Cache Impostata per 2 Gb di RAM[/COLOR]"
        if risp == 3:
            valore = opt[3]
            testo = "\n[COLOR orange]Cache Impostata a superiore di 2 Gb di RAM[/COLOR]"
        if risp < 0:
            return itemlist


        file = '''<advancedsettings>
                    <network>
                        <autodetectpingtime>30</autodetectpingtime>
                        <curlclienttimeout>60</curlclienttimeout>
                        <curllowspeedtime>60</curllowspeedtime>
                        <curlretries>2</curlretries>
                        <disableipv6>true</disableipv6>
                    </network>
                    <cache>
                        <buffermode>1</buffermode>
                        <memorysize>''' + valore + '''</memorysize>
                        <readfactor>10</readfactor>
                    </cache>
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

    platformtools.dialog_ok("plugin", "E' stato creato un file advancedsettings.xml","con la configurazione ideale per lo streaming.", testo)

    return itemlist

def Leggi_Parametro():
    logger.info("streamondemand.channels.ayuda Leggi_Parametro")
    itemlist=[]

    advancedsettings = xbmc.translatePath("special://userdata/advancedsettings.xml")

    if os.path.exists(advancedsettings):
        infile = open(advancedsettings, "rb")
        data = infile.read()
        infile.close()


        if scrapertools.find_single_match(data, "<memorysize>([^<]*)</memorysize>")=='':
            if scrapertools.find_single_match(data, "<cachemembuffersize>([^<]*)</cachemembuffersize>")==opt[0]:
                return ram[0]
            elif scrapertools.find_single_match(data, "<cachemembuffersize>([^<]*)</cachemembuffersize>")==opt[1]:
                return ram[1]
            elif scrapertools.find_single_match(data, "<cachemembuffersize>([^<]*)</cachemembuffersize>")==opt[2]:
                return ram[2]
            elif scrapertools.find_single_match(data, "<cachemembuffersize>([^<]*)</cachemembuffersize>")==opt[3]:
                return ram[3]

        else:
            if scrapertools.find_single_match(data, "<memorysize>([^<]*)</memorysize>")==opt[0]:
                return ram[0]
            elif scrapertools.find_single_match(data, "<memorysize>([^<]*)</memorysize>")==opt[1]:
                return ram[1]
            elif scrapertools.find_single_match(data, "<memorysize>([^<]*)</memorysize>")==opt[2]:
                return ram[2]
            elif scrapertools.find_single_match(data, "<memorysize>([^<]*)</memorysize>")==opt[3]:
                return ram[3]
    return " - "
