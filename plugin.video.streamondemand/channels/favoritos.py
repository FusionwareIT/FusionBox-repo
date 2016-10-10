# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand 5
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of streamondemand 5.
#
# streamondemand 5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# streamondemand 5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with streamondemand 5.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
# Lista de vídeos favoritos
# ------------------------------------------------------------

import os
import sys
import urllib

from lib.sambatools import libsmb as samba

from core import config
from core import logger
from core.item import Item

if config.is_xbmc():
    import xbmc

CHANNELNAME = "favoritos"
DEBUG = config.get_setting("debug")
BOOKMARK_PATH = config.get_setting("bookmarkpath")

if not BOOKMARK_PATH.upper().startswith("SMB://"):
    if BOOKMARK_PATH.startswith("special://") and config.is_xbmc():
        # logger.info("pelisalacarta.channels.favoritos Se esta utilizando el protocolo 'special'")
        BOOKMARK_PATH = xbmc.translatePath(config.get_setting("bookmarkpath"))
    if BOOKMARK_PATH == "":
        BOOKMARK_PATH = os.path.join(config.get_data_path(), "bookmarks")
    if not os.path.exists(BOOKMARK_PATH):
        # logger.debug("[favoritos.py] Path de bookmarks no existe, se crea: " + BOOKMARK_PATH)
        os.mkdir(BOOKMARK_PATH)

def mainlist(item):
    logger.info("streamondemand.channels.favoritos mainlist")
    itemlist = []

    # Crea un listado con las entradas de favoritos
    if samba.usingsamba(BOOKMARK_PATH):
        ficheros = samba.get_files(BOOKMARK_PATH)
    else:
        ficheros = os.listdir(BOOKMARK_PATH)
    
    # Ordena el listado por nombre de fichero (orden de incorporación)
    ficheros.sort()
    
    # Rellena el listado
    for fichero in ficheros:

        try:
            # Lee el bookmark
            canal, titulo, thumbnail, plot, server, url, fulltitle = readbookmark(fichero)
            if canal == "":
                canal = "favoritos"

            # Crea la entrada
            # En extra va el nombre del fichero para poder borrarlo
            # <-- Añado fulltitle con el titulo de la peli
            itemlist.append(Item(channel=canal, action="play", url=url, server=server, title=fulltitle,
                                 thumbnail=thumbnail, plot=plot, fanart=thumbnail,
                                 extra=os.path.join(BOOKMARK_PATH, fichero), fulltitle=fulltitle, folder=False))
        except:
            for line in sys.exc_info():
                logger.error("%s" % line)
    
    return itemlist


def readbookmark(filename, readpath=BOOKMARK_PATH):
    logger.info("streamondemand.channels.favoritos readbookmark")

    if samba.usingsamba(readpath):
        bookmarkfile = samba.get_file_handle_for_reading(filename, readpath)
    else:
        filepath = os.path.join(readpath, filename)

        # Lee el fichero de configuracion
        logger.info("streamondemand.channels.favoritos filepath="+filepath)
        bookmarkfile = open(filepath)
    lines = bookmarkfile.readlines()

    try:
        titulo = urllib.unquote_plus(lines[0].strip())
    except:
        titulo = lines[0].strip()
    
    try:
        url = urllib.unquote_plus(lines[1].strip())
    except:
        url = lines[1].strip()
    
    try:
        thumbnail = urllib.unquote_plus(lines[2].strip())
    except:
        thumbnail = lines[2].strip()
    
    try:
        server = urllib.unquote_plus(lines[3].strip())
    except:
        server = lines[3].strip()
        
    try:
        plot = urllib.unquote_plus(lines[4].strip())
    except:
        plot = lines[4].strip()

    # Campos fulltitle y canal añadidos
    if len(lines) >= 6:
        try:
            fulltitle = urllib.unquote_plus(lines[5].strip())
        except:
            fulltitle = lines[5].strip()
    else:
        fulltitle = titulo

    if len(lines) >= 7:
        try:
            canal = urllib.unquote_plus(lines[6].strip())
        except:
            canal = lines[6].strip()
    else:
        canal = ""

    bookmarkfile.close()

    return canal, titulo, thumbnail, plot, server, url, fulltitle


def savebookmark(canal=CHANNELNAME, titulo="", url="", thumbnail="", server="", plot="", fulltitle="",
                 savepath=BOOKMARK_PATH):
    logger.info("streamondemand.channels.favoritos savebookmark(path="+savepath+")")

    # Crea el directorio de favoritos si no existe
    if not samba.usingsamba(savepath):
        try:
            os.mkdir(savepath)
        except:
            pass

    # Lee todos los ficheros
    if samba.usingsamba(savepath):
        ficheros = samba.get_files(savepath)
    else:
        ficheros = os.listdir(savepath)
    ficheros.sort()
    
    # Averigua el último número
    if len(ficheros) > 0:
        # XRJ: Linea problemática, sustituida por el bucle siguiente
        # filenumber = int( ficheros[len(ficheros)-1][0:-4] )+1
        filenumber = 1
        for fichero in ficheros:
            logger.info("streamondemand.channels.favoritos fichero="+fichero)
            try:
                tmpfilenumber = int(fichero[0:8])+1
                if tmpfilenumber > filenumber:
                    filenumber = tmpfilenumber
            except:
                pass
    else:
        filenumber = 1

    # Genera el contenido
    filecontent = ""
    filecontent = filecontent + urllib.quote_plus(titulo)+'\n'
    filecontent = filecontent + urllib.quote_plus(url)+'\n'
    filecontent = filecontent + urllib.quote_plus(thumbnail)+'\n'
    filecontent = filecontent + urllib.quote_plus(server)+'\n'
    filecontent = filecontent + urllib.quote_plus(plot)+'\n'
    filecontent = filecontent + urllib.quote_plus(fulltitle)+'\n'
    filecontent = filecontent + urllib.quote_plus(canal)+'\n'

    # Genera el nombre de fichero
    from core import scrapertools
    filename = '%08d-%s.txt' % (filenumber, scrapertools.slugify(fulltitle))
    logger.info("streamondemand.channels.favoritos savebookmark filename="+filename)

    # Graba el fichero
    if not samba.usingsamba(savepath):
        fullfilename = os.path.join(savepath, filename)
        bookmarkfile = open(fullfilename, "w")
        bookmarkfile.write(filecontent)
        bookmarkfile.flush()
        bookmarkfile.close()
    else:
        samba.store_File(filename, filecontent, savepath)


def deletebookmark(fullfilename, deletepath=BOOKMARK_PATH):
    logger.info("streamondemand.channels.favoritos deletebookmark(fullfilename="+fullfilename+",deletepath="+deletepath+")")

    if not samba.usingsamba(deletepath):
        os.remove(os.path.join(urllib.unquote_plus(deletepath), urllib.unquote_plus(fullfilename)))
    else:
        fullfilename = fullfilename.replace("\\", "/")
        partes = fullfilename.split("/")
        filename = partes[len(partes)-1]
        logger.info("streamondemand.channels.favoritos filename="+filename)
        logger.info("streamondemand.channels.favoritos deletepath="+deletepath)
        samba.delete_files(filename, deletepath)
