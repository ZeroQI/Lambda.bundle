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
  if os.path.exists(filename) and os.path.getsize(filename)==len(content):  Log.Info('[=] {}: {}'.format(field, os.path.basename(filename)))
  else:
    Log.Info('[{}] {}: {}'.format('!' if os.path.exists(filename) else '*', field, os.path.basename(filename)))
    try:
      with open(filename, 'wb') as file:
        file.write(content)
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
  
  ### PLEX_LIBRARY_URL - Plex libraries ###
  '''
  <MediaContainer size="3" allowSync="0" identifier="com.plexapp.plugins.library" mediaTagPrefix="/system/bundle/media/flags/" mediaTagVersion="1390169701" title1="Plex Library">
    <Directory allowSync="0" art="/:/resources/movie-fanart.jpg" filters="1" refreshing="0" thumb="/:/resources/movie.png" key="29" type="movie" title="Movies" agent="com.plexapp.agents.imdb" scanner="Plex Movie Scanner" language="en" uuid="07a4b132-a67b-477e-a245-585935d08c0b" updatedAt="1394559305" createdAt="1390438950">
      <Location id="4" path="/Users/plexuser/Movies/Media/Movies"/>
    </Directory>
    <Directory allowSync="0" art="/:/resources/artist-fanart.jpg" filters="1" refreshing="0" thumb="/:/resources/artist.png" key="31" type="artist" title="Music" agent="com.plexapp.agents.lastfm" scanner="Plex Music Scanner" language="en" uuid="10254ef0-a0a4-481b-ad9c-46ab3db39d0b" updatedAt="1394039950" createdAt="1390440566">
      <Location id="7" path="/Users/plexuser/Movies/Media/Music"/>
   </Directory>
   <Directory allowSync="0" art="/:/resources/show-fanart.jpg" filters="1" refreshing="0" thumb="/:/resources/show.png" key="30" type="show" title="Television" agent="com.plexapp.agents.thetvdb" scanner="Plex Series Scanner" language="en" uuid="540e7c98-5a92-4e8f-b255-9cca2870060c" updatedAt="1394482680" createdAt="1390438925">
      <Location id="3" path="/Users/plexuser/Movies/Media/TV Shows"/>
   </Directory>
  </MediaContainer>
  '''
  PLEX_LIBRARY = {}
  try:
    PLEX_LIBRARY_XML = XML.ElementFromURL(PLEX_LIBRARY_URL, timeout=float(TIMEOUT))
    for library in PLEX_LIBRARY_XML.iterchildren('Directory'):
      for  path in library.iterchildren('Location'):
        PLEX_LIBRARY[path.get("path")] = library.get("key")
        #<MediaContainer   
        #Directory         art="/:/resources/movie-fanart.jpg" thumb="/:/resources/artist.png" key="31" type="artist" title="Music" language="en" agent="com.plexapp.agents.lastfm" scanner="Plex Music Scanner" 
        #Location:         id="7" path="/Users/plexuser/Movies/Media/Music"/
  except Exception as e:  Log.Info("Exception: '{}'".format(e))
  Log.Info('PLEX_LIBRARY: {}'.format(PLEX_LIBRARY))
  
  ### PLEX_TVSHOWS_URL - TV Shows###
  count = 0
  while count==0 or int(PLEX_TVSHOWS_XML.get('size')) != 0:
    try:
      PLEX_TVSHOWS_XML = XML.ElementFromURL(PLEX_TVSHOWS_URL.format(count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
      count += 1
      total  = PLEX_TVSHOWS_XML.get('totalSize')
      Log.Debug("PLEX_TVSHOWS_URL size: {} [{} of {}]".format(PLEX_TVSHOWS_XML.get('size'), count, total))
      for media in PLEX_TVSHOWS_XML.xpath('.//Video'):
        Log.Debug("Media #{} from database: '{}'".format( str(count), media.get('title') )) #if bExtraInfo:  media = XML.ElementFromURL('http://127.0.0.1:32400/library/metadata/'+mediaget('ratingKey')).xpath('//Video')[0]
        #"thumb=" 
        #banner
        #themes
        
    except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     

  ###Series loop for posters, art, themes
  #XML: thumb="/library/metadata/25199/thumb/1398798243"
  #http://127.0.0.1:32400/library/metadata/25199/thumb/1398798243
  #try:
  #  with io.open(os.path.join(posterDir, rowentry['Media ID'] + '.jpg'), 'wb') as handler:
  #    handler.write(HTTP.Request('http://127.0.0.1:32400/photo/:/transcode?width={}&height={}&minSize=1&url={}', String.Quote(rowentry['Poster url'])).content)
  #except Exception, e:  Log.Exception('Exception was %s' % str(e))
 
  ### PLEX_SEASONS_URL  - TV Shows seasons ###
  '''
    <MediaContainer size="1" allowSync="1" identifier="com.plexapp.plugins.library" librarySectionID="2" librarySectionTitle="Old TV Shows" librarySectionUUID="94102838-a992-411c-b237-cedaf41e26f0" mediaTagPrefix="/system/bundle/media/flags/" mediaTagVersion="1531739939">
    <Directory ratingKey="5687" key="/library/metadata/5687/children" parentRatingKey="5638" guid="com.plexapp.agents.thetvdb://268592/1?lang=en" librarySectionTitle="Old TV Shows" librarySectionID="2" librarySectionKey="/library/sections/2" type="season" title="Season 1" parentKey="/library/metadata/5638" parentTitle="The 100" summary="" index="1" parentIndex="1" thumb="/library/metadata/5687/thumb/1532246173" art="/library/metadata/5638/art/1532247429" parentThumb="/library/metadata/5638/thumb/1532247429" parentTheme="/library/metadata/5638/theme/1532247429" leafCount="13" viewedLeafCount="0" addedAt="1532246025" updatedAt="1532246173">
    <Extras size="0"> </Extras>
    </Directory>
    </MediaContainer>
  '''
  count = 0
  while count==0 or int(PLEX_TVSHOWS_XML.get('size')) != 0:
    try:
      PLEX_TVSHOWS_XML = XML.ElementFromURL(PLEX_TVSHOWS_URL.format(count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
      count += 1
      total  = PLEX_TVSHOWS_XML.get('totalSize')
      Log.Debug("PLEX_TVSHOWS_URL size: {} [{} of {}]".format(PLEX_TVSHOWS_XML.get('size'), count, total))
      for media in PLEX_TVSHOWS_XML.xpath('.//Video'):
        Log.Debug("Media #{} from database: '{}'".format( str(count), media.get('title') )) #if bExtraInfo:  media = XML.ElementFromURL('http://127.0.0.1:32400/library/metadata/'+mediaget('ratingKey')).xpath('//Video')[0]
        #librarySectionID="2" librarySectionTitle="Old TV Shows" 
        #MediaContainer>Directory type="season" title="Season 1" thumb="/library/metadata/5687/thumb/1532246173" art="/library/metadata/5638/art/1532247429" parentThumb="/library/metadata/5638/thumb/1532247429"
    except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     

  
  ### PLEX_COLLECT_URL - Collection loop for collection poster, summary ###
  # "http://IPOfPMS:32400/library/sections/X/all?collection=15213" <Collection id="15213" filter="collection=15213" tag="28 Days/Weeks Later"/>
  #  xxx.get('Collection')
  count = 0
  while count==0 or int(PLEX_TVSHOWS_XML.get('size')) != 0:
    try:
      PLEX_TVSHOWS_XML = XML.ElementFromURL(PLEX_COLLECT_XML.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
      count += 1
      total  = PLEX_TVSHOWS_XML.get('totalSize')
      Log.Debug("PLEX_TVSHOWS_URL size: {} [{} of {}]".format(PLEX_TVSHOWS_XML.get('size'), count, total))
      for media in PLEX_TVSHOWS_XML.xpath('.//Video'):
        Log.Debug("Media #{} from database: '{}'".format( str(count), media.get('title') )) #if bExtraInfo:  media = XML.ElementFromURL('http://127.0.0.1:32400/library/metadata/'+mediaget('ratingKey')).xpath('//Video')[0]
    except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     
  
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
PLEX_COLLECT_URL = 'http://127.0.0.1:32400/library/sections/{}/all?type=18&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
TIMEOUT          = 30
WINDOW_SIZE      = {'Movies': 30, 'TV_Shows': 20, 'Artist': 10, 'Album': 10, 'Photo': 20}
