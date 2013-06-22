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

SACSID = 'AJKiYcGy_CtKRd_lWt7ALGhaatAX5o2al6wp_ALAdrsaN9JoMiZEj6vOhzU7O9-kguh4gVntlEUJn6rFhloXtJTHm85LuVEPuCE5WLH6QutNcMINyIL0n92v8lZwcHS0A9A4_FGdASxx0TBHZrv7s-HE1MEdiLnFAq72lot05pxnhm3RdqxPvNg2e0XrVhgamjUcja30n3mWwyhzrZNPsuZjGWUHUgUxwaiN9yWqURa0Aa2G7UideuBm2buesfCoGpbzvAgG_BUZZ9UhOu_5xSY1A6FBl1dTEknOgsRVzkkNIEXi475Id2puB9WGkn3o_7_zM_WGK-c-K2shaFwePXa4AmpD7iNa68LZKiSHpYiXZEO4bVzGnXLMOI6n4d8EbIPb5df1QIavTxRIEw-hIY92wvRAHVvkhHAPTWWU3b2hncW5t-38WDr-bh4LAyQBcQjvf6LzgOoApKd8A0NBCDWNY4E812BBkR5qHJkyX1_r_nFluzpaHrPIguBUGhjdwk4SWJp_MMFUjLA7kK8DWKjtLCdPaa78nDgUPCrGc8D_hnERxoFssQf0G2q4h_y3cGTOpBydyvqJ'
XSRF = 'oftfRavemc4ohG5UWlKpdsspAwg:1371919969911'

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

		#self.response.out.write("Ahoj")
		#return

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
				"playerLocation":"02fc2853,00dc2e1f",
				"location" : "02fc2853,00dc2e1f",
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
	  
		#self.response.out.write(result.content)
		#return
	  
		jsonResult = json.loads(result.content)

		gameEntities = jsonResult["gameBasket"]["gameEntities"]

		for gameEntity in gameEntities:

			if "portalV2" in gameEntity[2]:
				
				name = gameEntity[2]["portalV2"]["descriptiveText"]["TITLE"]
				lat = int(gameEntity[2]["locationE6"]["latE6"])/1E6
				lng = int(gameEntity[2]["locationE6"]["lngE6"])/1E6
				
				self.response.out.write(name + " (" + str(lat) + ", " + str(lng) + ")<br>")



INGRESSAPI_ROUTES = [
    ('/ingresstest', IngressApiHandler)
]
