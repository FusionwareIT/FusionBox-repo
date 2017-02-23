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
# update_servers.py
# ------------------------------------------------------------

import glob
import os
from threading import Thread

from core import config
from core import updater

DEBUG = config.get_setting("debug")


### Procedures
def update_servers():
    server_path = os.path.join(config.get_runtime_path(), "servers", '*.xml')

    server_files = glob.glob(server_path)

    # ----------------------------
    import xbmcgui
    progress = xbmcgui.DialogProgressBG()
    progress.create("Update servers list")
    # ----------------------------

    for index, server in enumerate(server_files):
        # ----------------------------
        percentage = index * 100 / len(server_files)
        # ----------------------------
        server_name = os.path.basename(server)[:-4]
        t = Thread(target=updater.update_server, args=[server_name])
        t.setDaemon(True)
        t.start()
        # ----------------------------
        progress.update(percentage, ' Update server: ' + server_name)
        # ----------------------------

    # ----------------------------
    progress.close()
    # ----------------------------


### Run
Thread(target=update_servers).start()
