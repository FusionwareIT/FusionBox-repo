# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para safelinking (ocultador de url)
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#------------------------------------------------------------

from core import logger
from core import scrapertools


def get_long_url( short_url ):
    logger.info("[safelinking.py] get_long_url(short_url='%s')" % short_url)
    
    location = scrapertools.get_header_from_response(short_url,header_to_get="location")
    logger.info("location="+location)

    return location
