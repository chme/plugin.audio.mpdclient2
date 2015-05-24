#
#  Copyright (c) chme
#
#  This file is part of the mpdclient kodi plugin
#
#  This plugin is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 3 of
#  the License, or (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#

import sys
import urlparse

import xbmcaddon

class Env:
    def __init__(self):
        self.__addon = xbmcaddon.Addon("plugin.audio.mpdclient2")
        self.__addon_handle = int(sys.argv[1])
        self.__base_url = sys.argv[0]
        self.__addon_args = urlparse.parse_qs(sys.argv[2][1:])
        print sys.argv
    
    def base_url(self):
        return self.__base_url
    
    def addon_handle(self):
        return self.__addon_handle
    
    def param_string(self, name, default=""):
        param = self.__addon_args.get(name, None)
        if param is None:
            return default
        return param[0]
    
    def param_list(self, name, default=[]):
        param = self.__addon_args.get(name, default)
        print param
        return param
    
    def localized(self, stringid):
        return self.__addon.getLocalizedString(stringid)
    
    def setting(self, name):
        return self.__addon.getSetting(name)

