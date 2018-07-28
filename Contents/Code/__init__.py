# -*- coding: utf-8 -*-
# [ ] Music
# [ ] Threads
# [ ] collection nfo

### Imports ###
import os                        # path.abspath, join, dirname
import re                        # split, compile
import inspect                   # getfile, currentframe
import time                      # sleep
from   io           import open  #
#import hashlib                   #
#import urllib2                   # Request

### Variables ###
PlexRoot         = os.path.abspath(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), "..", "..", "..", ".."))
CachePath        = os.path.join(PlexRoot, "Plug-in Support", "Data", "com.plexapp.agents.hama", "DataItems")
PLEX_URL_LIBRARY = 'http://127.0.0.1:32400/library/sections'  
PLEX_URL_MOVIES  = 'http://127.0.0.1:32400/library/sections/{}/all?type=1&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_TVSHOWS = 'http://127.0.0.1:32400/library/sections/{}/all?type=2&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_SEASONS = 'http://127.0.0.1:32400/library/sections/{}/all?type=3&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_ARTISTS = 'http://127.0.0.1:32400/library/sections/{}/all?type=8&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_ALBUM   = 'http://127.0.0.1:32400/library/sections/{}/all?type=9&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_TRACK   = 'http://127.0.0.1:32400/library/sections/{}/all?type=10&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_COLLECT = 'http://127.0.0.1:32400/library/sections/{}/all?type=18&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_SERVER_NAME = 'http://127.0.0.1:32400'
WINDOW_SIZE      = {'movie': 30, 'show': 20, 'artist': 10, 'album': 10}
TIMEOUT          = 30

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
        folder = os.path.dirname(media.seasons[s].episodes[e].items[0].parts[0].file)
        if folder not in dirs:  dirs.append(folder)
    for folder in dirs:
      if folder.startswith('Season'): return os.path.dirname(folder), ''
    else:
      if len(dirs)==1:  return folder
      else:             return os.path.dirname(folder)
  if agent_type=='album':
    for track in media.tracks:
      for item in media.tracks[track].items:
        for part in item.parts:
          return os.path.dirname(part.file)

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

  #metadata = media.primary_metadata
  Log(''.ljust(157, '='))
  Log("search() - ")
  if agent_type=='movie':   results.Append(MetadataSearchResult(id = 'null', name=media.title,  score = 100))
  if agent_type=='show':    results.Append(MetadataSearchResult(id = 'null', name=media.show,   score = 100))
  if agent_type=='artist':  results.Append(MetadataSearchResult(id = 'null', name=media.artist, score = 100))
  if agent_type=='album':   results.Append(MetadataSearchResult(id = 'null', name=media.title,  score = 100))  #if manual media.name,name=media.title,  
  Log(''.ljust(157, '='))

  # show --------------------------------------------------------------------------------------------------------------------------------------------------
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
      folder= os.path.dirname(media.seasons[season].episodes[episode].items[0].parts[0].file)
      if foldernot in dirs:  dirs.append(dir)

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
  
  # artist --------------------------------------------------------------------------------------------------------------------------------------------------

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
  
def Update(metadata, media, lang, force, agent_type):

  Log(''.ljust(157, '='))
  Log.Info('Update(metadata, media="{}", lang="{}", force={}, agent_type={})'.format(media.title, lang, force, agent_type))
  folder        = GetMediaDir(media, agent_type)
  collections = []
  Log.Info(dir(media))  
  ### PLEX_URL_LIBRARY - Plex libraries ###
  PLEX_LIBRARY = {}
  key, path = '', ''
  try:
    PLEX_LIBRARY_XML = XML.ElementFromURL(PLEX_URL_LIBRARY, timeout=float(TIMEOUT))
    Log.Info(XML.StringFromElement(PLEX_LIBRARY_XML))
    for directory in PLEX_LIBRARY_XML.iterchildren('Directory'):
      Log.Info('Library: [{:>2}] [{:<6}] {}'.format(directory.get('key'), directory.get('type'), directory.get('title')))
      Log.Info("agent_type: '{}', directory.get('type'): '{}'".format(agent_type, directory.get('type')))
      if ('artist' if agent_type=='album' else agent_type) ==directory.get('type'):
        Log.Info('the one')
        for location in directory:
          Log.Info("folder: '{}', location.get('path'): '{}'".format(folder, location.get('path')))
          if folder and location.get('path') in folder:
            Log.Info('[=] id: {:>2}, path: {}'.format(location.get("id"), location.get("path")))
            PLEX_LIBRARY[location.get("path")] = directory.get("key")
            key  = directory.get("key")
            path = location.get("path")
          else:                                    Log.Info('[ ] id: {:>2}, path: {}'.format(location.get("id"), location.get("path")))
      else: Log.Info('not the one')
  except Exception as e:  Log.Info("Exception: '{}'".format(e))
  Log.Info('PLEX_LIBRARY: {}'.format(PLEX_LIBRARY))

  ### Movies ###
  if agent_type=='movie':
    
    filenoext = os.path.basename(os.path.splitext(media.items[0].parts[0].file)[0])
    
    ### PLEX_URL_MOVIES - MOVIES ###
    count, found    = 0, False
    parentRatingKey = ""
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_MOVIES_XML = XML.ElementFromURL(PLEX_URL_MOVIES.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        total = int(PLEX_MOVIES_XML.get('totalSize'))
        Log.Debug("PLEX_URL_MOVIES [{}-{} of {}]".format(count+1, count+int(PLEX_MOVIES_XML.get('size')) ,total))
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

    ### PLEX_URL_TVSHOWS - TV Shows###
    count, found    = 0, False
    parentRatingKey = ""
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_TVSHOWS_XML = XML.ElementFromURL(PLEX_URL_TVSHOWS.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        total = int(PLEX_TVSHOWS_XML.get('totalSize'))
        Log.Debug("PLEX_URL_TVSHOWS [{}-{} of {}]".format(count+1, count+int(PLEX_TVSHOWS_XML.get('size')) ,total))
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

    ### PLEX_URL_SEASONS  - TV Shows seasons ###
    count, found = 0, False
    while count==0 or count<total and int(PLEX_SEASONS_XML.get('size')) == WINDOW_SIZE[agent_type]:
      try:
        PLEX_SEASONS_XML = XML.ElementFromURL(PLEX_URL_SEASONS.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        total  = PLEX_SEASONS_XML.get('totalSize')
        Log.Debug("PLEX_URL_SEASONS [{}-{} of {}]".format(count+1, count+int(PLEX_SEASONS_XML.get('size')) ,total))
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

  ### PLEX_URL_COLLECT - Collection loop for collection poster, summary ###
  count = 0
  while collections and (count==0 or count<total and int(PLEX_COLLECT_XML.get('size')) == WINDOW_SIZE[agent_type]):
    try:
      PLEX_COLLECT_XML = XML.ElementFromURL(PLEX_URL_COLLECT.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
      total  = PLEX_COLLECT_XML.get('totalSize')
      Log.Debug("PLEX_URL_COLLECT size: [{}-{} of {}]".format(count+1, count+int(PLEX_COLLECT_XML.get('size')), total))
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

    '''
    #if no collection downloaded but 1 present in collections and on disk, upload
    
    PLEX_COLLECTIONS       = '%s/library/sections/%%s/all?type=18' % PLEX_SERVER
    PLEX_COLLECTIONS_ITEMS = '%s/library/metadata/%%s/children'    % PLEX_SERVER

    # upload collection summary, posters, backdrops
    #r = requests.put('http://127.0.0.1:32400/library/sections/{}/all?type=18&id={}&summary.value={}'.format(section_id, col_id, summary]), data=payload, headers=HEADERS)
    #UploadImagesToPlex(poster_url_list, ratingKey, 'poster')
    #UploadImagesToPlex(fanart_url_list, ratingKey, 'art'   )

    def UploadImagesToPlex(url_list, ratingKey, image_type):
      main_image = ''
      for url in url_list or []:
        if main_image == '':
          r = requests.get('http://127.0.0.1:32400/library/metadata/{}/{}?url={}'.format(ratingKey, image_type + 's', url), headers=HEADERS)
          for child in ET.fromstring(r.text):
            if child.attrib['selected'] == '1':
              url = child.attrib['key']
              main_image = url[url.index('?url=')+5:]
              break
        r = requests.post(PLEX_IMAGES % (ratingKey, image_type + 's', url       ), data=payload, headers=HEADERS)
        r = requests.put (PLEX_IMAGES % (ratingKey, image_type,       main_image), data=payload, headers=HEADERS)  # set the highest rated image as selected again
    '''

  if agent_type=='album':

    '''### PLEX_URL_ARTISTS - MOVIES ###
    count, found    = 0, False
    parentRatingKey = ""
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        Log.Info(key)
        PLEX_ARTIST_XML = XML.ElementFromURL(PLEX_URL_ARTISTS.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        Log.Info(XML.StringFromElement(PLEX_ARTIST_XML))  #Un-comment for XML code displayed in logs
        total = int(PLEX_ARTIST_XML.get('totalSize'))
        Log.Debug("PLEX_URL_MOVIES [{}-{} of {}]".format(count+1, count+int(PLEX_ARTIST_XML.get('size')) ,total))
        #for directory in PLEX_ARTIST_XML.iterchildren('Directory'):
        #  Log.Info("media.title: {}, media.parentTitle: {}, media.id: {}, directory.get('title'): {}".format(media.title, media.parentTitle, media.id, directory.get('title')))
        count += WINDOW_SIZE[agent_type]
      except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     
    
    ### PLEX_URL_ALBUM - MOVIES ###
    count, found    = 0, False
    parentRatingKey = ""
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        Log.Info(key)
        PLEX_ALBUM_XML = XML.ElementFromURL(PLEX_URL_ALBUM.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        Log.Info(XML.StringFromElement(PLEX_ALBUM_XML))  #Un-comment for XML code displayed in logs
        total = int(PLEX_ALBUM_XML.get('totalSize'))
        Log.Debug("PLEX_URL_MOVIES [{}-{} of {}]".format(count+1, count+int(PLEX_ALBUM_XML.get('size')) ,total))
        for directory in PLEX_ALBUM_XML.iterchildren('Directory'):
          Log.Info("media.title: {}, media.parentTitle: {}, media.id: {}, directory.get('title'): {}".format(media.title, media.parentTitle, media.id, directory.get('title')))
          if media.title==directory.get('title'):   
            Log.Info('title:                 {}'.format(directory.get('title')))
            if directory.get('summary'              ):  Log.Info('summary:               {}'.format(directory.get('summary')))
            if directory.get('parentTitle'          ):  Log.Info('parentTitle:           {}'.format(directory.get('parentTitle')))
            if directory.get('title'                ):  Log.Info('title:                 {}'.format(directory.get('title')))
            if Prefs['album_poster' ] and directory.get('thumb'):                                        SaveFile(PLEX_SERVER_NAME+directory.get('thumb' ), os.path.join(dir, filenoext+       '.jpg'), 'poster')
            if Prefs['artist_poster'] and directory.get('parentThumb') not in ('', directory.get('thumb')):  SaveFile(PLEX_SERVER_NAME+directory.get('thumb' ), os.path.join(dir, filenoext+       '.jpg'), 'poster')
            for collection in directory.iterchildren('Collection'):  Log.Info('collection:            {}'.format(collection.get('tag')));  collections.append(collection.get('tag'))
            found = True
            break
        else:  count += WINDOW_SIZE[agent_type];  continue
        break      
      except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     

    ### PLEX_URL_ARTISTS ###
    count, found    = 0, False
    parentRatingKey = ""
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        Log.Info(key)
        PLEX_ARTIST_XML = XML.ElementFromURL(PLEX_URL_ARTISTS.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        Log.Info(XML.StringFromElement(PLEX_ARTIST_XML))  #Un-comment for XML code displayed in logs
        total = int(PLEX_ARTIST_XML.get('totalSize'))
        Log.Debug("PLEX_URL_ALBUM [{}-{} of {}]".format(count+1, count+int(PLEX_ARTIST_XML.get('size')) ,total))
        #for directory in PLEX_ARTIST_XML.iterchildren('Directory'):
        #  Log.Info("media.title: {}, media.parentTitle: {}, media.id: {}, directory.get('title'): {}".format(media.title, media.parentTitle, media.id, directory.get('title')))
        count += WINDOW_SIZE[agent_type]
      except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     
    '''
    ### PLEX_URL_TRACK ###
    count, found    = 0, False
    parentRatingKey = ""
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_XML_TRACK = XML.ElementFromURL(PLEX_URL_TRACK.format(key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        Log.Info(XML.StringFromElement(PLEX_XML_TRACK))  #Un-comment for XML code displayed in logs
        total = int(PLEX_XML_TRACK.get('totalSize'))
        Log.Debug("PLEX_URL_TRACK [{}-{} of {}]".format(count+1, count+int(PLEX_XML_TRACK.get('size')) ,total))
        for track in PLEX_XML_TRACK.iterchildren('Track'):
          Log.Info("media.title: {}, media.parentTitle: {}, media.id: {}, track.get('title'): {}".format(media.title, media.parentTitle, media.id, track.get('title')))
          #<Track ratingKey="7950" key="/library/metadata/7950" parentRatingKey="7949" grandparentRatingKey="7948" type="track" title="She Said" grandparentKey="/library/metadata/7948" parentKey="/library/metadata/7949" grandparentTitle="Plan B" parentTitle="Uk Top 40 Singles Chart 09-05-" originalTitle="Plan B" summary="" index="3" parentIndex="1" ratingCount="1337515" thumb="/library/metadata/7949/thumb/1531652573" parentThumb="/library/metadata/7949/thumb/1531652573" grandparentThumb="/library/metadata/7948/thumb/1532314890" duration="211017" addedAt="1316823048" updatedAt="1531652573">
          #ratingKey, key, parentRatingKey, grandparentRatingKey, type, title, grandparentKey, parentKey, grandparentTitle, parentTitle, summary, parentIndex, ratingCount, thumb, parentThumb, grandparentThumb, duration, addedAt, updatedAt
          # title="She Said", grandparentTitle="Plan B" parentTitle="Uk Top 40 Singles Chart 09-05-" originalTitle="Plan B" 
          
          Log.Info("media.title: {}, media.parentTitle: {}, media.id: {}, directory.get('title'): {}".format(media.title, media.parentTitle, media.id, directory.get('title')))
        count += WINDOW_SIZE[agent_type]
      except ValueError, Argument:  Log.Critical('Unknown error in {}'.format(Argument));  raise     
    
### Agent declaration ##################################################################################################################################################
class LMETV(Agent.TV_Shows):  # 'com.plexapp.agents.none', 'com.plexapp.agents.opensubtitles'
  contributes_to   = ['com.plexapp.agents.localmedia', 'com.plexapp.agents.hama']
  languages        = [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
  name             = 'LME'
  primary_provider = False
  fallback_agent   = False
  def search (self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'show')
  def update (self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'show')

class LMEMovie(Agent.Movies):
  contributes_to   = ['com.plexapp.agents.localmedia', 'com.plexapp.agents.hama']
  languages        = [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
  name             = 'LME'
  primary_provider = False
  fallback_agent   = False
  def search (self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'movie')
  def update (self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'movie')

class LMEAlbum(Agent.Album):
  contributes_to   = ['com.plexapp.agents.discogs', 'com.plexapp.agents.lastfm', 'com.plexapp.agents.plexmusic', 'com.plexapp.agents.none']
  languages        = [Locale.Language.English]
  name             = 'LME'
  primary_provider = False
  fallback_agent   = False
  def search(self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'album')
  def update(self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'album')
