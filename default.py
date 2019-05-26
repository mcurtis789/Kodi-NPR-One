#
#  Copyright 2012 (stieg)
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
import csv, urllib2, urlparse, os, sys, re
import npr
from xml.etree.ElementTree import ElementTree

__XBMC_Revision__ = xbmc.getInfoLabel('System.BuildVersion')
__settings__      = xbmcaddon.Addon(id='plugin.audio.nprone')
__home__          = __settings__.getAddonInfo('path')
__language__      = __settings__.getLocalizedString
__version__       = __settings__.getAddonInfo('version')
__name__           = __settings__.getAddonInfo('name')
__addonname__     = "NPR One - National Public Radio"
__addonid__       = "plugin.audio.nprone"
__author__        = "Mike Curtis"

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
_stationsList = []
_streamList = []
_arg = sys.argv[2]

## {{{ http://code.activestate.com/recipes/577305/ (r1)
__STATES = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}
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

def getstations(locations):
    location = locations.replace('%20',' ')
    stations = npr.Stations(location)
    data = stations.a['station']
    streamlist = []
    for d in data:
        s = str(d)
        if d.get('mp3') is not None:
             if d.get('name') is not None:
                #work around for crappy kodi only using HTTP
                _stationsList.append(d['name'])
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
                                _streamList.append(regexurl(urls))
                            else:
                                _streamList.append(regexurl(urls))
                else:
                        _streamList.append(d['mp3'])

def main():
    if "stream" in sys.argv[2]:
        # Play it.%3a%2f%2f
        http= sys.argv[2].split("?stream=",1)[1].replace('%2f','/')
        httpc= http.replace('%3a',':')
        print ("Playing stream %s" % httpc)
        xbmc.Player().play(httpc)

    elif "sid" in sys.argv[2]:
        # Display all stations in the state
        print("Station %s selected" % sys.argv[2])
        getstations(sys.argv[2].split("?sid=",1)[1])
        for k in _streamList:
                u = _url + "?stream=" + str(k)
                liz = xbmcgui.ListItem(k)
                xbmcplugin.addDirectoryItem(_handle,
                                  url = u, listitem = liz,
                                  isFolder = True)
        xbmcplugin.endOfDirectory(_handle)

    elif "state" in sys.argv[2]:
        # Display all stations in the state
        print("State of %s selected" % sys.argv[2])
        getstations(sys.argv[2].split("?state=",1)[1])
        for k in _stationsList:
                u = _url + "?sid=" + str(k)
                liz = xbmcgui.ListItem(k)
                xbmcplugin.addDirectoryItem(_handle,
                                  url = u, listitem = liz,
                                  isFolder = True)
        xbmcplugin.endOfDirectory(_handle)

    else:
        dialog = xbmcgui.Dialog()
        try:
                data = ""
                configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npr.conf')
                with open(configfile, 'r') as file:
                        data = file.read().replace('\n', '')
                if 'token' in data:
                        # Set plugin category. It is displayed in some skins as the name
                        # of the current section.
                        xbmcplugin.setPluginCategory(_handle, 'NPR')
                        # Set plugin content. It allows Kodi to select appropriate views
                        # for this type of content.
                        xbmcplugin.setContent(_handle, 'Music')
                        for key, value in __STATES.items():
                                u = _url + "?state=" +value
                                liz = xbmcgui.ListItem(value)
                                xbmcplugin.addDirectoryItem(_handle,
                                          url = u, listitem = liz,
                                          isFolder = True)
                        xbmcplugin.endOfDirectory(_handle)
                else:
                        npr.auth()
                        npr.login()
                        dialog.ok("NPR One", "All Done now relaunch the addon.")
        except:
                npr.auth()
                npr.login()
                dialog.ok("NPR One", "All Done now relaunch the addon.")

# Enter here.
main()
