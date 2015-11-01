#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import sys
import re

import simplejson as json
from BeautifulSoup import BeautifulSoup

LNK_URL = 'http://lnkgo.alfa.lt'
LNK_LATEST_VIDEOS = LNK_URL + '/visi-video/list/new?start=%d'
LNK_POPULAR_VIDEOS = LNK_URL + '/visi-video/list/popular?start=%d'
LNK_END_SOON_VIDEOS = LNK_URL + '/visi-video/list/catchup?start=%d'
LNK_ALL_VIDEOS = LNK_URL + '/visi-video/'
LNK_PROGRAM = LNK_URL + '/visi-video/%s/list?start=%d'
LNK_SEARCH =  LNK_URL + '/visi-video/search/?Search=%s&start=%d'

def getURL(url):
  
  res = urllib.urlopen(url)
  return res.read()

reload(sys) 
sys.setdefaultencoding('utf8')

def getTvShowsList():
  
  html = getURL(LNK_ALL_VIDEOS)  
  soup = BeautifulSoup(html)
  
  if not soup:
    return None
  
  shows = []
  
  for link in soup.findAll('a', { 'data-type' : 'program' } ):
    
    show = {}
    
    program = link.get('data-program')
    if program:
      show['program'] = program
    else:
      continue
      
    title = link.findAll('span', { 'class' : 'show-title' } )
    if title:
      show['title'] = title[0].getText().strip()
    else:
      continue
    
    shows.append(show)
  
  return shows

def search(key, page=0):
  return getInfo(LNK_SEARCH % (urllib.quote_plus(key.strip()), page * 35))

def getTvShow(program, page=0):
  return getInfo(LNK_PROGRAM % (program, page * 35))
  
def get_end_soon_videos(page=0):
  return getInfo(LNK_END_SOON_VIDEOS % (page * 35))

def get_popular_videos(page=0):
  return getInfo(LNK_POPULAR_VIDEOS % (page * 35))

def get_latest_videos(page=0):
  return getInfo(LNK_LATEST_VIDEOS % (page * 35))

def getInfo(url):
  html = getURL(url)
  html = re.sub('<p\s+class="time-left">.*?<\/p>', '', html)
  soup = BeautifulSoup(html)
  
  if not soup:
    return None
  
  data = []
  for link in soup.findAll('a', { 'class' : 'grid-item' } ):
    
    video = {}
   
    title = link.findAll('h2')    
    if title:
      title = title[0].getText()
      
      episode = re.findall('(\/\s*(\d+)\s*$)', title)
      if episode:
	video['episode'] = int(episode[0][1])
	
	#title = title[:-len(episode[0][0])].strip()
      
      video['title'] = title
        
    style = link.get('style')
    if style:
      bi = re.findall("background-image: url\(\'([^\']*)\'\);", style)
      if bi:
	video['thumbnailURL'] = LNK_URL + bi[0]
    
    url = link.get('href')
    if url:
      video['url'] = url
    else:
      continue
      
    date = link.findAll('span', { 'class' : 'date'})
    if date:
      video['aired'] = date[0].getText().replace(' ', '.')
    
    plot = link.findAll('p', { 'class' : 'desc' })
    if plot:
      video['plot'] = plot[0].getText().strip()
    
    data.append(video)
    
  return data 

def getVideo(url):
  
  html = getURL(LNK_URL + url)  
  data = re.findall('episodePlayer\(({.*?)}\s*,\s*{(.*?})\);', html, re.DOTALL)
  
  if not data:
    return None
  
  js = json.loads(data[0][0] + ', ' + data[0][1])
  if not js:
    return None
  
  result = {}
  
  if 'EpisodeVideoLink_HLS' in js:
    result['videoURL'] = js['EpisodeVideoLink_HLS']
  else:
    return None
  
  if 'gTitle' in js:
    result['title'] = js['gTitle']
  
  if 'VideoCover' in js:
    result['thumbnailURL'] = LNK_URL + js['VideoCover']

  return result
  

if __name__ == '__main__': 
  print getTvShowsList()