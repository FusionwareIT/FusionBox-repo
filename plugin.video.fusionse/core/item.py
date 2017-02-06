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
# Item is the object we use for representing data 
# --------------------------------------------------------------------------------

import base64
import copy
import os
import urllib
from HTMLParser import HTMLParser

from core import jsontools as json


class Item(object):
    def __init__(self, **kwargs):
        '''
        Inicializacion del item
        '''
        if kwargs.has_key("parentContent"):
            self.set_parent_content(kwargs["parentContent"])
            del kwargs["parentContent"]

        # Creamos el atributo infoLabels si no existe
        if not type(self.__dict__.get("infoLabels", "")) == dict:
            self.__dict__["infoLabels"] = {}

        self.__dict__.update(kwargs)
        self.__dict__ = self.toutf8(self.__dict__)

    def __contains__(self, m):
        '''
        Comprueba si un atributo existe en el item
        '''
        return m in self.__dict__

    def __setattr__(self, name, value):
        '''
        Función llamada al modificar cualquier atributo del item, modifica algunos atributos en función de los datos modificados
        '''
        if name == "__dict__":
            for key in value:
                self.__setattr__(key, value[key])
            return

        # Descodificamos los HTML entities
        if name in ["title", "plot", "fulltitle", "contentPlot", "contentTitle"]: value = self.decode_html(value)

        # Al modificar cualquiera de estos atributos content...
        if name in ["contentTitle", "contentPlot", "contentSerieName", "contentType", "contentEpisodeTitle",
                    "contentSeason", "contentEpisodeNumber", "contentThumbnail"]:
            # ... marcamos hasContentDetails como "true"...
            self.__dict__["hasContentDetails"] = "true"
            # ...y actualizamos infoLables
            if name == "contentTitle":
                self.__dict__["infoLabels"]["title"] = value
            elif name == "contentPlot":
                self.__dict__["infoLabels"]["plot"] = value
            elif name == "contentSerieName":
                self.__dict__["infoLabels"]["tvshowtitle"] = value
            elif name == "contentType":
                self.__dict__["infoLabels"]["mediatype"] = value
            elif name == "contentEpisodeTitle":
                self.__dict__["infoLabels"]["episodeName"] = value
            elif name == "contentSeason":
                self.__dict__["infoLabels"]["season"] = value
            elif name == "contentEpisodeNumber":
                self.__dict__["infoLabels"]["episode"] = value
            elif name == "contentThumbnail":
                self.__dict__["infoLabels"]["thumbnail"] = value

        else:

            super(Item, self).__setattr__(name, value)

    def __getattr__(self, name):
        '''
        Devuelve los valores por defecto en caso de que el atributo solicitado no exista en el item
        '''
        if name.startswith("__"): return super(Item, self).__getattribute__(name)

        # valor por defecto para folder
        if name == "folder":
            return True

        # valor por defecto para viewmode y contentChannel
        elif name in ["viewmode", "contentChannel"]:
            return "list"

        # Valor por defecto para hasContentDetails
        elif name == "hasContentDetails":
            return "false"

        elif name in ["contentTitle", "contentPlot", "contentSerieName", "contentType", "contentEpisodeTitle",
                      "contentSeason", "contentEpisodeNumber", "contentThumbnail"]:
            if name == "contentTitle":
                return self.__dict__["infoLabels"].get("title", "")
            elif name == "contentPlot":
                return self.__dict__["infoLabels"].get("plot", "")
            elif name == "contentSerieName":
                return self.__dict__["infoLabels"].get("tvshowtitle", "")
            elif name == "contentType":
                return self.__dict__["infoLabels"].get("mediatype", "")
            elif name == "contentEpisodeTitle":
                return self.__dict__["infoLabels"].get("episodeName", "")
            elif name == "contentSeason":
                return self.__dict__["infoLabels"].get("season", "")
            elif name == "contentEpisodeNumber":
                return self.__dict__["infoLabels"].get("episode", "")
            elif name == "contentThumbnail":
                return self.__dict__["infoLabels"].get("thumbnail", "")

        # valor por defecto para el resto de atributos
        else:
            return ""

    def set_parent_content(self, parentContent):
        '''
        Rellena los campos contentDetails con la informacion del item "padre"
        '''
        # Comprueba que parentContent sea un Item
        if not type(parentContent) == type(self):
            return
        # Copia todos los atributos que empiecen por "content" y esten declarados y los infoLabels
        for attr in parentContent.__dict__:

            if attr.startswith("content") or attr == "infoLabels":
                self.__setattr__(attr, parentContent.__dict__[attr])

    def tostring(self, separator=", "):
        '''
        Genera una cadena de texto con los datos del item para el log
        Uso: logger.info(item.tostring())
        '''
        dic = self.__dict__.copy()

        # Añadimos los campos content... si tienen algun valor
        for key in ["contentTitle", "contentPlot", "contentSerieName", "contentType",
                    "contentSeason", "contentEpisodeNumber", "contentThumbnail"]:
            value = self.__getattr__(key)
            if value: dic[key] = value

        return separator.join([var + "=[" + str(dic[var]) + "]" for var in sorted(dic)])

    def tourl(self):
        '''
        Genera una cadena de texto con los datos del item para crear una url, para volver generar el Item usar item.fromurl()
        Uso: url = item.tourl()
        '''
        return urllib.quote(base64.b64encode(json.dumps(self.__dict__)))

    def fromurl(self, url):
        '''
        Genera un item a partir de una cadena de texto. La cadena puede ser creada por la funcion tourl() o tener
        el formato antiguo: plugin://plugin.video.fusionse/?channel=... (+ otros parametros)
        Uso: item.fromurl("cadena")
        '''
        if "?" in url: url = url.split("?")[1]
        try:
            STRItem = base64.b64decode(urllib.unquote(url))
            JSONItem = json.loads(STRItem, object_hook=self.toutf8)
            self.__dict__.update(JSONItem)
        except:
            url = urllib.unquote_plus(url)
            dct = dict([[param.split("=")[0], param.split("=")[1]] for param in url.split("&") if "=" in param])
            self.__dict__.update(dct)
            self.__dict__ = self.toutf8(self.__dict__)
        return self

    def tojson(self, path=""):
        '''
        Crea un JSON a partir del item, para guardar archivos de favoritos, lista de descargas, etc...
        Si se especifica un path, te lo guarda en la ruta especificada, si no, devuelve la cadena json
        Usos: item.tojson(path="ruta\archivo\json.json")
              file.write(item.tojson())
        '''
        if path:
            open(path, "wb").write(json.dumps(self.__dict__, indent=4, sort_keys=True))
        else:
            return json.dumps(self.__dict__, indent=4, sort_keys=True)

    def fromjson(self, STRItem={}, path=""):
        '''
        Genera un item a partir de un archivo JSON
        Si se especifica un path, lee directamente el archivo, si no, lee la cadena de texto pasada.
        Usos: item = Item().fromjson(path="ruta\archivo\json.json")
              item = Item().fromjson("Cadena de texto json")
        '''
        if path:
            if os.path.exists(path):
                STRItem = open(path, "rb").read()
            else:
                STRItem = {}

        JSONItem = json.loads(STRItem, object_hook=self.toutf8)
        self.__dict__.update(JSONItem)
        return self

    def clone(self, **kwargs):
        '''
        Genera un nuevo item clonando el item actual
        Usos: NuevoItem = item.clone()
              NuevoItem = item.clone(title="Nuevo Titulo", action = "Nueva Accion")
        '''
        newitem = copy.deepcopy(self)
        newitem.__dict__.update(kwargs)
        newitem.__dict__ = newitem.toutf8(newitem.__dict__)
        return newitem

    def decode_html(self, value):
        '''
        Descodifica las HTML entities
        '''
        try:
            unicode_title = unicode(value, "utf8", "ignore")
            return HTMLParser().unescape(unicode_title).encode("utf8")
        except:
            return value

    def toutf8(self, *args):
        '''
        Pasa el item a utf8
        '''
        if len(args) > 0:
            value = args[0]
        else:
            value = self.__dict__

        if type(value) == unicode:
            return value.encode("utf8")

        elif type(value) == str:
            return unicode(value, "utf8", "ignore").encode("utf8")

        elif type(value) == list:
            for x, key in enumerate(value):
                value[x] = self.toutf8(value[x])
            return value

        elif type(value) == dict:
            newdct = {}
            for key in value:
                if type(key) == unicode:
                    key = key.encode("utf8")

                newdct[key] = self.toutf8(value[key])

            if len(args) > 0: return newdct

        else:
            return value
