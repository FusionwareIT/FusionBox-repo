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
# Updater daemon
# --------------------------------------------------------------------------------

import os
import re
import time

import config
import logger
import scrapertools

ROOT_DIR = config.get_runtime_path()

REMOTE_VERSION_FILE = "https://raw.githubusercontent.com/fusionse/plugin.video.fusionse/master/version.xml"
LOCAL_VERSION_FILE = os.path.join(ROOT_DIR, "version.xml")
LOCAL_FILE = os.path.join(ROOT_DIR, config.PLUGIN_NAME + "-")

# DESTINATION_FOLDER sera siempre el lugar donde este la carpeta del plugin,
# No hace falta "xbmc.translatePath", get_runtime_path() ya tiene que devolver la ruta correcta
DESTINATION_FOLDER = os.path.join(config.get_runtime_path(), "..")

REMOTE_FILE = "https://github.com/fusionse/plugin.video.fusionse/archive/master.zip"


def checkforupdates():
    logger.info("fusionse.core.updater checkforupdates")

    # Descarga el fichero con la versión en la web
    logger.info("fusionse.core.updater Verificando actualizaciones...")
    logger.info("fusionse.core.updater Version remota: " + REMOTE_VERSION_FILE)
    data = scrapertools.cachePage(REMOTE_VERSION_FILE)

    version_publicada = scrapertools.find_single_match(data, "<version>([^<]+)</version>").strip()
    tag_publicada = scrapertools.find_single_match(data, "<tag>([^<]+)</tag>").strip()
    logger.info("fusionse.core.updater version remota=" + tag_publicada + " " + version_publicada)

    # Lee el fichero con la versión instalada
    logger.info("fusionse.core.updater fichero local version: " + LOCAL_VERSION_FILE)
    data = open(LOCAL_VERSION_FILE).read()

    version_local = scrapertools.find_single_match(data, "<version>([^<]+)</version>").strip()
    tag_local = scrapertools.find_single_match(data, "<tag>([^<]+)</tag>").strip()

    logger.info("fusionse.core.updater version local=" + tag_local + " " + version_local)

    try:
        numero_version_publicada = int(version_publicada)
        numero_version_local = int(version_local)
    except:
        import traceback
        logger.info(traceback.format_exc())
        version_publicada = None
        version_local = None

    hayqueactualizar = False
    # Si no tenemos la versión, comprobamos el tag
    if version_publicada is None or version_local is None:
        logger.info("fusionse.core.updater comprobando el tag")
        from distutils.version import StrictVersion
        hayqueactualizar = StrictVersion(tag_publicada) > StrictVersion(tag_local)

    else:
        logger.info("fusionse.core.updater comprobando la version")
        hayqueactualizar = numero_version_publicada > numero_version_local

    # Si hay actualización disponible, devuelve la Nueva versión para que cada plataforma se encargue de mostrar los avisos
    if hayqueactualizar:
        return tag_publicada
    else:
        return None


def update(item):
    # Descarga el ZIP
    logger.info("fusionse.core.updater update")
    remotefilename = REMOTE_FILE
    localfilename = LOCAL_FILE + item.version + ".zip"
    if os.path.exists(localfilename):
        os.remove(localfilename)
    logger.info("fusionse.core.updater remotefilename=%s" % remotefilename)
    logger.info("fusionse.core.updater localfilename=%s" % localfilename)
    logger.info("fusionse.core.updater descarga fichero...")
    inicio = time.clock()

    # urllib.urlretrieve(remotefilename,localfilename)
    from core import downloadtools
    downloadtools.downloadfile(remotefilename, localfilename, continuar=False)

    fin = time.clock()
    logger.info("fusionse.core.updater Descargado en %d segundos " % (fin - inicio + 1))

    # Lo descomprime
    logger.info("fusionse.core.updater descomprime fichero...")
    import ziptools
    unzipper = ziptools.ziptools()
    destpathname = DESTINATION_FOLDER
    logger.info("fusionse.core.updater destpathname=%s" % destpathname)
    unzipper.extract(localfilename, destpathname)

    # Borra el zip descargado
    logger.info("fusionse.core.updater borra fichero...")
    os.remove(localfilename)
    logger.info("fusionse.core.updater ...fichero borrado")


def get_channel_remote_url(channel_name):
    _remote_channel_url_ = "https://raw.githubusercontent.com/fusionse/plugin.video.fusionse/master/"

    if channel_name != "channelselector":
        _remote_channel_url_ += "channels/"

    remote_channel_url = _remote_channel_url_ + channel_name + ".py"
    remote_version_url = _remote_channel_url_ + channel_name + ".xml"

    logger.info("fusionse.core.updater remote_channel_url=" + remote_channel_url)
    logger.info("fusionse.core.updater remote_version_url=" + remote_version_url)

    return remote_channel_url, remote_version_url


def get_channel_local_path(channel_name):
    # TODO: (3.2) El XML debería escribirse en el userdata, de forma que se leerán dos ficheros locales: el del userdata y el que está junto al py (vendrá con el plugin). El mayor de los 2 es la versión actual, y si no existe fichero se asume versión 0
    if channel_name != "channelselector":
        local_channel_path = os.path.join(config.get_runtime_path(), 'channels', channel_name + ".py")
        local_version_path = os.path.join(config.get_runtime_path(), 'channels', channel_name + ".xml")
        local_compiled_path = os.path.join(config.get_runtime_path(), 'channels', channel_name + ".pyo")
    else:
        local_channel_path = os.path.join(config.get_runtime_path(), channel_name + ".py")
        local_version_path = os.path.join(config.get_runtime_path(), channel_name + ".xml")
        local_compiled_path = os.path.join(config.get_runtime_path(), channel_name + ".pyo")

    logger.info("fusionse.core.updater local_channel_path=" + local_channel_path)
    logger.info("fusionse.core.updater local_version_path=" + local_version_path)
    logger.info("fusionse.core.updater local_compiled_path=" + local_compiled_path)

    return local_channel_path, local_version_path, local_compiled_path


def updatechannel(channel_name):
    logger.info("fusionse.core.updater updatechannel('" + channel_name + "')")

    # Canal remoto
    remote_channel_url, remote_version_url = get_channel_remote_url(channel_name)

    # Canal local
    local_channel_path, local_version_path, local_compiled_path = get_channel_local_path(channel_name)

    # Version remota
    try:
        data = scrapertools.cachePage(remote_version_url)
        logger.info("fusionse.core.updater remote_data=" + data)

        if "<tag>" in data:
            patronvideos = '<tag>([^<]+)</tag>'
        elif "<version>" in data:
            patronvideos = '<version>([^<]+)</version>'

        matches = re.compile(patronvideos, re.DOTALL).findall(data)
        remote_version = int(matches[0])
    except:
        remote_version = 0

    logger.info("fusionse.core.updater remote_version=%d" % remote_version)

    # Version local
    if os.path.exists(local_version_path):
        infile = open(local_version_path)
        data = infile.read()
        infile.close()
        logger.info("fusionse.core.updater local_data=" + data)

        if "<tag>" in data:
            patronvideos = '<tag>([^<]+)</tag>'
        elif "<version>" in data:
            patronvideos = '<version>([^<]+)</version>'

        matches = re.compile(patronvideos, re.DOTALL).findall(data)

        local_version = int(matches[0])
    else:
        local_version = 0
    logger.info("fusionse.core.updater local_version=%d" % local_version)

    # Comprueba si ha cambiado
    updated = remote_version > local_version

    if updated:
        logger.info("fusionse.core.updater updated")
        download_channel(channel_name)

    return updated


def download_channel(channel_name):
    logger.info("fusionse.core.updater download_channel('" + channel_name + "')")
    # Canal remoto
    remote_channel_url, remote_version_url = get_channel_remote_url(channel_name)

    # Canal local
    local_channel_path, local_version_path, local_compiled_path = get_channel_local_path(channel_name)

    # Descarga el canal
    updated_channel_data = scrapertools.cachePage(remote_channel_url)
    try:
        outfile = open(local_channel_path, "wb")
        outfile.write(updated_channel_data)
        outfile.flush()
        outfile.close()
        logger.info("fusionse.core.updater Grabado a " + local_channel_path)
    except:
        logger.info("fusionse.core.updater Error al grabar " + local_channel_path)
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    # Descarga la version (puede no estar)
    try:
        updated_version_data = scrapertools.cachePage(remote_version_url)
        outfile = open(local_version_path, "w")
        outfile.write(updated_version_data)
        outfile.flush()
        outfile.close()
        logger.info("fusionse.core.updater Grabado a " + local_version_path)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    if os.path.exists(local_compiled_path):
        os.remove(local_compiled_path)


def get_server_remote_url(server_name):
    _remote_server_url_ = "https://raw.githubusercontent.com/fusionse/plugin.video.fusionse/master/servers/"

    remote_server_url = _remote_server_url_ + server_name + ".py"
    remote_version_url = _remote_server_url_ + server_name + ".xml"

    logger.info("fusionse.core.updater remote_server_url=" + remote_server_url)
    logger.info("fusionse.core.updater remote_version_url=" + remote_version_url)

    return remote_server_url, remote_version_url


def get_server_local_path(server_name):
    local_server_path = os.path.join(config.get_runtime_path(), 'servers', server_name + ".py")
    local_version_path = os.path.join(config.get_runtime_path(), 'servers', server_name + ".xml")
    local_compiled_path = os.path.join(config.get_runtime_path(), 'servers', server_name + ".pyo")

    logger.info("fusionse.core.updater local_servers_path=" + local_server_path)
    logger.info("fusionse.core.updater local_version_path=" + local_version_path)
    logger.info("fusionse.core.updater local_compiled_path=" + local_compiled_path)

    return local_server_path, local_version_path, local_compiled_path


def updateserver(server_name):
    logger.info("fusionse.core.updater updateserver('" + server_name + "')")

    # Canal remoto
    remote_server_url, remote_version_url = get_server_remote_url(server_name)

    # Canal local
    local_server_path, local_version_path, local_compiled_path = get_server_local_path(server_name)

    # if not os.path.exists(local_server_path):
    #    return False;

    # Version remota
    try:
        data = scrapertools.cachePage(remote_version_url)
        logger.info("fusionse.core.updater remote_data=" + data)

        if "<tag>" in data:
            patronvideos = '<tag>([^<]+)</tag>'
        elif "<version>" in data:
            patronvideos = '<version>([^<]+)</version>'

        matches = re.compile(patronvideos, re.DOTALL).findall(data)
        remote_version = int(matches[0])
    except:
        remote_version = 0

    logger.info("fusionse.core.updater remote_version=%d" % remote_version)

    # Version local
    if os.path.exists(local_version_path):
        infile = open(local_version_path)
        data = infile.read()
        infile.close()
        logger.info("fusionse.core.updater local_data=" + data)

        if "<tag>" in data:
            patronvideos = '<tag>([^<]+)</tag>'
        elif "<version>" in data:
            patronvideos = '<version>([^<]+)</version>'

        matches = re.compile(patronvideos, re.DOTALL).findall(data)

        local_version = int(matches[0])
    else:
        local_version = 0
    logger.info("fusionse.core.updater local_version=%d" % local_version)

    # Comprueba si ha cambiado
    updated = remote_version > local_version

    if updated:
        logger.info("fusionse.core.updater updated")
        download_server(server_name)

    return updated


def download_server(server_name):
    logger.info("fusionse.core.updater download_server('" + server_name + "')")
    # Canal remoto
    remote_server_url, remote_version_url = get_server_remote_url(server_name)

    # Canal local
    local_server_path, local_version_path, local_compiled_path = get_server_local_path(server_name)

    # Descarga el canal
    updated_server_data = scrapertools.cachePage(remote_server_url)
    try:
        outfile = open(local_server_path, "wb")
        outfile.write(updated_server_data)
        outfile.flush()
        outfile.close()
        logger.info("fusionse.core.updater Grabado a " + local_server_path)
    except:
        logger.info("fusionse.core.updater Error al grabar " + local_server_path)
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    # Descarga la version (puede no estar)
    try:
        updated_version_data = scrapertools.cachePage(remote_version_url)
        outfile = open(local_version_path, "w")
        outfile.write(updated_version_data)
        outfile.flush()
        outfile.close()
        logger.info("fusionse.core.updater Grabado a " + local_version_path)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    if os.path.exists(local_compiled_path):
        os.remove(local_compiled_path)
