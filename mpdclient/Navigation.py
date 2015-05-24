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

import urllib

import xbmcgui
import xbmcplugin

from lib import mpd
from mpdclient.Env import Env
from mpdclient.Language import Language


class NavUrl:
    __KEY_NAVID = "navid"
    __KEY_PARAM = "param"
    __SEPARATOR = "###"

    @staticmethod
    def build_url(env, navid, params=[]):
        return env.base_url() + "?" + urllib.urlencode({NavUrl.__KEY_NAVID: navid}) + "&" + urllib.urlencode({NavUrl.__KEY_PARAM: NavUrl.__SEPARATOR.join(params)})

    @staticmethod
    def get_navid(env):
        return env.param_string(NavUrl.__KEY_NAVID)

    @staticmethod
    def get_params(env):
        return env.param_string(NavUrl.__KEY_PARAM).split(NavUrl.__SEPARATOR)


class Nav:
    NAV_FILE = "file"
    NAV_PL = "playlist"
    NAV_LIST = "list"
    NAV_FIND = "find"
    NAV_QUEUE = "queue"
    NAV_PLAYLISTS = "playlists"

    ACTION_ADD = "add"
    ACTION_LOAD = "load"
    ACTION_FINDADD = "findadd"
    ACTION_REMOVE = "remove"
    ACTION_CLEAR = "clear"
    ACTION_PLAY = "play"
    ACTION_PAUSE = "pause"
    ACTION_PREV = "prev"
    ACTION_NEXT = "next"
    ACTION_STOP = "stop"
    ACTION_OUTPUTS = "outputs"

    def __init__(self):
        self.__env = Env()
        self.__mpc = mpd.MPDClient()
        return

    def handle(self):
        self.__connect_mpd()

        params = NavUrl.get_params(self.__env)
        navid = NavUrl.get_navid(self.__env)
        if navid == Nav.NAV_FILE:
            xbmcplugin.setContent(self.__env.addon_handle(), "files")
            xbmcplugin.addSortMethod(self.__env.addon_handle(), xbmcplugin.SORT_METHOD_TITLE)
            self.__nav_file(self.__env, self.__mpc, params)
        elif navid == Nav.NAV_PL:
            xbmcplugin.setContent(self.__env.addon_handle(), "songs")
            xbmcplugin.addSortMethod(self.__env.addon_handle(), xbmcplugin.SORT_METHOD_NONE)
            self.__nav_pl(self.__env, self.__mpc, params)
        elif navid == Nav.NAV_PLAYLISTS:
            xbmcplugin.setContent(self.__env.addon_handle(), "files")
            xbmcplugin.addSortMethod(self.__env.addon_handle(), xbmcplugin.SORT_METHOD_TRACKNUM)
            self.__nav_playlists(self.__env, self.__mpc, params)
        elif navid == Nav.NAV_LIST:
            if "albumartist" == params[0]:
                xbmcplugin.setContent(self.__env.addon_handle(), "artists")
                xbmcplugin.addSortMethod(self.__env.addon_handle(), xbmcplugin.SORT_METHOD_ARTIST)
            elif "album" == params[0]:
                xbmcplugin.setContent(self.__env.addon_handle(), "albums")
                xbmcplugin.addSortMethod(self.__env.addon_handle(), xbmcplugin.SORT_METHOD_ALBUM)
            elif "genre" == params[0]:
                xbmcplugin.setContent(self.__env.addon_handle(), "files")
                xbmcplugin.addSortMethod(self.__env.addon_handle(), xbmcplugin.SORT_METHOD_GENRE)
            self.__nav_list(self.__env, self.__mpc, params)
        elif navid == Nav.NAV_FIND:
            xbmcplugin.setContent(self.__env.addon_handle(), "songs")
            #xbmcplugin.addSortMethod(self.__env.addon_handle(), xbmcplugin.SORT_METHOD_TITLE)
            xbmcplugin.addSortMethod(self.__env.addon_handle(), xbmcplugin.SORT_METHOD_TRACKNUM)
            self.__nav_find(self.__env, self.__mpc, params)
        elif navid == Nav.NAV_QUEUE:
            xbmcplugin.setContent(self.__env.addon_handle(), "songs")
            xbmcplugin.addSortMethod(self.__env.addon_handle(), xbmcplugin.SORT_METHOD_NONE)
            self.__nav_queue(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_ADD:
            self.__action_add(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_LOAD:
            self.__action_load(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_FINDADD:
            self.__action_findadd(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_REMOVE:
            self.__action_remove(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_CLEAR:
            self.__action_clear(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_PLAY:
            self.__action_play(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_PAUSE:
            self.__action_pause(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_PREV:
            self.__action_prev(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_NEXT:
            self.__action_next(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_STOP:
            self.__action_stop(self.__env, self.__mpc, params)
        elif navid == Nav.ACTION_OUTPUTS:
            self.__action_outputs(self.__env, self.__mpc, params)
        else:
            xbmcplugin.setContent(self.__env.addon_handle(), "files")
            self.__nav_root(self.__env, self.__mpc, params)

        self.__deinit()

    def __connect_mpd(self):
        self.__mpc.connect(
            self.__env.setting("host"), self.__env.setting("port"))
        return

    def __deinit(self):
        self.__mpc.disconnect()
        xbmcplugin.endOfDirectory(self.__env.addon_handle())

    def __nav_root(self, env, mpc, params=[]):
        item = ItemRoot()
        item.add(env, Nav.NAV_QUEUE, env.localized(Language.QUEUE), [], "DefaultMusicPlaylists.png")
        item.add(env, Nav.NAV_FILE, env.localized(Language.FILES), ["/"], "")
        item.add(env, Nav.NAV_LIST, env.localized(
            Language.ARTISTS), ["albumartist"], "DefaultMusicArtists.png")
        item.add(env, Nav.NAV_LIST, env.localized(
            Language.ALBUMS), ["album"], "DefaultMusicAlbums.png")
        item.add(env, Nav.NAV_LIST, env.localized(
            Language.GENRE), ["genre"], "DefaultMusicGenres.png")
        item.add(env, Nav.NAV_PLAYLISTS, env.localized(Language.PLAYLISTS), [], "DefaultMusicPlaylists.png")
        return

    def __nav_file(self, env, mpc, params=[]):
        path = params[0]
        item = ItemFile()
        for metadata in mpc.lsinfo(path):
            item.add(env, metadata)
        return

    def __nav_playlists(self, env, mpc, params=[]):
        item = ItemFile()
        for metadata in mpc.listplaylists():
            item.add(env, metadata)
        return

    def __nav_pl(self, env, mpc, params=[]):
        path = params[0]
        item = ItemFile()
        for metadata in mpc.listplaylistinfo(path):
            item.add(env, metadata)
        return

    def __nav_list(self, env, mpc, params=[]):
        item = ItemTag()
        for tag in mpc.list(*params):
            item.add(env, mpc, params[0], tag, params[1:])
        return

    def __nav_find(self, env, mpc, params=[]):
        item = ItemFile()
        for metadata in mpc.find(*params):
            item.add(env, metadata)
        return

    def __nav_queue(self, env, mpc, params=[]):
        item = ItemFile()
        for metadata in mpc.playlistinfo():
            item.add(env, metadata)
        return

    def __action_add(self, env, mpc, params=[]):
        mpc.add(params[0])
        xbmcgui.Dialog().notification(
            "MPD", self.__env.localized(Language.SONGS_ADDED), xbmcgui.NOTIFICATION_INFO, 5000)
        # mpc.play()
        return

    def __action_load(self, env, mpc, params=[]):
        mpc.load(params[0])
        xbmcgui.Dialog().notification(
            "MPD", self.__env.localized(Language.SONGS_ADDED), xbmcgui.NOTIFICATION_INFO, 5000)
        # mpc.play()
        return

    def __action_findadd(self, env, mpc, params=[]):
        mpc.findadd(*params)
        xbmcgui.Dialog().notification(
            "MPD", self.__env.localized(Language.SONGS_ADDED), xbmcgui.NOTIFICATION_INFO, 5000)
        # mpc.play()
        return

    def __action_play(self, env, mpc, params=[]):
        if params[0] >=0:
            mpc.play(int(params[0]))
        else:
            mpc.play()
        return

    def __action_pause(self, env, mpc, params=[]):
        mpc.pause()
        return

    def __action_stop(self, env, mpc, params=[]):
        mpc.stop()
        return

    def __action_prev(self, env, mpc, params=[]):
        mpc.previous()
        return

    def __action_next(self, env, mpc, params=[]):
        mpc.next()
        return

    def __action_remove(self, env, mpc, params=[]):
        mpc.delete(params[0])
        return

    def __action_clear(self, env, mpc, params=[]):
        mpc.clear()
        return

    def __action_outputs(self, env, mpc, params=[]):
        outputs = []
        outputids = []
        for output in mpc.outputs():
            if output["outputenabled"] == "1":
                enabled = " [enabled]"
            else:
                enabled = " [disabled]"
            outputs.append(output["outputname"] + enabled)
            outputids.append(output["outputid"])

        ret = xbmcgui.Dialog().select("Toggle outputs", outputs, False)
        if ret >= 0:
            mpc.toggleoutput(outputids[ret])
            # xbmcgui.Dialog().notification("MPD",
            #                              self.__env.localized(Language.SONGS_ADDED),
            #                              xbmcgui.NOTIFICATION_INFO,
            #                              2000)
        return


class Item:

    def global_contextmenu(self, env, pospl=-1):
        return [(env.localized(Language.PLAY), "RunPlugin(" + NavUrl.build_url(env, Nav.ACTION_PLAY, [str(pospl)]) + ")"),
                (env.localized(Language.PAUSE),
                 "RunPlugin(" + NavUrl.build_url(env, Nav.ACTION_PAUSE) + ")"),
                (env.localized(Language.STOP),
                 "RunPlugin(" + NavUrl.build_url(env, Nav.ACTION_STOP) + ")"),
                (env.localized(Language.PREVIOUS),
                 "RunPlugin(" + NavUrl.build_url(env, Nav.ACTION_PREV) + ")"),
                (env.localized(Language.NEXT),
                 "RunPlugin(" + NavUrl.build_url(env, Nav.ACTION_NEXT) + ")"),
                (env.localized(Language.CLEAR),
                 "RunPlugin(" + NavUrl.build_url(env, Nav.ACTION_CLEAR) + ")"),
                (env.localized(Language.OUTPUTS), "RunPlugin(" + NavUrl.build_url(env, Nav.ACTION_OUTPUTS) + ")"), ]


class ItemRoot(Item):

    def add(self, env, navid, name, param, icon="DefaultFolder.png"):
        li = xbmcgui.ListItem(name, iconImage=icon)
        li.addContextMenuItems(self.global_contextmenu(env), True)
        url = NavUrl.build_url(env, navid, param)
        xbmcplugin.addDirectoryItem(
            handle=env.addon_handle(),
            url=url,
            listitem=li,
            isFolder=True)
        return


class ItemTag(Item):

    def add(self, env, mpc, tag, val, what):
        #t = [tag, val] + what + ["0:1"]
        #print t
        #mpc.find(*t)
        if "albumartist" == tag:
            self.__add_artist(env, val, what)
        elif "album" == tag:
            self.__add_album(env, val, what)
        elif "genre" == tag:
            self.__add_genre(env, val, what)
        return

    def __add_artist(self, env, artist, what):
        li = xbmcgui.ListItem(artist, iconImage="DefaultMusicArtists.png")
        li.setInfo("music", {#"genre": metadata.get("genre", env.localized(Language.UNKNOWN)),
                             #"year": metadata.get("date", None),
                             #"title": metadata.get("title", ""),
                             #"album": metadata.get("album", env.localized(Language.UNKNOWN)),
                             "artist": artist,
                             #"duration": metadata.get("time", 0),
                             #"tracknumber": metadata.get("track", None),
                             # "rating": "0", # TODO
                             # "playcount": 0, # TODO
                             # "lastplayed": "", # TODO
                             # "lyrics": "", # TODO
                             }
                   )
        li.addContextMenuItems(
            [(env.localized(Language.ADD), "RunPlugin(" + NavUrl.build_url(env,
                                                                           Nav.ACTION_FINDADD, ["albumartist", artist] + what) + ")")]
            + self.global_contextmenu(env), True)
        url = NavUrl.build_url(
            env, Nav.NAV_LIST, ["album", "albumartist", artist] + what)
        xbmcplugin.addDirectoryItem(
            handle=env.addon_handle(),
            url=url,
            listitem=li,
            isFolder=True)
        return

    def __add_album(self, env, album, what):
        li = xbmcgui.ListItem(album, iconImage="DefaultMusicAlbums.png")
        li.setInfo("music", {#"genre": metadata.get("genre", env.localized(Language.UNKNOWN)),
                             #"year": metadata.get("date", None),
                             #"title": metadata.get("title", ""),
                             "album": album,
                             #"artist": artist,
                             #"duration": metadata.get("time", 0),
                             #"tracknumber": metadata.get("track", None),
                             # "rating": "0", # TODO
                             # "playcount": 0, # TODO
                             # "lastplayed": "", # TODO
                             # "lyrics": "", # TODO
                             }
                   )
        li.addContextMenuItems(
            [(env.localized(Language.ADD), "RunPlugin(" + NavUrl.build_url(env,
                                                                           Nav.ACTION_FINDADD, ["album", album] + what) + ")")]
            + self.global_contextmenu(env), True)
        url = NavUrl.build_url(env, Nav.NAV_FIND, ["album", album] + what)
        xbmcplugin.addDirectoryItem(
            handle=env.addon_handle(),
            url=url,
            listitem=li,
            isFolder=True)
        return

    def __add_genre(self, env, genre, what):
        li = xbmcgui.ListItem(genre, iconImage="DefaultMusicGenres.png")
        li.setInfo("music", {"genre": genre,
                             #"year": metadata.get("date", None),
                             #"title": metadata.get("title", ""),
                             #"album": album,
                             #"artist": artist,
                             #"duration": metadata.get("time", 0),
                             #"tracknumber": metadata.get("track", None),
                             # "rating": "0", # TODO
                             # "playcount": 0, # TODO
                             # "lastplayed": "", # TODO
                             # "lyrics": "", # TODO
                             }
                   )
        li.addContextMenuItems(
            [(env.localized(Language.ADD), "RunPlugin(" + NavUrl.build_url(env,
                                                                           Nav.ACTION_FINDADD, ["genre", genre] + what) + ")")]
            + self.global_contextmenu(env), True)
        url = NavUrl.build_url(
            env, Nav.NAV_LIST, ["albumartist", "genre", genre] + what)
        xbmcplugin.addDirectoryItem(
            handle=env.addon_handle(),
            url=url,
            listitem=li,
            isFolder=True)
        return


class ItemFile(Item):

    def add(self, env, metadata):
        if "directory" in metadata:
            self.__add_dir(env, metadata)
        elif "playlist" in metadata:
            self.__add_playlist(env, metadata)
        elif "file" in metadata:
            self.__add_song(env, metadata)
        return

    def __add_dir(self, env, metadata):
        path = metadata["directory"]
        name = path[path.rfind("/") + 1:]
        li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png")
        li.addContextMenuItems(
            [(env.localized(Language.ADD),
              "RunPlugin(" + NavUrl.build_url(env, Nav.ACTION_ADD, [path]) + ")")]
            + self.global_contextmenu(env), True)
        url = NavUrl.build_url(env, Nav.NAV_FILE, [path])
        xbmcplugin.addDirectoryItem(
            handle=env.addon_handle(),
            url=url,
            listitem=li,
            isFolder=True)
        return

    def __add_playlist(self, env, metadata):
        path = metadata["playlist"]
        name = path[path.rfind("/") + 1:]
        li = xbmcgui.ListItem(name, iconImage="DefaultMusicPlaylists.png")
        li.addContextMenuItems(
            [(env.localized(Language.ADD), "RunPlugin(" +
              NavUrl.build_url(env, Nav.ACTION_LOAD, [path]) + ")")]
            + self.global_contextmenu(env), True)
        url = NavUrl.build_url(env, Nav.NAV_PL, [path])
        xbmcplugin.addDirectoryItem(
            handle=env.addon_handle(),
            url=url,
            listitem=li,
            isFolder=True)
        return

    def __add_song(self, env, metadata):
        path = metadata["file"]
        name = path[path.rfind("/") + 1:]
        
        # If pos is given, this lists the current playlist and tracknumber
        # is the position in the playlist instead of the album.
        is_queue = "pos" in metadata
        if is_queue:
            pospl = int(metadata.get("pos", "-1"))
            tracknumber = int(metadata.get("pos", "-1")) + 1
        else:
            pospl = -1
            tracknumber = metadata.get("track", None)

        li = xbmcgui.ListItem(name, iconImage="DefaultMusicSongs.png")
        li.setInfo("music", {"genre": metadata.get("genre", env.localized(Language.UNKNOWN)),
                             "year": metadata.get("date", None),
                             "title": metadata.get("title", ""),
                             "album": metadata.get("album", env.localized(Language.UNKNOWN)),
                             "artist": metadata.get("artist", env.localized(Language.UNKNOWN)),
                             "duration": metadata.get("time", 0),
                             "tracknumber": tracknumber,
                             # "rating": "0", # TODO
                             # "playcount": 0, # TODO
                             # "lastplayed": "", # TODO
                             # "lyrics": "", # TODO
                             }
                   )
        if is_queue:
            li.addContextMenuItems(
                [(env.localized(Language.REMOVE), "RunPlugin(" +
                  NavUrl.build_url(env, Nav.ACTION_REMOVE, [metadata.get("pos", "-1")]) + ")"), ]
                + self.global_contextmenu(env, pospl), True)
            url = NavUrl.build_url(env, Nav.ACTION_PLAY, [str(pospl)])
        else:
            li.addContextMenuItems(
                [(env.localized(Language.ADD), "RunPlugin(" +
                  NavUrl.build_url(env, Nav.ACTION_ADD, [path]) + ")"), ]
                + self.global_contextmenu(env), True)
            url = NavUrl.build_url(env, Nav.ACTION_ADD, [path])
        xbmcplugin.addDirectoryItem(
            handle=env.addon_handle(), url=url, listitem=li)
        return
