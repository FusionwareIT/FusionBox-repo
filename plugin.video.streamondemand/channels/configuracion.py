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
# ------------------------------------------------------------
# Configuración
# ------------------------------------------------------------

from core import config
from core import logger
from core.item import Item

DEBUG = True
CHANNELNAME = "configuracion"


def mainlist(item):
    logger.info("tvalacarta.channels.configuracion mainlist")

    itemlist = []
    itemlist.append(Item(channel=CHANNELNAME, title="Preferenze", action="settings", folder=False))
    itemlist.append(Item(channel=CHANNELNAME, title="", action="", folder=False))
    itemlist.append(Item(channel="novedades", title="Impostazioni 'Novità'", action="menu_opciones", folder=True))
    itemlist.append(Item(channel="buscador", title="Impostazioni della ricerca globale", action="opciones", folder=True))
    if config.is_xbmc():
        itemlist.append(Item(channel=item.channel, action="updatebiblio",
                             title="Recupera nuovi episodi e aggiorna la libreria", folder=False))
    itemlist.append(Item(channel=CHANNELNAME, title="", action="", folder=False))
    itemlist.append(Item(channel=CHANNELNAME, title="Avvia aggiornamenti", action="check_for_updates", folder=False))

    return itemlist


def check_for_updates(item):
    from core import updater

    try:
        version = updater.checkforupdates()
        if version:
            import xbmcgui
            yes_pressed = xbmcgui.Dialog().yesno( "Versione "+version+" disponible" , "Installarla?" )
      
            if yes_pressed:
                item = Item(version=version)
                updater.update(item)

    except:
        pass

def settings(item):
    config.open_settings()

def updatebiblio(item):
    logger.info("streamondemand.channels.ayuda updatebiblio")

    import library_service
    library_service.main()

