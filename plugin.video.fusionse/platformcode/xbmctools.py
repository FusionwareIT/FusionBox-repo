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
# ------------------------------------------------------------
# XBMC Tools
#------------------------------------------------------------

import os
import sys
import urllib

import xbmc
import xbmcgui
import xbmcplugin

from core import config
from core import logger
from platformcode import library

# Esto permite su ejecución en modo emulado
try:
    pluginhandle = int( sys.argv[ 1 ] )
except:
    pluginhandle = ""

DEBUG = config.get_setting("debug")

def add_new_folder(item, totalItems=0):
    logger.info('fusionse.platformcode.xbmctools add_new_folder item='+item.tostring())

    if item.fulltitle=="":
        item.fulltitle=item.title

    contextCommands = []
    ok = False
    
    try:
        item.context = urllib.unquote_plus(item.context)
    except:
        item.context = ""
    
    if "|" in item.context:
        item.context = item.context.split("|")

    listitem = xbmcgui.ListItem( item.title, iconImage="DefaultFolder.png", thumbnailImage=item.thumbnail )

    if item.action !="":
        set_infoLabels(listitem,item)
    
    if item.fanart!="":
        listitem.setProperty('fanart_image',item.fanart) 
        xbmcplugin.setPluginFanart(pluginhandle, item.fanart)

    try:
        item.title = item.title.encode("utf-8") #This only aplies to unicode strings. The rest stay as they are.
    except:
        pass
    
    itemurl = '%s?%s' % ( sys.argv[ 0 ] , item.tourl())
    logger.info("fusionse.platformcode.xbmctools add_new_folder itemurl="+itemurl)

    #if item.show != "": #Añadimos opción contextual para Añadir la serie completa a la biblioteca
    #    addSerieCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(action="addlist2Library").tourl())
    #    contextCommands.append(("Añadir Serie a Biblioteca",addSerieCommand))
    if "menu filtro" in item.context:
        filter_serie_command = "XBMC.RunPlugin(%s?%s)" % \
                               (sys.argv[0], item.clone(channel="filtertools", action="config_filter",
                                                        from_channel=item.channel).tourl())
        contextCommands.append(("Menu Filtro", filter_serie_command))

    if "guardar filtro" in item.context:
        filter_serie_command = "XBMC.RunPlugin(%s%s)" % \
                               (sys.argv[0], item.clone(channel="filtertools", action="save_filter",
                                                        from_channel=item.channel).tourl())
        contextCommands.append(("Salva filtro", filter_serie_command))

    if "borrar filtro" in item.context:
        filter_serie_command = "XBMC.Container.Update(%s%s)" % \
                               (sys.argv[0], item.clone(channel="filtertools", action="del_filter",
                                                        from_channel=item.channel).tourl())
        contextCommands.append(("Elimina filtro", filter_serie_command))

    if "1" in item.context and accion != "por_teclado":
        DeleteCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="buscador", action="borrar_busqueda").tourl())
    if "4" in item.context:
        searchSubtitleCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="subtitletools", action="searchSubtitle").tourl())
    if "5" in item.context:
        trailerCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="trailertools", action="buscartrailer", contextual=True).tourl())
        contextCommands.append(("Buscar Trailer", trailerCommand))
    if config.get_platform()=="boxee":
        #logger.info("Modo boxee")
        ok = xbmcplugin.addDirectoryItem( handle = pluginhandle, url = itemurl , listitem=listitem, isFolder=True)
    else:
        #logger.info("Modo xbmc")
        if len(contextCommands) > 0:
            listitem.addContextMenuItems ( contextCommands, replaceItems=False)
        if item.action == "":
            listitem.addContextMenuItems ( list(), replaceItems=True)
            
        if item.totalItems == 0:
            ok = xbmcplugin.addDirectoryItem( handle = pluginhandle, url = itemurl , listitem=listitem, isFolder=True)
        else:
            ok = xbmcplugin.addDirectoryItem( handle = pluginhandle, url = itemurl , listitem=listitem, isFolder=True, totalItems=item.totalItems)
    return ok

def add_new_video(item, IsPlayable='false', totalItems = 0):
    logger.info('fusionse.platformcode.xbmctools add_new_video item='+item.tostring())

    # TODO: Posible error en trailertools.py
    contextCommands = []
    ok = False

    try:
        item.context = urllib.unquote_plus(item.context)
    except:
        item.context=""

    if "|" in item.context:
        item.context = item.context.split("|")

    icon_image = os.path.join( config.get_runtime_path() , "resources" , "images" , "servers" , item.server+".png" )
    if not os.path.exists(icon_image):
        icon_image = "DefaultVideo.png"

    listitem = xbmcgui.ListItem( item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail )

    if item.action !="":
        set_infoLabels(listitem,item)
   
    if item.fanart!="":
        #logger.info("item.fanart :%s" %item.fanart)
        listitem.setProperty('fanart_image',item.fanart)
        xbmcplugin.setPluginFanart(pluginhandle, item.fanart)

    if item.isPlayable == 'true': #Esta opcion es para poder utilizar el xbmcplugin.setResolvedUrl()
        listitem.setProperty('IsPlayable', 'true')

    if len (contextCommands) > 0:
        listitem.addContextMenuItems ( contextCommands, replaceItems=False)
    
    if item.action == "":
        listitem.addContextMenuItems ( list(), replaceItems=True)
    
    try:
        item.title = item.title.encode ("utf-8")     #This only aplies to unicode strings. The rest stay as they are.
        item.plot  = item.plot.encode ("utf-8")
    except:
        pass

    itemurl = '%s?%s' % ( sys.argv[ 0 ] , item.tourl())
    logger.info("fusionse.platformcode.xbmctools add_new_video itemurl="+itemurl)

    if item.totalItems == 0:
        ok = xbmcplugin.addDirectoryItem( handle = pluginhandle, url=itemurl, listitem=listitem, isFolder=False)
    else:
        ok = xbmcplugin.addDirectoryItem( handle = pluginhandle, url=itemurl, listitem=listitem, isFolder=False, totalItems=item.totalItems)
    return ok

def play_video(item,desdefavoritos=False,desdedescargados=False,desderrordescargas=False,strmfile=False):
    from core import servertools
    
    logger.info("fusionse.platformcode.xbmctools play_video")
    #logger.info(item.tostring('\n'))

    try:
        item.server = item.server.lower()
    except:
        item.server = ""

    if item.server=="":
        item.server="directo"

    view = False
    # Abre el diálogo de selección
    opciones = []
    default_action = config.get_setting("default_action")
    logger.info("default_action="+default_action)

    # Si no es el modo normal, no muestra el diálogo porque cuelga XBMC
    muestra_dialogo = (config.get_setting("player_mode")=="0" and not strmfile)

    # Extrae las URL de los vídeos, y si no puedes verlo te dice el motivo
    video_urls,puedes,motivo = servertools.resolve_video_urls_for_playing(item.server,item.url,item.password,muestra_dialogo)

    # Si puedes ver el vídeo, presenta las opciones
    if puedes:
        
        for video_url in video_urls:
            opciones.append(config.get_localized_string(30151) + " " + video_url[0])

        if item.server=="local":
            opciones.append(config.get_localized_string(30164))
        else:
            opcion = config.get_localized_string(30153)
            opciones.append(opcion) # "Descargar"
    
            if item.channel=="favoritos": 
                opciones.append(config.get_localized_string(30154)) # "Quitar de favoritos"
            else:
                opciones.append(config.get_localized_string(30155)) # "Añadir a favoritos"
        
            if not strmfile:
                opciones.append(config.get_localized_string(30161)) # "Añadir a Biblioteca"
        
            if item.channel!="descargas":
                opciones.append(config.get_localized_string(30157)) # "Añadir a lista de descargas"
            else:
                if item.category=="errores":
                    opciones.append(config.get_localized_string(30159)) # "Borrar descarga definitivamente"
                    opciones.append(config.get_localized_string(30160)) # "Pasar de nuevo a lista de descargas"
                else:
                    opciones.append(config.get_localized_string(30156)) # "Quitar de lista de descargas"

            if config.get_setting("jdownloader_enabled")=="true":
                opciones.append(config.get_localized_string(30158)) # "Enviar a JDownloader"

        if default_action=="3":
            seleccion = len(opciones)-1
    
        # Busqueda de trailers en youtube    
        if not item.channel in ["Trailer","ecarteleratrailers"]:
            opciones.append(config.get_localized_string(30162)) # "Buscar Trailer"

    # Si no puedes ver el vídeo te informa
    else:
        if item.server!="":
            advertencia = xbmcgui.Dialog()
            if "<br/>" in motivo:
                resultado = advertencia.ok("Non è possibile guardare il video perché...", motivo.split("<br/>")[0],
                                           motivo.split("<br/>")[1], item.url)
            else:
                resultado = advertencia.ok("Non è possibile guardare il video perché...", motivo, item.url)
        else:
            resultado = advertencia.ok("Non è possibile guardare il video perché...", "Il server che lo ospita non è",
                                       "ancora supportato da fusionse", item.url)

        if item.channel=="favoritos": 
            opciones.append(config.get_localized_string(30154)) # "Quitar de favoritos"

        if item.channel=="descargas":
            if item.category=="errores":
                opciones.append(config.get_localized_string(30159)) # "Borrar descarga definitivamente"
            else:
                opciones.append(config.get_localized_string(30156)) # "Quitar de lista de descargas"
        
        if len(opciones)==0:
            return

    # Si la accion por defecto es "Preguntar", pregunta
    if default_action=="0": # and server!="torrent":
        dia = xbmcgui.Dialog()
        seleccion = dia.select(config.get_localized_string(30163), opciones) # "Elige una opción"
        #dia.close()
        '''
        elif default_action=="0" and server=="torrent":
            advertencia = xbmcgui.Dialog()
            logger.info("video_urls[0]="+str(video_urls[0][1]))
            if puedes and ('"status":"COMPLETED"' in video_urls[0][1] or '"percent_done":100' in video_urls[0][1]):
                listo  = "y está listo para ver"
            else:
                listo = "y se está descargando"
            resultado = advertencia.ok( "Torrent" , "El torrent ha sido añadido a la lista" , listo )
            seleccion=-1
        '''
    elif default_action=="1":
        seleccion = 0
    elif default_action=="2":
        seleccion = len(video_urls)-1
    elif default_action=="3":
        seleccion = seleccion
    else:
        seleccion=0

    logger.info("seleccion=%d" % seleccion)
    logger.info("seleccion=%s" % opciones[seleccion])

    # No ha elegido nada, lo más probable porque haya dado al ESC 
    if seleccion==-1:
        #Para evitar el error "Uno o más elementos fallaron" al cancelar la selección desde fichero strm
        listitem = xbmcgui.ListItem( item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail)
        xbmcplugin.setResolvedUrl(int(sys.argv[ 1 ]),False,listitem)    # JUR Added
        #if config.get_setting("subtitulo") == "true":
        #    config.set_setting("subtitulo", "false")
        return

    if opciones[seleccion]==config.get_localized_string(30158): # "Enviar a JDownloader"
        #d = {"web": url}urllib.urlencode(d)
        from core import scrapertools
        
        if item.subtitle!="":
            data = scrapertools.cachePage(config.get_setting("jdownloader")+"/action/add/links/grabber0/start1/web="+item.url+ " " +item.thumbnail + " " + item.subtitle)
        else:
            data = scrapertools.cachePage(config.get_setting("jdownloader")+"/action/add/links/grabber0/start1/web="+item.url+ " " +item.thumbnail)

        return

    if opciones[seleccion]==config.get_localized_string(30158).replace("jDownloader","pyLoad"): # "Enviar a pyLoad"
        logger.info("Enviando a pyload...")

        if item.show!="":
            package_name = item.show
        else:
            package_name = "fusionse"

        from core import pyload_client
        pyload_client.download(url=item.url,package_name=package_name)
        return

    elif opciones[seleccion]==config.get_localized_string(30164): # Borrar archivo en descargas
        # En "extra" está el nombre del fichero en favoritos
        os.remove( item.url )
        xbmc.executebuiltin( "Container.Refresh" )
        return

    # Ha elegido uno de los vídeos
    elif seleccion < len(video_urls):
        mediaurl = video_urls[seleccion][1]
        if len(video_urls[seleccion])>3:
            wait_time = video_urls[seleccion][2]
            item.subtitle = video_urls[seleccion][3]
        elif len(video_urls[seleccion])>2:
            wait_time = video_urls[seleccion][2]
        else:
            wait_time = 0
        view = True

    # Descargar
    elif opciones[seleccion]==config.get_localized_string(30153): # "Descargar"

        download_title = item.fulltitle
        if item.hasContentDetails=="true":
            download_title = item.contentTitle

        # El vídeo de más calidad es el último
        mediaurl = video_urls[len(video_urls)-1][1]

        from core import downloadtools
        keyboard = xbmc.Keyboard(download_title)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            download_title = keyboard.getText()
            devuelve = downloadtools.downloadbest(video_urls,download_title)
            
            if devuelve==0:
                advertencia = xbmcgui.Dialog()
                resultado = advertencia.ok("Download", "Scaricato con successo")
            elif devuelve==-1:
                advertencia = xbmcgui.Dialog()
                resultado = advertencia.ok("Download", "Download interrotto")
            else:
                advertencia = xbmcgui.Dialog()
                resultado = advertencia.ok("Download", "Errore nel download")
        return

    elif opciones[seleccion]==config.get_localized_string(30154): #"Quitar de favoritos"
        from channels import favoritos
        # En "extra" está el nombre del fichero en favoritos
        favoritos.deletebookmark(urllib.unquote_plus( item.extra ))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30102) , item.title , config.get_localized_string(30105)) # 'Se ha quitado de favoritos'

        xbmc.executebuiltin( "Container.Refresh" )
        return

    elif opciones[seleccion]==config.get_localized_string(30159): #"Borrar descarga definitivamente"
        from channels import descargas
        descargas.delete_error_bookmark(urllib.unquote_plus( item.extra ))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30106)) # 'Se ha quitado de la lista'
        xbmc.executebuiltin( "Container.Refresh" )
        return

    elif opciones[seleccion]==config.get_localized_string(30160): #"Pasar de nuevo a lista de descargas":
        from channels import descargas
        descargas.mover_descarga_error_a_pendiente(urllib.unquote_plus( item.extra ))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30107)) # 'Ha pasado de nuevo a la lista de descargas'
        return

    elif opciones[seleccion]==config.get_localized_string(30155): #"Añadir a favoritos":
        from channels import favoritos
        from core import downloadtools

        download_title = item.fulltitle
        download_thumbnail = item.thumbnail
        download_plot = item.plot

        if item.hasContentDetails=="true":
            download_title = item.contentTitle
            download_thumbnail = item.contentThumbnail
            download_plot = item.contentPlot

        keyboard = xbmc.Keyboard(downloadtools.limpia_nombre_excepto_1(download_title)+" ["+item.channel+"]")
        keyboard.doModal()
        if keyboard.isConfirmed():
            title = keyboard.getText()
            favoritos.savebookmark(titulo=title,url=item.url,thumbnail=download_thumbnail,server=item.server,plot=download_plot,fulltitle=title)
            advertencia = xbmcgui.Dialog()
            resultado = advertencia.ok(config.get_localized_string(30102) , title , config.get_localized_string(30108)) # 'se ha añadido a favoritos'
        return

    elif opciones[seleccion]==config.get_localized_string(30156): #"Quitar de lista de descargas":
        # La categoría es el nombre del fichero en la lista de descargas
        from channels import descargas
        descargas.deletebookmark((urllib.unquote_plus( item.extra )))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30106)) # 'Se ha quitado de lista de descargas'

        xbmc.executebuiltin( "Container.Refresh" )
        return

    elif opciones[seleccion]==config.get_localized_string(30157): #"Añadir a lista de descargas":
        from core import downloadtools

        download_title = item.fulltitle
        download_thumbnail = item.thumbnail
        download_plot = item.plot

        if item.hasContentDetails=="true":
            download_title = item.contentTitle
            download_thumbnail = item.contentThumbnail
            download_plot = item.contentPlot

        keyboard = xbmc.Keyboard(downloadtools.limpia_nombre_excepto_1(download_title))
        keyboard.doModal()
        if keyboard.isConfirmed():
            download_title = keyboard.getText()

            from channels import descargas
            descargas.savebookmark(titulo=download_title,url=item.url,thumbnail=download_thumbnail,server=item.server,plot=download_plot,fulltitle=download_title)

            advertencia = xbmcgui.Dialog()
            resultado = advertencia.ok(config.get_localized_string(30101) , download_title , config.get_localized_string(30109)) # 'se ha añadido a la lista de descargas'
        return

    elif opciones[seleccion] == config.get_localized_string(30161):  # "Añadir a Biblioteca":  # Library

        titulo = item.fulltitle
        if titulo == "":
            titulo = item.title
        #library.savelibrary(titulo,item.url,item.thumbnail,item.server,item.plot,canal=item.channel,category=item.category,Serie=item.show)
        # TODO ¿SOLO peliculas?
        #logger.debug(item.tostring('\n'))
        new_item = item.clone(title=titulo, action="play_from_library", category="Cine",
                              fulltitle=item.fulltitle, channel=item.channel)
        #logger.debug(new_item.tostring('\n'))
        insertados, sobreescritos, fallidos = library.save_library_movie(new_item)

        advertencia = xbmcgui.Dialog()
        if fallidos == 0:
            advertencia.ok(config.get_localized_string(30131), titulo,
                           config.get_localized_string(30135))  # 'se ha añadido a la biblioteca'
        return

    elif opciones[seleccion]==config.get_localized_string(30162): #"Buscar Trailer":
        config.set_setting("subtitulo", "false")
        xbmc.executebuiltin("XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="trailertools", action="buscartrailer", contextual=True).tourl()))
        return

    # Si no hay mediaurl es porque el vídeo no está :)
    logger.info("fusionse.platformcode.xbmctools mediaurl="+mediaurl)
    if mediaurl=="":
        if server == "unknown":
            alertUnsopportedServer()
        else:
            alertnodisponibleserver(item.server)
        return

    # Si hay un tiempo de espera (como en megaupload), lo impone ahora
    if wait_time>0:
        continuar = handle_wait(wait_time,server,"Cargando vídeo...")
        if not continuar:
            return

    # Obtención datos de la Biblioteca (solo strms que estén en la biblioteca)
    if strmfile:
        xlistitem = getLibraryInfo(mediaurl)
    else:
        play_title = item.fulltitle
        play_thumbnail = item.thumbnail
        play_plot = item.plot

        if item.hasContentDetails=="true":
            play_title = item.contentTitle
            play_thumbnail = item.contentThumbnail
            play_plot = item.contentPlot

        try:
            xlistitem = xbmcgui.ListItem( play_title, iconImage="DefaultVideo.png", thumbnailImage=play_thumbnail, path=mediaurl)
        except:
            xlistitem = xbmcgui.ListItem( play_title, iconImage="DefaultVideo.png", thumbnailImage=play_thumbnail)

        xlistitem.setInfo( "video", { "Title": play_title, "Plot" : play_plot , "Studio" : item.channel , "Genre" : item.category } )

        #set_infoLabels(listitem,plot) # Modificacion introducida por super_berny para añadir infoLabels al ListItem

    # Lanza el reproductor
        # Lanza el reproductor

    if strmfile and not item.from_biblioteca: #Si es un fichero strm no hace falta el play
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xlistitem)
        if item.subtitle != "":
            xbmc.sleep(2000)
            xbmc.Player().setSubtitles(item.subtitle)

    #Movido del conector "torrent" aqui
    elif item.server=="torrent":

        #Opciones disponibles para Reproducir torrents
        torrent_options = []
        torrent_options.append(["Client  (necessario libtorrent)"])
        torrent_options.append(["Client interno MCT (necessario libtorrent)"])

        #Plugins externos se pueden añadir otros
        if xbmc.getCondVisibility('System.HasAddon("plugin.video.xbmctorrent")'):
            torrent_options.append(["Plugin esterno: xbmctorrent","plugin://plugin.video.xbmctorrent/play/%s"])
        if xbmc.getCondVisibility('System.HasAddon("plugin.video.pulsar")'):
            torrent_options.append(["Plugin esterno: pulsar","plugin://plugin.video.pulsar/play?uri=%s"])
        if xbmc.getCondVisibility('System.HasAddon("plugin.video.quasar")'):
            torrent_options.append(["Plugin esterno: quasar","plugin://plugin.video.quasar/play?uri=%s"])
        if xbmc.getCondVisibility('System.HasAddon("plugin.video.stream")'):
            torrent_options.append(["Plugin esterno: stream","plugin://plugin.video.stream/play/%s"])
        if xbmc.getCondVisibility('System.HasAddon("plugin.video.torrenter")'):
            torrent_options.append(["Plugin esterno: torrenter","plugin://plugin.video.torrenter/?action=playSTRM&url=%s"])
        if xbmc.getCondVisibility('System.HasAddon("plugin.video.torrentin")'):
            torrent_options.append(["Plugin esterno: torrentin","plugin://plugin.video.torrentin/?uri=%s&image="])


        if len(torrent_options)>1:
            seleccion = xbmcgui.Dialog().select("Aprire torrent con...", [opcion[0] for opcion in torrent_options])
        else:
            seleccion = 0

        #Plugins externos
        if seleccion > 1:
            mediaurl = urllib.quote_plus(item.url)
            xbmc.executebuiltin( "PlayMedia(" + torrent_options[seleccion][1] % mediaurl +")" )

        if seleccion ==1:
            from platformcode import mct
            mct.play( mediaurl, xbmcgui.ListItem("", iconImage=item.thumbnail, thumbnailImage=item.thumbnail), subtitle=item.subtitle )

        #Reproductor propio (libtorrent)
        if seleccion == 0:
            import time
            videourl = None
            played = False
  
            #Importamos el cliente
            from btserver import Client
  
            #Iniciamos el cliente:
            c = Client(url=mediaurl, is_playing_fnc= xbmc.Player().isPlaying, wait_time=None, timeout=5, temp_path =os.path.join(config.get_data_path(),"torrent") )
  
            #Mostramos el progreso
            progreso = xbmcgui.DialogProgress()
            progreso.create( "fusionse - Torrent" , "Avviando...")
  
  
            #Mientras el progreso no sea cancelado ni el cliente cerrado
            while not progreso.iscanceled() and not c.closed:
  
                try:
                    #Obtenemos el estado del torrent
                    s = c.status
      
                    #Montamos las tres lineas con la info del torrent
                    txt = '%.2f%% de %.1fMB %s | %.1f kB/s' % \
                    (s.progress_file, s.file_size, s.str_state, s._download_rate)
                    txt2 =  'S: %d(%d) P: %d(%d) | DHT:%s (%d) | Trakers: %d' % \
                    (s.num_seeds, s.num_complete, s.num_peers, s.num_incomplete, s.dht_state, s.dht_nodes, s.trackers)
                    txt3 = 'Origen Peers TRK: %d DHT: %d PEX: %d LSD %d ' % \
                    (s.trk_peers,s.dht_peers, s.pex_peers, s.lsd_peers)
      
                    progreso.update(s.buffer,txt, txt2, txt3)
      
      
                    time.sleep(1)
      
                    #Si el buffer se ha llenado y la reproduccion no ha sido iniciada, se inicia
                    if s.buffer == 100 and not played:
      
                        #Cerramos el progreso
                        progreso.close()
        
                        #Obtenemos el playlist del torrent
                        videourl = c.get_play_list()
        
                        #Iniciamos el reproductor
                        playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
                        playlist.clear()
                        playlist.add( videourl, xlistitem )
                        xbmcPlayer = xbmc.Player()
                        xbmcPlayer.play(playlist)
        
                        #Marcamos como reproducido para que no se vuelva a iniciar
                        played = True
        
                        #Y esperamos a que el reproductor se cierre
                        while xbmc.Player().isPlaying():
                          time.sleep(1)
        
                        #Cuando este cerrado,  Volvemos a mostrar el dialogo
                        progreso.create( "fusionse - Torrent" , "Avviando...")
      
                except:
                    import traceback
                    logger.info(traceback.format_exc())
                    break

            progreso.update(100,"Terminato, elimina dati"," "," ")

            #Detenemos el cliente
            if not c.closed:
                c.stop()

            #Y cerramos el progreso
            progreso.close()

            return

    else:
        logger.info("player_mode="+config.get_setting("player_mode"))
        logger.info("mediaurl="+mediaurl)
        if config.get_setting("player_mode")=="3" or "megacrypter.com" in mediaurl:
            import download_and_play
            download_and_play.download_and_play( mediaurl , "download_and_play.tmp" , config.get_setting("downloadpath") )
            return

        elif config.get_setting("player_mode")=="0" or (config.get_setting("player_mode")=="3" and mediaurl.startswith("rtmp")):
            # Añadimos el listitem a una lista de reproducción (playlist)
            playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            playlist.clear()
            playlist.add( mediaurl, xlistitem )

            # Reproduce
            playersettings = config.get_setting('player_type')
            logger.info("fusionse.platformcode.xbmctools playersettings="+playersettings)

            if config.get_system_platform()=="xbox":
                player_type = xbmc.PLAYER_CORE_AUTO
                if playersettings == "0":
                    player_type = xbmc.PLAYER_CORE_AUTO
                    logger.info("fusionse.platformcode.xbmctools PLAYER_CORE_AUTO")
                elif playersettings == "1":
                    player_type = xbmc.PLAYER_CORE_MPLAYER
                    logger.info("fusionse.platformcode.xbmctools PLAYER_CORE_MPLAYER")
                elif playersettings == "2":
                    player_type = xbmc.PLAYER_CORE_DVDPLAYER
                    logger.info("fusionse.platformcode.xbmctools PLAYER_CORE_DVDPLAYER")

                xbmcPlayer = xbmc.Player( player_type )
            else:
                xbmcPlayer = xbmc.Player()

            xbmcPlayer.play(playlist)

            if item.channel=="cuevana" and item.subtitle!="":
                logger.info("subtitulo="+subtitle)
                if item.subtitle!="" and (opciones[seleccion].startswith("Ver") or opciones[seleccion].startswith("Watch")):
                    logger.info("fusionse.platformcode.xbmctools Con subtitulos")
                    setSubtitles()

        elif config.get_setting("player_mode")=="1":
            logger.info("mediaurl :"+ mediaurl)
            logger.info("Tras setResolvedUrl")
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=mediaurl))

        elif config.get_setting("player_mode")=="2":
            xbmc.executebuiltin( "PlayMedia("+mediaurl+")" )

    if item.subtitle!="" and view:
        logger.info("Subtítulos externos: "+item.subtitle)
        xbmc.Player().setSubtitles(item.subtitle)

def handle_wait(time_to_wait,title,text):
    logger.info ("[xbmctools.py] handle_wait(time_to_wait=%d)" % time_to_wait)
    espera = xbmcgui.DialogProgress()
    ret = espera.create(' '+title)

    secs=0
    percent=0
    increment = int(100 / time_to_wait)

    cancelled = False
    while secs < time_to_wait:
        secs = secs + 1
        percent = increment*secs
        secs_left = str((time_to_wait - secs))
        remaining_display = ' Attendi ' + secs_left + ' secondi per il video...'
        espera.update(percent,' '+text,remaining_display)
        xbmc.sleep(1000)
        if (espera.iscanceled()):
             cancelled = True
             break

    if cancelled:
        logger.info('Attesa eliminata')
        return False
    else:
        logger.info('Attesa conclusa')
        return True

def getLibraryInfo (mediaurl):
    '''Obtiene información de la Biblioteca si existe (ficheros strm) o de los parámetros
    '''
    if DEBUG:
        logger.info('fusionse.platformcode.xbmctools playlist OBTENCIÓN DE DATOS DE BIBLIOTECA')

    # Información básica
    label = xbmc.getInfoLabel( 'listitem.label' )
    label2 = xbmc.getInfoLabel( 'listitem.label2' )
    iconImage = xbmc.getInfoImage( 'listitem.icon' )
    thumbnailImage = xbmc.getInfoImage( 'listitem.Thumb' ) #xbmc.getInfoLabel( 'listitem.thumbnailImage' )
    if DEBUG:
        logger.info ("[xbmctools.py]getMediaInfo: label = " + label)
        logger.info ("[xbmctools.py]getMediaInfo: label2 = " + label2)
        logger.info ("[xbmctools.py]getMediaInfo: iconImage = " + iconImage)
        logger.info ("[xbmctools.py]getMediaInfo: thumbnailImage = " + thumbnailImage)

    # Creación de listitem
    listitem = xbmcgui.ListItem(label, label2, iconImage, thumbnailImage, mediaurl)

    # Información adicional
    lista = [
        ('listitem.genre', 's'),            #(Comedy)
        ('listitem.year', 'i'),             #(2009)
        ('listitem.episode', 'i'),          #(4)
        ('listitem.season', 'i'),           #(1)
        ('listitem.top250', 'i'),           #(192)
        ('listitem.tracknumber', 'i'),      #(3)
        ('listitem.rating', 'f'),           #(6.4) - range is 0..10
#        ('listitem.watched', 'd'),          # depreciated. use playcount instead
        ('listitem.playcount', 'i'),        #(2) - number of times this item has been played
#        ('listitem.overlay', 'i'),          #(2) - range is 0..8.  See GUIListItem.h for values
        ('listitem.overlay', 's'),          #JUR - listitem devuelve un string, pero addinfo espera un int. Ver traducción más abajo
        #('listitem.cast', 's'),             # (Michal C. Hall) - List concatenated into a string
        #('listitem.castandrole', 's'),      #(Michael C. Hall|Dexter) - List concatenated into a string
        ('listitem.director', 's'),         #(Dagur Kari)
        ('listitem.mpaa', 's'),             #(PG-13)
        ('listitem.plot', 's'),             #(Long Description)
        ('listitem.plotoutline', 's'),      #(Short Description)
        ('listitem.title', 's'),            #(Big Fan)
        ('listitem.duration', 's'),         #(3)
        ('listitem.studio', 's'),           #(Warner Bros.)
        ('listitem.tagline', 's'),          #(An awesome movie) - short description of movie
        ('listitem.writer', 's'),           #(Robert D. Siegel)
        ('listitem.tvshowtitle', 's'),      #(Heroes)
        ('listitem.premiered', 's'),        #(2005-03-04)
        ('listitem.status', 's'),           #(Continuing) - status of a TVshow
        ('listitem.code', 's'),             #(tt0110293) - IMDb code
        ('listitem.aired', 's'),            #(2008-12-07)
        ('listitem.credits', 's'),          #(Andy Kaufman) - writing credits
        ('listitem.lastplayed', 's'),       #(%Y-%m-%d %h
        ('listitem.album', 's'),            #(The Joshua Tree)
        ('listitem.votes', 's'),            #(12345 votes)
        ('listitem.trailer', 's'),          #(/home/user/trailer.avi)
    ]
    # Obtenemos toda la info disponible y la metemos en un diccionario
    # para la función setInfo.
    infodict = dict()
    for label,tipo in lista:
        key = label.split('.',1)[1]
        value = xbmc.getInfoLabel( label )
        if value != "":
            if DEBUG:
                logger.info ("[xbmctools.py]getMediaInfo: "+key+" = " + value) #infoimage=infolabel
            if tipo == 's':
                infodict[key]=value
            elif tipo == 'i':
                infodict[key]=int(value)
            elif tipo == 'f':
                infodict[key]=float(value)

    #Transforma el valor de overlay de string a int.
    if infodict.has_key('overlay'):
        value = infodict['overlay'].lower()
        if value.find('rar') > -1:
            infodict['overlay'] = 1
        elif value.find('zip')> -1:
            infodict['overlay'] = 2
        elif value.find('trained')> -1:
            infodict['overlay'] = 3
        elif value.find('hastrainer')> -1:
            infodict['overlay'] = 4
        elif value.find('locked')> -1:
            infodict['overlay'] = 5
        elif value.find('unwatched')> -1:
            infodict['overlay'] = 6
        elif value.find('watched')> -1:
            infodict['overlay'] = 7
        elif value.find('hd')> -1:
            infodict['overlay'] = 8
        else:
            infodict.pop('overlay')
    if len (infodict) > 0:
        listitem.setInfo( "video", infodict )

    return listitem

def alertnodisponible():
    advertencia = xbmcgui.Dialog()
    #'Vídeo no disponible'
    #'No se han podido localizar videos en la página del canal'
    resultado = advertencia.ok(config.get_localized_string(30055) , config.get_localized_string(30056))

def alertnodisponibleserver(server):
    advertencia = xbmcgui.Dialog()
    # 'El vídeo ya no está en %s' , 'Prueba en otro servidor o en otro canal'
    resultado = advertencia.ok( config.get_localized_string(30055),(config.get_localized_string(30057)%server),config.get_localized_string(30058))

def alertUnsopportedServer():
    advertencia = xbmcgui.Dialog()
    # 'Servidor no soportado o desconocido' , 'Prueba en otro servidor o en otro canal'
    resultado = advertencia.ok( config.get_localized_string(30065),config.get_localized_string(30058))

def alerterrorpagina():
    advertencia = xbmcgui.Dialog()
    #'Error en el sitio web'
    #'No se puede acceder por un error en el sitio web'
    resultado = advertencia.ok(config.get_localized_string(30059) , config.get_localized_string(30060))

def alertanomegauploadlow(server):
    advertencia = xbmcgui.Dialog()
    #'La calidad elegida no esta disponible', 'o el video ha sido borrado',
    #'Prueba a reproducir en otra calidad'
    resultado = advertencia.ok( config.get_localized_string(30055) , config.get_localized_string(30061) , config.get_localized_string(30062))

# AÑADIDO POR JUR. SOPORTE DE FICHEROS STRM
def playstrm(params,url,category):
    '''Play para videos en ficheros strm
    '''
    logger.info("fusionse.platformcode.xbmctools playstrm url="+url)

    title = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "utf-8" )
    thumbnail = urllib.unquote_plus( params.get("thumbnail") )
    plot = unicode( xbmc.getInfoLabel( "ListItem.Plot" ), "utf-8" )
    server = params["server"]
    if (params.has_key("Serie")):
        serie = params.get("Serie")
    else:
        serie = ""
    if (params.has_key("subtitle")):
        subtitle = params.get("subtitle")
    else:
        subtitle = ""
    from core.item import Item
    from platformcode.subtitletools import saveSubtitleName
    item = Item(title=title,show=serie)
    saveSubtitleName(item)
    play_video("Biblioteca fusionse",server,url,category,title,thumbnail,plot,strmfile=True,Serie=serie,subtitle=subtitle)

def renderItems(itemlist, parentitem, isPlayable='false'):
    logger.info("fusionse.platformcode.xbmctools renderItems")

    viewmode = "list"

    if itemlist <> None:
        for item in itemlist:
            logger.info("item="+item.tostring())
            item.totalItems = len(itemlist)
            item.isPlayable = isPlayable

            if item.category == "":
                item.category = parentitem.category

            if item.fulltitle=="":
                item.fulltitle=item.title

            if item.fanart=="":
                channel_fanart = os.path.join( config.get_runtime_path(), 'resources', 'images', 'fanart', item.channel+'.jpg')

                if os.path.exists(channel_fanart):
                    item.fanart = channel_fanart
                else:
                    item.fanart = os.path.join(config.get_runtime_path(),"fanart.jpg")

            # Formatear titulo
            if 'text_color' in item and item.text_color:
                item.title= '[COLOR %s]%s[/COLOR]' %(item.text_color, item.title)
            if 'text_blod' in item and item.text_blod:
                item.title= '[B]%s[/B]' %(item.title)
            if 'text_italic' in item and item.text_italic:
                item.title= '[I]%s[/I]' %(item.title)

            if item.folder:
                add_new_folder(item, totalItems = len(itemlist))
            else:
                if config.get_setting("player_mode")=="1": # SetResolvedUrl debe ser siempre "isPlayable = true"
                    item.isPlayable = 'true'
                
                add_new_video( item, IsPlayable=item.isPlayable, totalItems = len(itemlist))

            if item.viewmode!="list":
                viewmode = item.viewmode
        viewmode = parentitem.viewmode
        # Cierra el directorio
        # if not parentitem.channel in ["channelselector",""]:
        # xbmcplugin.setContent(pluginhandle,"Movies")
        xbmcplugin.setPluginCategory( handle=pluginhandle, category=parentitem.category )
        xbmcplugin.addSortMethod( handle=pluginhandle, sortMethod=xbmcplugin.SORT_METHOD_NONE )

        # Modos biblioteca
        # MediaInfo3 - 503
        #
        # Modos fichero
        # WideIconView - 505
        # ThumbnailView - 500

        if config.get_setting("forceview")=="true":
            if viewmode=="list":
                xbmc.executebuiltin("Container.SetViewMode(50)")
            elif viewmode=="movie_with_plot":
                xbmc.executebuiltin("Container.SetViewMode(503)")
            elif viewmode=="movie":
                xbmc.executebuiltin("Container.SetViewMode(500)")

    xbmcplugin.endOfDirectory( handle=pluginhandle, succeeded=True )

def wait2second():
    logger.info("fusionse.platformcode.xbmctools wait2second")
    import time
    contador = 0
    while xbmc.Player().isPlayingVideo()==False:
        logger.info("fusionse.platformcode.xbmctools setSubtitles: Waiting 2 seconds for video to start before setting subtitles")
        time.sleep(2)
        contador = contador + 1

        if contador>10:
            break

def setSubtitles():
    logger.info("fusionse.platformcode.xbmctools setSubtitles")
    import time
    contador = 0
    while xbmc.Player().isPlayingVideo()==False:
        logger.info("fusionse.platformcode.xbmctools setSubtitles: Waiting 2 seconds for video to start before setting subtitles")
        time.sleep(2)
        contador = contador + 1

        if contador>10:
            break

    subtitlefile = os.path.join( config.get_data_path(), 'subtitulo.srt' )
    logger.info("fusionse.platformcode.xbmctools setting subtitle file %s" % subtitlefile)
    xbmc.Player().setSubtitles(subtitlefile)

def trailer(item):
    logger.info("fusionse.platformcode.xbmctools trailer")
    config.set_setting("subtitulo", "false")
    xbmc.executebuiltin("XBMC.RunPlugin(%s?channel=%s&action=%s&category=%s&title=%s&url=%s&thumbnail=%s&plot=%s&server=%s)" % ( sys.argv[ 0 ] , "trailertools" , "buscartrailer" , urllib.quote_plus( item.category ) , urllib.quote_plus( item.fulltitle ) , urllib.quote_plus( item.url ) , urllib.quote_plus( item.thumbnail ) , urllib.quote_plus( "" ) ))
    return

def alert_no_puedes_ver_video(server,url,motivo):

    if server!="":
        advertencia = xbmcgui.Dialog()
        if "<br/>" in motivo:
            resultado = advertencia.ok("Non è possibile visualizzare questo video perché...", motivo.split("<br/>")[0],
                                       motivo.split("<br/>")[1], url)
        else:
            resultado = advertencia.ok("Non è possibile visualizzare questo video perché...", motivo, url)
    else:
        resultado = advertencia.ok("Non è possibile visualizzare questo video perché...",
                                   "Il server che lo ospita non è", "ancora supportato da StreamOnDemand", url)


def set_infoLabels(listitem,item):
    """
    Metodo para pasar la informacion al listitem (ver tmdb.set_InfoLabels() )
    item.infoLabels es un dicionario con los pares de clave/valor descritos en:
    http://mirrors.xbmc.org/docs/python-docs/14.x-helix/xbmcgui.html#ListItem-setInfo
    :param listitem: objeto xbmcgui.ListItem
    :param item: objeto Item que representa a una pelicula, serie o capitulo
    :return: None
    """
    if item.plot and item.infoLabels.get("plot","") == "":
        item.infoLabels['plot'] = item.plot

    it = item.clone()
    it.infoLabels['title'] = it.title

    listitem.setInfo("video", it.infoLabels)
