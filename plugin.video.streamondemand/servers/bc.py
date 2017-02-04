# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Conector para bc (acortador de url)
# http://www.mimediacenter.info/foro/viewforum.php?f=36
# ------------------------------------------------------------

import urllib
import requests
import re
import time
import json
from core import logger
from core import scrapertools



def get_long_url(short_url):
    logger.info("servers.bc get_long_url(short_url='%s')" % short_url)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.46 Safari/535.11",
            "Accept-Encoding": "gzip,deflate,sdch",
            "Accept-Language": "en-US,en;,q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "bc.vc",
            "Referer": short_url,
            "Origin": "http://bc.vc",
            "X-Requested-With": "XMLHttpRequest"}
        session = requests.session()
        r = session.get(short_url, headers=headers)
        html = r.text.encode('utf-8')
        html = re.sub(r"\s+", '', html)
        args = re.findall(r"aid:(\d+),lid:(\d+),oid:(\d+)", html, re.S)
        aid = args[0][0]
        lid = args[0][1]
        oid = args[0][2]
        
        payload_make_log = 'opt=make_log&args[aid]=' + aid+ '&args[lid]='+ lid +'&args[oid]=' + oid +'&args[afg]=&args[bfg]=&args[cfg]=&args[dfg]=&args[efg]=&args[ref]='+ short_url  +'&args[nok]=no&args[mob]=no'
        payload_check_log = 'opt=check_log&args[aid]=' + aid+ '&args[lid]='+ lid +'&args[oid]=' + oid +'&args[afg]=&args[bfg]=&args[cfg]=&args[dfg]=&args[efg]=&args[ref]='+ short_url  +'&args[nok]=no&args[mob]=no'
        payload_checks_log = {'opt':'checks_log'}
        
        uri = ''
        count = 0   
        while (count < 9 and uri ==''):
            L = 'http://bc.vc/fly/ajax.fly.php'
            r = session.post(L, payload_checks_log, cookies=session.cookies, headers=headers)
           
            time.sleep(2)
            r = session.post(L, payload_check_log, cookies=session.cookies, headers=headers)
            
            time.sleep(2)
            r = session.post(L, payload_make_log, cookies=session.cookies, headers=headers)
            
            data = json.loads(r.text)

            if data['message'] and len(data['message']['url']) > 1:
                uri = data['message']['url']
                 
        
        return uri

    except Exception as e:
        return short_url
        