# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# fusionse - XBMC Plugin
# update_channels.py
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------
import glob
import os
from threading import Thread

from core import config
from core import updater

DEBUG = config.get_setting("debug")


### Procedures
def update_channels():
    channel_path = os.path.join(config.get_runtime_path(), "channels", '*.xml')

    channel_files = glob.glob(channel_path)

    # ----------------------------
    import xbmcgui
    progress = xbmcgui.DialogProgressBG()
    progress.create("Update channels list")
    # ----------------------------

    for index, channel in enumerate(channel_files):
        # ----------------------------
        percentage = index * 100 / len(channel_files)
        # ----------------------------
        channel_id = os.path.basename(channel)[:-4]
        t = Thread(target=updater.updatechannel, args=[channel_id])
        t.setDaemon(True)
        t.start()
        # ----------------------------
        progress.update(percentage, ' Update channel: ' + channel_id)
        # ----------------------------

    # ----------------------------
    progress.close()
    # ----------------------------


### Run
Thread(target=update_channels).start()
