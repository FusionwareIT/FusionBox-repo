# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# fusionse - XBMC Plugin
# update_servers.py
# http://www.mimediacenter.info/foro/viewforum.php?f=36
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
        t = Thread(target=updater.updateserver, args=[server_name])
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
