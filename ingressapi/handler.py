# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Ingress API"""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import webapp2
from google.appengine.api import urlfetch
from model import Credentials
import util
import json
import logging

SACSID = 'AJKiYcGy_CtKRd_lWt7ALGhaatAX5o2al6wp_ALAdrsaN9JoMiZEj6vOhzU7O9-kguh4gVntlEUJn6rFhloXtJTHm85LuVEPuCE5WLH6QutNcMINyIL0n92v8lZwcHS0A9A4_FGdASxx0TBHZrv7s-HE1MEdiLnFAq72lot05pxnhm3RdqxPvNg2e0XrVhgamjUcja30n3mWwyhzrZNPsuZjGWUHUgUxwaiN9yWqURa0Aa2G7UideuBm2buesfCoGpbzvAgG_BUZZ9UhOu_5xSY1A6FBl1dTEknOgsRVzkkNIEXi475Id2puB9WGkn3o_7_zM_WGK-c-K2shaFwePXa4AmpD7iNa68LZKiSHpYiXZEO4bVzGnXLMOI6n4d8EbIPb5df1QIavTxRIEw-hIY92wvRAHVvkhHAPTWWU3b2hncW5t-38WDr-bh4LAyQBcQjvf6LzgOoApKd8A0NBCDWNY4E812BBkR5qHJkyX1_r_nFluzpaHrPIguBUGhjdwk4SWJp_MMFUjLA7kK8DWKjtLCdPaa78nDgUPCrGc8D_hnERxoFssQf0G2q4h_y3cGTOpBydyvqJ'
XSRF = 'oftfRavemc4ohG5UWlKpdsspAwg:1371919969911'

_BUNDLE_ID = "ingress_bundle"


def getGameEntities():
	headers = {
		"Content-Type" : "application/json;charset=UTF-8",
		#"Accept-Encoding" : "gzip",
		"User-Agent" : "Nemesis (gzip)",
		"X-XsrfToken" : XSRF,
		"Host" : "m-dot-betaspike.appspot.com",
		"Connection" : "Keep-Alive",
		"Cookie" : "SACSID=%s" % (SACSID),
	}

	form_fields = {
		"params": {
			"playerLocation":"0304bd77,00d2f4fb",
			"location" : "0304bd77,00d2f4fb",
			"knobSyncTimestamp":0,
			"energyGlobGuids":[],
			"cellsAsHex":["470b948d90000000","470b9492d0000000","470b948d50000000","470b948c50000000","470b949210000000","470b949310000000","470b94ed30000000","470b948e10000000","470b948d10000000","470b949250000000","470b948dd0000000","470b949290000000","470b94f2b0000000","470b9492f0000000","470b94f2d0000000","470b9491f0000000","470b948db0000000","470b949230000000","470b949330000000","470b94ed50000000","470b948e70000000","470b948d70000000","470b949270000000","470b948d30000000","470b9492b0000000","470b9493b0000000","470b948df0000000","470b948cf0000000"],
			"dates":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

		}
	}
	form_data = json.dumps(form_fields)
	
	result = urlfetch.fetch(url="https://m-dot-betaspike.appspot.com/rpc/gameplay/getObjectsInCells",
                          payload=form_data,
                          method=urlfetch.POST,
                          headers=headers)
  
	jsonResult = json.loads(result.content)

	gameEntities = jsonResult["gameBasket"]["gameEntities"]
	
	return gameEntities

class IngressApiHandler(webapp2.RequestHandler):
	@util.auth_required
	def get(self):

	    gameEntities = getGameEntities()

	    # 1. retrieve current bundle cards and delete non-cover cards
	    current_cards = self.mirror_service.timeline().list(bundleId=_BUNDLE_ID).execute()

	    bundleCoverId = None
	    if "items" in current_cards:
	        for card in current_cards["items"]:
	            if "isBundleCover" in card and card["isBundleCover"] == True:
	                bundleCoverId = card["id"]
	                break
               
	        for card in current_cards["items"]:
	            if bundleCoverId is None or card["id"] != bundleCoverId:
	                # delete old cards
	                self.mirror_service.timeline().delete(id=card["id"]).execute()
                
	    # 2. create or update cover card
	    map = "glass://map?w=640&h=360&"
	    #map += "marker=0;%s,%s" % (location["latitude"], location["longitude"])
	    i = 1
	    for gameEntity in gameEntities:
	        if "portalV2" in gameEntity[2]:
	            lat = int(gameEntity[2]["locationE6"]["latE6"])/1E6
	            lng = int(gameEntity[2]["locationE6"]["lngE6"])/1E6
	            map += "&marker=%s;%s,%s" % (i-1, lat, lng)
	            i = i + 1
	            if i > 10:
	                break

	    count = i - 1
	    html = "<article class=\"photo\">"
	    html += "<img src=\"%s\" width=\"100%%\" height=\"100%%\">" % map
	    html += "<div class=\"photo-overlay\"></div>"
	    html += "<footer><div>%s portal%s nearby</div></footer>" % (count, "" if count == 1 else "s")
	    html += "</article>"

	    if bundleCoverId is None:
	        body = {}
	        body["html"] = html
	        body["bundleId"] = _BUNDLE_ID
	        body["isBundleCover"] = True
	        result = self.mirror_service.timeline().insert(body=body).execute()
	        logging.info(result)
	    else:
	        result = self.mirror_service.timeline().update(id=bundleCoverId, body={"html": html}).execute()
	        logging.info(result)
    
	    # 3. create up to 10 detailed cards
	    i = 1
    
	    hackAction = {}
	    hackAction["action"] = "CUSTOM"
	    hackAction["id"] = "HACK"
	    actionValue = {}
	    actionValue["state"] = "DEFAULT"
	    actionValue["displayName"] = "Hack"
	    actionValue["iconUrl"] = "https://ingressforglass.appspot.com/static/images/drill.png"
	    hackAction["values"] = [actionValue]

	    for gameEntity in gameEntities:
	        if "portalV2" in gameEntity[2]:

		        name = gameEntity[2]["portalV2"]["descriptiveText"]["TITLE"]
		        lat = int(gameEntity[2]["locationE6"]["latE6"])/1E6
		        lng = int(gameEntity[2]["locationE6"]["lngE6"])/1E6

		        body = {}
		        map = "glass://map?w=200&h=200&"
		        #map += "marker=0;%s,%s" % (location["latitude"], location["longitude"])
		        map += "&marker=0;%s,%s" % (lat, lng)

		        html = "<article><section>"
		        html += "<div class=\"layout-two-column\">"
		        html += "<div class=\"align-center\"><img src=\"%s\" width=\"200\" height=\"200\"></div>" % map
		        html += "<div class=\"align-center\"><img src=\"%s\" width=\"200\" height=\"200\"></div>" % gameEntity[2]["imageByUrl"]["imageUrl"]
		        html += "</div></section>"
		        html += "<footer><p>%s</p></footer>" % name
		        html += "</article>"

		        body["html"] = html
		        body["bundleId"] = _BUNDLE_ID
		        body["isBundleCover"] = False
		        body["location"] = {}
		        body["location"]["latitude"] = lat
		        body["location"]["longitude"] = lng
		        body["sourceItemId"] = gameEntity[0]
		        #body["canonicalUrl"] = "https://ingressforglass.appspot.com/checkin/place/%s" % (place["reference"])
        
		        body["menuItems"] = []
		        body["menuItems"].append({"action": "NAVIGATE"})
		        body["menuItems"].append(hackAction)
        
		        result = self.mirror_service.timeline().insert(body=body).execute()

		        i = i + 1
		        if i > 10:
		            break

INGRESSAPI_ROUTES = [
    ('/ingresstest', IngressApiHandler)
]
