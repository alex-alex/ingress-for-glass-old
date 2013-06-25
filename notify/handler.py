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

"""Request Handler for /notify endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import io
import json
import logging
import webapp2

from apiclient.http import MediaIoBaseUpload
from oauth2client.appengine import StorageByKeyName
from model import Credentials
import util
import ingressapi

_BUNDLE_ID = "ingress_bundle"

class NotifyHandler(webapp2.RequestHandler):
  """Request Handler for notification pings."""

  def post(self):
    """Handles notification pings."""
    logging.info('Got a notification with payload %s', self.request.body)
    data = json.loads(self.request.body)
    userid = data['userToken']
    # TODO: Check that the userToken is a valid userToken.
    self.mirror_service = util.create_service(
        'mirror', 'v1',
        StorageByKeyName(Credentials, userid, 'credentials').get())
    if data.get('collection') == 'locations':
      self._handle_locations_notification(data)
    elif data.get('collection') == 'timeline':
      self._handle_timeline_notification(data)

  def _handle_locations_notification(self, data):
    """Handle locations notification."""
    location = self.mirror_service.locations().get(id=data['itemId']).execute()
			
	###################################################
	
    if not "longitude" in location or not "latitude" in location:
        # Incomplete location information
        return

    gameEntities = ingressapi.handler.getGameEntities()

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
	        map += "marker=0;%s,%s" % (lat, lng)

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

  def _handle_timeline_notification(self, data):
    """Handle timeline notification."""
    for user_action in data.get('userActions', []):
      if user_action.get('type') == 'SHARE':
        # Fetch the timeline item.
        item = self.mirror_service.timeline().get(id=data['itemId']).execute()
        attachments = item.get('attachments', [])
        media = None
        if attachments:
          # Get the first attachment on that timeline item and do stuff with it.
          attachment = self.mirror_service.timeline().attachments().get(
              itemId=data['itemId'],
              attachmentId=attachments[0]['id']).execute()
          resp, content = self.mirror_service._http.request(
              attachment['contentUrl'])
          if resp.status == 200:
            media = MediaIoBaseUpload(
                io.BytesIO(content), attachment['contentType'],
                resumable=True)
          else:
            logging.info('Unable to retrieve attachment: %s', resp.status)
        body = {
            'text': 'Echoing your shared item: %s' % item.get('text', ''),
            'notification': {'level': 'DEFAULT'}
        }
        self.mirror_service.timeline().insert(
            body=body, media_body=media).execute()
        # Only handle the first successful action.
        break
      elif user_action.get('type') == 'HACK':
        item = self.mirror_service.timeline().get(id=data['itemId']).execute()
        break
      else:
        logging.info(
            "I don't know what to do with this notification: %s", user_action)


NOTIFY_ROUTES = [
    ('/notify', NotifyHandler)
]
