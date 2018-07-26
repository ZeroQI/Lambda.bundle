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
  if agent_type=='show':
    '''  
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
    '''    
    results.Append(MetadataSearchResult(id = 'null', name=media.show, score = 100))
  #--------------------------------------------------------------------------------------------------------------------------------------------------
  if agent_type=='Artist':
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
  if agent_type=='Album':
    results.Append(MetadataSearchResult(id = 'null', score = 100))
  Log(''.ljust(157, '='))

def Update(metadata, media, lang, force, agent_type):
  
  Log(''.ljust(157, '='))
  Log.Info('Update(metadata, media="{}", lang="{}", force={}, agent_type={})'.format(media.title, lang, force, agent_type))
  
  dir      = GetMediaDir(media, agent_type)
  
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
    for directory in PLEX_LIBRARY_XML.iterchildren('Directory'):
      Log.Info('Library: [{:>2}] [{:<6}] {}'.format(directory.get('key'), directory.get('type'), directory.get('title')))
      if agent_type==directory.get('type'):
        for location in directory:
          if dir and location.get("path") in dir:
            Log.Info('[=] id: {:>2}, path: {}'.format(location.get("id"), location.get("path")))
            PLEX_LIBRARY[location.get("path")] = directory.get("key")
            key = directory.get("key")
          else:                                    Log.Info('[ ] id: {:>2}, path: {}'.format(location.get("id"), location.get("path")))
          
  except Exception as e:  Log.Info("Exception: '{}'".format(e))
  Log.Info('PLEX_LIBRARY: {}'.format(PLEX_LIBRARY))
  
  ### PLEX_TVSHOWS_URL - TV Shows###
  '''
  <Directory ratingKey="2064" key="/library/metadata/2064/children" studio="Sunrise" type="show" title="Cowboy Bebop" contentRating="TV-MA" summary="The year is 2071 AD. With the systematic collapse of the old nation-states, a mixed jumble of races and peoples were driven out of their terrestrial Eden and spread to the stars, taking with them the now confused concepts of justice, freedom, violence, and love. New rules were established, and a new generation of bounty hunters came into being. People referred to these bounty hunters as &quot;cowboys&quot;.&#10;Meet Spike Spiegel and Jet Black, a drifter and a retired cyborg cop who have started a bounty hunting partnership. In the converted ship The Bebop, Spike and Jet search the galaxy for criminals with bounties on their heads. They meet a lot of interesting characters, including the unusually intelligent dog Ein, the bizarre hacker child prodigy Ed, and the voluptuous and vexing femme fatale, Faye Valentine.&#10;Source: AnimeNfo&#10;Note: Originally aired on TV Tokyo, but after 12 episodes the show was cancelled due to the violence portrayed in the Cowboy Bebop world and violence in Japanese schools. The final and also the 13th episode on TV Tokyo was a compilation episode where the characters provide a philosophical commentary and end with the words: &quot;[i]This Is Not The End. You Will See The Real &quot;Cowboy Bebop&quot; Someday!&quot; Four months later, WOWOW started to broadcast all 26 episodes of Cowboy Bebop. The ordering was different with completely new episodes mixed in between episodes previously broadcast on TV Tokyo, including a new episode 1.[/i]" index="1" rating="8.6" year="1998" thumb="/library/metadata/2064/thumb/1527940525" art="/library/metadata/2064/art/1527940525" banner="/library/metadata/2064/banner/1527940525" theme="/library/metadata/2064/theme/1527940525" duration="1500000" originallyAvailableAt="1998-04-03" leafCount="1" viewedLeafCount="0" childCount="1" addedAt="1523205540" updatedAt="1527940525">
  '''
  count, found = 0, False
  parentRatingKey=""
  while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
    try:
      PLEX_TVSHOWS_XML = XML.ElementFromURL(PLEX_TVSHOWS_URL.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
      total = int(PLEX_TVSHOWS_XML.get('totalSize'))
      Log.Debug("PLEX_TVSHOWS_URL [{}-{} of {}]".format(count+1, count+int(PLEX_TVSHOWS_XML.get('size')) ,total))
      for show in PLEX_TVSHOWS_XML.iterchildren('Directory'):
        if media.title==show.get('title'):
          Log.Info('title:                 {}'.format(show.get('title')))
          #Log.Info('summary:               {}'.format(show.get('summary')))
          #Log.Info('contentRating:         {}'.format(show.get('contentRating')))
          #Log.Info('studio:                {}'.format(show.get('studio')))
          #Log.Info('rating:                {}'.format(show.get('rating')))
          #Log.Info('year:                  {}'.format(show.get('year')))
          #Log.Info('duration:              {}'.format(show.get('duration')))
          #Log.Info('originallyAvailableAt: {}'.format(show.get('originallyAvailableAt')))
          
          if show.get('thumb'    ):  SaveFile(PLEX_SERVER_NAME+show.get('thumb' ), os.path.join(dir, 'poster.jpg'    ), 'poster')
          if show.get('art'      ):  SaveFile(PLEX_SERVER_NAME+show.get('art'   ), os.path.join(dir, 'background.jpg'), 'art'   )
          if show.get('banner'   ):  SaveFile(PLEX_SERVER_NAME+show.get('banner'), os.path.join(dir, 'banner.jpg'    ), 'banner')
          if show.get('theme'    ):  SaveFile(PLEX_SERVER_NAME+show.get('theme' ), os.path.join(dir, 'theme.mp3'     ), 'theme' )
          if show.get('ratingKey'):  parentRatingKey = show.get('ratingKey')
          #if show.get('key'      ):  Log.Info('[ ] key:                   {}'.format(show.get('key'      ))); 
          #Log.Info(XML.StringFromElement(show))
          found = True
          break
      else:  count += WINDOW_SIZE[agent_type];  continue
      break      
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
  count, found = 0, False
  while count==0 or count<total and int(PLEX_SEASONS_XML.get('size')) == WINDOW_SIZE[agent_type]:
    try:
      PLEX_SEASONS_XML = XML.ElementFromURL(PLEX_SEASONS_URL.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
      total  = PLEX_SEASONS_XML.get('totalSize')
      Log.Debug("PLEX_SEASONS_URL [{}-{} of {}]".format(count+1, count+int(PLEX_SEASONS_XML.get('size')) ,total))
      for show in PLEX_SEASONS_XML.iterchildren('Directory'):
        if parentRatingKey == show.get('parentRatingKey'):  #parentTitle
          Log.Info(XML.StringFromElement(show))
          Log.Debug("title: '{}'".format(show.get('title')))
          if show.get('thumb'    ):  SaveFile(PLEX_SERVER_NAME+show.get('thumb' ), os.path.join(dir, show.get('title'), 'season-specials-poster.jpg'     if show.get('title')=='Specials' else show.get('title')+'-poster.jpg'    ), 'season_poster')
          if show.get('art'      ):  SaveFile(PLEX_SERVER_NAME+show.get('art'   ), os.path.join(dir, show.get('title'), 'season-specials-background.jpg' if show.get('title')=='Specials' else show.get('title')+'-background.jpg'), 'season_art'   )
    except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     
    count += WINDOW_SIZE[agent_type]

  ### PLEX_COLLECT_URL - Collection loop for collection poster, summary ###
  # "http://IPOfPMS:32400/library/sections/X/all?collection=15213" <Collection id="15213" filter="collection=15213" tag="28 Days/Weeks Later"/>
  #  xxx.get('Collection')
  count = 0
  while count==0 or count<total and int(PLEX_COLLECT_XML.get('size')) == WINDOW_SIZE[agent_type]:
    try:
      PLEX_COLLECT_XML = XML.ElementFromURL(PLEX_COLLECT_URL.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
      total  = PLEX_COLLECT_XML.get('totalSize')
      Log.Debug("PLEX_COLLECT_URL size: [{}-{} of {}]".format(count+1, count+int(PLEX_COLLECT_XML.get('size')), total))
      for media in PLEX_COLLECT_XML.xpath('.//Video'):
        Log.Debug("Media #{} from database: '{}'".format( str(count), media.get('title') )) #if bExtraInfo:  media = XML.ElementFromURL('http://127.0.0.1:32400/library/metadata/'+mediaget('ratingKey')).xpath('//Video')[0]
    except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     
    count += WINDOW_SIZE[agent_type]
  
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
PLEX_TVSHOWS_URL = 'http://127.0.0.1:32400/library/sections/{}/all?type=2&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_SEASONS_URL = 'http://127.0.0.1:32400/library/sections/{}/all?type=3&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_COLLECT_URL = 'http://127.0.0.1:32400/library/sections/{}/all?type=18&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_SERVER_NAME = 'http://127.0.0.1:32400'
TIMEOUT          = 30
WINDOW_SIZE      = {'movie': 30, 'show': 20, 'artist': 10, 'Album': 10}
