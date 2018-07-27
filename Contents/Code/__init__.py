# -*- coding: utf-8 -*-
'''
- [ ] Stage 1: Movies: Poster, art saved if not present or if file changed
- [ ] Stage 2: TV: Single series poster art, season themes thumbs
- [ ] Stage 3: Music libraries
- [ ] Stage 4: Collections
- [ ] Stage 5: NFO + import NFO
'''

### Imports ###
import os          # path.abspath, join, dirname
import re          #
import inspect     # getfile, currentframe
import urllib2     # Request
import time        # sleep
import hashlib
from   io          import open  #

###
def natural_sort_key(s):
  return [int(text) if text.isdigit() else text for text in re.split(re.compile('([0-9]+)'), str(s).lower())]  # list.sort(key=natural_sort_key) #sorted(list, key=natural_sort_key) - Turn a string into string list of chunks "z23a" -> ["z", 23, "a"]

### Get media root folder ###
def GetLibraryRootPath(dir):
  library, root, path = '', '', ''
  for root in [os.sep.join(dir.split(os.sep)[0:x+2]) for x in range(0, dir.count(os.sep))]:
    if root in PLEX_LIBRARY:
      library = PLEX_LIBRARY[root]
      path    = os.path.relpath(dir, root)
      break
  else:  #401 no right to list libraries (windows)
    Log.Info('[!] Library access denied')
    filename = os.path.join(CachePath, '_Logs', '_root_.scanner.log')
    if os.path.isfile(filename):
      Log.Info('[!] ASS root scanner file present: "{}"'.format(filename))
      try:
        with open(filename, 'r', -1, 'utf-8') as file:  line=file.read()
      except Exception as e:  line='';  Log.Info('Exception: "{}"'.format(e))

      for root in [os.sep.join(dir.split(os.sep)[0:x+2]) for x in range(dir.count(os.sep)-1, -1, -1)]:
        if "root: '{}'".format(root) in line:
          path = os.path.relpath(dir, root).rstrip('.')
          break
        Log.Info('[!] root not found: "{}"'.format(root))
      else: path, root = '_unknown_folder', '';  
    else:  Log.Info('[!] ASS root scanner file missing: "{}"'.format(filename))
  return library, root, path

def GetMediaDir (media, agent_type):
  if agent_type=='movie':  return os.path.dirname(media.items[0].parts[0].file)
  if agent_type=='show':
    dirs=[]
    for s in media.seasons if media else []: # TV_Show:
      for e in media.seasons[s].episodes:
        dir = os.path.dirname(media.seasons[s].episodes[e].items[0].parts[0].file)
        if dir not in dirs:  dirs.append(dir)
    for dir in dirs:
      if dir.startswith('Season'): return os.path.dirname(dir), ''
    else:
      if len(dirs)==1:  return dir
      else:             return os.path.dirname(dir)

def SaveFile(source, destination, field=''):
  try:                    content = HTTP.Request(source).content
  except Exception as e:  Log.Info('Exception: "{}"'.format(e));  return
  if os.path.exists(destination) and os.path.getsize(destination)==len(content):  Log.Info('[=] {}: {}'.format(field, os.path.basename(destination)))
  else:
    Log.Info('[{}] {}: {}'.format('!' if os.path.exists(destination) else '*', field, os.path.basename(destination)))
    try:
      with open(destination, 'wb') as file:
        file.write(content)
    except Exception as e:  Log.Info('Exception: "{}"'.format(e))

def Start():
  HTTP.CacheTime                  = CACHE_1MONTH
  HTTP.Headers['User-Agent'     ] = 'Mozilla/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.54'
  HTTP.Headers['Accept-Language'] = 'en-us'

### Download metadata using unique ID ###
def Search(results, media, lang, manual, agent_type):

  metadata = media.primary_metadata

  #--------------------------------------------------------------------------------------------------------------------------------------------------
  if agent_type=='movie':
    
    #folder/poster/show show-2.ext
    #art/backdrop/fanart/fanart
    results.Append(MetadataSearchResult(id = 'null', name=media.title, score = 100))
    
  #--------------------------------------------------------------------------------------------------------------------------------------------------
  if agent_type=='show':
    '''  
    dir, _ = GetMediaDir(media, agent_type)  #Log.Info(dir)
    for root in [os.sep.join(dir.split(os.sep)[0:x+2]) for x in range(0, dir.count(os.sep))]:
      if root in PLEX_LIBRARY:
        key = PLEX_LIBRARY[root]
        Log.Info('key: {}, root: {}'.format(key, root))
        break
    else:  key='';  Log.Info('[!] Library access denied')  #401 no right to list libraries (windows)

    ###Theme song "theme.mp3"
    for url in metadata.themes.keys():  SaveFile(os.path.join(dir, 'themes.mp3'), metadata.themes[url], 'themes');  break
    else: Log.Info("[ ] themes: None")

    ###Series poster
    #posters = metadata.posters
    #Log.Info("{}".format(dir(posters.keys)))
    #for url in posters.keys():
      #filename = 'season-specials-poster' if season=='0' else 'Season{:02}'.format(int(season))
      #if len(posters.keys()) > 1:  filename += chr(ord('a')+posters.keys().index(url))
      #SaveFile(os.path.join(dir, filename+os.path.splitext(url)[1]), posters[url], 'posters')
      #if posters.keys().index(url)==25:  break
    #  pass

    ###Season loop
    for season in sorted(media.seasons, key=natural_sort_key):  # For each season, media, then use metadata['season'][season]...
      Log.Info("metadata.seasons[{:>2}]".format(season).ljust(157, '-'))

      dirs=[]
      for episode in media.seasons[season].episodes:
        dir = os.path.dirname(media.seasons[season].episodes[episode].items[0].parts[0].file)
        if dir not in dirs:  dirs.append(dir)

      #Season poster
      #Log.Info(metadata.seasons[season].attrs.keys())
      #for i in inspect.getmembers(metadata.seasons[season]):  # Ignores anything starting with underscore (that is, private and protected attributes)
      #  Log.Info(i)
      for url in metadata.seasons[season].posters.keys():
        filename = 'season-specials-poster' if season=='0' else 'Season{:02}'.format(int(season))
        if len(metadata.seasons[season].posters.keys()) > 1:  filename += chr(ord('a')+metadata.seasons[season].posters.keys().index(url))
        SaveFile(os.path.join(dir, filename+os.path.splitext(url)[1]), metadata.seasons[season].posters[url], 'posters')
        if metadata.seasons[season].posters.keys().index(url)==25:  break

      ###Episodes Loop
      for episode in sorted(media.seasons[season].episodes, key=natural_sort_key):
        Log.Info("metadata.seasons[{:>2}].episodes[{:>3}]".format(season, episode))
        dir, file = os.path.split(media.seasons[season].episodes[episode].items[0].parts[0].file)
        thumbs    = getattr(metadata.seasons[season].episodes[episode], 'thumbs')
        for url in thumbs.keys():  SaveFile(os.path.join(dir, os.path.join(os.path.splitext(file)[0]+os.path.splitext(url)[1])), thumbs[url], 'thumbs');  break
        else:                      Log.Info('thumbs.keys(): {}'.format(thumbs.keys()))
    '''    
    results.Append(MetadataSearchResult(id = 'null', name=media.show, score = 100))
  #--------------------------------------------------------------------------------------------------------------------------------------------------
  if agent_type=='artist':
    '''
    metadata.title = None  # Clear out the title to ensure stale data doesn't clobber other agents' contributions.

    for album in media.children:
      Log.Info('[ ] Album title: {}'.format(album.title))
      #Log.Info('[ ] Album posters:      {}'.format(metadata.keys()))
      for track in album.children:
        file     = track.items[0].parts[0].file
        filename = os.path.basename(file)
      Log.Info('[ ] Artist:      {}'.format(media.title))
    Log.Info('[ ] Artist posters:      {}'.format(metadata.posters.keys()))
    Log.Info('[ ] Artist art:          {}'.format(metadata.art.keys()))
    for album in media.children:
      Log.Info('[ ] Album title: {}'.format(album.title))
      #Log.Info('[ ] Album posters:      {}'.format(metadata.keys()))
      for track in album.children:
        file     = track.items[0].parts[0].file
        filename = os.path.basename(file)
        path     = os.path.dirname (file)
        ext      = filename[1:] if filename.count('.')==1 and file.startswith('.') else os.path.splitext(filename)[1].lstrip('.').lower()
        title    = filename[:-len(ext)+1]
        lrc      = filename[:-len(ext)+1]+'.lrc'

        # Chech if lrc file present
        if os.path.exists(lrc):  Log.Info('[X] Track: {}, filename: {}, file: {}'.format('', lrc, file))
        else:
          Log.Info('[ ] Track title: {}, file: {}'.format(track.title, file))
          # Check if embedded lrc and decompress
          # https://github.com/dmo60/lLyrics/issues/26
    '''      
    results.Append(MetadataSearchResult(id = 'null', name=media.artist, score = 100))
  #--------------------------------------------------------------------------------------------------------------------------------------------------
  if agent_type=='album':
    results.Append(MetadataSearchResult(id = 'null', score = 100))
  Log(''.ljust(157, '='))

def Update(metadata, media, lang, force, agent_type):

  Log(''.ljust(157, '='))
  Log.Info('Update(metadata, media="{}", lang="{}", force={}, agent_type={})'.format(media.title, lang, force, agent_type))
  dir         = GetMediaDir(media, agent_type)
  collections = []
    
  ### PLEX_LIBRARY_URL - Plex libraries ###
  PLEX_LIBRARY = {}
  key, path = '', ''
  try:
    PLEX_LIBRARY_XML = XML.ElementFromURL(PLEX_LIBRARY_URL, timeout=float(TIMEOUT))
    for directory in PLEX_LIBRARY_XML.iterchildren('Directory'):
      Log.Info('Library: [{:>2}] [{:<6}] {}'.format(directory.get('key'), directory.get('type'), directory.get('title')))
      if agent_type==directory.get('type'):
        for location in directory:
          if dir and location.get("path") in dir:
            Log.Info('[=] id: {:>2}, path: {}'.format(location.get("id"), location.get("path")))
            PLEX_LIBRARY[location.get("path")] = directory.get("key")
            key  = directory.get("key")
            path = location.get("path")
          else:                                    Log.Info('[ ] id: {:>2}, path: {}'.format(location.get("id"), location.get("path")))

  except Exception as e:  Log.Info("Exception: '{}'".format(e))
  Log.Info('PLEX_LIBRARY: {}'.format(PLEX_LIBRARY))

  ### Movies ###
  if agent_type=='movie':
    
    filenoext = os.path.basename(os.path.splitext(media.items[0].parts[0].file)[0])
    
    ### PLEX_MOVIES_URL - MOVIES ###
    count, found    = 0, False
    parentRatingKey = ""
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_MOVIES_XML = XML.ElementFromURL(PLEX_MOVIES_URL.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        total = int(PLEX_MOVIES_XML.get('totalSize'))
        Log.Debug("PLEX_MOVIES_URL [{}-{} of {}]".format(count+1, count+int(PLEX_MOVIES_XML.get('size')) ,total))
        for video in PLEX_MOVIES_XML.iterchildren('Video'):
          if media.title==video.get('title'):   
            #Log.Info(XML.StringFromElement(PLEX_MOVIES_XML))  #Un-comment for XML code displayed in logs
            Log.Info('title:                 {}'.format(video.get('title')))
            #if video.get('summary'              ):  Log.Info('summary:               {}'.format(video.get('summary')))
            #if video.get('contentRating'        ):  Log.Info('contentRating:         {}'.format(video.get('contentRating')))
            #if video.get('studio'               ):  Log.Info('studio:                {}'.format(video.get('studio')))
            #if video.get('rating'               ):  Log.Info('rating:                {}'.format(video.get('rating')))
            #if video.get('year'                 ):  Log.Info('year:                  {}'.format(video.get('year')))
            #if video.get('duration'             ):  Log.Info('duration:              {}'.format(video.get('duration')))
            #if video.get('originallyAvailableAt'):  Log.Info('originallyAvailableAt: {}'.format(video.get('originallyAvailableAt')))
            #if video.get('key'      ):  Log.Info('[ ] key:                   {}'.format(video.get('key'      ))); 
            #if video.get('ratingKey'):  parentRatingKey = video.get('ratingKey')
            if Prefs['movies_poster'] and video.get('thumb'    ):  SaveFile(PLEX_SERVER_NAME+video.get('thumb' ), os.path.join(dir, filenoext+       '.jpg'), 'poster')
            if Prefs['movies_fanart'] and video.get('art'      ):  SaveFile(PLEX_SERVER_NAME+video.get('art'   ), os.path.join(dir, filenoext+'-fanart.jpg'), 'art'   )
            for collection in video.iterchildren('Collection'):  Log.Info('collection:            {}'.format(collection.get('tag')));  collections.append(collection.get('tag'))
            found = True
            break
        else:  count += WINDOW_SIZE[agent_type];  continue
        break      
      except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     


  ### TV Shows ###
  if agent_type=='show':

    ### PLEX_TVSHOWS_URL - TV Shows###
    count, found    = 0, False
    parentRatingKey = ""
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_TVSHOWS_XML = XML.ElementFromURL(PLEX_TVSHOWS_URL.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        total = int(PLEX_TVSHOWS_XML.get('totalSize'))
        Log.Debug("PLEX_TVSHOWS_URL [{}-{} of {}]".format(count+1, count+int(PLEX_TVSHOWS_XML.get('size')) ,total))
        for show in PLEX_TVSHOWS_XML.iterchildren('Directory'):
          if media.title==show.get('title'):   
            Log.Info('title:                 {}'.format(show.get('title')))
            #if show.get('summary'              ):  Log.Info('summary:               {}'.format(show.get('summary')))
            #if show.get('contentRating'        ):  Log.Info('contentRating:         {}'.format(show.get('contentRating')))
            #if show.get('studio'               ):  Log.Info('studio:                {}'.format(show.get('studio')))
            #if show.get('rating'               ):  Log.Info('rating:                {}'.format(show.get('rating')))
            #if show.get('year'                 ):  Log.Info('year:                  {}'.format(show.get('year')))
            #if show.get('duration'             ):  Log.Info('duration:              {}'.format(show.get('duration')))
            #if show.get('originallyAvailableAt'):  Log.Info('originallyAvailableAt: {}'.format(show.get('originallyAvailableAt')))
            #if show.get('key'      ):  Log.Info('[ ] key:                   {}'.format(show.get('key'      ))); 
            if show.get('ratingKey'):  parentRatingKey = show.get('ratingKey')
            if Prefs['series_poster'] and show.get('thumb'    ):  SaveFile(PLEX_SERVER_NAME+show.get('thumb' ), os.path.join(dir, 'poster.jpg'), 'poster')
            if Prefs['series_fanart'] and show.get('art'      ):  SaveFile(PLEX_SERVER_NAME+show.get('art'   ), os.path.join(dir, 'fanart.jpg'), 'art'   )
            if Prefs['series_banner'] and show.get('banner'   ):  SaveFile(PLEX_SERVER_NAME+show.get('banner'), os.path.join(dir, 'banner.jpg'), 'banner')
            if Prefs['series_themes'] and show.get('theme'    ):  SaveFile(PLEX_SERVER_NAME+show.get('theme' ), os.path.join(dir, 'theme.mp3' ), 'theme' )
            for collection in show.iterchildren('Collection'):  Log.Info('collection:            {}'.format(collection.get('tag')));  collections.append(collection.get('tag'))
            #Log.Info(XML.StringFromElement(show))  #Un-comment for XML code displayed in logs
            found = True
            break
        else:  count += WINDOW_SIZE[agent_type];  continue
        break      
      except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     

    ### PLEX_SEASONS_URL  - TV Shows seasons ###
    count, found = 0, False
    while count==0 or count<total and int(PLEX_SEASONS_XML.get('size')) == WINDOW_SIZE[agent_type]:
      try:
        PLEX_SEASONS_XML = XML.ElementFromURL(PLEX_SEASONS_URL.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        total  = PLEX_SEASONS_XML.get('totalSize')
        Log.Debug("PLEX_SEASONS_URL [{}-{} of {}]".format(count+1, count+int(PLEX_SEASONS_XML.get('size')) ,total))
        for show in PLEX_SEASONS_XML.iterchildren('Directory'):
          if parentRatingKey == show.get('parentRatingKey'):  #parentTitle
            #Log.Info(XML.StringFromElement(show))
            Log.Debug("title: '{}'".format(show.get('title')))
            if show.get('thumb'    ):  SaveFile(PLEX_SERVER_NAME+show.get('thumb' ), os.path.join(dir, show.get('title') if os.path.exists(os.path.join(dir, show.get('title'))) else '', 'season-specials-poster.jpg' if show.get('title')=='Specials' else show.get('title')+'-poster.jpg'), 'season_poster')
            if show.get('art'      ):  SaveFile(PLEX_SERVER_NAME+show.get('art'   ), os.path.join(dir, show.get('title') if os.path.exists(os.path.join(dir, show.get('title'))) else '', 'season-specials-fanart.jpg' if show.get('title')=='Specials' else show.get('title')+'-fanart.jpg'), 'season_art'   )
      except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     
      count += WINDOW_SIZE[agent_type]
    ### transcoding picture
    #  with io.open(os.path.join(posterDir, rowentry['Media ID'] + '.jpg'), 'wb') as handler:
    #    handler.write(HTTP.Request('http://127.0.0.1:32400/photo/:/transcode?width={}&height={}&minSize=1&url={}', String.Quote(rowentry['Poster url'])).content)
    #except Exception, e:  Log.Exception('Exception was %s' % str(e))

  ### PLEX_COLLECT_URL - Collection loop for collection poster, summary ###
  count = 0
  while collections and (count==0 or count<total and int(PLEX_COLLECT_XML.get('size')) == WINDOW_SIZE[agent_type]):
    try:
      PLEX_COLLECT_XML = XML.ElementFromURL(PLEX_COLLECT_URL.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
      total  = PLEX_COLLECT_XML.get('totalSize')
      Log.Debug("PLEX_COLLECT_URL size: [{}-{} of {}]".format(count+1, count+int(PLEX_COLLECT_XML.get('size')), total))
      for directory in PLEX_COLLECT_XML.iterchildren('Directory'):
        if  directory.get('title') in collections:
          #Log.Info(XML.StringFromElement(PLEX_COLLECT_XML))
          Log.Debug("[ ] Directory: '{}'".format( directory.get('title') ))
          dirname = os.path.join(path, '_Collections', directory.get('title'))
          #Log.Info('summary:               {}'.format(directory.get('summary')))
          if (directory.get('art') or directory.get('thumb')) and not os.path.exists(dirname):  os.makedirs(dirname)
          if Prefs['collection_poster'] and directory.get('thumb'):  SaveFile(PLEX_SERVER_NAME+directory.get('thumb' ), os.path.join(dirname, 'poster.jpg'), 'collection_poster')
          if Prefs['collection_fanart'] and directory.get('art'  ):  SaveFile(PLEX_SERVER_NAME+directory.get('art'   ), os.path.join(dirname, 'fanart.jpg'), 'collection_fanart')
    except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     
    count += WINDOW_SIZE[agent_type]
  
  if agent_type=='artist':
    pass

  if agent_type=='album':
    pass

### Agent declaration ##################################################################################################################################################
class LMETVAgent(Agent.TV_Shows):  # 'com.plexapp.agents.none', 'com.plexapp.agents.opensubtitles'
  name, primary_provider, fallback_agent, contributes_to, accepts_from = 'LME', False, False, ['com.plexapp.agents.localmedia', 'com.plexapp.agents.hama'], ['com.plexapp.agents.localmedia', 'com.plexapp.agents.hama']
  languages = [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
  def search (self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'show')
  def update (self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'show')

class LMEMovieAgent(Agent.Movies):
  name, primary_provider, fallback_agent, contributes_to, accepts_from = 'LME', False, False, ['com.plexapp.agents.localmedia', 'com.plexapp.agents.hama'], ['com.plexapp.agents.localmedia', 'com.plexapp.agents.hama']
  languages = [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
  def search (self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'movie')
  def update (self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'movie')

class LMEArtistAgent(Agent.Artist):
  contributes_to       = ['com.plexapp.agents.discogs', 'com.plexapp.agents.lastfm', 'com.plexapp.agents.plexmusic', 'com.plexapp.agents.none']
  languages            = [Locale.Language.NoLanguage]  #[Locale.Language.English]
  name                 = 'LME'
  primary_provider     = False
  persist_stored_files = False
  def search(self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'artist')
  def update(self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'artist')

class LMEAlbumAgent(Agent.Album):
  contributes_to       = ['com.plexapp.agents.discogs', 'com.plexapp.agents.lastfm', 'com.plexapp.agents.plexmusic', 'com.plexapp.agents.none']
  languages            = [Locale.Language.NoLanguage]  #[Locale.Language.English]
  name                 = 'LME'
  primary_provider     = False
  persist_stored_files = False
  def search(self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'Album')
  def update(self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'Album')

### Variables ###
PlexRoot         = os.path.abspath(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), "..", "..", "..", ".."))
CachePath        = os.path.join(PlexRoot, "Plug-in Support", "Data", "com.plexapp.agents.hama", "DataItems")
PLEX_LIBRARY_URL = 'http://127.0.0.1:32400/library/sections'  
PLEX_MOVIES_URL  = 'http://127.0.0.1:32400/library/sections/{}/all?type=1&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_TVSHOWS_URL = 'http://127.0.0.1:32400/library/sections/{}/all?type=2&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_SEASONS_URL = 'http://127.0.0.1:32400/library/sections/{}/all?type=3&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_COLLECT_URL = 'http://127.0.0.1:32400/library/sections/{}/all?type=18&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
#PLEX_ALBUM_URL   = 'http://127.0.0.1:32400/library/sections/{}/all?type=18&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
#PLEX_ARTIST_URL  = 'http://127.0.0.1:32400/library/sections/{}/all?type=18&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_SERVER_NAME = 'http://127.0.0.1:32400'
WINDOW_SIZE      = {'movie': 30, 'show': 20, 'artist': 10, 'Album': 10}
TIMEOUT          = 30
#(/library/metadata/<ratingkey>/art/<artid>
#/library/metadata/<ratingkey>).thumb