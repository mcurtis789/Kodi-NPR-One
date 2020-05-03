#
#  Copyright 2019 (Curtis)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#


import xbmc,xbmcaddon,xbmcplugin,xbmcgui
import csv, urllib2, os, sys, re
import npr
from requests.utils import unquote
from requests.utils import quote

__XBMC_Revision__ = xbmc.getInfoLabel('System.BuildVersion')
__settings__      = xbmcaddon.Addon(id='plugin.audio.nprone')
__addondir__      = __settings__.getAddonInfo('path') 
__language__      = __settings__.getLocalizedString
__version__       = __settings__.getAddonInfo('version')
__name__          = __settings__.getAddonInfo('name')
__addonname__     = "NPR One - National Public Radio"
__addonid__       = "plugin.audio.nprone"
__author__        = "Mike Curtis"

__url__ = sys.argv[0]
# Get the plugin handle as an integer number.
__handle__ = int(sys.argv[1])
__arg__ = sys.argv[2]
__stationsList__ = []
__streamList__ = []
__podcastList__ = []

_MAINMENU = [
        'Live Radio',
        'Podcasts'
]
_SAVEDPODCASTS = (
        'Tink Desk Concerts',
        'Planet Money',
        'Detroit Today',
        'Life Kit',
        'Car Talk',
        'Wait Wait...Don\'t Tell Me!',
        'The NPR Politics Podcast',
        '1A',
        'TED Radio Hour',
        'Hidden Brain',
        'Fresh Air',
        'Code Switch',
        'Radiolab',
        'Invisibilia',
        'Freakonomics Radio',
        'On the Media'
)
## {{{ http://code.activestate.com/recipes/577305/ (r1)
_STATES = (
        'Alaska',
        'Alabama',
        'Arkansas',
        'American Samoa',
        'Arizona',
        'California',
        'Colorado',
        'Connecticut',
        'District of Columbia',
        'Delaware',
        'Florida',
        'Georgia',
        'Guam',
        'Hawaii',
        'Iowa',
        'Idaho',
        'Illinois',
        'Indiana',
        'Kansas',
        'Kentucky',
        'Louisiana',
        'Massachusetts',
        'Maryland',
        'Maine',
        'Michigan',
        'Minnesota',
        'Missouri',
        'Northern Mariana Islands',
        'Mississippi',
        'Montana',
        'North Carolina',
        'North Dakota',
        'Nebraska',
        'New Hampshire',
        'New Jersey',
        'New Mexico',
        'Nevada',
        'New York',
        'Ohio',
        'Oklahoma',
        'Oregon',
        'Pennsylvania',
        'Puerto Rico',
        'Rhode Island',
        'South Carolina',
        'South Dakota',
        'Tennessee',
        'Texas',
        'Utah',
        'Virginia',
        'Virgin Islands',
        'Vermont',
        'Washington',
        'Wisconsin',
        'West Virginia',
        'Wyoming'
)    
## end of http://code.activestate.com/recipes/577305/ }}}

def regexurl(url):
    l = re.findall(r"(http.*)",url)
    return l[0]

def readAuth(path):
    if os.path.isfile(path):
        f=open(path,'r')
        config = ast.literal_eval(f.read())
        if "token" in config:
            return False

def getpodcasts(podcasts):
    podcast = unquote(podcasts)
    xbmc.log("looking for: "+podcast,level=xbmc.LOGNOTICE)
    search = npr.Search(podcast)
    stories = search.response['items']
    i = 0
    for key in stories:
        if len(stories[i]["items"]) > 0:
            lst = [stories[i]["items"][0]['attributes']['title'],stories[i]["items"][0]['links']['audio'][0]['href']]
            __podcastList__.append(lst)
        else:
            break
        i = i+1

def getstations(locations):
    location = unquote(locations)
    xbmc.log("looking for: "+location,level=xbmc.LOGNOTICE)
    stations = npr.Stations(location)
    data = stations.a['station']
    streamlist = []
    for d in data:
        s = str(d)
        if d.get('mp3') is not None:
            if d.get('name') is not None:
                #work around for crappy kodi only using HTTP
                __stationsList__.append(d['name'])
                if "playerservices.streamtheworld.com/pls" in d['mp3']:
                    f = urllib2.urlopen(d['mp3'])
                    myfile = f.read()
                    s = myfile.splitlines()
                    for i in range(len(s)):
                        url = s[i].decode()
                        name= d['name']
                        if "File" in url:
                            if ".com:443" in url:
                                urls = url.replace(":443", "")
                                __streamList__.append(regexurl(urls))
                            else:
                                __streamList__.append(regexurl(urls))
                else:
                        __streamList__.append(d['mp3'])

def buildMenu(pluginaddress, stationsList, F):
    for k in stationsList: 
        #combine the plugin URL router code and actual url in url encoded format
        u =  pluginaddress + quote(str(k))
        #display name of menu item
        liz = xbmcgui.ListItem(k)
        #build the menu 
        xbmcplugin.addDirectoryItem(__handle__,
                        url = u, listitem = liz,
                        isFolder = F)
    xbmcplugin.endOfDirectory(__handle__)

def buildPodcastMenu(pluginaddress, podcastList):
    for k in podcastList: 
        #combine the plugin URL router code and actual url in url encoded format
        u =  pluginaddress + quote(str(k[1]))
        #display name of menu item
        liz = xbmcgui.ListItem(k[0])
        #build the menu 
        xbmcplugin.addDirectoryItem(__handle__,
                        url = u, listitem = liz)
    xbmcplugin.endOfDirectory(__handle__)

def main():
    global __arg__
    dialog = xbmcgui.Dialog()
    xbmc.log("looking for argument 0 plugin name: "+__url__,level=xbmc.LOGNOTICE)
    xbmc.log("looking for argument 1 handle: "+str(__handle__),level=xbmc.LOGNOTICE)
    xbmc.log("looking for argument 2 program argument: "+__arg__,level=xbmc.LOGNOTICE)
    if "?stream" in __arg__:
        url = unquote(__arg__.split("?stream=",1)[1])
        xbmc.log("opening url: "+url,level=xbmc.LOGNOTICE)
        xbmc.Player().play(url)
        #xbmc.executebuiltin('ShowPicture("{0}")'.format(__addondir__+"\icon.png"))
    elif "?stations" in __arg__:
        getstations(__arg__.split("?stations=",1)[1])
        buildMenu(__url__+"?sid=",__stationsList__,True)
    elif "?pstations" in __arg__:
        getpodcasts(__arg__.split("?pstations=",1)[1])
        buildPodcastMenu(__url__+"?stream=",__podcastList__)
    elif "?sid" in __arg__:
        getstations(__arg__.split("?sid=",1)[1])
        buildMenu(__url__+"?stream=",__streamList__,False)
    elif "?mainmenu" in __arg__:
        if "Live%20Radio" in __arg__:
            buildMenu(__url__+"?stations=",_STATES,True)
        elif "Podcasts" in __arg__:
            buildMenu(__url__+"?pstations=",_SAVEDPODCASTS,True)
    else:
        try:
            data = ""
            configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npr.conf')
            if os.path.exists(configfile):
                with open(configfile, 'r') as file:
                    xbmc.log("looking for token...",level=xbmc.LOGNOTICE)
                    data = file.read().replace('\n', '')
            else:
                npr.auth()
            if 'token' in data:
                xbmc.log("token found...",level=xbmc.LOGNOTICE)
                try:
                    buildMenu(__url__+"?mainmenu=",_MAINMENU,True)
                except Exception, e:
                    xbmc.log(str(e),level=xbmc.LOGNOTICE)
                    dialog.ok("NPR One", "failed to build menu. ")
            else:
                dialog.ok("NPR One", "If this is your first time running this app please open the addon configuration and set id and secret under general")
                xbmc.log("starting auth",level=xbmc.LOGNOTICE)
                npr.auth()
                npr.login()
                dialog.ok("NPR One", "All Done now relaunch the addon.")
        except Exception, ex:
            xbmc.log(str(ex),level=xbmc.LOGNOTICE)
            dialog.ok("NPR One", "failed. "+str(ex))

main()
