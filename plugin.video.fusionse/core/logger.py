# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# fusionse 5
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of fusionse 5.
#
# fusionse 5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# fusionse 5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fusionse 5.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
# Logger (kodi)
#------------------------------------------------------------

from core import config
loggeractive = (config.get_setting("debug")=="true")

import xbmc

def log_enable(active):
    global loggeractive
    loggeractive = active

def info(texto):
    if loggeractive:
        try:
            xbmc.log(texto)
        except:
            # FIXME: ¿Esto de que falle al poner un log no se puede resolver con un encode("ascii",errors="ignore") ?
            validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in texto if c in validchars)
            xbmc.log("(stripped) "+stripped)

def debug(texto):
    if loggeractive:
        try:
            import inspect
            import os
            last=inspect.stack()[1]
            modulo= os.path.basename(os.path.splitext(last[1])[0])
            funcion= last [3]
            texto= "    [" + modulo + "." + funcion + "] " + texto
            xbmc.log("######## DEBUG #########")
            xbmc.log(texto)
        except:
            validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in texto if c in validchars)
            xbmc.log("(stripped) "+stripped)

def error(texto):
    if loggeractive:
        try:
            import inspect
            import os
            last=inspect.stack()[1]
            modulo= os.path.basename(os.path.splitext(last[1])[0])
            funcion= last [3]
            texto= "    [" + modulo + "." + funcion + "] " + texto
            xbmc.log("######## ERROR #########")
            xbmc.log(texto)
        except:
            validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in texto if c in validchars)
            xbmc.log("(stripped) "+stripped)
