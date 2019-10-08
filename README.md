## Local Assets-Metadata Double Agent Features:
- Takes Plex metadata and save it locally alongside media files, including collections
- allow to import back local metadata exported through 'Local Media Assets' and also what isn't handled by 'Local Media Assets' (collection summary, not yet supported for upload: collection poster, fanart, not yet supported for upload/download: metadata text fields in NFO file)


### Agent Settings allow to ignore or select the naming convention for the exported files (* if enabled by default)
- Series:      (*)Poster, Fanart, Banner, Themes, 
- Seasons:     (*)Poster, Fanart, Banner
- Episodes:       Thumbs
- Movies:      (*)Poster, Fanart
- Collections: (*)Poster, Fanart, Resume (all fields for Movies and Series only as music collection only link to these)
- Artist:      (*)Poster, Fanart (in Album agent)
- Albums:      (*)poster, Fanart

you refresh metadata and it will export selected metadata


### Installation
WebTools manual install:
- Install WebTools https://forums.plex.tv/t/rel-webtools-unsupported-appstore/206843
- Connect to http://127.0.0.1:33400/
- paste the url for manual installation: https://github.com/ZeroQI/Lambda.bundle
 
Plex Manual Install:
- Get the latest source zip in github release https://github.com/ZeroQI/Lambda.bundle > "Clone or download > Download Zip (named Lambda.bundle-master.zip) and copy the folder inside named Lambda.bundle-master into plug-ins folders but rename it into "Lambda.bundle" (by removing '-master' from foldername):
- Here is how to find the plug-in folder location: https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-


### Troubleshooting:
Attach the following log on all queries:  Plex Media Server\Logs\PMS Plugin Logs\com.plexapp.agents.lambda.log
If you ask for something already answered in the readme, please donate (will be refered to as the RTFM tax)


### History
Commissionned by rbeatse on the forum post: https://forums.plex.tv/t/looking-for-a-developer-to-make-an-app/274692
I took on the challenge and started coding.

The aim is to replace with this double agent (import export):
- https://github.com/joshuaavalon/AvalonXmlAgent.bundle Avalon XML agent
- https://github.com/gboudreau/XBMCnfoTVImporter.bundle XBMC nfo TV Importer
- https://github.com/gboudreau/XBMCnfoMoviesImporter.bundle XBMC ndo Movies Importer

 
### Donation link:
[PayPal.Me/ZeroQI](https://PayPal.Me/ZeroQI) or better [Donation link](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=S8CUKCX4CWBBG&lc=IE&item_name=ZeroQI&item_number=Local%20Media%20Export%20Agent&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)


### Possible improvement ([X] to be included in next version)
- [ ] Import into plex exported Collection posters/fanart if not present (through HTTP post, makes it a double agent)
- [ ] XBMC compatible nfo export (manually updated/locked field detection) and import (if locked/manually edited)
- [ ] mp3/m4a cover+LRC file downloader from hte media file headers
- [ ] LRC Lyric file file downloader
