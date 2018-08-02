##Local Assets-Metadata Double Agent
- takes metadata in Plex and save it locally, including collections
- allow to import back local metadata that isn't handled by 'Local Media Assets' (collections, NFO files)

### Settings ([X] on by default, [ ] off by default, type: movie/show/album)
- [ ]  Series Themes ('library_root/show/theme.mp3')
- [X]  Series Poster ('library_root/show/poster.jpg')
- [ ]  Series Fanart ('library_root/show/fanart.jpg')
- [ ]  Series Banner ('library_root/show/banner.jpg')
- [X]  Season Poster ('library_root/show(/Season 1)/season-specials-poster.jpg|Season 1-poster.jpg')
- [ ]  Season Fanart ('library_root/show(/Season 1)/season-specials-fanart.jpg|Season 1-fanart.jpg')
- [ ] Episode Thumbs ('library_root/show(/Season 1)/xxx.jpg')
- [X]  Movies Poster ('library_root(/Movie)/Movie (year).jpg')
- [ ]  Movies Fanart ('library_root(/Movie)/Movie (year)-fanart.jpg')
- [X]  Collec Poster ('library_root/_Collections/collection_name/type-poster.jpg')
- [ ]  Collec Fanart ('library_root/_Collections/collection_name/type-fanart.jpg')
- [ ]  Collec Resume ('library_root/_Collections/collection_name/type-lang-summary.txt')
- [ ]  Artist Poster ('library_root/Artist/artist-poster.jpg')     (if in its own folder only?)
- [ ]  Artist Fanart ('library_root/Artist/artist-background.jpg') (if in its own folder only?)
- [X]  Albums poster ('library_root(/Artist)/Album/cover.jpg') 
- [ ]  Albums poster ('library_root(/Artist)/Album/background.jpg') 

### Installation

WebTools install
- Install WebTools https://forums.plex.tv/t/rel-webtools-unsupported-appstore/206843
- Connect to http://127.0.0.1:33400/
- paste https://github.com/ZeroQI/Lambda.bundle

Here is how to find the plug-in folder location: https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-
Plex main folder location:

    * '%LOCALAPPDATA%\Plex Media Server\'                                        # Windows Vista/7/8
    * '%USERPROFILE%\Local Settings\Application Data\Plex Media Server\'         # Windows XP, 2003, Home Server
    * '$HOME/Library/Application Support/Plex Media Server/'                     # Mac OS
    * '$PLEX_HOME/Library/Application Support/Plex Media Server/',               # Linux
    * '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/', # Debian,Fedora,CentOS,Ubuntu
    * '/usr/local/plexdata/Plex Media Server/',                                  # FreeBSD
    * '/usr/pbi/plexmediaserver-amd64/plexdata/Plex Media Server/',              # FreeNAS
    * '${JAIL_ROOT}/var/db/plexdata/Plex Media Server/',                         # FreeNAS
    * '/c/.plex/Library/Application Support/Plex Media Server/',                 # ReadyNAS
    * '/share/MD0_DATA/.qpkg/PlexMediaServer/Library/Plex Media Server/',        # QNAP
    * '/volume1/Plex/Library/Application Support/Plex Media Server/',            # Synology, Asustor
    * '/raid0/data/module/Plex/sys/Plex Media Server/',                          # Thecus
    * '/raid0/data/PLEX_CONFIG/Plex Media Server/'                               # Thecus Plex community    

Get the latest source zip in github release for hama https://github.com/ZeroQI/MLE.bundle > "Clone or download > Download Zip (named MLE.bundle-master.zip) and copy the folder inside named MLE.bundle-master into plug-ins folders but rename it into "MLE.bundle" (in short remove '-master' from foldername) :

### Troubleshooting:

If you ask for something already answered in the readme, or post scanner issues on the agent page or vice-versa, please donate (will be refered to as the RTFM tax)

### Possible improvement ([X] to be included in next version)

- [ ] Import into plex exported Collection and meta if not present (through HTTP post, makes it a double agent)
- [ ] XBMC compatible nfo export
- [ ] mp3/m4a cover+LRC file downloader from hte media file headers
- [ ] LRC Lyric file file downloader

LRC
- https://github.com/rikels/LyricsSearch/blob/master/lyrics.py Lyrics wikia & MiniLyrics
- https://github.com/serantes/getlyrics/blob/master/getlyrics.py Lyrics Workshop, lrc, lrcShow, ttplayer, lyricwiki chartlyric+,  romaji convertor
- https://gist.github.com/blueset/43172f5ecd32e75d9f9bc6b7e0177755 music.163.com
- https://github.com/blueset/LyricDownloader/blob/master/LyricDownloader.py qianqian.com
- https://github.com/doakey3/pylrc LRC to SRT
      
### History

Commissionned by rbeatse on the forum post: https://forums.plex.tv/t/looking-for-a-developer-to-make-an-app/274692
 
### Donation link:

[PayPal.Me/ZeroQI](https://PayPal.Me/ZeroQI) or better [Donation link](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=S8CUKCX4CWBBG&lc=IE&item_name=ZeroQI&item_number=Local%20Media%20Export%20Agent&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)
