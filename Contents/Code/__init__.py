# -*- coding: utf-8 -*-

### Imports ##########################################################################################################################################
import os                        # [path] abspath, join, dirname
import re                        # split, compile
import time                      # sleep, strftime, localtime
import inspect                   # getfile, currentframe
import time                      # Used to print start time to console
import hashlib                   # md5
import copy                      # deepcopy
from   io import open as open

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
  return file[1:] if file.count('.') == 1 and file.startswith('.') else file.lower().split('.')[-1] if '.' in os.path.basename(file) else 'jpg'


def xml_from_url_paging_load(URL, key, count, window):
  ''' Load the URL xml page while handling total number of items and paging
  '''
  xml   = XML.ElementFromURL(URL.format(key, count, window), timeout=float(TIMEOUT))
  total = int(xml.get('totalSize') or 0)
  Log.Info("# [{:>4}-{:>4} of {:>4}] {}".format(count+1, count+int(xml.get('size') or 0), total, URL.format(key, count, window)))
  return xml, count+window, total

def SaveFile(thumb, path, field, key="", ratingKey="", dynamic_name="", nfo_xml=None, xml_field='', metadata_field=None, agent_type='no_agent_type', tags=''):
  ''' Save Metadata to file if different, or restore it to Plex if it doesn't exist anymore
      thumb:        url to picture or text or list...
      destination:  path to export file
      field:        Prefs field name to check if export/importing
  '''
  Log.Info('SaveFile("{}", "{}", "{}", "{}"...) Prefs[field]: "{}"'.format(thumb, path, field, Prefs[field], xml_field))
  if not thumb or not path or not field or not Prefs[field]:  return  #Log.Info('return due to empy field')
  
  ext = file_extension(thumb)
  if ext not in ('jpg', 'jpeg', 'png', 'tbn', 'mp3', 'txt', 'nfo'):  ext='jpg'  #ext=='' or len(ext)>4 or
  filename = Prefs[field].split('¦')[1 if dynamic_name  and '¦' in Prefs[field] else 0] if 'season' in field and '¦' in Prefs[field] else Prefs[field]  #dynamic name for seasons 1+ not specials
  if '{}'   in filename:  filename = filename.format(dynamic_name)
  if '.ext' in filename:  filename = filename.replace('.ext', '.'+ext)
  destination = os.path.join(path, filename)
  ext         = file_extension(destination)
  
  ### plex_value
  try:
    if thumb:
      if ext in ('jpg', 'mp3'):  plex_value = HTTP.Request(PMS+thumb).content #response.headers['content-length']
      else:                      plex_value = thumb #txt, nfo
    else:                        plex_value = ''  
    if DEBUG:  Log.Info('[?] plex_value:   "{}"'.format('binary...' if ext in ('jpg', 'jpeg', 'png', 'tbn', 'mp3') and plex_value else plex_value))
  except Exception as e:         Log.Info('plex_value - Exception: "{}"'.format(e));  return
  
  ### local_value
  try:
    #Log.Info('[!] ext:    "{}", destination: "{}"'.format(ext, destination))
    if ext=='nfo':
      tag         = nfo_xml.xpath('//{}/{}'.format(nfo_root_tag[field], xml_field))  #Log.Info('tag: {}'.format(tag))
      local_value = tag[0].text if tag else ''                                        #xml_field_value=nfo_xml.find(xml_field).text if nfo and nfo_xml.find(xml_field) else ''  # get xml field
    elif ext in ('jpg', 'jpeg', 'png', 'tbn', 'mp3', 'txt'): local_value = Core.storage.load(destination) if os.path.exists(destination) else ''
    else:
      if DEBUG:  Log.Info('[!] extension:    "{}"'.format(ext))
      local_value=None
      return
    if DEBUG:  Log.Info('[?] local_value: "{}"'.format('binary...' if ext in ('jpg', 'jpeg', 'png', 'tbn', 'mp3') and local_value else local_value))
  
  except Exception as e:         Log.Info('local_value - Exception: "{}"'.format(e));  return
 
  if Prefs[field]=='Ignored':    Log.Info('[^] {}: {}'.format(''.format() if xml_field else field, destination))  # Ignored but text output given for checking behaviour without updating 
  elif local_value==plex_value:  Log.Info('[=] No update - {}: {}'.format(field, destination))  # Identical
  else:
    
    # Plex update
    if local_value and (not plex_value or Prefs['metadata_source']=='local'):
      Log.Info('[@] Plex update {}: {}'.format(field, os.path.basename(destination)))
      if ext in ('jpg', 'mp3'):  UploadImagesToPlex(destination, ratingKey, 'poster' if 'poster' in field else 'art' if 'fanart' in field else field)
      elif ext=='nfo':
        if metadata_field is not None:  metadata_field = local_value  #setattr(metadata_field, field, tag[0].text)
      elif ext=='txt':
        if DEBUG:  Log.Info("destination: '{}'".format(destination))
        r = HTTP.Request(PLEX_UPLOAD_TEXT.format(key, ratingKey, String.Quote(Core.storage.load(destination))), headers=HEADERS, method='PUT')
        Log.Info('request content: {}, headers: {}, load: {}'.format(r.content, r.headers, r.load))
         
    # Local update
    elif plex_value and (not local_value or Prefs['metadata_source']=='plex'):
      Log.Info('[@] Local update - {}: {}'.format(field, os.path.basename(destination)))
      if ext in ('jpg', 'mp3', 'txt'):  
        if DEBUG:  Log.Info('[{}] {}: {}'.format('!' if os.path.exists(destination) else '*', field, os.path.basename(destination)))
        if not os.path.exists(os.path.dirname(destination)):  os.makedirs(os.path.dirname(destination))
        try:                                                  Core.storage.save(destination, plex_value)
        except Exception as e:                                Log.Info('Exception: "{}"'.format(e))
      elif ext=='nfo':
        tag = nfo_xml.find (".//elm")
        if tag:  tag.text = plex_value  #tag[0].text =   #"_setText" is an invalid attribute name because it starts with "_"
        else:
          if tags:
            tags['text']=thumb
            nfo_xml.append( XML.Element(xml_field, **tags ) )
          else:  nfo_xml.append( XML.Element(xml_field, text=thumb) )  #, **kwargs
      
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

#
def nfo_load(NFOs, path, field, filenoext=''):
  ''' Load local NFO file into 'NFOs' dict containing the following fields:
      - nfo preference name:
          Dict
          - path:  fullbath including filename to nfo                    Ex: NFOs['artist.nfo']['path' ]
          - xml:   local nfo xml object that will be updated in memory   Ex: NFOs['artist.nfo']['xml'  ]
          - local: copy of local nfo xml object for comparison           Ex: NFOs['artist.nfo']['local']
  '''
  Log.Info('nfo_load("{}", "{}", "{}")'.format(str(NFOs)[:20]+'...', path, field))
  nfo_file = os.path.join(path, Prefs[ field ])
  if '{}' in nfo_file:
    if filenoext=='':  Log.Info('alert - need to add filenoext to nfo_load to replace "{}" in agent setting filename: '+field)
    else:              nfo_file = nfo_file.format(os.path.basename(filenoext))
  Log.Info('nfo_load("{}", "{}", "{}") - nfo_file: "{}"'.format(str(NFOs)[:20]+'...', path, field, nfo_file))
  if Prefs[ field ]=='Ignored' and not DEBUG:  nfo_xml = None
  elif os.path.exists(nfo_file):               nfo_xml = XML.ObjectFromString(Core.storage.load(nfo_file))
  else:                                        nfo_xml = XML.Element(nfo_root_tag[field], xsd="http://www.w3.org/2001/XMLSchema", xsi="http://www.w3.org/2001/XMLSchema-instance", text=None)
  NFOs[field] = {'path': os.path.join(path, nfo_file), 'xml': nfo_xml, 'local': copy.deepcopy(nfo_xml)}
  if DEBUG:  Log.Info('nfo_xml: {}'.format(XML.StringFromElement(nfo_xml)))
  
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
  Log('search() - lang:"{}", manual="{}", agent_type="{}", media.primary_metadata.id: "{}"'.format(lang, manual, agent_type, media.primary_metadata.id))
  if agent_type=='movie':   results.Append(MetadataSearchResult(id = media.primary_metadata.id, name=media.title,  score = 100))
  if agent_type=='show':    results.Append(MetadataSearchResult(id = media.primary_metadata.id, name=media.show,   score = 100))
  if agent_type=='artist':  results.Append(MetadataSearchResult(id = media.primary_metadata.id, name=media.artist, score = 100))
  if agent_type=='album':   results.Append(MetadataSearchResult(id = media.primary_metadata.id, name=media.title,  score = 100))  #if manual media.name,name=media.title,  
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
    PLEX_LIBRARY_XML = XML.ElementFromURL(PMSSEC, timeout=float(TIMEOUT))
    Log.Info('Libraries: ')
    for directory in PLEX_LIBRARY_XML.iterchildren('Directory'):
      for location in directory:
        Log.Info('[{}] id: {:>2}, type: {:>6}, library: {:<24}, path: {}'.format('*' if location.get('path') in path else ' ', directory.get("key"), directory.get('type'), directory.get('title'), location.get("path")))
        if ('artist' if agent_type=='album' else agent_type)==directory.get('type') and location.get('path') in path:
          library_key, library_path, library_name = directory.get("key"), location.get("path"), directory.get('title')
  except Exception as e:  Log.Info("PMSSEC - Exception: '{}'".format(e));  library_key, library_path, library_name = '', '', ''
  else:
    
    ### Extract season and transparent folder to reduce complexity and use folder as serie name ###
    rel_path            = os.path.relpath(path, library_path).lstrip('.')
    series_root_folder  = os.path.join   (library_path, rel_path.split(os.sep, 1)[0]).rstrip('\\')
    rel_reverse_path    = list(reversed(rel_path.split(os.sep))) if rel_path!='' else []
    Log.Info('series_root_folder: "{}", rel_path: "{}", rel_reverse_path: "{}"'.format(series_root_folder, rel_path, rel_reverse_path))
    subfolder_count     = len([file for file in os.listdir(series_root_folder) if os.path.isdir(os.path.join(series_root_folder, file))] or [])
    SEASON_RX = [ 'Specials',                                                                                                                                           # Specials (season 0)
                  '(Season|Series|Book|Saison|Livre|S)[ _\-]*(?P<season>[0-9]{1,2}).*',  # Season ##, Series #Book ## Saison ##, Livre ##, S##, S ##
                  '(?P<show>.*?)[\._\- ]+[sS](?P<season>[0-9]{2})',                      # (title) S01
                  '(?P<season>[0-9]{1,2})a? Stagione.*',                                 # ##a Stagione
                  '(?P<season>[0-9]{1,2}).*',	                                           # ##
                  '^.*([Ss]aga]|([Ss]tory )?[Aa][Rr][KkCc]).*$'                          # Last entry in array, folder name droped but files kept: Story, Arc, Ark, Video
                ]                                                                                                                                                       #
    for folder in rel_reverse_path:
      for rx in SEASON_RX:
        if re.match(rx, folder, re.IGNORECASE):
          Log.Info('rx: {}'.format(rx))
          if rx!=SEASON_RX[-1]:  rel_reverse_path.remove(folder) # get season number but Skip last entry in seasons (skipped folders) #  iterating slice [:] or [:-1] doesn't hinder iteration. All ways to remove: reverse_path.pop(-1), reverse_path.remove(thing|array[0])
          break
    path = os.path.join(library_path, rel_path.split(rel_reverse_path[0])[0], rel_reverse_path[0]) if rel_reverse_path else library_path
    Log.Info('library_key: {}, library_path: {}, library_name: {}'.format(library_key, library_path, library_name))
    Log.Info("rel_path: {}, rel_reverse_path: {}".format(rel_path, rel_reverse_path))
    Log.Info("series folder detected: {}".format(path))
    Log.Info('')
    
  ### Variables initialization ###
  NFOs            = {}
  collections     = []
  parentRatingKey = ""
  
  ### Movies (PLEX_URL_MOVIES) ###
  if agent_type=='movie':
    
    #Load nfo file if present
    count, total = 0, 0
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_XML_MOVIES, count, total = xml_from_url_paging_load(PLEX_URL_MOVIES, library_key, count, WINDOW_SIZE[agent_type])
        for video in PLEX_XML_MOVIES.iterchildren('Video'):
          if media.title==video.get('title'):   
            Log.Info('title:                 {}'.format(video.get('title')))
            filenoext = '.'.join(media.items[0].parts[0].file.split('.')[:-1])
            
            ### Poster, Fanart ###            
            SaveFile(video.get('thumb'), path, 'movies_poster', dynamic_name=filenoext)
            SaveFile(video.get('art'  ), path, 'movies_fanart', dynamic_name=filenoext)
            
            ### NFO ###
            nfo_load(NFOs, path, 'movies_nfo', filenoext=filenoext)
            duration = str(int(video.get('duration'))/ (1000 * 60)) if video.get('duration').isdigit() else "0" # in minutes in nfo in ms in Plex
            rated      = ('Rated '+video.get('contentRating')) if video.get('contentRating') else ''
            date_added = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(video.get('addedAt'))))
            SaveFile(video.get('title'                ), path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='title',          metadata_field=metadata.title,                   agent_type=agent_type, dynamic_name=filenoext)
            #SaveFile(video.get('titleSort'            ), path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='sorttitle',      metadata_field=metadata.sort_title,              agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(video.get('originalTitle'        ), path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='originaltitle',  metadata_field=metadata.original_title,          agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(video.get('tagline'              ), path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='tagline',        metadata_field=metadata.tagline,                 agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(video.get('rating'               ), path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='rating',         metadata_field=metadata.rating,                  agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(video.get('studio'               ), path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='studio',         metadata_field=metadata.studio,                  agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(video.get('summary'              ), path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='plot',           metadata_field=metadata.summary,                 agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(video.get('year'                 ), path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='year',           metadata_field=metadata.year,                    agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(duration                          , path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='runtime',        metadata_field=metadata.duration,                agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(video.get('originallyAvailableAt'), path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='aired',          metadata_field=metadata.originally_available_at, agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(rated                             , path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='mpaa',           metadata_field=metadata.content_rating,          agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(date_added                        , path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='dateadded',      metadata_field=None,                             agent_type=agent_type, dynamic_name=filenoext)
            SaveFile(metadata.id                        , path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='uniqueid',      metadata_field=None,                             agent_type=agent_type, dynamic_name=filenoext, tags={'type':"unknown", 'default':"true"})
            for tag in video.iterchildren('Director'  ):  SaveFile(tag.get('tag') , path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='director', metadata_field=metadata.directors, agent_type=agent_type, dynamic_name=filenoext)
            for tag in video.iterchildren('Writer'    ):  SaveFile(tag.get('tag') , path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='credits',  metadata_field=metadata.writers,   agent_type=agent_type, dynamic_name=filenoext)
            for tag in video.iterchildren('Genre'     ):  SaveFile(tag.get('tag') , path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='genre',    metadata_field=metadata.genres,    agent_type=agent_type, dynamic_name=filenoext)
            for tag in video.iterchildren('Country'   ):  SaveFile(tag.get('tag') , path, 'movies_nfo', nfo_xml=NFOs['movies_nfo']['xml'], xml_field='country',  metadata_field=metadata.countries, agent_type=agent_type, dynamic_name=filenoext)
            for tag in video.iterchildren('Collection'):  collections.append(tag.get('tag'))
            Log.Info('collection:            {}'.format(collections))
            '''for tag in video.iterchildren('Role'      ):  tag.get('tag')
              <actor clear="true"> 
                <name></name>
                <role></role>
                <order></order>
                <thumb></thumb>
              </actor>
            '''
            #Log.Info(XML.StringFromElement(video))  #Un-comment for XML code displayed in logs
            #if video.get('ratingKey'            ):  Log.Info('[ ] ratingKey:             {}'.format(video.get('ratingKey'            )));  parentRatingKey = video.get('ratingKey')
            #if video.get('key'                  ):  Log.Info('[ ] key:                   {}'.format(video.get('key'                  )))
            break
        else:  continue
        break      
      except Exception as e:  Log.Info('PLEX_URL_MOVIES - Exception: "{}", e.message: {}, e.args: {}'.format(e, e.message, e.args)); count+=1
    Log.Info('')
  
  ##### TV Shows (PLEX_URL_TVSHOWS) ###
  if agent_type=='show':

    #Load nfo file if present
    nfo_load(NFOs, path,  'series_nfo')
    
    ### PLEX_URL_TVSHOWS
    count, total = 0, 0
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        PLEX_TVSHOWS_XML, count, total = xml_from_url_paging_load(PLEX_URL_TVSHOWS, library_key, count, WINDOW_SIZE[agent_type])
        for show in PLEX_TVSHOWS_XML.iterchildren('Directory'):
          if media.title==show.get('title'):   
            duration = str(int(show.get('duration'))/ (1000 * 60)) if show.get('duration').isdigit() else "0" # in minutes in nfo in ms in Plex
            rated      = ('Rated '+show.get('contentRating')) if show.get('contentRating') else ''
            #date_added = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(show.get('addedAt'))))
            Log.Info('title:                 {}'.format(show.get('title')))
            if show.get('ratingKey'):  parentRatingKey = show.get('ratingKey')
            
            SaveFile(show.get('thumb'                ), path, 'series_poster')
            SaveFile(show.get('art'                  ), path, 'series_fanart')
            SaveFile(show.get('banner'               ), path, 'series_banner')
            SaveFile(show.get('theme'                ), path, 'series_themes')
            SaveFile(show.get('title'                ), path, 'series_nfo', nfo_xml=NFOs['series_nfo']['xml'], xml_field='title',   metadata_field=metadata.title,                   agent_type=agent_type)
            SaveFile(show.get('summary'              ), path, 'series_nfo', nfo_xml=NFOs['series_nfo']['xml'], xml_field='plot',    metadata_field=metadata.summary,                 agent_type=agent_type)
            SaveFile(rated                            , path, 'series_nfo', nfo_xml=NFOs['series_nfo']['xml'], xml_field='mpaa',    metadata_field=metadata.summary,                 agent_type=agent_type)
            SaveFile(show.get('studio'               ), path, 'series_nfo', nfo_xml=NFOs['series_nfo']['xml'], xml_field='studio',  metadata_field=metadata.studio,                  agent_type=agent_type)
            SaveFile(show.get('rating'               ), path, 'series_nfo', nfo_xml=NFOs['series_nfo']['xml'], xml_field='rating',  metadata_field=metadata.rating,                  agent_type=agent_type)
            SaveFile(duration                         , path, 'series_nfo', nfo_xml=NFOs['series_nfo']['xml'], xml_field='runtime', metadata_field=metadata.duration,                agent_type=agent_type)
            SaveFile(show.get('originallyAvailableAt'), path, 'series_nfo', nfo_xml=NFOs['series_nfo']['xml'], xml_field='aired',   metadata_field=metadata.originally_available_at, agent_type=agent_type)
            for tag in show.iterchildren('Collection'):  collections.append(tag.get('tag'))
            for tag in show.iterchildren('Genre'     ):  SaveFile(tag.get('tag'                ), path, 'series_nfo', nfo_xml=NFOs['series_nfo']['xml'], xml_field='genre',   metadata_field=metadata.genres,                   agent_type=agent_type)
            for tag in show.iterchildren('Role'      ):  Log.Info('role:                  {}'.format(tag.get('tag')))
            Log.Info('collection:            {}'.format(collections))  
            
            #if show.get('key'                  ):  Log.Info('[ ] key:                   {}'.format(show.get('key'                  )))
            #Log.Info("test: {}".format(XML.StringFromElement(show)))  #Un-comment for XML code displayed in logs
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
              Log.Info('1')
              season_folder = os.path.split(media.seasons[season].episodes[episode].items[0].parts[0].file)[0]
              Log.Info('2')
              SaveFile(show.get('thumb' ), season_folder, 'season_poster', dynamic_name='' if show.get('title')=='Specials' else season.zfill(2) if show.get('title') else '') #SeasonXX
              Log.Info('3')
              SaveFile(show.get('art'   ), season_folder, 'season_fanart', dynamic_name='' if show.get('title')=='Specials' else season.zfill(2) if show.get('title') else '') #SeasonXX)
              break
      except Exception as e:  Log.Info("PLEX_URL_SEASONS - Exception: '{}'".format(e));  #raise
      
    ### Episode thumbs list
    if Prefs['episode_thumbs']!='Ignore':
      episodes={}
      for season in sorted(media.seasons, key=natural_sort_key):
        for episode in sorted(media.seasons[season].episodes, key=natural_sort_key):
          episodes[media.seasons[season].episodes[episode].items[0].parts[0].file] = (season, episode)
      
      ### PLEX_URL_EPISODE - TV Shows###
      count, total = 0, 0
      while count==0 or count<total and episodes:
        try:
          PLEX_XML_EPISODE, count, total = xml_from_url_paging_load(PLEX_URL_EPISODE, library_key, count, WINDOW_SIZE[agent_type])
          for video in PLEX_XML_EPISODE.iterchildren('Video'):
            for part in video.iterdescendants('Part'):
              if part.get('file') in episodes:
                season, episode  = episodes[part.get('file')]
                filenoext        = '.'.join(os.path.basename(part.get('file')).split('.')[:-1])
                #return file[1:] if file.count('.') == 1 and file.startswith('.') else file.lower().split('.')[-1]
                Log.Info('filenoext: "{}"'.format(filenoext))
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
                del episodes[part.get('file')]  #.pop('key', None)
                dirname, filename = os.path.split(part.get('file'))
                
                #nfo
                nfo_load(NFOs, dirname, 'episode_nfo', filenoext)
                SaveFile(video.get('title'),                 os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='title',     metadata_field=metadata.seasons[season].episodes[episode].title,                    agent_type=agent_type, dynamic_name=filenoext)
                SaveFile(video.get('summary'),               os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='plot',      metadata_field=metadata.seasons[season].episodes[episode].summary,                  agent_type=agent_type, dynamic_name=filenoext)
                SaveFile(video.get('originallyAvailableAt'), os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='aired',     metadata_field=metadata.seasons[season].episodes[episode].originally_available_at,  agent_type=agent_type, dynamic_name=filenoext)
                SaveFile(video.get('thumb'                ), dirname,                           'episode_thumbs', dynamic_name=os.path.splitext(filename)[0])
                #SaveFile(video.get('thumb'                ), os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='thumb',      metadata_field=metadata.seasons[season].episodes[episode].thumbs,                  agent_type=agent_type, dynamic_name=filenoext)
                #art/fanart|poster
                
                for director in video.iterdescendants('Director'):
                  Log.Info(  '[ ] director: {}'.format(director.get('tag')))
                  SaveFile(director.get('tag'),  os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='director',     metadata_field=metadata.seasons[season].episodes[episode].directors,  agent_type=agent_type, dynamic_name=filenoext)
                  break
                for writer   in video.iterdescendants('Director'):
                  Log.Info(  '[ ] writer:   {}'.format(writer.get('tag')))
                  SaveFile(writer.get('tag'),  os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='credits',     metadata_field=metadata.seasons[season].episodes[episode].writers,  agent_type=agent_type, dynamic_name=filenoext)
                  
                '''
                #originaltitle
                #showtitle
                #userrating
                #tagline'
                #runtime
                #thumb
                #mpaa
                #playcount
                #last played
                #genre multi
                #
                <premiered></premiered>	No	No	
                <status></status>
                <studio></studio>	No	Yes	Supports "clear" attribute
                <trailer></trailer>
                <actor>
                  <name></name>
                  <role></role>
                  <order></order>
                  <thumb></thumb>
                </actor>
                <art>
                  <fanart></fanart>
                  <poster></poster>
                </art>
                '''
                #nfo no upload to metadata
                SaveFile(season,               os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='season',          metadata_field=None, agent_type=agent_type)
                SaveFile(episode,              os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='episode',         metadata_field=None, agent_type=agent_type)
                SaveFile(video.get('addedAt'), os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='dateadded',       metadata_field=None, agent_type=agent_type)
                SaveFile(filename,             os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='file',            metadata_field=None, agent_type=agent_type)
                SaveFile(dirname,              os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='path',            metadata_field=None, agent_type=agent_type)
                SaveFile(part.get('file'),     os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='filenameandpath', metadata_field=None, agent_type=agent_type)
                SaveFile(path,                 os.path.dirname(part.get('file')), 'episode_nfo', nfo_xml=NFOs['episode_nfo']['xml'], xml_field='basepath',        metadata_field=None, agent_type=agent_type)
                #<file><path><filenameandpath><basepath></basepath>
                
        except Exception as e:  Log.Info("PLEX_URL_EPISODE - Exception: '{}', count: {}, total: {}".format(e, count, total));  
    Log.Info('')
  
  if agent_type=='album':

    #Load nfo file if present
    nfo_load(NFOs, path, 'album_nfo')
    nfo_load(NFOs, path, 'artist_nfo')
    
    ### PLEX_URL_ARTISTS ###
    '''count = 0
    while count==0 or count<total:  #int(PLEX_TVSHOWS_XML.get('size')) == WINDOW_SIZE[agent_type] and
      try:
        #Log.Info(library_key)
        PLEX_ARTIST_XML, count, total = xml_from_url_paging_load(PLEX_URL_ARTISTS, library_key, count, WINDOW_SIZE[agent_type])
        Log.Debug("PLEX_URL_ARTISTS [{}-{} of {}]".format(count+1, count+int(PLEX_ARTIST_XML.get('size')) ,total))
        for directory in PLEX_ARTIST_XML.iterchildren('Directory'):
          if media.parentTitle==directory.get('title'):
            Log.Info(XML.StringFromElement(directory))  #Un-comment for XML code displayed in logs
            #Log.Info("media.title: {}, media.parentTitle: {}, media.id: {}, directory.get('title'): {}".format(media.title, media.parentTitle, media.id, directory.get('title')))
            SaveFile(directory.get('title'           ), path, 'artist_nfo', nfo_xml=nfo_xml, xml_field='name',      metadata_field=metadata.title,                   agent_type=agent_type)
            SaveFile(directory.get('summary'         ), path, 'artist_nfo', nfo_xml=nfo_xml, xml_field='biography', metadata_field=metadata.summary,                 agent_type=agent_type)
            for genre in directory.iterdescendants('Genre'):
              Log.Info(  '[ ] genre: {}'.format(genre.get('tag')))
              SaveFile(genre.get('tag'               ), path, 'artist_nfo', nfo_xml=nfo_xml, xml_field='style',      metadata_field=metadata.genres,                   agent_type=agent_type)
              
      except Exception as e:  Log.Info("Exception: '{}'".format(e))    
    '''
    
    ### ALBUM ###
    '''count = 0
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
      Log.Info('PLEX_URL_COLLECT')
      PLEX_COLLECT_XML, count, total = xml_from_url_paging_load(PLEX_URL_COLLECT, library_key, count, WINDOW_SIZE[agent_type])
      for directory in PLEX_COLLECT_XML.iterchildren('Directory'):
        if directory.get('title') in collections:
          dirname = os.path.join(library_path if Prefs['collection_folder']=='root' else AgentDataFolder, '_Collections', directory.get('title'))
          Log.Info(''.ljust(157, '-'))
          Log.Info('[ ] Collection: "{}", path: "{}"'.format( directory.get('title'), dirname ))
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
  Log.Info(''.ljust(157, '-'))
  
  ### Save NFOs if different from local copy or file didn't exist ###
  Log.Info('NFO files')
  for nfo in NFOs:
    if Prefs[nfo]!='Ignored':
      nfo_string_xml     = XML.StringFromElement(NFOs[nfo]['xml'  ], encoding='utf-8')
      if nfo_string_xml == XML.StringFromElement(NFOs[nfo]['local'], encoding='utf-8'):  Log.Info('[=] {:<12} path: "{}"'.format(nfo, NFOs[nfo]['path']))
      else:                                                                              Log.Info('[X] {:<12} path: "{}"'.format(nfo, NFOs[nfo]['path']));  Core.storage.save(NFOs[nfo]['path'], nfo_string_xml)
    else:                                                                                Log.Info('[ ] {:<12} path: "{}"'.format(nfo, NFOs[nfo]['path']))
    #if DEBUG:  Log.Info(XML.StringFromElement(NFOs[nfo]['xml']))
         
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
DEBUG            = False #True
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

nfo_root_tag     = {'movies_nfo': 'movie', 'series_nfo': 'tvshow', 'album_nfo': 'album', 'artist_nfo':'artist_nfo', 'episode_nfo':'episodedetails'} #top level parent tag
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
