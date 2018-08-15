# -*- coding: utf-8 -*-

### Imports ##########################################################################################################################################
import os                        # [path] abspath, join, dirname
import re                        # split, compile
import time                      # sleep
import inspect                   # getfile, currentframe
import time                      # Used to print start time to console
import hashlib                   # md5

### Functions ########################################################################################################################################
def natural_sort_key(s):
  '''
    Turn a string into a chunks list like "z23a" -> ["z", 23, "a"] so it is sorted (1, 2, 3...) and not (1, 11, 12, 2, 3...). Usage:
    - In-place list sorting:  list.sort(key=natural_sort_key)
    - Return list copy:    sorted(list, key=natural_sort_key)
  '''
  return [ int(text) if text.isdigit() else text for text in re.split( re.compile('([0-9]+)'), str(s).lower() ) ]

def file_extension(file):
  ''' return file extension, and if starting with single dot in filename, equals what's after the dot 
  '''
  return file[1:] if file.count('.') == 1 and file.startswith('.') else os.path.splitext(file)[1].lstrip('.').lower()


def xml_from_url_paging_load(URL, key, count, window):
  ''' Load the URL xml page while handling total number of items and paging
  '''
  xml   = XML.ElementFromURL(URL.format(key, count, window), timeout=float(TIMEOUT))
  total = int(xml.get('totalSize') or 0)
  Log.Info("# [{:>4}-{:>4} of {:>4}] {}".format(count+1, count+int(xml.get('size') or 0), total, URL.format(key, count, window)))
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
  destination = os.path.join(path, filename.format(dynamic_name).replace('.ext', '.'+(file_extension(PMS+thumb) or 'jpg')))  #Log.Info("destination: {}".format(destination))
  ext         = file_extension(destination)  #Log.Info("ext: {}".format(ext))
  Log.Info("filename: {}, destination: {}, ext: {}".format(filename, destination, ext))
  if thumb:
    if Prefs[field]!='Ignored':
      try:
        if ext in ('jpg', 'mp3'):  content = HTTP.Request(PMS+thumb).content #response.headers['content-length']
        if ext=='txt':             content = thumb
        if ext=='xml':
          content='' #content have list of fields?
          #if meta in plex:  update mem xml  field
          #else if in mem:   update metadata field
          #save file if different
          #{ 'contentRating': directory.get('contentRating')
          #  'minYear'      : directory.get('minYear'      )
          #  'maxYear'      : directory.get('maxYear'      )
          #}
          '''
            file         = os.path.join(path, agent_type, '.nfo')
            nfo, changed = load_nfo_to_dict(file)  #no need to empty fill, loop will do
            for field in FieldsMovies:
              plex_meta = getattr(metadata, field)
              nfo_meta  = Dict   (nfo,      field)
              if plex_meta:
                if plex_meta==nfo_meta:  Log.Ingo('[=] field: xxxx identical')
                else:                    SaveDict(plex_meta, nfo, field);  changed = 1
              elif nfo_meta:             UpdateMetaField(metadata, metadata, MetaSources[language_source], FieldListMovies if movie else FieldListSeries, 'title', language_source, movie, source_list) 
              elif not present:          SaveDict(None, nfo, field)
            if not present or changed nfo in mem: Write_nfo_to_disk(file, nfo)
          
            for field in FieldsSeries:
              pass
            for season in sorted(media.seasons, key=natural_sort_key):
              for field in FieldsSeasons:
                pass  
              for episode in sorted(media.seasons[season].episodes, key=natural_sort_key):
                #episodes.append(media.seasons[season].episodes[episode].items[0].parts[0].file)
              
                for field in FieldsEpisodes:
            
          try:                 import xml.etree.cElementTree as ET
          except ImportError:  import xml.etree.ElementTree  as ET
          root   = etree.Element("root")                         #b'<root>'
          root   = etree.Element("root", interesting="totally")  #b'<root interesting="totally"/>'
          root = XML.Element(name, text=None, **kwargs)
          root.insert(0, etree.Element("child0"))
          root.append( etree.Element("child1") )
          child2 = etree.SubElement(root, "child2", attrib={}, **extra)
          start  = root[:1]
          end    = root[-1:]
          root.attrib["hello"] = "Guten Tag"
          root.attrib.get("no-such-attribute")
          root.text = "TEXT"
          root.tail = "TEXT"
          
          Core.storage.copy
          Core.storage.join_path
          Core.storage.file_exists
          Core.storage.remove_tree(Core.storage.join_path(Core.plugin_support_path, "Data", identifier)) 
          Core.storage.rename(Core.storage.join_path(self.system.bundleservice.plugins_path, bundle.name), inactive_path) 
          '''
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
    if ext in ('xml', nfo):  #update nfo in mem
      content='' #content have list of fields?
  else:  Log.Info('[ ] {} not present in Plex nor on disk'.format(field))

def UploadImagesToPlex(url_list, ratingKey, image_type):
  ''' URL uploader for field not in metadata like collections
  
      https://github.com/defract/TMDB-Collection-Data-Retriever/blob/master/collection_updater.py line 211
      - url_list:    url or [url, ...]
      - ratingKey:   #
      - image_type:  poster, fanart, season

      http://127.0.0.1:32400/photo/:/transcode?url=%2Flibrary%2Fmetadata%2F1326%2Ffile%3Furl%3Dupload%253A%252F%252Fposters%252Febe213fdbabb44fe6706c33bec7fa576a50da008%26X-Plex-Token%3Dxxxxxxxx&X-Plex-Token=
      url var decode1: /library/metadata/1326/file?url=upload%3A%2F%2Fposters%2Febe213fdbabb44fe6706c33bec7fa576a50da008&X-Plex-Token=TNmxEi64CzFSnbKhbQnw
      url var decode2: upload://posters/ebe213fdbabb44fe6706c33bec7fa576a50da008
      md5:             8954037BD59365EE7830FCFC3A72EE68
      sha1:            C5DC6B1D5128D3AE2D19A712074C52E992438954
      http://127.0.0.1:32400/library/metadata/1326/posters?X-Plex-Token=xxxxxxxxxxxxxxxx
      
      String.Quote()
      Hash.XXX(data): MD5, SHA1. SHA224, SHA256, SHA384, SHA512, CRC32
      hashlib.md5(data).hexdigest()      
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

def SetRating(key, rating):
  ''' Called when changing rating in Plex interface
  '''
  pass
  
def ValidatePrefs():
  ''' Agent settings shared and accessible in Settings>Tab:Plex Media Server>Sidebar:Agents>Tab:Movies/TV Shows/Albums>Tab:Lambda
      Pre-Defined ValidatePrefs function called when settings changed and output settings choosen (loading json file to get default settings and Prefs var list)
      Last option reset agent to default values in "DefaultPrefs.json" by deleting Prefs settings file 
  '''
  Prefs['reset_to_defaults']  #'Loaded preferences from DefaultPrefs.json' + 'Loaded the user preferences for com.plexapp.agents.lambda'
  filename_xml  = os.path.join(PlexRoot, 'Plug-in Support', 'Preferences',   'com.plexapp.agents.Lambda.xml')
  filename_json = os.path.join(PlexRoot, 'Plug-ins',        'Lambda.bundle', 'Contents', 'DefaultPrefs.json')
  Log.Info("".ljust(157, '='))
  Log.Info ("ValidatePrefs() - PlexRoot: '{}'".format(PlexRoot))
  Log.Info ("# agent settings json file: '{}'".format(os.path.relpath(filename_json, PlexRoot)))
  Log.Info ("# agent settings xml prefs: '{}'".format(os.path.relpath(filename_xml , PlexRoot)))
  if Prefs['reset_to_defaults'] and os.path.isfile(filename_xml):  os.remove(filename_xml)  #delete filename_xml file to reset settings to default
  elif os.path.isfile(filename_json):
    try:
      json = JSON.ObjectFromString(Core.storage.load(filename_json), encoding=None)
      for entry in json or []:  Log.Info("[{active}] Prefs[{key:<{width}}] = {value:<{width2}}, default = {default}".format(active=' ' if Prefs[entry['id']] in ('Ignored', False) else 'X', key="'"+entry['id']+"'", width=max(map(len, [x['id'] for x in json]))+2, value="'"+str(Prefs[entry['id']]).replace('¦','|')+"'", width2=max(map(len, [str(Prefs[x['id']]).replace('¦','|') for x in json]))+2, default="'{}'".format(entry['default'])))
    except Exception as e:  Log.Info("Error :"+str(e)+", filename_json: "+filename_json)
  Log.Info("".ljust(157, '='))
  return MessageContainer('Success', "DefaultPrefs.json valid")
 
def Start():
  ''' Called when starting the agent
  '''
  ValidatePrefs()

def Search(results, media, lang, manual, agent_type):
  ''' Assign unique ID
  '''
  Log(''.ljust(157, '='))
  Log("search() - lang:'{}', manual='{}', agent_type='{}'".format(lang, manual, agent_type))
  if agent_type=='movie':   results.Append(MetadataSearchResult(id = 'null', name=media.title,  score = 100))
  if agent_type=='show':    results.Append(MetadataSearchResult(id = 'null', name=media.show,   score = 100))
  if agent_type=='artist':  results.Append(MetadataSearchResult(id = 'null', name=media.artist, score = 100))
  if agent_type=='album':   results.Append(MetadataSearchResult(id = 'null', name=media.title,  score = 100))  #if manual media.name,name=media.title,  
  Log(''.ljust(157, '='))
  #metadata = media.primary_metadata  #full metadata object from here with all data, otherwise in Update() metadata will be empty
  
def Update(metadata, media, lang, force, agent_type):
  ''' Download metadata using unique ID, but 'title' needs updating so metadata changes are saved
  '''
  Log.Info(''.ljust(157, '='))
  Log.Info('Update(metadata, media="{}", lang="{}", force={}, agent_type={})'.format(media.title, lang, force, agent_type))
  
  ### Media folder retrieval ###
  if   agent_type=='movie':  path, item = os.path.split(media.items[0].parts[0].file)
  elif agent_type=='show':
    dirs=[]
    for s in media.seasons if media else []: # TV_Show:
      for e in media.seasons[s].episodes:
        path, item =  os.path.split(media.seasons[s].episodes[e].items[0].parts[0].file)
        break
      else: continue
      break
  elif agent_type=='album':
    for track in media.tracks:
      path, item = os.path.split(media.tracks[track].items[0].parts[0].file)
      break
  
  ### Plex libraries ###
  try:
    PLEX_LIBRARY_XML = XML.ElementFromURL(PMSSEC, timeout=float(TIMEOUT))  #Log.Info(XML.StringFromElement(PLEX_LIBRARY_XML))
    Log.Info('Libraries: ')
    for directory in PLEX_LIBRARY_XML.iterchildren('Directory'):
      for location in directory:
        Log.Info('[{}] id: {:>2}, type: {:>6}, library: {:<24}, path: {}'.format('*' if location.get('path') in path else ' ', directory.get("key"), directory.get('type'), directory.get('title'), location.get("path")))
        if ('artist' if agent_type=='album' else agent_type)==directory.get('type') and location.get('path') in path:
          library_key, library_path, library_name = directory.get("key"), location.get("path"), directory.get('title')
  except Exception as e:  Log.Info("PMSSEC - Exception: '{}'".format(e));  library_key, library_path, library_name = '', '', ''
  else:
    
    ### Extract season and transparent folder to reduce complexity and use folder as serie name ###
    rel_path            = os.path.relpath(path, library_path)
    series_root_folder  = os.path.join   (library_path, rel_path.split(os.sep, 1)[0])
    rel_reverse_path    = list(reversed(rel_path.split(os.sep)))
    subfolder_count     = len([file for file in os.listdir(series_root_folder) if os.path.isdir(os.path.join(series_root_folder, file))])
    SEASON_RX = [ 'Specials',                                                                                                                                           # Specials (season 0)
                  '(Season|Series|Book|Saison|Livre|S)[ _\-]*(?P<season>[0-9]{1,2}).*',                                                                                 # Season ##, Series #Book ## Saison ##, Livre ##, S##, S ##
                  '(?P<show>.*?)[\._\- ]+[sS](?P<season>[0-9]{2})',                                                                                                     # (title) S01
                  '(?P<season>[0-9]{1,2})a? Stagione.*',                                                                                                                # ##a Stagione
                  '(?P<season>[0-9]{1,2}).*',	                                                                                                                          # ##
                  '^.*([Ss]aga]|([Ss]tory )?[Aa][Rr][KkCc]).*$'                                                                                                         # Last entry in array, folder name droped but files kept: Story, Arc, Ark, Video
                ]                                                                                                                                                       #
    for folder in rel_reverse_path:              # 
      for rx in SEASON_RX:                      # in anime, more specials folders than season folders, so doing it first
        if re.match(rx, folder, re.IGNORECASE):  # get season number but Skip last entry in seasons (skipped folders)
          Log.Info('rx: {}'.format(rx))
          if rx!=SEASON_RX[-1]:  rel_reverse_path.remove(folder)        # Since iterating slice [:] or [:-1] doesn't hinder iteration. All ways to remove: reverse_path.pop(-1), reverse_path.remove(thing|array[0])
          break
    
    Log.Info('library_key: {}, library_path: {}, library_name: {}'.format(library_key, library_path, library_name))
    Log.Info("rel_path: {}, rel_reverse_path: {}".format(rel_path, rel_reverse_path))
    path = os.path.join(library_path, rel_path.split(rel_reverse_path[0])[0], rel_reverse_path[0])
    Log.Info("series folder detected: {}".format(path))
    Log.Info('')
    
  ### NFO - generate filename, Load nfo if present, empty root element otherwise, create nfo xml object backup ###
  #nfo_file = os.path.join(path, Prefs[ nfo_pref[agent_type] ])
  #if Prefs[ nfo_pref[agent_type] ]=='Ignored':  nfo_xml = None
  #elif os.path.exists(nfo_file):                nfo_xml  = XML.ObjectFromString(Core.storage.load(nfo_file))
  #else:                                         nfo_xml  = XML.Element(nfo_root_tag[agent_type], xsd="http://www.w3.org/2001/XMLSchema", xsi="http://www.w3.org/2001/XMLSchema-instance", text=None)
  #nfo_copy = nfo_xml
  
  ###  ###
  collections, parentRatingKey = [], ""
  
  ### Movies (PLEX_URL_MOVIES) ###
  if agent_type=='movie':
    
    count, total = 0, 0
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_XML_MOVIES, count, total = xml_from_url_paging_load(PLEX_URL_MOVIES, library_key, count, WINDOW_SIZE[agent_type])
        #Log.Info(XML.StringFromElement(PLEX_XML_MOVIES))  #Un-comment for XML code displayed in logs
        for video in PLEX_XML_MOVIES.iterchildren('Video'):
          if media.title==video.get('title'):   
            #Log.Info(XML.StringFromElement(video))  #Un-comment for XML code displayed in logs
            
            Log.Info('title:                 {}'.format(video.get('title')))
            filenoext = os.path.basename(os.path.splitext(media.items[0].parts[0].file)[0])
            
            ### Poster, Fanart ###            
            SaveFile(video.get('thumb'), path, 'movies_poster', dynamic_name=filenoext)
            SaveFile(video.get('art'  ), path, 'movies_fanart', dynamic_name=filenoext)
            
            ### Collections ###
            for collection in video.iterchildren('Collection'):
              collections.append(collection.get('tag'))
              Log.Info('collection:            {}'.format(collection.get('tag')))
            
            ### NFO ###
            #xml_element_add(nfo_xml, tag='title',          text=video.get('title'                ))
            #xml_element_add(nfo_xml, tag='sorttitle',     text=video.get(''                ))
            #xml_element_add(nfo_xml, tag='originaltitle', text=video.get(''                ))
            #xml_element_add(nfo_xml, tag='originaltitle', text=video.get('rating'               ))
            #xml_element_add(nfo_xml, tag='mpaa',           text=video.get('contentRating'        ))  #need to start with 'Rated '
            #xml_element_add(nfo_xml, tag='studio',         text=video.get('studio'               ))
            #xml_element_add(nfo_xml, tag='tagline',       text=video.get(''              ))
            #xml_element_add(nfo_xml, tag='plot',           text=video.get('summary'              ))
            #xml_element_add(nfo_xml, tag='director',      text=video.get(''              ))
            #xml_element_add(nfo_xml, tag='country',       text=video.get(''              ))
            #xml_element_add(nfo_xml, tag='genre',         text=video.get(''              ))
            #xml_element_add(nfo_xml, tag='credit',        text=video.get('summary'              ))  #writer
            if video.get('ratingKey'            ):  Log.Info('[ ] ratingKey:             {}'.format(video.get('ratingKey'            )));  parentRatingKey = video.get('ratingKey')
            if video.get('contentRating'        ):  Log.Info('[ ] contentRating:         {}'.format(video.get('contentRating'        )))
            if video.get('year'                 ):  Log.Info('[ ] year:                  {}'.format(video.get('year'                 )))
            if video.get('duration'             ):  Log.Info('[ ] duration:              {}'.format(video.get('duration'             )))
            if video.get('originallyAvailableAt'):  Log.Info('[ ] originallyAvailableAt: {}'.format(video.get('originallyAvailableAt')))
            if video.get('key'                  ):  Log.Info('[ ] key:                   {}'.format(video.get('key'                  )))
            break
        else:  continue
        break      
      except Exception as e:  Log.Info("PLEX_URL_MOVIES - Exception: '{}'".format(e)); count+=1
    Log.Info('')
  
  ##### TV Shows (PLEX_URL_TVSHOWS) ###
  if agent_type=='show':

    count, total = 0, 0
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_TVSHOWS_XML, count, total = xml_from_url_paging_load(PLEX_URL_TVSHOWS, library_key, count, WINDOW_SIZE[agent_type])
        for show in PLEX_TVSHOWS_XML.iterchildren('Directory'):
          if media.title==show.get('title'):   
            Log.Info('title:                 {}'.format(show.get('title')))
            if show.get('ratingKey'):  parentRatingKey = show.get('ratingKey')
            SaveFile(show.get('thumb' ), path, 'series_poster')
            SaveFile(show.get('art'   ), path, 'series_fanart')
            SaveFile(show.get('banner'), path, 'series_banner')
            SaveFile(show.get('theme' ), path, 'series_themes')
            
            for collection in show.iterchildren('Collection'):
              Log.Info('collection:            {}'.format(collection.get('tag')))
              collections.append(collection.get('tag'))
            #SaveFile(show.get('title' ), path, 'nfo', nfo=nfo, metadata_field=metadata.title)
            if show.get('summary'              ):  Log.Info('[ ] summary:               {}'.format(show.get('summary'              )))
            if show.get('contentRating'        ):  Log.Info('[ ] contentRating:         {}'.format(show.get('contentRating'        )))
            if show.get('studio'               ):  Log.Info('[ ] studio:                {}'.format(show.get('studio'               )))
            if show.get('rating'               ):  Log.Info('[ ] rating:                {}'.format(show.get('rating'               )))
            if show.get('year'                 ):  Log.Info('[ ] year:                  {}'.format(show.get('year'                 )))
            if show.get('duration'             ):  Log.Info('[ ] duration:              {}'.format(show.get('duration'             )))
            if show.get('originallyAvailableAt'):  Log.Info('[ ] originallyAvailableAt: {}'.format(show.get('originallyAvailableAt')))
            if show.get('key'                  ):  Log.Info('[ ] key:                   {}'.format(show.get('key'                  )))
            #Log.Info(XML.StringFromElement(show))  #Un-comment for XML code displayed in logs
            break
        else:  continue
        break      
      except Exception as e:  Log.Info("PLEX_URL_TVSHOWS - Exception: '{}'".format(e));  count=total+1
    Log.Info('')
  
    ### PLEX_URL_SEASONS  - TV Shows seasons ###
    count, total = 0, 0
    while count==0 or count<total and int(PLEX_XML_SEASONS.get('size')) == WINDOW_SIZE[agent_type]:
      try:
        PLEX_XML_SEASONS, count, total = xml_from_url_paging_load(PLEX_URL_SEASONS, library_key, count, WINDOW_SIZE[agent_type])
        for show in PLEX_XML_SEASONS.iterchildren('Directory') or []:
          if parentRatingKey == show.get('parentRatingKey'):  #parentTitle
            #Log.Info(XML.StringFromElement(show))
            if show.get('title'):  Log.Info('[ ] title:               {}'.format(show.get('title')))
            season = show.get('title')[6:].strip()
            for episode in media.seasons[season].episodes:
              season_folder = os.path.split(media.seasons[season].episodes[episode].items[0].parts[0].file)[0]
              SaveFile(show.get('thumb' ), season_folder, 'season_poster', dynamic_name='' if show.get('title')=='Specials' else season.zfill(2) if show.get('title') else '') #SeasonXX
              SaveFile(show.get('art'   ), season_folder, 'season_fanart', dynamic_name='' if show.get('title')=='Specials' else season.zfill(2) if show.get('title') else '') #SeasonXX)
              break
      except Exception as e:  Log.Info("PLEX_URL_SEASONS - Exception: '{}'".format(e));  raise
      
    ### Episode thumbs list
    if Prefs['episode_thumbs']!='Ignore':
      episodes=[]
      for season in sorted(media.seasons, key=natural_sort_key):
        for episode in sorted(media.seasons[season].episodes, key=natural_sort_key):
          episodes.append(media.seasons[season].episodes[episode].items[0].parts[0].file)
      Log.Info('episodes: {}'.format(episodes[:1]))
      Log.Info('')
  
      ### PLEX_URL_EPISODE - TV Shows###
      count, total = 0, 0
      while count==0 or count<total and episodes:
        try:
          PLEX_XML_EPISODE, count, total = xml_from_url_paging_load(PLEX_URL_EPISODE, library_key, count, WINDOW_SIZE[agent_type])
          for video in PLEX_XML_EPISODE.iterchildren('Video'):
            for part in video.iterdescendants('Part'):
              if part.get('file') in episodes:
                Log.Info('[{}]'.format(video.get('type')))
                Log.Info('[ ] grandparent Key / RatingKey / Thumb / Art / Title: {}, {}, {:<39}, {:<39}, {}'.format(video.get('grandparentKey'), video.get('grandparentRatingKey'), video.get('grandparentThumb'), video.get('grandparentArt'), video.get('grandparentTitle')))
                Log.Info('[ ]      parent Key / RatingKey / Thumb / Art / Title: {}, {}, {:<39}, {:<39}, {}'.format(video.get(     'parentKey'), video.get(     'parentRatingKey'), video.get(     'parentThumb'), video.get(     'parentArt'), video.get(     'parentTitle')))
                Log.Info('[ ]             key / ratingKey / thumb / art / title: {}, {}, {:<39}, {:<39}. {}'.format(video.get(           'key'), video.get(           'ratingKey'), video.get(           'thumb'), video.get(           'art'), video.get(           'title')))
                Log.Info('[ ] summary:               {}'.format(video.get('summary'              )))
                Log.Info('[ ] file:                  {}'.format(video.get('file'                 )))
                Log.Info('[ ] year:                  {}'.format(video.get('year'                 )))
                Log.Info('[ ] originallyAvailableAt: {}'.format(video.get('originallyAvailableAt')))
                Log.Info('[ ]               addedAt: {}'.format(video.get(              'addedAt')))
                Log.Info('[ ]             updatedAt: {}'.format(video.get(            'updatedAt')))
                #index, parentIndex
                Log.Info('[ ] id:                    {}'.format( part.get('id'     )))
                Log.Info('[ ] key:                   {}'.format( part.get('key'    )))
                Log.Info('[ ] file:                  {}'.format( part.get('file'   )))
                episodes.remove(part.get('file'))
                path, filename = os.path.split(part.get('file'))
                SaveFile(video.get('thumb'), path, 'episode_thumbs', dynamic_name=os.path.splitext(filename)[0])
                for director in video.iterdescendants('Director'):
                  Log.Info(  '[ ] director: {}'.format(director.get('tag')))
                for writer   in video.iterdescendants('Director'):
                  Log.Info(  '[ ] writer:   {}'.format(director.get('tag')))
            
        except Exception as e:  Log.Info("PLEX_URL_EPISODE - Exception: '{}', cound: {}, total: {}".format(e, count, total));  
    Log.Info('')
  
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
      except Exception as e:  Log.Info("Exception: '{}'".format(e))    
    
    ### ALBUM ###
    count = 0
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_ALBUM_XML = xml_from_url_paging_load(PLEX_URL_ALBUM, library_key, count, WINDOW_SIZE[agent_type])
        Log.Info("media.title: {}, media.parentTitle: {}, media.id: {}".format(media.title, media.parentTitle, media.id))
        for directory in PLEX_ALBUM_XML.iterchildren('Directory'):
          Log.Info("directory.get('title'): {}, directory.get('parentTitle'): {}".format(directory.get('title'), directory.get('parentTitle')))
          if media.title==directory.get('title'):   
            if directory.get('summary'              ):  Log.Info('summary:               {}'.format(directory.get('summary')))
            if directory.get('parentTitle'          ):  Log.Info('parentTitle:           {}'.format(directory.get('parentTitle')))
            if directory.get('title'                ):  Log.Info('title:                 {}'.format(directory.get('title')))
            if Prefs['album_poster' ] and directory.get('thumb'):
              Log.Info('thumb:                 {}'.format(directory.get('thumb')))
              SaveFile(PMS+directory.get('thumb' ), os.path.join(path, 'cover.jpg'     ), 'poster')
            if Prefs['artist_poster'] and directory.get('parentThumb') not in ('', directory.get('thumb')):  
              Log.Info('parentThumb:                 {}'.format(directory.get('parentThumb')))
              SaveFile(PMS+directory.get('thumb' ), os.path.join(path, 'artist-poster.jpg'), 'poster')
            for collection in directory.iterchildren('Collection'):  Log.Info('collection:            {}'.format(collection.get('tag')));  collections.append(collection.get('tag'))
            found = True
            break
        else:  continue
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
              
              # Artist poster, fanart
              if track.get('grandparentThumb') not in ('', track.get('parentThumb')):  SaveFile(track.get('grandparentThumb'), path, 'artist_poster')
              else:                                                                    Log.Info('[ ] artist_poster not present or same as album')
              if track.get('grandparentArt'  ) not in ('', track.get('art')):          SaveFile(track.get('grandparentThumb'), path, 'artist_fanart')
              else:                                                                    Log.Info('[ ] artist_fanart not present or same as album')
              
              SaveFile(track.get('parentThumb'), path, 'album_poster')  # Album poster
              SaveFile(track.get('art'        ), path, 'album_fanart')  # Album fanart
              # SaveFile(track.get('thumb'), os.path.join(path, 'track.jpg'), 'album_track_poster')
              # Log.Info(XML.StringFromElement(track))
              # Log.Info(XML.StringFromElement(part))
              
              #Can extract posters and LRC from MP3 and m4a files
              break
          else:  continue
          count=total
          break
      except Exception as e:  Log.Info("Exception: '{}'".format(e))
    
  ### Collection loop for collection poster, fanart, summary ###
  count, total = 0, 0
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
          #directory.get('contentRating')
          #directory.get('index')
          #directory.get('addedAt')
          #directory.get('updatedAt')
          #directory.get('childCount')
    except Exception as e:  Log.Info("Exception: '{}'".format(e))

  ### Save nfo if different from file or file didn't exist ###
  if Prefs[nfo_pref[agent_type]]!='Ignored' and nfo_xml and XML.StringFromObject(nfo_xml, encoding='utf-8')!=XML.StringFromObject(nfo_copy, encoding='utf-8'):
    Core.storage.save(nfo_file, XML.StringFromObject(nfo_xml, encoding='utf-8'))
  
### Agent declaration ################################################################################################################################
class LambdaTV(Agent.TV_Shows):
  name, primary_provider, fallback_agent, languages = 'Lambda', False, False, [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
  persist_stored_files = False
  contributes_to       = ['com.plexapp.agents.thetvdb', 'com.plexapp.agents.none']
  def search (self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'show')
  def update (self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'show')

class LambdaMovie(Agent.Movies):
  name, primary_provider, fallback_agent, languages = 'Lambda', False, False, [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
  persist_stored_files = False
  contributes_to       = ['com.plexapp.agents.imdb', 'com.plexapp.agents.none']
  def search (self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'movie')
  def update (self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'movie')

class LambdaAlbum(Agent.Album):
  name, primary_provider, fallback_agent, languages = 'Lambda', False, False, [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
  persist_stored_files = False
  contributes_to       = ['com.plexapp.agents.discogs', 'com.plexapp.agents.lastfm', 'com.plexapp.agents.plexmusic', 'com.plexapp.agents.none']
  def search(self, results,  media, lang, manual):  Search(results,  media, lang, manual, 'album')
  def update(self, metadata, media, lang, force ):  Update(metadata, media, lang, force,  'album')

### Variables ########################################################################################################################################
PlexRoot         = Core.app_support_path
AgentDataFolder  = os.path.join(PlexRoot, "Plug-in Support", "Data", "com.plexapp.agents.lambda", "DataItems")
PMS              = 'http://127.0.0.1:32400'  # Since PMS is hardcoded to listen on 127.0.0.1:32400, that's all we need
PMSLIB           = PMS + '/library'
PMSSEC           = PMSLIB + '/sections'
PAGING           = '&X-Plex-Container-Start={}&X-Plex-Container-Size={}'
PLEX_URL_MOVIES  = PMSSEC + '/{}/all?type=1'  + PAGING
PLEX_URL_TVSHOWS = PMSSEC + '/{}/all?type=2'  + PAGING
PLEX_URL_SEASONS = PMSSEC + '/{}/all?type=3'  + PAGING
PLEX_URL_EPISODE = PMSSEC + '/{}/all?type=4'  + PAGING
PLEX_URL_ARTISTS = PMSSEC + '/{}/all?type=8'  + PAGING
PLEX_URL_ALBUM   = PMSSEC + '/{}/all?type=9'  + PAGING
PLEX_URL_TRACK   = PMSSEC + '/{}/all?type=10' + PAGING
PLEX_URL_COLLECT = PMSSEC + '/{}/all?type=18' + PAGING
PLEX_URL_COITEMS = PMSSEC + '/{}/children'    + PAGING
PLEX_UPLOAD_TYPE = PMSLIB + '/metadata/{}/{}?url={}'
PLEX_UPLOAD_TEXT = PMSSEC + '/{}/all?type=18&id={}&summary.value={}'
WINDOW_SIZE      = {'movie': 30, 'show': 20, 'artist': 10, 'album': 10}
TIMEOUT          = 30
HTTP.CacheTime   = 0
HEADERS          = {}

nfo_pref         = {'movie': 'movies_nfo', 'show': 'series_nfo', 'album':'album_nfo'}
nfo_root_tag     = {'movie': '???',        'show': 'tvshow',     'album':'???'      }

FieldsMovies     = ('original_title', 'title', 'title_sort', 'roles', 'studio', 'year', 'originally_available_at', 'tagline', 'summary', 'content_rating', 'content_rating_age',
                    'producers', 'directors', 'writers', 'countries', 'posters', 'art', 'themes', 'rating', 'quotes', 'trivia')
FieldsSeries     = ('title', 'title_sort', 'originally_available_at', 'duration','rating',  'reviews', 'collections', 'genres', 'tags' , 'summary', 'extras', 'countries', 'rating_count',
                     'content_rating', 'studio', 'countries', 'posters', 'banners', 'art', 'themes', 'roles', 'original_title', 
                     'rating_image', 'audience_rating', 'audience_rating_image')  # Not in Framework guide 2.1.1, in https://github.com/plexinc-agents/TheMovieDb.bundle/blob/master/Contents/Code/__init__.py
FieldsSeasons    = ('summary','posters', 'art')  #'summary', 
FieldsEpisodes   = ('title', 'summary', 'originally_available_at', 'writers', 'directors', 'producers', 'guest_stars', 'rating', 'thumbs', 'duration', 'content_rating', 'content_rating_age', 'absolute_index') #'titleSort
FieldsArtists    = {}
FieldsAlbums     = {}
FieldsTracks     = {}

HTTP.Headers['User-Agent'     ] = 'Mozilla/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.54'
HTTP.Headers['Accept-Language'] = 'en-us'
