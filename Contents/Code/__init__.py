# -*- coding: utf-8 -*-

### Imports ###
import os                        # [path] abspath, join, dirname
import re                        # split, compile
import time                      # sleep
import inspect                   # getfile, currentframe

### Variables ### (move last in file if calling some functions declared afterwards, order between functions deosn't matter)
PlexRoot         = os.path.abspath(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), "..", "..", "..", ".."))
AgentDataFolder  = os.path.join(PlexRoot, "Plug-in Support", "Data", "com.plexapp.agents.hama", "DataItems")
PLEX_SERVER_NAME = 'http://127.0.0.1:32400' #Network.Address, Network.PublicAddress, Network.Hostname, port line 195 https://github.com/pkkid/python-plexapi/blob/master/plexapi/server.py
PLEX_URL_LIBRARY = 'http://127.0.0.1:32400/library/sections'  
PLEX_URL_MOVIES  = 'http://127.0.0.1:32400/library/sections/{}/all?type=1&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_TVSHOWS = 'http://127.0.0.1:32400/library/sections/{}/all?type=2&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_SEASONS = 'http://127.0.0.1:32400/library/sections/{}/all?type=3&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_EPISODE = 'http://127.0.0.1:32400/library/sections/{}/all?type=4&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_ARTISTS = 'http://127.0.0.1:32400/library/sections/{}/all?type=8&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_ALBUM   = 'http://127.0.0.1:32400/library/sections/{}/all?type=9&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_TRACK   = 'http://127.0.0.1:32400/library/sections/{}/all?type=10&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_COLLECT = 'http://127.0.0.1:32400/library/sections/{}/all?type=18&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_COITEMS = 'http://127.0.0.1:32400/library/sections/{}/children&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_UPLOAD_TYPE = 'http://127.0.0.1:32400/library/metadata/{}/{}?url={}'
PLEX_UPLOAD_TEXT = 'http://127.0.0.1:32400/library/sections/{}/all?type=18&id={}&summary.value={}'
WINDOW_SIZE      = {'movie': 30, 'show': 20, 'artist': 10, 'album': 10}
TIMEOUT          = 30
HEADERS          = {}

### One liners ###
def natural_sort_key(s   ):  return [int(text) if text.isdigit() else text for text in re.split(re.compile('([0-9]+)'), str(s).lower())]  # list.sort(key=natural_sort_key) #sorted(list, key=natural_sort_key) - Turn a string into string list of chunks "z23a" -> ["z", 23, "a"]
def file_extension  (file):  return file[1:] if file.count('.')==1 and file.startswith('.') else os.path.splitext(file)[1].lstrip('.').lower()

def find_command(arg):
  caller_lines = '' 
  frame        = inspect.currentframe()
  try:
    context      = inspect.getframeinfo(frame.f_back).code_context
    caller_lines = ''.join([line.strip() for line in context])
    m            = re.search(r'echo\s*\((.+?)\)$', caller_lines)
    if m:  caller_lines = m.group(1)
  finally:   del frame
  return caller_lines
  
def GetMediaDir (media, agent_type):
  ''' Returns folder and file touple for media
      - media:       media received by update()
      - agent_type:  movie|show|album
  '''
  if agent_type=='movie':  return os.path.split(media.items[0].parts[0].file)
  if agent_type=='show':
    dirs=[]
    for s in media.seasons if media else []: # TV_Show:
      for e in media.seasons[s].episodes:
        return os.path.split(media.seasons[s].episodes[e].items[0].parts[0].file)  #if folder.startswith('Season'): return os.path.split(folder), ''
  if agent_type=='album':
    for track in media.tracks:
      return os.path.split(media.tracks[track].items[0].parts[0].file)  #for item in media.tracks[track].items:  for part in item.parts:  return os.path.split(part.file)

def xml_from_url_paging_load(URL, key, count, window):
  '''
  '''
  xml   = XML.ElementFromURL(URL.format(key, count, window), timeout=float(TIMEOUT))
  total = int(xml.get('totalSize') or 0)
  Log.Info("# [{}-{} of {}] {}".format(count+1, count+int(xml.get('size') or 0), total, URL.format(key, count, window)))
  return xml, count+window, total

def SaveFile(thumb, path, field, key="", ratingKey="", dynamic_name=""):
  ''' Save Metadata to file if different, or restore it to Plex if it doesn't exist anymore
      thumb:        url to picture or text
      destination:  path to export file
      field:        Prefs field name to check if export/importing
  '''
  Log.Info("thumb: {}, path: {}, field:{}, Prefs[field]: {}, dynamic_name: {}".format(thumb, path, field, Prefs[field], dynamic_name))
  if not thumb or not path or not field or not Prefs[field]:  Log.Info('return'); return
  filename    = Prefs[field].split('¦')[1 if dynamic_name else 0] if 'season' in field and '¦' in Prefs[field] else Prefs[field]#dynamic name for seasons 1+ not specials  #Log.Info("filename: {}".format(filename))
  destination = os.path.join(path, filename.format(dynamic_name).replace('.ext', '.'+(file_extension(PLEX_SERVER_NAME+thumb) or 'jpg')))  #Log.Info("destination: {}".format(destination))
  ext         = file_extension(destination)  #Log.Info("ext: {}".format(ext))
  if thumb:
    if Prefs[field]!='Ignored':
      try:
        if ext in ('jpg', 'mp3'):  content = HTTP.Request(PLEX_SERVER_NAME+thumb).content #response.headers['content-length']
        if ext=='txt':             content = thumb
        if ext=='xml':             content='' #content have list of fields?
          #load xml file in mem
          #if meta in plex:  update mem xml  field
          #else if in mem:   update metadata field
          #save file if different
          #{ 'contentRating': directory.get('contentRating')
          #  'minYear'      : directory.get('minYear'      )
          #  'maxYear'      : directory.get('maxYear'      )
          #}

      except Exception as e:  Log.Info('Exception: "{}"'.format(e));  return
      if os.path.exists(destination) and os.path.getsize(destination)==len(content):  Log.Info('[=] {}: {}'.format(field, os.path.basename(destination)))
      else:
        if not os.path.exists(os.path.dirname(destination)):  os.makedirs(os.path.dirname(destination))
        Log.Info('[{}] {}: {}'.format('!' if os.path.exists(destination) else '*', field, os.path.basename(destination)))
        try:                    Core.storage.save(destination, content)  #  with open(destination, 'wb') as file:  file.write(response.content)
        except Exception as e:  Log.Info('Exception: "{}"'.format(e))
    else:  Log.Info('[ ] {} present but not selected in agent settings'.format(field))
  elif os.path.isfile(destination):
    if ext in ('jpg', 'mp3'):  UploadImagesToPlex(destination, ratingKey, 'poster' if 'poster' in field else 'art' if 'fanart' in field else field)
    if ext=='txt':
      Log.Info("destination: '{}'".format(destination))
      r = HTTP.Request(PLEX_UPLOAD_TEXT.format(key, ratingKey, String.Quote(Core.storage.load(destination))), headers=HEADERS, method='PUT')
      Log.Info('request content: {}, headers: {}, load: {}'.format(r.content, r.headers, r.load))
    if ext=='xml':             content='' #content have list of fields?
  else:  Log.Info('[ ] {} not present in Plex nor on disk'.format(field))

def UploadImagesToPlex(url_list, ratingKey, image_type):
  ''' https://github.com/defract/TMDB-Collection-Data-Retriever/blob/master/collection_updater.py line 211
      - url_list:    url or [url, ...]
      - ratingKey:   #
      - image_type:  poster, fanart, season 
  '''
  for url in url_list if isinstance(url_list, list) else [url_list] if url_list else []:
    r = HTTP.Request(PLEX_UPLOAD_TYPE.format(ratingKey, image_type+'s', ''), headers=HEADERS)
    Log.Info(r.content)
    r = HTTP.Request(PLEX_UPLOAD_TYPE.format(ratingKey, image_type + 's', 'default%3A%2F%2F'), headers=HEADERS, method='PUT')  # upload file  , data=Core.storage.load(url)
    Log.Info(r.content)
    for child in r.iter():
      if child.attrib['selected'] == '1':
        selected_url   = child.attrib['key'] #selected_image_url = selected_url[selected_url.index('?url=')+5:]
        #r = HTTP.Request(PLEX_IMAGES % (ratingKey, image_type + 's', url           ), headers=HEADERS, method='POST')  # upload file
        #r = HTTP.Request(PLEX_IMAGES % (ratingKey, image_type,       selected_image), headers=HEADERS, method='PUT' )  # set    file as selected again
        Log.Info('request content: {}, headers: {}, load: {}'.format(r.content, r.headers, r.load))
        break
    else: continue  #continue if no break occured
    break           #cascade first break to exit both loops

def nfo():  
  pass
  '''
    file         = os.path.join(path, 'xxxx', '.nfo')
    nfo, changed = load_nfo_to_dict(file)  #no need to empty fill, loop will do
    for field in fields:
      plex_meta = getattr(metadata, field)
      nfo_meta  = Dict   (nfo,      field)
      if plex_meta:
        if plex_meta==nfo_meta:  Log.Ingo('[=] field: xxxx identical')
        else:                    SaveDict(plex_meta, nfo, field);  changed = 1
      elif nfo_meta:             UpdateMetaField(metadata, metadata, MetaSources[language_source], FieldListMovies if movie else FieldListSeries, 'title', language_source, movie, source_list) 
      elif not present:          SaveDict(None, nfo, field)
    if not present or changed nfo in mem: Write_nfo_to_disk(file, nfo)
  '''
    
def Start():
  HTTP.CacheTime                  = 0
  HTTP.Headers['User-Agent'     ] = 'Mozilla/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.54'
  HTTP.Headers['Accept-Language'] = 'en-us'

### Download metadata using unique ID ###
def Search(results, media, lang, manual, agent_type):

  Log(''.ljust(157, '='))
  Log("search() - lang:'{}', manual='{}', agent_type='{}'".format(lang, manual, agent_type))
  if agent_type=='movie':   results.Append(MetadataSearchResult(id = 'null', name=media.title,  score = 100))
  if agent_type=='show':    results.Append(MetadataSearchResult(id = 'null', name=media.show,   score = 100))
  if agent_type=='artist':  results.Append(MetadataSearchResult(id = 'null', name=media.artist, score = 100))
  if agent_type=='album':   results.Append(MetadataSearchResult(id = 'null', name=media.title,  score = 100))  #if manual media.name,name=media.title,  
  Log(''.ljust(157, '='))
  #metadata = media.primary_metadata  #full metadata object from here with all data, otherwise in Update() metadata will be empty
  
def Update(metadata, media, lang, force, agent_type):

  folder, item       = GetMediaDir(media, agent_type)
  collections        = []
  parentRatingKey    = ""
  library_key, library_path, library_name = '', '', ''
  
  Log.Info(''.ljust(157, '='))
  Log.Info('Update(metadata, media="{}", lang="{}", force={}, agent_type={})'.format(media.title, lang, force, agent_type))
  Log.Info('folder: {}, item: {}'.format(folder, item))
  
  Log.Info("{}: {}".format('movies_poster', Prefs['movies_poster']))
  Log.Info("{}: {}".format('season_poster', Prefs['season_poster']))
  
  ### Plex libraries ###
  try:
    PLEX_LIBRARY_XML = XML.ElementFromURL(PLEX_URL_LIBRARY, timeout=float(TIMEOUT))  #Log.Info(XML.StringFromElement(PLEX_LIBRARY_XML))
    Log.Info('PLEX_URL_LIBRARY')
    for directory in PLEX_LIBRARY_XML.iterchildren('Directory'):
      for location in directory:
        Log.Info('[{}] id: {:>2}, type: {:>6}, library: {:<24}, path: {}'.format('*' if location.get('path') in folder else ' ', directory.get("key"), directory.get('type'), directory.get('title'), location.get("path")))
        if ('artist' if agent_type=='album' else agent_type)==directory.get('type') and location.get('path') in folder:
          library_key, library_path, library_name = directory.get("key"), location.get("path"), directory.get('title')
  except Exception as e:  Log.Info("PLEX_URL_LIBRARY - Exception: '{}'".format(e))
  Log.Info('')
  
  ### Movies ###
  if agent_type=='movie':
    
    ### PLEX_URL_MOVIES - MOVIES ###
    count = 0
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        
        # Paging PLEX_URL_MOVIES
        PLEX_MOVIES_XML = XML.ElementFromURL(PLEX_URL_MOVIES.format(library_key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        total = int(PLEX_MOVIES_XML.get('totalSize'))
        Log.Debug("PLEX_URL_MOVIES [{}-{} of {}]".format(count+1, count+int(PLEX_MOVIES_XML.get('size')) ,total))
        
        for video in PLEX_MOVIES_XML.iterchildren('Video'):
          if media.title==video.get('title'):   
            Log.Info('title:                 {}'.format(video.get('title')))
            if video.get('ratingKey'):  parentRatingKey = video.get('ratingKey')
            filenoext = os.path.basename(os.path.splitext(media.items[0].parts[0].file)[0])
            SaveFile(video.get('thumb'), folder, 'movies_poster', dynamic_name=filenoext)
            SaveFile(video.get('art'  ), folder, 'movies_fanart', dynamic_name=filenoext)
            for collection in video.iterchildren('Collection'):
              Log.Info('collection:            {}'.format(collection.get('tag')))
              collections.append(collection.get('tag'))
            
            #if video.get('summary'              ):  Log.Info('summary:               {}'.format(video.get('summary')))
            #if video.get('contentRating'        ):  Log.Info('contentRating:         {}'.format(video.get('contentRating')))
            #if video.get('studio'               ):  Log.Info('studio:                {}'.format(video.get('studio')))
            #if video.get('rating'               ):  Log.Info('rating:                {}'.format(video.get('rating')))
            #if video.get('year'                 ):  Log.Info('year:                  {}'.format(video.get('year')))
            #if video.get('duration'             ):  Log.Info('duration:              {}'.format(video.get('duration')))
            #if video.get('originallyAvailableAt'):  Log.Info('originallyAvailableAt: {}'.format(video.get('originallyAvailableAt')))
            #if video.get('key'      ):  Log.Info('[ ] key:                   {}'.format(video.get('key'      ))); 
            #Log.Info(XML.StringFromElement(PLEX_MOVIES_XML))  #Un-comment for XML code displayed in logs
            break
        else:  count += WINDOW_SIZE[agent_type];  continue
        break      
      except Exception as e:  Log.Info("PLEX_URL_MOVIES - Exception: '{}'".format(e))     

  ##### TV Shows ###
  if agent_type=='show':

    ### PLEX_URL_TVSHOWS - TV Shows###
    count = 0
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_TVSHOWS_XML, count, total = xml_from_url_paging_load(PLEX_URL_TVSHOWS, library_key, count, WINDOW_SIZE[agent_type])
        for show in PLEX_TVSHOWS_XML.iterchildren('Directory'):
          if media.title==show.get('title'):   
            Log.Info('title:                 {}'.format(show.get('title')))
            if show.get('ratingKey'):  parentRatingKey = show.get('ratingKey')
            SaveFile(show.get('thumb' ), folder, 'series_poster')
            SaveFile(show.get('art'   ), folder, 'series_fanart')
            SaveFile(show.get('banner'), folder, 'series_banner')
            SaveFile(show.get('theme' ), folder, 'series_themes')
            for collection in show.iterchildren('Collection'):  Log.Info('collection:            {}'.format(collection.get('tag')));  collections.append(collection.get('tag'))
            
            #if show.get('summary'              ):  Log.Info('summary:               {}'.format(show.get('summary')))
            #if show.get('contentRating'        ):  Log.Info('contentRating:         {}'.format(show.get('contentRating')))
            #if show.get('studio'               ):  Log.Info('studio:                {}'.format(show.get('studio')))
            #if show.get('rating'               ):  Log.Info('rating:                {}'.format(show.get('rating')))
            #if show.get('year'                 ):  Log.Info('year:                  {}'.format(show.get('year')))
            #if show.get('duration'             ):  Log.Info('duration:              {}'.format(show.get('duration')))
            #if show.get('originallyAvailableAt'):  Log.Info('originallyAvailableAt: {}'.format(show.get('originallyAvailableAt')))
            #if show.get('key'                  ):  Log.Info('[ ] key:               {}'.format(show.get('key')))
            #Log.Info(XML.StringFromElement(show))  #Un-comment for XML code displayed in logs
            break
        else:  continue
        break      
      except Exception as e:  Log.Info("PLEX_URL_TVSHOWS - Exception: '{}'".format(e));  count=total

    ### PLEX_URL_SEASONS  - TV Shows seasons ###
    count = 0
    while count==0 or count<total and int(PLEX_XML_SEASONS.get('size')) == WINDOW_SIZE[agent_type]:
      try:
        PLEX_XML_SEASONS, count, total = xml_from_url_paging_load(PLEX_URL_SEASONS, library_key, count, WINDOW_SIZE[agent_type])
        for show in PLEX_XML_SEASONS.iterchildren('Directory') or []:
          if parentRatingKey == show.get('parentRatingKey'):  #parentTitle
            #Log.Info(XML.StringFromElement(show))
            Log.Debug("title: '{}'".format(show.get('title')))
            SaveFile(show.get('thumb' ), folder, 'season_poster', dynamic_name='' if show.get('title')=='Specials' else show.get('title')[6:] if show.get('title') else '') #SeasonXX
            SaveFile(show.get('art'   ), folder, 'season_fanart', dynamic_name='' if show.get('title')=='Specials' else show.get('title')[6:] if show.get('title') else '') #SeasonXX)
      except Exception as e:  Log.Info("PLEX_URL_SEASONS - Exception: '{}'".format(e));  raise
      
    if Prefs['episode_thumbs']!='Ignore':
      ### Episode thumbs list
      episodes=[]
      for season in sorted(media.seasons, key=natural_sort_key):
        for episode in sorted(media.seasons[season].episodes, key=natural_sort_key):
          episodes.append(os.path.split(media.seasons[season].episodes[episode].items[0].parts[0].file))
      
      ### PLEX_URL_EPISODE - TV Shows###
      count, total = 0, 0
      while count==0 or count<total and episodes:
        try:
          PLEX_XML_EPISODE, count, total = xml_from_url_paging_load(PLEX_URL_EPISODE, library_key, count, WINDOW_SIZE[agent_type])
          for episode in PLEX_XML_EPISODE.iterchildren('Video'):
            for part in episode.iterdescendants('Part'):
              if part.get('file') in episodes:
                episodes.remove(part.get('file'))
                folder, filename = os.path.split(part.get('file'))
                SaveFile(episode.get('thumb'), folder, 'episode_thumbs', dynamic_name=os.path.splitext(filename)[0])
        except Exception as e:  Log.Info("PLEX_URL_EPISODE - Exception: '{}', cound: {}, total: {}".format(e, count, total));  
    
    '''
    <Video ratingKey="7938" key="/library/metadata/7938" parentRatingKey="7937" grandparentRatingKey="7936" type="episode" title="The Beginning of a Dream" titleSort="Beginning of a Dream" grandparentKey="/library/metadata/7936" parentKey="/library/metadata/7937" grandparentTitle="Aikatsu Stars!" parentTitle="Season 1" summary="Yume Nijino is a first year middle school student who attends the idol school, Four Star Academy as a freshman student. Within the school is an idol group consisting of four idols known as &quot;S4&quot;, and within that group is Hime Shiratori who Yume yearns to be partners with. To start this new life, there will be a show on the main stage for all freshman students to compete in. As this is the first stage, Yume is to show herself on that stage!?" index="1" parentIndex="1" year="2016" thumb="/library/metadata/7938/thumb/1533373216" art="/library/metadata/7936/art/1532936993" grandparentThumb="/library/metadata/7936/thumb/1532936993" grandparentArt="/library/metadata/7936/art/1532936993" originallyAvailableAt="2016-04-07" addedAt="1531551485" updatedAt="1533373216">
    <Media id="7506">
    <Part id="7541" key="/library/parts/7541/1531551468/file.mp4" file="C:\Users\benja\Videos\_temp2\Aikatsu Stars! [anidb-11934]\01.mp4"/>
    </Media>
    <Director tag="Satou Teruo"/>
    <Writer tag="BN Pictures"/>
    '''
  if agent_type=='album':

    '''### PLEX_URL_ARTISTS ###
    count = 0
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        Log.Info(library_key)
        PLEX_ARTIST_XML = XML.ElementFromURL(PLEX_URL_ARTISTS.format(library_key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        Log.Info(XML.StringFromElement(PLEX_ARTIST_XML))  #Un-comment for XML code displayed in logs
        total = int(PLEX_ARTIST_XML.get('totalSize'))
        Log.Debug("PLEX_URL_MOVIES [{}-{} of {}]".format(count+1, count+int(PLEX_ARTIST_XML.get('size')) ,total))
        #for directory in PLEX_ARTIST_XML.iterchildren('Directory'):
        #  Log.Info("media.title: {}, media.parentTitle: {}, media.id: {}, directory.get('title'): {}".format(media.title, media.parentTitle, media.id, directory.get('title')))
        count += WINDOW_SIZE[agent_type]
      except Exception as e:  Log.Info("Exception: '{}'".format(e))    
    
    ### ALBUM ###
    count = 0
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_ALBUM_XML = XML.ElementFromURL(PLEX_URL_ALBUM.format(library_key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        total = int(PLEX_ALBUM_XML.get('totalSize'))
        Log.Debug("PLEX_URL_ALBUM [{}-{} of {}]".format(count+1, count+int(PLEX_ALBUM_XML.get('size')) ,total))
        
        #Log.Info(XML.StringFromElement(PLEX_ALBUM_XML))  #Un-comment for XML code displayed in logs
        Log.Info("media.title: {}, media.parentTitle: {}, media.id: {}".format(media.title, media.parentTitle, media.id))
        for directory in PLEX_ALBUM_XML.iterchildren('Directory'):
          Log.Info("directory.get('title'): {}, directory.get('parentTitle'): {}".format(directory.get('title'), directory.get('parentTitle')))
          if media.title==directory.get('title'):   
            if directory.get('summary'              ):  Log.Info('summary:               {}'.format(directory.get('summary')))
            if directory.get('parentTitle'          ):  Log.Info('parentTitle:           {}'.format(directory.get('parentTitle')))
            if directory.get('title'                ):  Log.Info('title:                 {}'.format(directory.get('title')))
            if Prefs['album_poster' ] and directory.get('thumb'):
              Log.Info('thumb:                 {}'.format(directory.get('thumb')))
              SaveFile(PLEX_SERVER_NAME+directory.get('thumb' ), os.path.join(folder, 'cover.jpg'     ), 'poster')
            if Prefs['artist_poster'] and directory.get('parentThumb') not in ('', directory.get('thumb')):  
              Log.Info('parentThumb:                 {}'.format(directory.get('parentThumb')))
              SaveFile(PLEX_SERVER_NAME+directory.get('thumb' ), os.path.join(folder, 'artist-poster.jpg'), 'poster')
            for collection in directory.iterchildren('Collection'):  Log.Info('collection:            {}'.format(collection.get('tag')));  collections.append(collection.get('tag'))
            found = True
            break
        else:  count += WINDOW_SIZE[agent_type];  continue
        break      
      except Exception as e:  Log.Info("Exception: '{}'".format(e))
    '''

    ### PLEX_URL_TRACK ###
    count = 0
    Log.Info("media.title: {}, media.parentTitle: {}, media.id: {}".format(media.title, media.parentTitle, media.id))
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        
        # Paging load of PLEX_URL_TRACK
        PLEX_XML_TRACK = XML.ElementFromURL(PLEX_URL_TRACK.format(library_key, count, WINDOW_SIZE[agent_type]), timeout=float(TIMEOUT))
        total = int(PLEX_XML_TRACK.get('totalSize'))
        Log.Debug("PLEX_URL_TRACK [{}-{} of {}]".format(count+1, count+int(PLEX_XML_TRACK.get('size')) ,total))
        count += WINDOW_SIZE[agent_type]
        #Log.Info(XML.StringFromElement(PLEX_XML_TRACK))  #Un-comment for XML code displayed in logs
        
        for track in PLEX_XML_TRACK.iterchildren('Track'):
          #Log.Info(XML.StringFromElement(track))
          for part in track.iterdescendants('Part'):
            if os.path.basename(part.get('file'))==item:
              Log.Info("[*] {}".format(item))              
              if os.path.exists(os.path.join(library_path, item)):
                Log.Info('[!] Skipping since on root folder')
                break
              
              # Artist poster
              if track.get('grandparentThumb') not in ('', track.get('parentThumb')):  SaveFile(track.get('grandparentThumb'), folder, 'artist_poster')
              else:                                                                    Log.Info('[ ] artist_poster not present or same as album')
              
              # Artist fanart
              if track.get('grandparentArt') not in ('', track.get('art')):            SaveFile(track.get('grandparentThumb'), folder, 'artist_fanart')
              else:                                                                    Log.Info('[ ] artist_fanart not present or same as album')
              
              # Album poster
              SaveFile(track.get('parentThumb'), folder, 'album_poster')
              
              # Album fanart
              SaveFile(track.get('art'        ), folder, 'album_fanart')
              
              # Log.Info(XML.StringFromElement(track))
              # Log.Info(XML.StringFromElement(part))
              # track
              # SaveFile(track.get('thumb'), os.path.join(folder, 'track.jpg'), 'album_track_poster')
              
              #Can extract posters and LRC from MP3 and m4a files
              break
          else:  continue
          count=total
          break
      except Exception as e:  Log.Info("Exception: '{}'".format(e))
    
  ### Collection loop for collection poster, fanart, summary ###
  count = 0
  while collections and (count==0 or count<total and int(PLEX_COLLECT_XML.get('size')) == WINDOW_SIZE[agent_type]):
    try:
      
      PLEX_COLLECT_XML, count, total = xml_from_url_paging_load(PLEX_URL_COLLECT, library_key, count, WINDOW_SIZE[agent_type])
      for directory in PLEX_COLLECT_XML.iterchildren('Directory'):
        if directory.get('title') in collections:
          Log.Debug("[ ] Directory: '{}'".format( directory.get('title') ))
          
          dirname = os.path.join(library_path if Prefs['collection_folder']=='local' else AgentDataFolder, '_Collections', directory.get('title'))
          SaveFile(directory.get('thumb'  ), dirname, 'collection_poster', library_key, directory.get('ratingKey'), dynamic_name=lang)
          SaveFile(directory.get('art'    ), dirname, 'collection_fanart', library_key, directory.get('ratingKey'), dynamic_name=lang)
          SaveFile(directory.get('summary'), dirname, 'collection_resume', library_key, directory.get('ratingKey'), dynamic_name=lang)
          #Log.Info(XML.StringFromElement(PLEX_COLLECT_XML))
          
          #directory.get('ratingKey')
          #contentRating
          #index
          #addedAt="1522877260" updatedAt="1522877268" childCount="0"
          
    except Exception as e:  Log.Info("Exception: '{}'".format(e))

### Agent declaration ##################################################################################################################################################
class LambdaTV(Agent.TV_Shows):
  name, primary_provider, fallback_agent, languages = 'Lambda', False, False, [Locale.Language.English]
  def search (self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'show')
  def update (self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'show')

class LambdaMovie(Agent.Movies):
  name, primary_provider, fallback_agent, languages = 'Lambda', False, False, [Locale.Language.English]
  def search (self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'movie')
  def update (self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'movie')

class LambdaAlbum(Agent.Album):
  name, primary_provider, fallback_agent, languages = 'Lambda', False, False, [Locale.Language.English]
  def search(self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'album')
  def update(self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'album')
