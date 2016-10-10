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

def mainlist(item):
    logger.info("streamondemand.channels.ayuda mainlist")
    itemlist = []

    cuantos = 0
    if config.is_xbmc():
        itemlist.append(Item(channel=item.channel, action="force_creation_advancedsettings",
                             title="Crea advancedsettings.xml ottimizzato"))
        cuantos += cuantos

    if cuantos > 0:
        itemlist.append(Item(channel=item.channel, action="tutoriales", title="Consulta i video tutorial"))
    else:
        itemlist.extend(tutoriales(item))

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

    # =======================================================
    # Impostazioni
    #--------------------------------------------------------
    ram = ['512 Mega', '1 Gb', '2 Gb', 'più di 2 Gb']
    opt = ['20971520', '52428800', '157286400', '209715200']
    # =======================================================
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
            valore = opt[0]
            testo = "\n[COLOR orange]Cache Impostata per default a 512 Mega di RAM[/COLOR]"

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

    return mainlist(item)
