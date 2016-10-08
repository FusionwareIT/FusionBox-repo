# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# XBMC Tools
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand/
# Modificado por super_berny: inclusion de infoLabels
#------------------------------------------------------------

import urllib, urllib2
import xbmc
import xbmcgui
import xbmcplugin
import sys
import os

from servers import servertools
from core import config
from core import logger

# Esto permite su ejecución en modo emulado
try:
    pluginhandle = int( sys.argv[ 1 ] )
except:
    pluginhandle = ""

DEBUG = True

def addnewfolderextra(item, totalItems=0):

    if item.fulltitle=="":
        item.fulltitle=item.title
    
    contextCommands = []
    ok = False
    
    try:
        item.context = urllib.unquote_plus(item.context)
    except:
        item.context=""
    
    if "|" in item.context:
        item.context = item.context.split("|")
    
    if DEBUG:
       
        logger.info('[xbmctools.py] addnewfolderextra')
        logger.info(item.tostring())

    listitem = xbmcgui.ListItem( item.title, iconImage="DefaultFolder.png", thumbnailImage=item.thumbnail )

    listitem.setInfo( "video", { "Title" : item.title, "Plot" : item.plot, "Studio" : item.channel.capitalize() } )

    set_infoLabels(listitem,item.plot) # Modificacion introducida por super_berny para añadir infoLabels al ListItem

    if item.fanart!="":
        listitem.setProperty('fanart_image',item.fanart) 
        xbmcplugin.setPluginFanart(pluginhandle, item.fanart)
    #Realzamos un quote sencillo para evitar problemas con títulos unicode
#    title = title.replace("&","%26").replace("+","%2B").replace("%","%25")
    try:
        item.title = item.title.encode ("utf-8") #This only aplies to unicode strings. The rest stay as they are.
    except:
        pass

    itemurl = '%s?%s' % ( sys.argv[ 0 ] , item.tourl())

    if item.show != "": #Añadimos opción contextual para Añadir la serie completa a la biblioteca
        addSerieCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(action="addlist2Library").tourl())
        contextCommands.append(("Añadir Serie a Biblioteca",addSerieCommand))
        
    if "1" in item.context and accion != "por_teclado":
        DeleteCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="buscador", action="borrar_busqueda").tourl())
        contextCommands.append((config.get_localized_string( 30300 ),DeleteCommand))
    if "4" in item.context:
        searchSubtitleCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="subtitletools", action="searchSubtitle").tourl())
        contextCommands.append(("XBMC Subtitle",searchSubtitleCommand))
    if "5" in item.context:
        trailerCommand = "XBMC.Container.Update(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="trailertools", action="buscartrailer").tourl())
        contextCommands.append((config.get_localized_string(30162),trailerCommand))
    if "6" in item.context:# Ver canal en vivo en justintv
        justinCommand = "XBMC.PlayMedia(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="justintv", action="playVideo").tourl())
        contextCommands.append((config.get_localized_string(30410),justinCommand))

    if "8" in item.context:# Añadir canal a favoritos justintv
        justinCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="justintv", action="addToFavorites").tourl())
        contextCommands.append((config.get_localized_string(30406),justinCommand))

    if "9" in item.context:# Remover canal de favoritos justintv
        justinCommand = "XBMC.Container.Update(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="justintv", action="removeFromFavorites").tourl())
        contextCommands.append((config.get_localized_string(30407),justinCommand))

    logger.info("[xbmctools.py] addnewfolderextra itemurl="+itemurl)

    if config.get_platform()=="boxee":
        #logger.info("Modo boxee")
        ok = xbmcplugin.addDirectoryItem( handle = pluginhandle, url = itemurl , listitem=listitem, isFolder=True)
    else:
        #logger.info("Modo xbmc")
        if len(contextCommands) > 0:
            listitem.addContextMenuItems ( contextCommands, replaceItems=False)
    
        if totalItems == 0:
            ok = xbmcplugin.addDirectoryItem( handle = pluginhandle, url = itemurl , listitem=listitem, isFolder=True)
        else:
            ok = xbmcplugin.addDirectoryItem( handle = pluginhandle, url = itemurl , listitem=listitem, isFolder=True, totalItems=totalItems)
    return ok

def addnewvideo(item, IsPlayable='false', totalItems = 0):
    contextCommands = []
    ok = False
    try:
        item.context = urllib.unquote_plus(item.context)
    except:
        item.context=""
    if "|" in item.context:
        item.context = item.context.split("|")
    if DEBUG:
        logger.info('[xbmctools.py] addnewvideo')
        logger.info(item.tostring())  

    icon_image = os.path.join( config.get_runtime_path() , "resources" , "images" , "servers" , item.server+".png" )
    if not os.path.exists(icon_image):
        icon_image = "DefaultVideo.png"

    listitem = xbmcgui.ListItem( item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail )
    listitem.setInfo( "video", { "Title" : item.title, "FileName" : item.title, "Plot" : item.plot, "Duration" : item.duration, "Studio" : item.channel.capitalize(), "Genre" : item.category } )

    set_infoLabels(listitem,item.plot) # Modificacion introducida por super_berny para añadir infoLabels al ListItem
        
    if item.fanart!="":
        #logger.info("fanart :%s" %fanart)
        listitem.setProperty('fanart_image',item.fanart)
        xbmcplugin.setPluginFanart(pluginhandle, item.fanart)

    if IsPlayable == 'true': #Esta opcion es para poder utilizar el xbmcplugin.setResolvedUrl()
        listitem.setProperty('IsPlayable', 'true')
    #listitem.setProperty('fanart_image',os.path.join(IMAGES_PATH, "cinetube.png"))
    if "1" in item.context: #El uno añade al menu contextual la opcion de guardar en megalive un canal a favoritos
        addItemCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(action="saveChannelFavorites").tourl())
        contextCommands.append((config.get_localized_string(30301),addItemCommand))
        
    if "2" in item.context:#El dos añade al menu contextual la opciones de eliminar y/o renombrar un canal en favoritos 
        addItemCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(action="deleteSavedChannel").tourl())
        contextCommands.append((config.get_localized_string(30302),addItemCommand))
        addItemCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(action="renameChannelTitle").tourl())
        contextCommands.append((config.get_localized_string(30303),addItemCommand))
            
    if "6" in item.context:# Ver canal en vivo en justintv
        justinCommand = "XBMC.PlayMedia(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="justintv", action="playVideo").tourl())
        contextCommands.append((config.get_localized_string(30410),justinCommand))

    if "7" in item.context:# Listar videos archivados en justintv
        justinCommand = "XBMC.Container.Update(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="justintv", action="listarchives").tourl())
        contextCommands.append((config.get_localized_string(30409),justinCommand))

    if "8" in item.context:# Añadir canal a favoritos justintv
        justinCommand = "XBMC.RunPlugin(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="justintv", action="addToFavorites").tourl())
        contextCommands.append((config.get_localized_string(30406),justinCommand))

    if "9" in item.context:# Remover canal de favoritos justintv
        justinCommand = "XBMC.Container.Update(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="justintv", action="removeFromFavorites").tourl())
        contextCommands.append((config.get_localized_string(30407),justinCommand))

    if len (contextCommands) > 0:
        listitem.addContextMenuItems ( contextCommands, replaceItems=False)
    try:
        item.title = item.title.encode ("utf-8")     #This only aplies to unicode strings. The rest stay as they are.
        item.plot  = item.plot.encode ("utf-8")
    except:
        pass

    itemurl = '%s?%s' % ( sys.argv[ 0 ] , item.tourl())

    #logger.info("[xbmctools.py] itemurl=%s" % itemurl)
    if totalItems == 0:
        ok = xbmcplugin.addDirectoryItem( handle = pluginhandle, url=itemurl, listitem=listitem, isFolder=False)
    else:
        ok = xbmcplugin.addDirectoryItem( handle = pluginhandle, url=itemurl, listitem=listitem, isFolder=False, totalItems=totalItems)
    return ok

# FIXME: ¿Por qué no pasar el item en lugar de todos los parámetros?
def play_video(item,desdefavoritos=False,desdedescargados=False,desderrordescargas=False,strmfile=False):
    from servers import servertools
    import sys
    import xbmcgui,xbmc
    
    logger.info("[xbmctools.py] play_video")
    logger.info(item.tostring())

    try:
        item.server = item.server.lower()
    except:
        item.server = ""

    if item.server=="":
        item.server="directo"

    try:
        from core import descargas
        download_enable=True
    except:
        download_enable=False

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
            if download_enable:
                opcion = config.get_localized_string(30153)
                opciones.append(opcion) # "Descargar"
    
            if item.channel=="favoritos": 
                opciones.append(config.get_localized_string(30154)) # "Quitar de favoritos"
            else:
                opciones.append(config.get_localized_string(30155)) # "Añadir a favoritos"
        
            if not strmfile:
                opciones.append(config.get_localized_string(30161)) # "Añadir a Biblioteca"
        
            if download_enable:
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
            if config.get_setting("pyload_enabled")=="true":
                opciones.append(config.get_localized_string(30158).replace("jDownloader","pyLoad")) # "Enviar a pyLoad"

        if default_action=="3":
            seleccion = len(opciones)-1
    
        # Busqueda de trailers en youtube    
        if not item.channel in ["Trailer","ecarteleratrailers"]:
            opciones.append(config.get_localized_string(30162)) # "Buscar Trailer"

    # Si no puedes ver el vídeo te informa
    else:
        import xbmcgui
        if item.server!="":
            advertencia = xbmcgui.Dialog()
            if "<br/>" in motivo:
                resultado = advertencia.ok( "Non è possibile guardare il video perché...",motivo.split("<br/>")[0],motivo.split("<br/>")[1],item.url)
            else:
                resultado = advertencia.ok( "Non è possibile guardare il video perché...",motivo,item.url)
        else:
            resultado = advertencia.ok( "Non è possibile guardare il video perché...","Il server che lo ospita non è","ancora supportato da streamondemand",item.url)

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
        import xbmcgui
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
        import sys
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
            package_name = "streamondemand"

        from core import pyload_client
        pyload_client.download(url=item.url,package_name=package_name)
        return

    elif opciones[seleccion]==config.get_localized_string(30164): # Borrar archivo en descargas
        # En "extra" está el nombre del fichero en favoritos
        import os
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

        import xbmc
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
                resultado = advertencia.ok("plugin" , "Scaricato con successo")
            elif devuelve==-1:
                advertencia = xbmcgui.Dialog()
                resultado = advertencia.ok("plugin" , "Download interrotto")
            else:
                advertencia = xbmcgui.Dialog()
                resultado = advertencia.ok("plugin" , "Errore nel download")
        return

    elif opciones[seleccion]==config.get_localized_string(30154): #"Quitar de favoritos"
        from core import favoritos
        # En "extra" está el nombre del fichero en favoritos
        favoritos.deletebookmark(urllib.unquote_plus( item.extra ))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30102) , item.title , config.get_localized_string(30105)) # 'Se ha quitado de favoritos'

        xbmc.executebuiltin( "Container.Refresh" )
        return

    elif opciones[seleccion]==config.get_localized_string(30159): #"Borrar descarga definitivamente"
        from core import descargas
        descargas.delete_error_bookmark(urllib.unquote_plus( item.extra ))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30106)) # 'Se ha quitado de la lista'
        xbmc.executebuiltin( "Container.Refresh" )
        return

    elif opciones[seleccion]==config.get_localized_string(30160): #"Pasar de nuevo a lista de descargas":
        from core import descargas
        descargas.mover_descarga_error_a_pendiente(urllib.unquote_plus( item.extra ))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30107)) # 'Ha pasado de nuevo a la lista de descargas'
        return

    elif opciones[seleccion]==config.get_localized_string(30155): #"Añadir a favoritos":
        from core import favoritos
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
            favoritos.savebookmark(titulo=download_title,url=item.url,thumbnail=download_thumbnail,server=item.server,plot=download_plot,fulltitle=item.title)
            advertencia = xbmcgui.Dialog()
            resultado = advertencia.ok(config.get_localized_string(30102) , item.title , config.get_localized_string(30108)) # 'se ha añadido a favoritos'
        return

    elif opciones[seleccion]==config.get_localized_string(30156): #"Quitar de lista de descargas":
        from core import descargas
        # La categoría es el nombre del fichero en la lista de descargas
        descargas.deletebookmark((urllib.unquote_plus( item.extra )))

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , item.title , config.get_localized_string(30106)) # 'Se ha quitado de lista de descargas'

        xbmc.executebuiltin( "Container.Refresh" )
        return

    elif opciones[seleccion]==config.get_localized_string(30157): #"Añadir a lista de descargas":
        from core import descargas
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

            descargas.savebookmark(titulo=download_title,url=item.url,thumbnail=download_thumbnail,server=item.server,plot=download_plot,fulltitle=download_title)

            advertencia = xbmcgui.Dialog()
            resultado = advertencia.ok(config.get_localized_string(30101) , download_title , config.get_localized_string(30109)) # 'se ha añadido a la lista de descargas'
        return

    elif opciones[seleccion]==config.get_localized_string(30161): #"Añadir a Biblioteca":  # Library
        from platformcode import library
        
        titulo = item.fulltitle
        if item.fulltitle=="":
            titulo = item.title
        
        library.savelibrary(titulo,item.url,item.thumbnail,item.server,item.plot,canal=item.channel,category=item.category,Serie=item.show)

        advertencia = xbmcgui.Dialog()
        resultado = advertencia.ok(config.get_localized_string(30101) , titulo , config.get_localized_string(30135)) # 'se ha añadido a la lista de descargas'
        return

    elif opciones[seleccion]==config.get_localized_string(30162): #"Buscar Trailer":
        config.set_setting("subtitulo", "false")
        import sys
        xbmc.executebuiltin("Container.Update(%s?%s)" % ( sys.argv[ 0 ] , item.clone(channel="trailertools", action="buscartrailer").tourl()))
        return

    # Si no hay mediaurl es porque el vídeo no está :)
    logger.info("[xbmctools.py] mediaurl="+mediaurl)
    if mediaurl=="":
        logger.info("b1")
        if server == "unknown":
            alertUnsopportedServer()
        else:
            alertnodisponibleserver(item.server)
        return

    # Si hay un tiempo de espera (como en megaupload), lo impone ahora
    if wait_time>0:
        logger.info("b2")
        continuar = handle_wait(wait_time,server,"Caricamento vídeo...")
        if not continuar:
            return

    # Obtención datos de la Biblioteca (solo strms que estén en la biblioteca)
    import xbmcgui
    if strmfile:
        logger.info("b3")
        xlistitem = getLibraryInfo(mediaurl)
    else:
        logger.info("b4")

        play_title = item.fulltitle
        play_thumbnail = item.thumbnail
        play_plot = item.plot

        if item.hasContentDetails=="true":
            play_title = item.contentTitle
            play_thumbnail = item.contentThumbnail
            play_plot = item.contentPlot

        try:
            xlistitem = xbmcgui.ListItem( play_title, iconImage="DefaultVideo.png", thumbnailImage=play_thumbnail, path=mediaurl)
            logger.info("b4.1")
        except:
            xlistitem = xbmcgui.ListItem( play_title, iconImage="DefaultVideo.png", thumbnailImage=play_thumbnail)
            logger.info("b4.2")      
        
        xlistitem.setInfo( "video", { "Title": play_title, "Plot" : play_plot , "Studio" : item.channel , "Genre" : item.category } )
        
        #set_infoLabels(listitem,plot) # Modificacion introducida por super_berny para añadir infoLabels al ListItem
    
    # Lanza el reproductor
        # Lanza el reproductor
    if strmfile:           # and item.server != "torrent": #Si es un fichero strm no hace falta el play
        logger.info("b6")
        import sys
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xlistitem)
        if item.subtitle != "":
            xbmc.sleep(2000)
            xbmc.Player().setSubtitles(item.subtitle)

    else:
        logger.info("b7")
        logger.info("player_mode="+config.get_setting("player_mode"))
        logger.info("mediaurl="+mediaurl)
        if config.get_setting("player_mode")=="3" or "megacrypter.com" in mediaurl:
            logger.info("b11")
            import download_and_play
            download_and_play.download_and_play( mediaurl , "download_and_play.tmp" , config.get_setting("downloadpath") )
            return

        elif config.get_setting("player_mode")=="0" or (config.get_setting("player_mode")=="3" and mediaurl.startswith("rtmp")):
            logger.info("b8")
            # Añadimos el listitem a una lista de reproducción (playlist)
            playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            playlist.clear()
            playlist.add( mediaurl, xlistitem )

            # Reproduce
            playersettings = config.get_setting('player_type')
            logger.info("[xbmctools.py] playersettings="+playersettings)
        
            if config.get_system_platform()=="xbox":
                player_type = xbmc.PLAYER_CORE_AUTO
                if playersettings == "0":
                    player_type = xbmc.PLAYER_CORE_AUTO
                    logger.info("[xbmctools.py] PLAYER_CORE_AUTO")
                elif playersettings == "1":
                    player_type = xbmc.PLAYER_CORE_MPLAYER
                    logger.info("[xbmctools.py] PLAYER_CORE_MPLAYER")
                elif playersettings == "2":
                    player_type = xbmc.PLAYER_CORE_DVDPLAYER
                    logger.info("[xbmctools.py] PLAYER_CORE_DVDPLAYER")
            
                xbmcPlayer = xbmc.Player( player_type )
            else:
                xbmcPlayer = xbmc.Player()
    
            xbmcPlayer.play(playlist)
            
            if item.channel=="cuevana" and item.subtitle!="":
                logger.info("subtitulo="+subtitle)
                if item.subtitle!="" and (opciones[seleccion].startswith("Ver") or opciones[seleccion].startswith("Watch")):
                    logger.info("[xbmctools.py] Con subtitulos")
                    setSubtitles()

        elif config.get_setting("player_mode")=="1":
            logger.info("b9")
            logger.info("mediaurl :"+ mediaurl)
            logger.info("Tras setResolvedUrl")
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=mediaurl))
        
        elif config.get_setting("player_mode")=="2":
            logger.info("b10")
            xbmc.executebuiltin( "PlayMedia("+mediaurl+")" )
      
    if item.subtitle!="" and view:
        logger.info("b11")
        logger.info("Subtítulos externos: "+item.subtitle)
        xbmc.Player().setSubtitles(item.subtitle)

def handle_wait(time_to_wait,title,text):
    logger.info ("[xbmctools.py] handle_wait(time_to_wait=%d)" % time_to_wait)
    import xbmc,xbmcgui
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
        remaining_display = ' Attendi '+secs_left+' secondi per il video...'
        espera.update(percent,' '+text,remaining_display)
        xbmc.sleep(1000)
        if (espera.iscanceled()):
             cancelled = True
             break

    if cancelled == True:     
         logger.info ('Attesa eliminata')
         return False
    else:
         logger.info ('Attesa conclusa')
         return True

def getLibraryInfo (mediaurl):
    '''Obtiene información de la Biblioteca si existe (ficheros strm) o de los parámetros
    '''
    if DEBUG:
        logger.info('[xbmctools.py] playlist OBTENCIÓN DE DATOS DE BIBLIOTECA')

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
        ('listitem.cast', 's'),             # (Michal C. Hall) - List concatenated into a string
        ('listitem.castandrole', 's'),      #(Michael C. Hall|Dexter) - List concatenated into a string
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
    logger.info("[xbmctools.py] playstrm url="+url)

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
    play_video("Biblioteca streamondemand",server,url,category,title,thumbnail,plot,strmfile=True,Serie=serie,subtitle=subtitle)

def renderItems(itemlist, item, isPlayable='false'):
    
    viewmode = "list"
    
    if itemlist <> None:
        for item in itemlist:
            logger.info("item="+item.tostring())
            
            if item.category == "":
                item.category = item.category
                
            if item.fulltitle=="":
                item.fulltitle=item.title
            
            if item.fanart=="":

                channel_fanart = os.path.join( config.get_runtime_path(), 'resources', 'images', 'fanart', item.channel+'.jpg')

                if os.path.exists(channel_fanart):
                    item.fanart = channel_fanart
                else:
                    item.fanart = os.path.join(config.get_runtime_path(),"fanart.jpg")

            if item.folder:
                addnewfolderextra(item, totalItems = len(itemlist))
            else:
                if config.get_setting("player_mode")=="1": # SetResolvedUrl debe ser siempre "isPlayable = true"
                    isPlayable = "true"

                addnewvideo( item, IsPlayable=isPlayable, totalItems = len(itemlist))
                
            if item.viewmode!="list":
                viewmode = item.viewmode

        # Cierra el directorio
        xbmcplugin.setContent(pluginhandle,"Movies")
        xbmcplugin.setPluginCategory( handle=pluginhandle, category=item.category )
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
    logger.info("[xbmctools.py] wait2second")
    import time
    contador = 0
    while xbmc.Player().isPlayingVideo()==False:
        logger.info("[xbmctools.py] setSubtitles: Waiting 2 seconds for video to start before setting subtitles")
        time.sleep(2)
        contador = contador + 1
        
        if contador>10:
            break

def setSubtitles():
    logger.info("[xbmctools.py] setSubtitles")
    import time
    contador = 0
    while xbmc.Player().isPlayingVideo()==False:
        logger.info("[xbmctools.py] setSubtitles: Waiting 2 seconds for video to start before setting subtitles")
        time.sleep(2)
        contador = contador + 1
        
        if contador>10:
            break

    subtitlefile = os.path.join( config.get_data_path(), 'subtitulo.srt' )
    logger.info("[xbmctools.py] setting subtitle file %s" % subtitlefile)
    xbmc.Player().setSubtitles(subtitlefile)

def trailer(item):
    logger.info("[xbmctools.py] trailer")
    config.set_setting("subtitulo", "false")
    import sys
    xbmc.executebuiltin("XBMC.RunPlugin(%s?channel=%s&action=%s&category=%s&title=%s&url=%s&thumbnail=%s&plot=%s&server=%s)" % ( sys.argv[ 0 ] , "trailertools" , "buscartrailer" , urllib.quote_plus( item.category ) , urllib.quote_plus( item.fulltitle ) , urllib.quote_plus( item.url ) , urllib.quote_plus( item.thumbnail ) , urllib.quote_plus( "" ) ))
    return

def alert_no_puedes_ver_video(server,url,motivo):
    import xbmcgui

    if server!="":
        advertencia = xbmcgui.Dialog()
        if "<br/>" in motivo:
            resultado = advertencia.ok( "Non è possibile visualizzare questo video perché...",motivo.split("<br/>")[0],motivo.split("<br/>")[1],url)
        else:
            resultado = advertencia.ok( "Non è possibile visualizzare questo video perché...",motivo,url)
    else:
        resultado = advertencia.ok( "Non è possibile visualizzare questo video perché...","Il server che lo ospita non è","ancora supportato da StreamOnDemand",url)
        
def set_infoLabels(listitem,plot):
    # Modificacion introducida por super_berny para añadir infoLabels al ListItem
    if plot.startswith("{'infoLabels'"):
        # Necesitaba un parametro que pase los datos desde Item hasta esta funcion 
        # y el que parecia mas idoneo era plot.
        # plot tiene que ser un str con el siguiente formato:
        #   plot="{'infoLabels':{dicionario con los pares de clave/valor descritos en 
        #               http://mirrors.xbmc.org/docs/python-docs/14.x-helix/xbmcgui.html#ListItem-setInfo}}"
        try:
            import ast
            infodict=ast.literal_eval(plot)['infoLabels']
            listitem.setInfo( "video", infodict)
        except:
            pass
            
