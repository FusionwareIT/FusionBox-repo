# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand 4
# Copyright 2015 tvalacarta@gmail.com
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
#------------------------------------------------------------
# This file is part of streamondemand 4.
#
# streamondemand 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# streamondemand 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with streamondemand 4.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------

import base64
import copy
import urllib

from core import jsontools as json


class Item(object):  

    def __contains__(self, m):
        return m in self.__dict__
        
    def __init__(self,  **kwargs):     
        #Campos por defecto de la clase Item
        kwargs.setdefault("channel", "")            #Canal en el que se ejecuta
        kwargs.setdefault("action", "")             #funcion que ejecutará en el canal
        kwargs.setdefault("title", "")              #Nombre para mostrar y nombre de la pelicula
        kwargs.setdefault("fulltitle", "")          #Titulo de la pelicula en caso de ser distinto al del campo "title"
        kwargs.setdefault("show", "")               #Nombre de la serie
        kwargs.setdefault("plot", "")               #Descripción
        kwargs.setdefault("url", "")                #Url
        kwargs.setdefault("thumbnail", "")          #Imagen
        kwargs.setdefault("fanart", "")             #Imagen de Fondo
        kwargs.setdefault("password", "")           #Password del video

        kwargs.setdefault("folder", True)           #Carpeta o vídeo
        kwargs.setdefault("server", "")      #Servidor que contiene el vídeo
        kwargs.setdefault("extra", "")              #Datos extra

        kwargs.setdefault("type", "")              #dentaku65 - needed for biblioteca

        kwargs.setdefault("language", "")           #Idioma del contenido
        kwargs.setdefault("context", "")            #Items para el Menú Contextual
        kwargs.setdefault("subtitle", "")           #Subtitulos
        kwargs.setdefault("duration", 0)            #Duracion de la pelicula
        kwargs.setdefault("category", "")           #Categoria de la pelicula
        
        kwargs.setdefault("viewmode", "list")       #Modo de ventana

        kwargs.setdefault("hasContentDetails", "false")

        kwargs.setdefault("contentChannel", "list") # En qué canal estaba el contenido
        kwargs.setdefault("contentTitle","")
        kwargs.setdefault("contentThumbnail","")
        kwargs.setdefault("contentPlot","")
        kwargs.setdefault("contentType","")
        kwargs.setdefault("contentSerieName","")
        kwargs.setdefault("contentSeason","")
        kwargs.setdefault("contentEpisodeNumber","")
        kwargs.setdefault("contentEpisodeTitle","")

        if kwargs.has_key("parentContent") and kwargs["parentContent"] is not None:

            print "Tiene parentContent: "+repr(kwargs["parentContent"])
            parentContent = kwargs["parentContent"]
            # Removed from dictionary, should not be included
            kwargs.pop("parentContent",None)

        else:
            parentContent = None

        self.__dict__.update(kwargs)
        self.__dict__ = self.toutf8(self.__dict__)

        if parentContent is not None:
            self.contentChannel = parentContent.contentChannel;
            self.contentTitle = parentContent.contentTitle;
            self.contentThumbnail = parentContent.contentThumbnail;
            self.contentPlot = parentContent.contentPlot;

            self.hasContentDetails = parentContent.hasContentDetails;
            self.contentType = parentContent.contentType;
            self.contentSerieName = parentContent.contentSerieName;
            self.contentSeason = parentContent.contentSeason;
            self.contentEpisodeNumber = parentContent.contentEpisodeNumber;
            self.contentEpisodeTitle = parentContent.contentEpisodeTitle;

    def tostring(self):
        '''
        Genera una cadena de texto con los datos del item para el log
        Uso: logger.info(item.tostring())
        '''
        return ", ".join([var + "=["+str(self.__dict__[var])+"]" for var in sorted(self.__dict__)])        
        

    def tourl(self):
        '''
        Genera una cadena de texto con los datos del item para crear una url, para volver generar el Item usar item.fromurl()
        Uso: url = item.tourl()
        '''
        return urllib.quote(base64.b64encode(json.dumps(self.__dict__)))
              

    def fromurl(self,url): 
        '''
        Genera un item a partir de la cadena de texto creada por la funcion tourl()
        Uso: item.fromurl("cadena")
        '''
        STRItem = base64.b64decode(urllib.unquote(url))
        JSONItem = json.loads(STRItem,object_hook=self.toutf8)
        self.__dict__.update(JSONItem)
        return self


    def tojson(self, path=""):
        '''
        Crea un JSON a partir del item, para guardar archivos de favoritos, lista de descargas, etc...
        Si se especifica un path, te lo guarda en la ruta especificada, si no, devuelve la cadena json
        Usos: item.tojson(path="ruta\archivo\json.json")
              file.write(item.tojson())
        '''      
        if path:
          open(path,"wb").write(json.dumps(self.__dict__, indent=4, sort_keys=True))
        else:
          return json.dumps(self.__dict__, indent=4, sort_keys=True)
              

    def fromjson(self,STRItem={}, path=""): 
        '''
        Genera un item a partir de un archivo JSON
        Si se especifica un path, lee directamente el archivo, si no, lee la cadena de texto pasada.
        Usos: item = Item().fromjson(path="ruta\archivo\json.json")
              item = Item().fromjson("Cadena de texto json")
        '''
        if path:
          if os.path.exists(path):
            STRItem = open(path,"rb").read()
          else:
            STRItem = {}
            
        JSONItem = json.loads(STRItem,object_hook=self.toutf8)
        self.__dict__.update(JSONItem)
        return self
          
        
    def clone(self,**kwargs):
        '''
        Genera un nuevo item clonando el item actual
        Usos: NuevoItem = item.clone()
              NuevoItem = item.clone(title="Nuevo Titulo", action = "Nueva Accion")
        '''
        newitem = copy.deepcopy(self)
        newitem.__dict__.update(kwargs)
        newitem.__dict__ = newitem.toutf8(newitem.__dict__)
        return newitem
      

    def toutf8(self, *args):
        if len(args)>0:  value = args[0]
        else: value = self.__dict__
        
        if type(value)== unicode:
            return value.encode("utf8")
          
        elif type(value)== str:
            return unicode(value,"utf8", "ignore").encode("utf8")
          
        elif type(value)== list:
            for x, key in enumerate(value):
                value[x] = self.toutf8(value[x])
            return value
          
        elif type(value)== dict:
            newdct = {}
            for key in value:
                if type(key) == unicode:
                    key = key.encode("utf8")
                  
                newdct[key] = self.toutf8(value[key])

            if len(args)>0: return newdct
        
        else:
            return value
