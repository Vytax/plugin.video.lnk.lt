#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import sys
import re

import simplejson as json

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
  
  shows = []
  
  parts = re.findall('<a\s*.*?data\-program="([^"]*)".*?\s*<span\s*class="show\-title">([^<]*)<span', html, re.DOTALL)
  for link in parts:
    show = {}
    show['program'] = link[0]
    show['title'] = link[1]
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
  
  data = []
  
  r_href = re.compile('href="([^"]*)"', re.DOTALL)
  r_bi = re.compile("background-image: url\(\'([^\']*)\'\);", re.DOTALL)
  r_title = re.compile('<h2>([^<]*)<\/h2>', re.DOTALL)
  r_episode = re.compile('(\/\s*(\d+)\s*$)', re.DOTALL)
  r_aired = re.compile('class="date">(\d{4} \d{2} \d{2})\s*<\/span>', re.DOTALL)
  r_plot = re.compile('class="desc">([^<]*)</p>', re.DOTALL)
  
  parts = re.findall('<a[^<>]*class="grid\-item">.*?<\/a>', html, re.DOTALL)
  for part in parts:
    
    video = {}

    href = re.findall(r_href, part)

    if href:
      video['url'] = href[0]
    else:
      continue
    
    bi = re.findall(r_bi, part)
    if bi:
      video['thumbnailURL'] = LNK_URL + bi[0]
    
    title = re.findall(r_title, part)
    if title:
      video['title'] = title[0]
      
      episode = re.findall(r_episode, title[0])
      if episode:
	video['episode'] = int(episode[0][1])
    
    aired = re.findall(r_aired, part)
    if aired:
      video['aired'] = aired[0].replace(' ', '.')
      
    plot = re.findall(r_plot, part)
    if plot:
      video['plot'] = plot[0].strip()
    
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
  
  #if 'EpisodeVideoLink_HLS' in js:
    #result['videoURL'] = js['EpisodeVideoLink_HLS']
  #else:
    #return None
    
  if 'EpisodeVideoLink' in js:
    rtmp_url = js['EpisodeVideoLink']
    i = rtmp_url.find('mp4:')
    result['videoURL'] = rtmp_url[0:i] + ' playpath=' + rtmp_url[i:]
  else:
    return None
  
  if 'gTitle' in js:
    result['title'] = js['gTitle']
  
  if 'VideoCover' in js:
    result['thumbnailURL'] = LNK_URL + js['VideoCover']

  return result
