#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib

import xbmcgui
import xbmcplugin
import xbmcaddon

import liblnk as lnk

settings = xbmcaddon.Addon(id='plugin.video.lnk.lt')

def getParameters(parameterString):
  commands = {}
  splitCommands = parameterString[parameterString.find('?') + 1:].split('&')
  for command in splitCommands:
    if (len(command) > 0):
      splitCommand = command.split('=')
      key = splitCommand[0]
      value = splitCommand[1]
      commands[key] = value
  return commands

def build_main_directory():
  
  data = lnk.getLandingPage()

  if data:
    for item in data:

      i_url = sys.argv[0]

      if 'id' in item:
        i_url = i_url + '?id=%d' % item['id']
      elif 'feed' in item:
        i_url = i_url + '?feed=%d' % item['feed']
      elif 'filterId' in item:
        i_url = i_url + '?filterId=%d' % item['filterId']
      else:
        continue

      listitem = xbmcgui.ListItem(item['title'])
      listitem.setProperty('IsPlayable', 'false')
      xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = i_url, listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem('Mediateka')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?media=start', listitem = listitem, isFolder = True, totalItems = 0)

  listitem = xbmcgui.ListItem('Paieška')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?searchStart=1', listitem = listitem, isFolder = True, totalItems = 0) 
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def loadDirectory(dir, page=-1, page_params={}):

  for item in dir:
    listitem = xbmcgui.ListItem(item['title'])
    listitem.setProperty('IsPlayable', 'true')

    if 'thumbnailURL' in item:
      listitem.setThumbnailImage(item['thumbnailURL'])
      del item['thumbnailURL']

    video_id = item['video_id']
    del item['video_id']
    listitem.setInfo(type = 'video', infoLabels = item )
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode({'video_id': video_id}), listitem = listitem, isFolder = False, totalItems = 0)

  if page >= 0 and len(dir) > 39:
    listitem = xbmcgui.ListItem("[Daugiau... ] %d" % (page + 1))
    listitem.setProperty('IsPlayable', 'false')
      
    page_params['page'] = page + 1
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(page_params), listitem = listitem, isFolder = True, totalItems = 0)


  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(503)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def loadIdDirectory(dir_id):

  data = lnk.getVideosFromLandingPage(dir_id)
  loadDirectory(data)

def loadFilterDirectory(filterId, page):

  if page < 1:
    page = 1

  data = lnk.getVideosFromFilterPage(filterId, page)
  loadDirectory(data, page, {'filterId': filterId})

def loadMediaDirectory(mediaID, page=-1):
  
  if mediaID == 'start':

    data = lnk.getMediatekaPage()

    for item in data:
      listitem = xbmcgui.ListItem(item['title'])
      listitem.setProperty('IsPlayable', 'false')
      xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode({'media': item['urlSegment']}), listitem = listitem, isFolder = True, totalItems = 0)

    xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
    xbmc.executebuiltin('Container.SetViewMode(503)')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

  else:

    if page < 1:
      page = 1

    data = lnk.getMediatekaPage(mediaID, page)
    loadDirectory(data, page, {'media': mediaID})

def searchVideo(key='', page=-1):

  if page < 1:
    page = 1

  if not key:
    dialog = xbmcgui.Dialog()
    key = dialog.input('Vaizdo įrašo paieška', type=xbmcgui.INPUT_ALPHANUM)

  if key:
    data = lnk.searchVideo(key, page)
    loadDirectory(data, page, {'search': key})

def playVideo(video_id):
  
  data = lnk.getVideo(video_id)
  
  if not data:
    dialog = xbmcgui.Dialog()
    ok = dialog.ok( "LNK TV" , 'Nepavyko paleisti vaizdo įrašo!' )
    return
  
  listitem = xbmcgui.ListItem(label = data['title'])
  listitem.setPath(data['videoURL'])
  if 'thumbnailUrl' in data:
    listitem.setThumbnailImage(data['thumbnailUrl'])
  xbmcplugin.setResolvedUrl(handle = int(sys.argv[1]), succeeded = True, listitem = listitem)
  
# **************** main ****************

path = sys.argv[0]
params = getParameters(sys.argv[2])
page = -1

if 'page' in params:
  page = int(params['page'])

if 'id' in params:
  loadIdDirectory(int(params['id']))
elif 'video_id' in params:
  playVideo(urllib.unquote_plus(params['video_id']))
elif 'filterId' in params:
  loadFilterDirectory(int(params['filterId']), page)
elif 'media' in params:
  loadMediaDirectory(urllib.unquote_plus(params['media']), page)
elif 'searchStart' in params:
  searchVideo(None)
elif 'search' in params:
  searchVideo(urllib.unquote_plus(params['search']), page)
else:
  build_main_directory()
