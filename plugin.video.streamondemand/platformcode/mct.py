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
# MCT - Mini Cliente Torrent para streamondemand
#------------------------------------------------------------

import os
import re
import shutil
import tempfile
import urllib
import urllib2

try:
    from python_libtorrent import get_libtorrent
    lt = get_libtorrent()
except Exception, e:
    import libtorrent as lt

import xbmc
import xbmcgui

from core import config
from core import scrapertools
from core import filetools


def play(url, xlistitem, is_view=None, subtitle=""):

    # -- Necesario para algunas webs ----------------------------
    if not url.endswith(".torrent") and not url.startswith("magnet"):
        t_file = scrapertools.get_header_from_response(url, header_to_get="location")
        if len(t_file) > 0:
            url = t_file
            t_file = scrapertools.get_header_from_response(url, header_to_get="location")
        if len(t_file) > 0:
            url = t_file

    # -- Crear dos carpetas en descargas para los archivos ------
    save_path_videos = os.path.join( config.get_setting("downloadpath") , "torrent-videos" )
    save_path_torrents = os.path.join( config.get_setting("downloadpath") , "torrent-torrents" )
    if not os.path.exists( save_path_torrents ): os.mkdir(save_path_torrents)

    # -- Usar - archivo torrent desde web, meagnet o HD ---------
    if not os.path.isfile(url) and not url.startswith("magnet"):
        # -- http - crear archivo torrent -----------------------
        data = url_get(url)
        # -- El nombre del torrent será el que contiene en los --
        # -- datos.                                             -
        re_name = urllib.unquote( scrapertools.get_match(data,':name\d+:(.*?)\d+:') )
        #torrent_file = os.path.join(save_path_torrents, re_name+'.torrent')
        torrent_file = filetools.join(save_path_torrents, unicode(re_name, "'utf-8'", errors="replace")+'.torrent')

        f = open(torrent_file,'wb')
        f.write(data)
        f.close()
    elif os.path.isfile(url):
        # -- file - para usar torrens desde el HD ---------------
        torrent_file = url
    else:
        # -- magnet ---------------------------------------------
        torrent_file = url
    # -----------------------------------------------------------

    # -- MCT - MiniClienteTorrent -------------------------------
    ses = lt.session()

    print "### Init session ########"
    print lt.version
    print "#########################"

    ses.add_dht_router("router.bittorrent.com",6881)
    ses.add_dht_router("router.utorrent.com",6881)
    ses.add_dht_router("router.bitcomet.com",554)
    ses.add_dht_router("dht.transmissionbt.com",6881)

    trackers = [
        "http://exodus.desync.com:6969/announce",
        "udp://tracker.publicbt.com:80/announce",
        "udp://tracker.openbittorrent.com:80/announce",
        "http://tracker.torrentbay.to:6969/announce",
        "http://fr33dom.h33t.com:3310/announce",
        "http://tracker.pow7.com/announce",
        "udp://tracker.ccc.de:80/announce",
        "http://tracker.bittorrent.am:80/announce",
        "http://denis.stalker.h3q.com:6969/announce",
        "udp://tracker.prq.to:80/announce",
        "udp://tracker.istole.it:80/announce",
        "udp://open.demonii.com:1337",

        "http://9.rarbg.com:2710/announce",
        "http://announce.torrentsmd.com:6969/announce",
        "http://bt.careland.com.cn:6969/announce",
        "http://explodie.org:6969/announce",
        "http://mgtracker.org:2710/announce",
        "http://tracker.best-torrents.net:6969/announce",
        "http://tracker.tfile.me/announce",
        "http://tracker.torrenty.org:6969/announce",
        "http://tracker1.wasabii.com.tw:6969/announce",
        "udp://9.rarbg.com:2710/announce",
        "udp://9.rarbg.me:2710/announce",
        "udp://coppersurfer.tk:6969/announce",
        "udp://tracker.btzoo.eu:80/announce",

        "http://www.spanishtracker.com:2710/announce",
        "http://www.todotorrents.com:2710/announce",
    ]

    video_file = ""
    # -- magnet2torrent -----------------------------------------
    if torrent_file.startswith("magnet"):
        tempdir = tempfile.mkdtemp()
        params = {
            'save_path': tempdir,
            'trackers':trackers,
            'storage_mode': lt.storage_mode_t.storage_mode_allocate,
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True
        }
        h = lt.add_magnet_uri(ses, torrent_file, params)
        dp = xbmcgui.DialogProgress()
        dp.create('streamondemand-MCT')
        while not h.has_metadata():
            message, porcent, msg_file, s, download = getProgress(h, "Creating torrent from magnet")
            dp.update(porcent, message, msg_file)
            if s.state == 1: download = 1
            if dp.iscanceled():
                dp.close()
                remove_files( download, torrent_file, video_file, ses, h )
                return
        dp.close()
        info = h.get_torrent_info()
        data = lt.bencode( lt.create_torrent(info).generate() )
        #torrent_file = os.path.join(save_path_torrents, info.name() + ".torrent")
        torrent_file = os.path.join(save_path_torrents, unicode(info.name(), "'utf-8'", errors="replace") + ".torrent")
        f = open(torrent_file,'wb')
        f.write(data)
        f.close()
        ses.remove_torrent(h)
        shutil.rmtree(tempdir)
    # -----------------------------------------------------------

    # -- Archivos torrent ---------------------------------------
    e = lt.bdecode(open(torrent_file, 'rb').read())
    info = lt.torrent_info(e)

    # -- El más gordo o uno de los más gordo se entiende que es -
    # -- el vídeo o es el vídeo que se usará como referencia    -
    # -- para el tipo de archivo                                -
    print "##### Archivos ## %s ##" % len(info.files())
    _index_file, _video_file, _size_file = get_video_file(info)

    _video_file_ext = os.path.splitext( _video_file )[1]
    if _video_file_ext == ".avi" or _video_file_ext == ".mp4":
        print "##### storage_mode_t.storage_mode_allocate ("+_video_file_ext+") #####"
        h = ses.add_torrent( { 'ti':info, 'save_path': save_path_videos, 'trackers':trackers, 'storage_mode':lt.storage_mode_t.storage_mode_allocate } )
    else:
        print "##### storage_mode: none ("+_video_file_ext+") #####"
        h = ses.add_torrent( { 'ti':info, 'save_path': save_path_videos, 'trackers':trackers, 'storage_mode':lt.storage_mode_t.storage_mode_sparse } )
    # -----------------------------------------------------------

    # -- Descarga secuencial - trozo 1, trozo 2, ... ------------
    h.set_sequential_download(True)

    h.force_reannounce()
    h.force_dht_announce()

    # -- Prioritarizar/Seleccionar archivo-----------------------
    _index, video_file, video_size = get_video_files_sizes( info )
    if _index == -1:
        _index = _index_file
        video_file = _video_file
        video_size = _size_file

    # -- Inicio de variables para 'pause' automático cuando el  -
    # -- el vídeo se acerca a una pieza sin completar           -
    is_greater_num_pieces = False
    is_greater_num_pieces_plus = False
    is_greater_num_pieces_pause = False

    #porcent4first_pieces = int( video_size / 1073741824 )
    porcent4first_pieces = int( video_size * 0.000000005 )
    if porcent4first_pieces < 10: porcent4first_pieces = 10
    if porcent4first_pieces > 100: porcent4first_pieces = 100
    #num_pieces_to_resume = int( video_size / 1610612736 )
    num_pieces_to_resume = int( video_size * 0.0000000025 )
    if num_pieces_to_resume < 5: num_pieces_to_resume = 5
    if num_pieces_to_resume > 25: num_pieces_to_resume = 25

    print "##### porcent4first_pieces ## %s ##" % porcent4first_pieces
    print "##### num_pieces_to_resume ## %s ##" % num_pieces_to_resume

    # -- Prioritarizar o seleccionar las piezas del archivo que -
    # -- se desea reproducir con 'file_priorities'              -
    piece_set = set_priority_pieces(h, _index, video_file, video_size)

    # -- Crear diálogo de progreso para el primer bucle ---------
    dp = xbmcgui.DialogProgress()
    dp.create('streamondemand-MCT')

    _pieces_info = {}

    # -- Doble bucle anidado ------------------------------------
    # -- Descarga - Primer bucle                                -
    while not h.is_seed():
        s = h.status()

        xbmc.sleep(100)

        # -- Recuperar los datos del progreso -------------------
        message, porcent, msg_file, s, download = getProgress(h, video_file, _pf=_pieces_info)

        # -- Si hace 'checking' existe descarga -----------------
        # -- 'download' Se usará para saber si hay datos        -
        # -- descargados para el diálogo de 'remove_files'      -
        if s.state == 1: download = 1

        # -- Player - play --------------------------------------
        # -- Comprobar si se han completado las piezas para el  -
        # -- inicio del vídeo    ...............                -
        first_pieces = True
        _p = ""
        _c = 0
        for i in range( piece_set[0], piece_set[porcent4first_pieces] ):
            _p+= "[%s:%s]" % ( i, h.have_piece(i) )
            first_pieces&= h.have_piece(i)
            if h.have_piece(i): _c+= 1
        _pieces_info = {'current': 0, 'continuous': "%s/%s" % (_c,porcent4first_pieces), 'have': h.status().num_pieces, 'len': len(piece_set)}
        _p = "##### first_pieces [%s/%s][%s]: " % ( _c, porcent4first_pieces, len(piece_set) ) + _p
        print _p
        # -- -------------------------------------------------- -

        if is_view != "Ok" and first_pieces:
            print "##### porcent [%.2f%%]" % (s.progress * 100)
            is_view = "Ok"
            dp.close()

            # -- Player - Ver el vídeo --------------------------
            playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            playlist.clear()
            #ren_video_file = os.path.join( save_path_videos, video_file ).replace('\\','\\\\')
            ren_video_file = os.path.join( save_path_videos, video_file )
            playlist.add( ren_video_file, xlistitem )
            #playlist.add( os.path.join( save_path_videos, video_file ), xlistitem )
            #playlist.add( "http://192.168.0.200/mctplay/" + video_file.replace(' ','%20'), xlistitem )
            player = play_video( xbmc.PLAYER_CORE_AUTO )
            player.play(playlist)
            '''
            # -- Player - Ver el vídeo --------------------------
            player = play_video()
            #player.play( os.path.join( save_path_videos, video_file ) )
            player.play( "http://192.168.0.200/mctplay/" + video_file.replace(' ','%20') )
            '''

            #player.play( os.path.join( save_path_videos, video_file ) )

            # -- Contador de cancelaciones para la ventana de   -
            # -- 'pause' automático                             -
            is_greater_num_pieces_canceled = 0
            continuous_pieces = 0
            porcent_time = 0.00
            current_piece = 0

            # -- Impedir que kodi haga 'resume' a un archivo ----
            # -- que se reprodució con anterioridad y que se    -
            # -- eliminó para impedir que intente la reprucción -
            # -- en una pieza que aún no se ha completado y se  -
            # -- active 'pause' automático                      -
            not_resume = True

            # -- Bandera subTítulos
            _sub = False

            # -- Segundo bucle - Player - Control de eventos ----
            while player.isPlaying():
                xbmc.sleep(100)

                # -- Añadir subTítulos
                if subtitle!="" and not _sub:
                    _sub = True
                    player.setSubtitles(subtitle)

                # -- Impedir que kodi haga 'resume' al inicio ---
                # -- de la descarga de un archivo conocido      -
                if not_resume:
                    player.seekTime(0)
                    not_resume = False
                    #xbmc.sleep(1000)

                # -- Control 'pause' automático                 -
                continuous_pieces = count_completed_continuous_pieces(h, piece_set)

                if xbmc.Player().isPlaying():

                    # -- Porcentage del progreso del vídeo ------
                    porcent_time = player.getTime() / player.getTotalTime() * 100

                    # -- Pieza que se está reproduciendo --------
                    current_piece = int( porcent_time / 100 * len(piece_set) )

                    # -- Banderas de control --------------------
                    is_greater_num_pieces = (current_piece > continuous_pieces - num_pieces_to_resume)
                    is_greater_num_pieces_plus = (current_piece + porcent4first_pieces > continuous_pieces)
                    is_greater_num_pieces_finished = (current_piece + porcent4first_pieces >= len(piece_set))

                    # -- Activa 'pause' automático --------------
                    if is_greater_num_pieces and not player.paused and not is_greater_num_pieces_finished:
                        is_greater_num_pieces_pause = True
                        player.pause()

                    # -- Log ------------------------------------
                    _TotalTime = player.getTotalTime()
                    _Time = player.getTime()
                    _print_log = "\n##### Player ##################################"
                    _print_log+= "\nTamaño del vídeo: %s" % video_size
                    _print_log+= "\nTotal piezas: %s" % len(piece_set)
                    _print_log+= "\nPiezas contiguas: %s" % continuous_pieces
                    _print_log+= "\n-----------------------------------------------"
                    _print_log+= "\nVídeo-Total segundos: %s" % _TotalTime
                    _print_log+= "\nVídeo-Progreso segundos: %s" % _Time
                    _print_log+= "\nVídeo-Progreso porcentaje: %.2f%%" % porcent_time
                    _print_log+= "\n-----------------------------------------------"
                    _print_log+= "\ncurrent_piece: %s" % current_piece
                    _print_log+= "\nis_greater_num_pieces: %s" % is_greater_num_pieces
                    _print_log+= "\nis_greater_num_pieces_plus: %s" % is_greater_num_pieces_plus
                    _print_log+= "\nis_greater_num_pieces_pause: %s" % is_greater_num_pieces_pause
                    _print_log+= "\nis_greater_num_pieces_finished: %s" % is_greater_num_pieces_finished
                    _print_log+= "\nPieza que se está visionando: %.2f" % ( porcent_time / 100 * len(piece_set) )
                    _print_log+= "\nOffset que se está visionando: %.2f" % ( porcent_time / 100 * video_size )
                    if is_greater_num_pieces and not player.paused and not is_greater_num_pieces_finished:
                        _print_log+= "\n+++++++++++++++++++++++++++++++++++++++++++++++"
                        _print_log+= "\nPausa con:"
                        _print_log+= "\n    current_piece = %s" % current_piece
                        _print_log+= "\n    continuous_pieces = %s" % continuous_pieces
                    _print_log+= "\n###############################################"
                    print _print_log
                    # -------------------------------------------
                    _pieces_info = {'current': current_piece, 'continuous': continuous_pieces, 'have': h.status().num_pieces, 'len': len(piece_set)}

                # -- Cerrar el diálogo de progreso --------------
                if player.resumed:
                    dp.close()

                # -- Mostrar el diálogo de progreso -------------
                if player.paused:
                    # -- Crear diálogo si no existe -------------
                    if not player.statusDialogoProgress:
                        dp = xbmcgui.DialogProgress()
                        dp.create('streamondemand-MCT')
                        player.setDialogoProgress()

                    # -- Diálogos de estado en el visionado -----
                    if not h.is_seed():
                        # -- Recuperar los datos del progreso ---
                        message, porcent, msg_file, s, download = getProgress(h, video_file, _pf=_pieces_info)
                        dp.update(porcent, message, msg_file)
                    else:
                        dp.update(100, "Download completo: " + video_file)

                    # -- Se canceló el progreso en el visionado -
                    # -- Continuar                              -
                    if dp.iscanceled():
                        dp.close()
                        player.pause()

                    # -- Se canceló el progreso en el visionado -
                    # -- en la ventana de 'pause' automático.   -
                    # -- Parar si el contador llega a 3         -
                    if dp.iscanceled() and is_greater_num_pieces_pause:
                        is_greater_num_pieces_canceled+= 1
                        if is_greater_num_pieces_canceled == 3:
                            player.stop()

                    # -- Desactiva 'pause' automático y ---------
                    # -- reinicia el contador de cancelaciones  -
                    if not dp.iscanceled() and not is_greater_num_pieces_plus and is_greater_num_pieces_pause:
                        dp.close()
                        player.pause()
                        is_greater_num_pieces_pause = False
                        is_greater_num_pieces_canceled = 0

                    # -- El usuario cancelo el visionado --------
                    # -- Terminar                               -
                    if player.ended:
                        # -- Diálogo eliminar archivos ----------
                        remove_files( download, torrent_file, video_file, ses, h )
                        return

        # -- Kodi - Se cerró el visionado -----------------------
        # -- Continuar | Terminar                               -
        if is_view == "Ok" and not xbmc.Player().isPlaying():

            if info.num_files() == 1:
                # -- Diálogo continuar o terminar ---------------
                d = xbmcgui.Dialog()
                ok = d.yesno('streamondemand-MCT', 'Kodi ha chiuso il video.', 'Continuare con la sessione?')
            else: ok = False
            # -- SI ---------------------------------------------
            if ok:
                # -- Continuar: ---------------------------------
                is_view=None
            else:
                # -- Terminar: ----------------------------------
                # -- Comprobar si el vídeo pertenece a una ------
                # -- lista de archivos                          -
                _index, video_file, video_size = get_video_files_sizes( info )
                if _index == -1 or info.num_files() == 1:
                    # -- Diálogo eliminar archivos --------------
                    remove_files( download, torrent_file, video_file, ses, h )
                    return
                else:
                    # -- Lista de archivos. Diálogo de opciones -
                    piece_set = set_priority_pieces(h, _index, video_file, video_size)
                    is_view=None
                    dp = xbmcgui.DialogProgress()
                    dp.create('streamondemand-MCT')

        # -- Mostar progeso antes del visionado -----------------
        if is_view != "Ok" :
            dp.update(porcent, message, msg_file)

        # -- Se canceló el progreso antes del visionado ---------
        # -- Terminar                                           -
        if dp.iscanceled():
            dp.close()
            # -- Comprobar si el vídeo pertenece a una lista de -
            # -- archivos                                       -
            _index, video_file, video_size = get_video_files_sizes( info )
            if _index == -1 or info.num_files() == 1:
                # -- Diálogo eliminar archivos ------------------
                remove_files( download, torrent_file, video_file, ses, h )
                return
            else:
                # -- Lista de archivos. Diálogo de opciones -----
                piece_set = set_priority_pieces(h, _index, video_file, video_size)
                is_view=None
                dp = xbmcgui.DialogProgress()
                dp.create('streamondemand-MCT')

    # -- Kodi - Error? - No debería llegar aquí -----------------
    if is_view == "Ok" and not xbmc.Player().isPlaying():
        dp.close()
        # -- Diálogo eliminar archivos --------------------------
        remove_files( download, torrent_file, video_file, ses, h )

    return

# -- Progreso de la descarga ------------------------------------
def getProgress(h, video_file, _pf={}):

    if len(_pf) > 0:
        #_pf_msg = "[%s] [%s] [%s] [%s][CR]" % (_pf['current'], _pf['continuous'], _pf['have'], _pf['len'])
        _pf_msg = "[%s] [%s] [%s] [%s]" % (_pf['current'], _pf['continuous'], _pf['have'], _pf['len'])
    else: _pf_msg = ""

    s = h.status()

    state_str = ['queued', 'checking', 'downloading metadata', \
        'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']

    message = '%.2f%% d:%.1f kb/s u:%.1f kb/s p:%d s:%d %s' % \
        (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
        s.num_peers, s.num_seeds, state_str[s.state])
    porcent = int( s.progress * 100 )

    download = ( s.progress * 100 )

    if "/" in video_file: video_file = video_file.split("/")[1]
    #msg_file = "..../"+video_file + " - %.2f MB" % (s.total_wanted/1048576.0)
    #msg_file = video_file + " - %.2f MB" % (s.total_wanted/1048576.0)
    msg_file = video_file
    #msg_file = "[%s] "%len(msg_file)+_pf_msg+msg_file
    if len(msg_file) > 50:
        msg_file = msg_file.replace( video_file, os.path.splitext(video_file)[0][:40] + "... " + os.path.splitext(video_file)[1] )
    msg_file = msg_file + "[CR]" + "%.2f MB" % (s.total_wanted/1048576.0) + " - " + _pf_msg

    return (message, porcent, msg_file, s, download)

# -- Clase play_video - Controlar eventos -----------------------
class play_video(xbmc.Player):

    def __init__( self, *args, **kwargs ):
        self.paused = False
        self.resumed = True
        self.statusDialogoProgress = False
        self.ended = False

    def onPlayBackPaused(self):
        self.paused = True
        self.resumed = False

    def onPlayBackResumed(self):
        self.paused = False
        self.resumed = True
        self.statusDialogoProgress = False

    def is_paused(self):
        return self.paused

    def setDialogoProgress(self):
        self.statusDialogoProgress = True

    def is_started(self):
        self.ended = False

    def is_ended(self):
        self.ended = True

# -- Conseguir el nombre un alchivo de vídeo del metadata -------
# -- El más gordo o uno de los más gordo se entiende que es el  -
# -- vídeo o es vídeo que se usará como referencia para el tipo -
# -- de archivo                                                 -
def get_video_file( info ):
    size_file = 0
    for i, f in enumerate(info.files()):
        if f.size > size_file:
            video_file = f.path.replace("\\","/")
            size_file = f.size
            index_file = i
    return index_file, video_file, size_file

# -- Listado de selección del vídeo a prioritarizar -------------
def get_video_files_sizes( info ):

    opciones = []
    vfile_name = {}
    vfile_size = {}

    for i, f in enumerate( info.files() ):
        #_title = f.path
        #try: _title = f.path.encode('iso-8859-1')
        #except: _title = f.path.decode('utf-8')
        #_title = f.path.encode('iso-8859-1')
        _title = unicode(f.path, "iso-8859-1", errors="replace")
        _title = unicode(f.path, "'utf-8'", errors="replace")

        _title = re.sub(r'(.*? )- Temporada (\d+) Completa(.*?)',
                        r'\1T\2\3',
                        _title)
        _title = re.sub(r'\s\([^\)]+\)|\s\-',
                        '',
                        _title)
        info.rename_file( i, _title )

    for i, f in enumerate( info.files() ):
        _index = int(i)
        _title = f.path.replace("\\","/")
        _size = f.size
        _offset = f.offset

        _file_name = os.path.splitext( _title )[0]
        if "/" in _file_name: _file_name = _file_name.split('/')[1]

        _file_ext = os.path.splitext( _title )[1]

        _caption = str(i) + \
            " - " + \
            _file_name + _file_ext + \
            " - %.2f MB" % (_size / 1048576.0)

        vfile_name[i] = _title
        vfile_size[i] = _size

        opciones.append(_caption)

    if len(opciones) > 1:
        d = xbmcgui.Dialog()
        seleccion = d.select("streamondemand-MCT: Lista dei vídeo", opciones)
    else: seleccion = 0

    if seleccion == -1:
        vfile_name[seleccion] = ""
        vfile_size[seleccion] = 0

    return seleccion, vfile_name[seleccion], vfile_size[seleccion]

# -- Preguntar si se desea borrar lo descargado -----------------
def remove_files( download, torrent_file, video_file, ses, h ):

    dialog_view = False
    torrent = False

    if os.path.isfile( torrent_file ):
        dialog_view = True
        torrent = True

    if download > 0:
        dialog_view = True

    if "/" in video_file: video_file = video_file.split("/")[0]

    if dialog_view:
        d = xbmcgui.Dialog()
        ok = d.yesno('streamondemand-MCT', 'Annullare il download', video_file)

        # -- SI -------------------------------------------------
        if ok:
            # -- Borrar archivo - torrent -----------------------
            if torrent:
                os.remove( torrent_file )
            # -- Borrar carpeta/archivos y sesión - vídeo -------
            ses.remove_torrent( h, 1 )
            print "### End session #########"
        else:
            # -- Borrar sesión ----------------------------------
            ses.remove_torrent( h )
            print "### End session #########"
    else:
        # -- Borrar sesión --------------------------------------
        ses.remove_torrent( h )
        print "### End session #########"

    return

# -- Descargar de la web los datos para crear el torrent --------
# -- Si queremos aligerar el script mct.py se puede importar la -
# -- función del conentor torrent.py                            -
def url_get(url, params={}, headers={}):
    from contextlib import closing

    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:20.0) Gecko/20100101 Firefox/20.0"

    if params:
        import urllib
        url = "%s?%s" % (url, urllib.urlencode(params))

    req = urllib2.Request(url)
    req.add_header("User-Agent", USER_AGENT)

    for k, v in headers.items():
        req.add_header(k, v)

    try:
        with closing(urllib2.urlopen(req)) as response:
            data = response.read()
            if response.headers.get("Content-Encoding", "") == "gzip":
                import zlib
                return zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(data)
            return data
    except urllib2.HTTPError:
        return None

# -- Procedimiento para log de have_piece en las pruebas --------
def print_have_piece_set(h, piece_set):
    c = 0
    _print = "\n"
    for i, _set in enumerate(piece_set):
        if h.have_piece(_set): _print+= "[%s]" % str(_set).zfill(5)
        else: _print+= "[XXXXX]"
        c+= 1
        if c == 20:
            c = 0
            _print+= "\n"
    print _print

# -- Contar las piezas contiguas completas del vídeo ------------
def count_completed_continuous_pieces(h, piece_set):
    not_zero = 0
    for i, _set in enumerate(piece_set):
        if not h.have_piece(_set): break
        else: not_zero = 1
    return i + not_zero

# -- Prioritarizar o seleccionar las piezas del archivo que se  -
# -- desea reproducir con 'file_priorities' estableciendo a 1   -
# -- el archivo deseado y a 0 el resto de archivos almacenando  -
# -- en una lista los índices de de las piezas del archivo      -
def set_priority_pieces(h, _index, video_file, video_size):

    for i, _set in enumerate(h.file_priorities()):
        if i != _index: h.file_priority(i,0)
        else: h.file_priority(i,1)

    piece_set = []
    for i, _set in enumerate(h.piece_priorities()):
        if _set == 1: piece_set.append(i)

    return piece_set
