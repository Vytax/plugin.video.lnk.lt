#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import sys

import simplejson as json

LNK_URL = 'http://lnk.lt'
LNK_API = LNK_URL +  '/api/main/'
LNK_LANDING_PAGE = LNK_API + 'landing-page'
LNK_IMAGE_PATH = LNK_URL + '/all-images/'
LNK_VIDEO_PATH = LNK_API + 'video-page/%s/false/0'
LNK_FILTER_PATH = LNK_API + 'feed-page-by-filter/%d/%d'
LNK_SEARCH_PATH = LNK_API + 'feed-page-by-phrase/%s/%d'
LNK_MEDIATEKA_PATH = LNK_API + 'mediateka-search'

WowzaVodUrl = 'https://vod.lnk.lt/lnk_vod/lnk/lnk/mp4:'

def getURL(url):
  
  res = urllib.urlopen(url)
  return res.read()

reload(sys) 
sys.setdefaultencoding('utf8')

def getLandingPage():

  json_data = getURL(LNK_LANDING_PAGE)
  js = json.loads(json_data)
  if not js:
    return None

  if 'components' not in js:
    return None

  result = []

  for id, item in enumerate(js['components']):

    r_item = {}

    if 'type' not in item or 'component' not in item:
      continue

    i_type = item['type']
    component = item['component']

    if i_type == 1:
      if 'videos' not in component:
        continue

      r_item['title'] = "Aktualu"
      r_item['id'] = id

    elif i_type == 2:
      if 'title' not in component or 'filterId' not in component:
        continue

      r_item['title'] = component['title']
      r_item['filterId'] = component['filterId']

    elif i_type == 3:

      if 'title' not in component or 'videos' not in component:
        continue

      r_item['title'] = component['title']
      r_item['id'] = id

    else:
      continue

    result.append(r_item)

  return result

def parseVideos(i_list):

  result = []

  for item in i_list:

    if type(item) == list:
      r_item = parseVideos(item)
      result.extend(r_item)

    else:

      r_item = {}

      r_item['title'] = item['title']

      if 'description' in item and item['description']:
        r_item['plot'] = item['description']
      if 'duration' in item:
        r_item['duration'] = item['duration']
      if 'airDateText' in item:
        r_item['aired'] = item['airDateText']
      if 'posterImage' in item and item['posterImage']:
        r_item['thumbnailURL'] = LNK_IMAGE_PATH + item['posterImage']
      if 'episodeNumber' in item and item['episodeNumber']:
        r_item['episode'] = int(item['episodeNumber'])
        r_item['title'] = r_item['title'] + ' (%d)' % r_item['episode']

      if 'id' not in item:
        continue

      r_item['video_id'] = item['urlSegment'] + '/%d' % item['id']

      result.append(r_item)

  return result

def getVideosFromLandingPage(i_id):

  json_data = getURL(LNK_LANDING_PAGE)
  js = json.loads(json_data)
  if not js:
    return None

  if 'components' not in js or len(js['components']) < i_id:
    return None

  item = js['components'][i_id]

  if 'component' not in item or 'videos' not in item['component']:
    return None

  return parseVideos(item['component']['videos'])

def getVideosFromPage(url):

  json_data = getURL(url)
  js = json.loads(json_data)
  if not js:
    return None

  if 'components' not in js or not js['components']:
    return None

  result = []

  for item in js['components']:
    if 'component' not in item or 'videos' not in item['component']:
      continue

    result.extend(parseVideos(item['component']['videos']))

  return result

def getVideosFromFilterPage(filterId, page=1):

  return getVideosFromPage(LNK_FILTER_PATH % (filterId, page))

def getMediatekaPage(uid='', page=1):

  url = LNK_MEDIATEKA_PATH

  if uid:
    url = url + '?program=%s&pageIndex=%d' % (urllib.quote_plus(uid), page)

  json_data = getURL(url)
  js = json.loads(json_data)
  if not js:
    return None

  if uid:
    if 'videoGrid' in js and 'videos' in js['videoGrid']:
      return parseVideos(js['videoGrid']['videos'])
  else:
    if 'programs' in js:
      return js['programs']

  return None

def searchVideo(key, page=1):

  return getVideosFromPage(LNK_SEARCH_PATH % (urllib.quote_plus(key), page))

def getVideo(video_id):
  
  json_data = getURL(LNK_VIDEO_PATH % video_id)  
  
  js = json.loads(json_data)
  if not js:
    return None

  item = {}
  if 'videoConfig' in js and 'videoInfo' in js['videoConfig']:
    item = js['videoConfig']['videoInfo']
  else:
    return None  

  result = {}
  
  if 'videoUrl' in item and item['videoUrl']:
    result['videoURL'] = WowzaVodUrl + item['videoUrl'] + '/playlist.m3u8'
    print result['videoURL']
  else:
    return None
    
  if 'title' in item:
    result['title'] = item['title']
  
  if 'posterImage' in item:
    result['thumbnailURL'] = LNK_IMAGE_PATH + item['posterImage']

  return result
