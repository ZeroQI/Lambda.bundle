# -*- coding: utf-8 -*-
'''
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
  if agent_type=='Movies':  return os.path.split(os.path.splitext(media.items[0].parts[0].file)[0])
  if agent_type=='TV_Shows':
    dirs=[]
    for s in media.seasons if media else []: # TV_Show:
      for e in media.seasons[s].episodes:
        dir = os.path.dirname(media.seasons[s].episodes[e].items[0].parts[0].file)
        if dir not in dirs:  dirs.append(dir)
    for dir in dirs:
      if dir.startswith('Season'): return os.path.dirname(dir), ''
    else:
      if len(dirs)==1:  return dir, ''
      else:             return os.path.dirname(dir), ''

def SaveFile(filename, content, field=''):
  if os.path.exists(filename):
    Log.Info('[#] {}: {}'.format(field, os.path.basename(filename)))
  else:
    Log.Info('[*] {}: {}'.format(field, os.path.basename(filename)))
    try:
      with open(filename, 'wb') as file:  file.write(content)
    except Exception as e:  Log.Info('Exception: "{}"'.format(e))

def Start():
  HTTP.CacheTime                  = CACHE_1MONTH
  HTTP.Headers['User-Agent'     ] = 'Mozilla/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.54'
  HTTP.Headers['Accept-Language'] = 'en-us'

### Download metadata using unique ID ###
def Search(results, media, lang, manual, agent_type):
  
  Log(''.ljust(157, '='))
  Log.Info('Search(metadata, media="{}", lang="{}", manual={}, agent_type={})'.format(media.title, lang, manual, agent_type))
  metadata = media.primary_metadata
  
  ### PLEX_LIBRARY_URL ###
  PLEX_LIBRARY = {}
  try:
    PLEX_LIBRARY_XML = XML.ElementFromURL(PLEX_LIBRARY_URL, timeout=float(TIMEOUT))
    for library in PLEX_LIBRARY_XML.iterchildren('Directory'):
      for  path in library.iterchildren('Location'):
        PLEX_LIBRARY[path.get("path")] = library.get("key")
  except Exception as e:  Log.Info("Exception: '{}'".format(e))
  Log.Info('PLEX_LIBRARY: {}'.format(PLEX_LIBRARY))
  
  ### PLEX_TVSHOWS_URL ###
  #count= 0
  #while True:
  #  PLEX_TVSHOWS_XML = XML.ElementFromURL(PLEX_TVSHOWS_URL.format(count, WINDOW_SIZE), timeout=float(TIMEOUT))
  #  count +=1
  #  if  int(partMedias.get('size')) == 0 or bScanStatus == 3:  break
  #
  
  ### PLEX_SEASONS_URL ###
  ### Season loop for season posters
  #PLEX_SEASONS_XML = XML.ElementFromURL(PLEX_TVSHOWS_URL.format(count, WINDOW_SIZE), timeout=float(TIMEOUT))
  
  ### PLEX_COLLECT_URL ###
  ### Collection loop for collection poster, summary
  #PLEX_COLLECT_XML = XML.ElementFromURL(PLEX_TVSHOWS_URL.format(count, WINDOW_SIZE), timeout=float(TIMEOUT))

  ###Series loop for posters, art, themes
  #http://127.0.0.1:32400/library/sections/X/all?type=2
  #posterUrl = ''.join((misc.GetLoopBack(), '/photo/:/transcode?width=', str(Prefs['Poster_Width']), '&height=', str(Prefs['Poster_Hight']),'&minSize=1&url=', String.Quote(rowentry['Poster url'])))
  #try:
  #  with io.open(os.path.join(posterDir, rowentry['Media ID'] + '.jpg'), 'wb') as handler:
  #    handler.write(HTTP.Request(posterUrl).content)
  #except Exception, e:  Log.Exception('Exception was %s' % str(e))
     
  '''
  
  @route(PREFIX + '/scanMovieDB')
  def scanMovieDB(myMediaURL, outFile):
    Log.Debug("*** Starting scanMovieDB with an URL of %s ***" % myMediaURL)
    Log.Debug('Movie Export level is %s' % Prefs['Movie_Level'])
    global bScanStatusCount, bScanStatusCountOf, global bScanStatus
    bScanStatusCount, bScanStatusCountOf, iCurrent = 0, 0, 0
    try:
        Log.Debug("About to open file %s" % outFile)
        output.createHeader(outFile, 'movies')
        bExtraInfo = False if Prefs['Movie_Level'] in moviefields.singleCall else True
        while True:
            Log.Debug("Walking medias")
            iCount     = bScanStatusCount
            partMedias = XML.ElementFromURL(''.join((myMediaURL, '?X-Plex-Container-Start=', str(iCurrent), '&X-Plex-Container-Size=', str(CONTAINERSIZEMOVIES))), timeout=float(PMSTIMEOUT))
            if bScanStatusCount == 0:
                bScanStatusCountOf = partMedias.get('totalSize')
                Log.Debug('Amount of items in this section is %s' % bScanStatusCountOf)
            Log.Debug("Retrieved part of medias okay [%s of %s]" % ( str(bScanStatusCount), str(bScanStatusCountOf)))
            medias = partMedias.xpath('.//Video')
            for media in medias:
                if bExtraInfo:  media = XML.ElementFromURL(genParam(''.join((misc.GetLoopBack(), '/library/metadata/', misc.GetRegInfo(media, 'ratingKey') )) ),  timeout=float(PMSTIMEOUT)).xpath('//Video')[0]
                myRow = {}
                output.writerow(movies.getMovieInfo(media, myRow))
                iCurrent         += 1
                bScanStatusCount += 1
                Log.Debug("Media #%s from database: '%s'" % ( str(iCurrent),  misc.GetRegInfo(media, 'title')))
            # Got to the end of the line?
            if int(partMedias.get('size')) == 0 or bScanStatus == 3:  break
        output.closefile()
    except ValueError, Argument:
        Log.Critical('Unknown error in scanMovieDb %s' % Argument)
        bScanStatus = 99
        raise
    Log.Debug("******* Ending scanMovieDB ***********")
  '''
  
  #--------------------------------------------------------------------------------------------------------------------------------------------------
  if agent_type in ('Movies', 'TV_Shows'):
  
    #dir, filenoext = GetMediaDir (media, agent_type)
    #folder/poster/show show-2.ext
    #art/backdrop/background/fanart
    results.Append(MetadataSearchResult(id = 'null', name=media.title, score = 100))
    
  #--------------------------------------------------------------------------------------------------------------------------------------------------
  if agent_type=='Movies':
    pass
    #folder/poster/show show-2.ext
    #art/backdrop/background/fanart
    
  #--------------------------------------------------------------------------------------------------------------------------------------------------
  if agent_type=='TV_Shows':
    
    dir, _ = GetMediaDir(media, agent_type)  #Log.Info(dir)
    for root in [os.sep.join(dir.split(os.sep)[0:x+2]) for x in range(0, dir.count(os.sep))]:
      if root in PLEX_LIBRARY:
        key = PLEX_LIBRARY[root]
        Log.Info('key: {}, root: {}'.format(key, root))
        break
    else:  key='';  Log.Info('[!] Library access denied')  #401 no right to list libraries (windows)
    
    ###Theme song "theme.mp3”
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
        
    results.Append(MetadataSearchResult(id = 'null', name=media.show, score = 100))
  #--------------------------------------------------------------------------------------------------------------------------------------------------
  if agent_type=='Artist':
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
          
    results.Append(MetadataSearchResult(id = 'null', name=media.artist, score = 100))
  #--------------------------------------------------------------------------------------------------------------------------------------------------
  if agent_type=='Album':
    results.Append(MetadataSearchResult(id = 'null', score = 100))
  Log(''.ljust(157, '='))

def Update(metadata, media, lang, force, agent_type):
  pass
  
### Agent declaration ##################################################################################################################################################
class LMETVAgent(Agent.TV_Shows):  # 'com.plexapp.agents.none', 'com.plexapp.agents.opensubtitles'
  name, primary_provider, fallback_agent, contributes_to, accepts_from = 'LME', False, False, ['com.plexapp.agents.localmedia', 'com.plexapp.agents.hama'], ['com.plexapp.agents.localmedia', 'com.plexapp.agents.hama']
  languages = [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
  def search (self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'TV_Shows')
  def update (self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'TV_Shows')

class LMEMovieAgent(Agent.Movies):
  name, primary_provider, fallback_agent, contributes_to, accepts_from = 'LME', False, False, ['com.plexapp.agents.localmedia', 'com.plexapp.agents.hama'], ['com.plexapp.agents.localmedia', 'com.plexapp.agents.hama']
  languages = [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
  def search (self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'Movies')
  def update (self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'Movies')

class LMEArtistAgent(Agent.Artist):
  contributes_to       = ['com.plexapp.agents.discogs', 'com.plexapp.agents.lastfm', 'com.plexapp.agents.plexmusic', 'com.plexapp.agents.none']
  languages            = [Locale.Language.NoLanguage]  #[Locale.Language.English]
  name                 = 'LME'
  primary_provider     = False
  persist_stored_files = False
  def search(self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'Artist')
  def update(self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'Artist')
    
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
PLEX_TVSHOWS_URL = 'http://127.0.0.1:32400/library/sections/{}/all?type=2&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_SEASONS_URL = 'http://127.0.0.1:32400/library/sections/{}/all?type=3&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_COLLECT_URL = 'http://127.0.0.1:32400/library/sections/X/all?type=18&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
TIMEOUT          = 30
WINDOW_SIZE      = {'Movies': 30, 'TV_Shows': 20, 'Artist': 10, 'Album': 10, 'Photo': 20}
