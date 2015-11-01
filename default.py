#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib

import xbmcgui
import xbmcplugin
import xbmcaddon

import liblnk as lnk

settings = xbmcaddon.Addon(id='plugin.video.delfi.lt')

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
  
  listitem = xbmcgui.ListItem('Naujausi video')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=1&page=0', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Populiariausi video')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=2&page=0', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Greitai baigsis')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=3&page=0', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Laidos')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=4', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Paieška')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=5&page=0', listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))


def loadCategory(cat, page, url=None):
  
  videos = []
  
  if cat == 1:
    videos = lnk.get_latest_videos(page)
  elif cat == 2:
    videos = lnk.get_popular_videos(page)
  elif cat == 3:
    videos = lnk.get_end_soon_videos(page)
  elif mode == 5:
    if not url:
      dialog = xbmcgui.Dialog()
      url = dialog.input('Vaizdo įrašo paieška', type=xbmcgui.INPUT_ALPHANUM)
    if url:
      videos = lnk.search(url, page)
  elif cat == 20:
    videos = lnk.getTvShow(url, page)
    
  for video in videos:
    listitem = xbmcgui.ListItem(video['title'])
    listitem.setProperty('IsPlayable', 'true')
      
    info = { 'title': video['title'], 'plot': video['plot']}
    
    if 'aired' in video:
      info['aired'] = video['aired']
        
    if 'episode' in video:
      info['episode'] = video['episode']
        
    listitem.setInfo(type = 'video', infoLabels = info )
    
    if 'thumbnailURL' in video:
      listitem.setThumbnailImage(video['thumbnailURL'])
      
    u = {}
    u['mode'] = 10
    u['url'] = video['url']
      
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = False, totalItems = 0)
    
  if videos and (len(videos)>33):
    listitem = xbmcgui.ListItem("[Daugiau... ] %d" % (page + 1))
    listitem.setProperty('IsPlayable', 'false')
      
    u = {}
    u['mode'] = mode
    u['page'] = page + 1
    if url:
      u['url'] = url
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
    
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(503)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def playVideo(url):
  
  data = lnk.getVideo(url)
  
  if not data:
    dialog = xbmcgui.Dialog()
    ok = dialog.ok( "DELFI TV" , 'Nepavyko paleisti vaizdo įrašo!' )
    return
    
  listitem = xbmcgui.ListItem(label = data['title'])
  listitem.setPath(data['videoURL'])
  if 'thumbnailUrl' in data:
    listitem.setThumbnailImage(data['thumbnailUrl'])
  xbmcplugin.setResolvedUrl(handle = int(sys.argv[1]), succeeded = True, listitem = listitem)
  
def build_tv_shows_list():
  
  shows = lnk.getTvShowsList()
  
  for show in shows:
    u = {}
    u['mode'] = 20
    u['url'] = show['program']
    u['page'] = 0
    listitem = xbmcgui.ListItem(show['title'])
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
    
  xbmcplugin.setContent(int( sys.argv[1] ), 'tvshows')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
  

# **************** main ****************

path = sys.argv[0]
params = getParameters(sys.argv[2])
mode = None
page = None
url = None

try:
  mode = int(params["mode"])
except:
  pass

try:
  page = int(params["page"])
except:
  pass

try:
  url = urllib.unquote_plus(params["url"])
except:
  pass
     
if mode == None:
  build_main_directory()
elif mode in [1, 2, 3, 5, 20]:
  loadCategory(mode, page, url)
elif mode == 4:
  build_tv_shows_list()
elif mode == 10:
  playVideo(url)
  