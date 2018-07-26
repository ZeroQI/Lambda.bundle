## Local Media Export Plex Agent

Allow to save locally:
- Movies: Posters
- TV_Shows: Series (Posters, art, banner, theme), Season (posters, art)
- Collections (Poster, summary)
- Music: Artists (poster), Albums (Cover)

### Settings ([X] on by default, [ ] off by default)

- [ ] TV Shows themes
- [X] TV Shows Poster
- [ ] TV Shows Art
- [X] TV Shows Season poster
- [X] Collection Poster
- [X] Collection Art
- [X] Movie Poster
- [ ] Movie Art
- [X] Artist poster (if in its own folder only?)
- [X] Album poster
- [ ] NFO creation
- [X] Import NFO/Creation (complement Local media Assets Agent)

### Installation

No need for Plex token!

Here is how to find the plug-in folder location:
https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-

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

Get the latest source zip in github release for hama https://github.com/ZeroQI/MLE.bundle > "Clone or download > Download Zip
Folders Youtube-Agent.bundle-master.zip and copy inside folder Youtube-Agent.bundle-master in plug-ins folders but rename to "Youtube-Agent.bundle" (remove -master) :

### Troubleshooting:

If you ask for something already answered in the readme, or post scanner issues on the agent page or vice-versa, please donate (will be refered to as the RTFM tax)

### Possible improvement ([X] to be included in next version)

- [ ] XBMC compatible nfo export
- [ ] Import into plex exported Collection and meta if not present (through HTTP post, makes it a double agent)

### History

Commissionned by rbeatse
 on the forum post: https://forums.plex.tv/t/looking-for-a-developer-to-make-an-app/274692
 
### Donation link:

[PayPal.Me/ZeroQI](https://PayPal.Me/ZeroQI) or better [Donation link](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=S8CUKCX4CWBBG&lc=IE&item_name=ZeroQI&item_number=Local%20Media%20Agent&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)
