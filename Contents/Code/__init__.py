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
from   lxml        import etree      # fromstring

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
  
  ### Plex Library XML ###
  PLEX_LIBRARY, PLEX_LIBRARY_URL = {}, "http://127.0.0.1:32400/library/sections/"    # Allow to get the library name to get a log per library https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token
  if Prefs['token']:  PLEX_LIBRARY_URL += "?X-Plex-Token=" + Prefs['token']  #Log.Info("Prefs['token']: {}".format(Prefs['token']))
  try:
    library_xml = etree.fromstring(urllib2.urlopen(PLEX_LIBRARY_URL).read())
    for library in library_xml.iterchildren('Directory'):
      for path in library.iterchildren('Location'):
        PLEX_LIBRARY[path.get("path")] = library.get("key")
        Log.Info( path.get("path") + " = " + library.get("key") )
  except Exception as e:  Log.Info("Exception: '{}'".format(e))
  Log.Info('PLEX_LIBRARY: {}'.format(PLEX_LIBRARY))
  
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
    
    '''
    #library items    http://127.0.0.1:32400/library/sections?X-Plex-Token=
    Collection list  http://127.0.0.1:32400/library/sections/X/all?type=18&X-Plex-Token=
    Series list      http://127.0.0.1:32400/library/sections/X/all?type=2&X-Plex-Token=
    Season           http://127.0.0.1:32400/library/sections/X/all?type=3&X-Plex-Token=
    posterUrl = ''.join((misc.GetLoopBack(), '/photo/:/transcode?width=', str(Prefs['Poster_Width']), '&height=', str(Prefs['Poster_Hight']),'&minSize=1&url=', String.Quote(rowentry['Poster url'])))
    try:
      with io.open(os.path.join(posterDir, rowentry['Media ID'] + '.jpg'), 'wb') as handler:
        handler.write(HTTP.Request(posterUrl).content)
    except Exception, e:  Log.Exception('Exception was %s' % str(e))
    '''   
    
    
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
      Log.Info(metadata.attrs.keys())
      for i in inspect.getmembers(metadata):  # Ignores anything starting with underscore (that is, private and protected attributes)
        Log.Info(i)
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
PlexRoot          = os.path.abspath(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), "..", "..", "..", ".."))
CachePath         = os.path.join(PlexRoot, "Plug-in Support", "Data", "com.plexapp.agents.hama", "DataItems")
