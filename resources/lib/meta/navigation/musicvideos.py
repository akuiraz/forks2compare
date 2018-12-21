import xbmcgui
from meta import plugin, LANG
from meta.gui import dialogs
from meta.utils.rpc import RPC
from meta.utils.text import to_utf8
from meta.play.players import ADDON_DEFAULT, ADDON_SELECTOR
from meta.play.musicvideos import play_musicvideo
from meta.play.music import play_music
from meta.navigation.base import get_icon_path, get_background_path, get_genre_icon, get_genres, get_tv_genres, caller_name, caller_args
from meta.library.musicvideos import setup_library, add_musicvideos_to_library
from meta.library.tools import scan_library
from language import get_string as _
from settings import SETTING_MUSICVIDEOS_LIBRARY_FOLDER, SETTING_FORCE_VIEW, SETTING_MUSICVIDEOS_VIEW
from xbmcswift2 import xbmc, xbmcplugin, xbmcvfs
from lastfm import lastfm
from audiodb import audiodb

if RPC.settings.get_setting_value(setting="filelists.ignorethewhensorting") == {u'value': True}:
    SORT = [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE]
else:
    SORT = [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL]

FORCE = plugin.get_setting(SETTING_FORCE_VIEW, bool)
VIEW  = plugin.get_setting(SETTING_MUSICVIDEOS_VIEW, int)

@plugin.route('/musicvideos')
def musicvideos():
    items = [
        {
            'label': "{0}: {1}".format(_("Search"), _("Music videos")),
            'path': plugin.url_for("musicvideos_search"),
            'icon': get_icon_path("search"),
        },
        {
            'label': "{0} {1}".format(_("Top 100"), _("Artists")),
            'path': plugin.url_for("musicvideos_top_artists"),
            'icon': get_icon_path("top_rated"),
        },
        {
            'label': "{0} {1}".format(_("Top 100"), _("Tracks")),
            'path': plugin.url_for("musicvideos_top_tracks"),
            'icon': get_icon_path("trending"),
        },
        {
            'label': "{0} {1} ({2})".format(_("Top 100"), _("Artists"), "NL"),
            'path': plugin.url_for("musicvideos_top_artists_by_country", country='netherlands'),
            'icon': get_icon_path("top_nl"),
        },
        {
            'label': "{0} {1} ({2})".format(_("Top 100"), _("Artists"), "UK"),
            'path': plugin.url_for("musicvideos_top_artists_by_country", country='united kingdom'),
            'icon': get_icon_path("top_uk"),
        },
        {
            'label': "{0} {1} ({2})".format(_("Top 100"), _("Artists"), "US"),
            'path': plugin.url_for("musicvideos_top_artists_by_country", country='united states'),
            'icon': get_icon_path("top_us"),
        },
        {
            'label': "{0} {1} ({2})".format(_("Top 100"), _("Artists"), "CA"),
            'path': plugin.url_for("musicvideos_top_artists_by_country", country='canada'),
            'icon': get_icon_path("top_ca"),
        },
        {
            'label': "{0} {1} ({2})".format(_("Top 100"), _("Artists"), "AU"),
            'path': plugin.url_for("musicvideos_top_artists_by_country", country='australia'),
            'icon': get_icon_path("top_au"),
        },
        {
            'label': "{0} {1} ({2})".format(_("Top 100"), _("Tracks"), "NL"),
            'path': plugin.url_for("musicvideos_top_tracks_by_country", country='netherlands'),
            'icon': get_icon_path("trending_nl"),
        },
        {
            'label': "{0} {1} ({2})".format(_("Top 100"), _("Tracks"), "UK"),
            'path': plugin.url_for("musicvideos_top_tracks_by_country", country='united kingdom'),
            'icon': get_icon_path("trending_uk"),
        },
        {
            'label': "{0} {1} ({2})".format(_("Top 100"), _("Tracks"), "US"),
            'path': plugin.url_for("musicvideos_top_tracks_by_country", country='united states'),
            'icon': get_icon_path("trending_us"),
        },
        {
            'label': "{0} {1} ({2})".format(_("Top 100"), _("Tracks"), "CA"),
            'path': plugin.url_for("musicvideos_top_tracks_by_country", country='canada'),
            'icon': get_icon_path("trending_ca"),
        },
        {
            'label': "{0} {1} ({2})".format(_("Top 100"), _("Tracks"), "AU"),
            'path': plugin.url_for("musicvideos_top_tracks_by_country", country='australia'),
            'icon': get_icon_path("trending_au"),
        }
    ]
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items

@plugin.route('/musicvideos/search')
def musicvideos_search():
    term = plugin.keyboard(heading=_("Enter search string"))
    if term != None and term != "": return musicvideos_search_term(term, 1)
    else: return

@plugin.route('/musicvideos/search/edit/<term>')
def musicvideos_search_edit(term):
    term = plugin.keyboard(default=term, heading=_("Enter search string"))
    if term != None and term != "": return musicvideos_search_term(term, 1)
    else: return

@plugin.route('/musicvideos/search/<term>/<page>')
def musicvideos_search_term(term, page):
    items = [
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("Albums"), "LastFM"),
            'path': plugin.url_for("musicvideos_search_album_term", term=term),
            'icon': get_icon_path("music"),
            'thumbnail': get_icon_path("music"),
        },
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("Artists"), "LastFM"),
            'path': plugin.url_for("musicvideos_search_artist_term", term=term),
            'icon': get_icon_path("music"),
            'thumbnail': get_icon_path("music"),
        },
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("Tracks"), "LastFM"),
            'path': plugin.url_for("musicvideos_search_track_term", term=term, page='1'),
            'icon': get_icon_path("music"),
            'thumbnail': get_icon_path("music"),
        },
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("Channels"), "Live addons"),
            'path': plugin.url_for("live_search_term", term=term),
            'icon': get_icon_path("live"),
            'thumbnail': get_icon_path("live"),
        },
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("Playlists"), "Trakt"),
            'path': plugin.url_for("lists_search_for_lists_term", term=term, page='1'),
            'icon': get_icon_path("lists"),
            'thumbnail': get_icon_path("lists"),
        },
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("Movies"), "TMDb"),
            'path': plugin.url_for("tmdb_movies_search_term", term=term, page='1'),
            'icon': get_icon_path("movies"),
            'thumbnail': get_icon_path("movies"),
        },
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("Movies"), "Trakt"),
            'path': plugin.url_for("trakt_movies_search_term", term=term, page='1'),
            'icon': get_icon_path("movies"),
            'thumbnail': get_icon_path("movies"),
        },
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("TV shows"), "TMDb"),
            'path': plugin.url_for("tmdb_tv_search_term", term=term, page='1'),
            'icon': get_icon_path("tv"),
            'thumbnail': get_icon_path("tv"),
        },
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("TV shows"), "Trakt"),
            'path': plugin.url_for("trakt_tv_search_term", term=term, page='1'),
            'icon': get_icon_path("tv"),
            'thumbnail': get_icon_path("tv"),
        },
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("TV shows"), "TVDb"),
            'path': plugin.url_for("tv_search_term", term=term, page='1'),
            'icon': get_icon_path("search"),
            'thumbnail': get_icon_path("search"),
        },
        {
            'label': "{0}: '{1}' - {2} ({3})".format(_("Search"), term, _("Music"), plugin.addon.getAddonInfo('name')),
            'path': plugin.url_for("musicvideos_search_term", term=term, page='1'),
            'icon': get_icon_path("search"),
            'thumbnail': get_icon_path("search"),
        },
        {
            'label': "{0} {1}".format(_("Edit"), _("Search string").lower()),
            'path': plugin.url_for("musicvideos_search_edit", term=term),
            'icon': get_icon_path("search"),
            'thumbnail': get_icon_path("search"),
        }
    ]
    for item in items:
        item['properties'] = {'fanart_image' : get_background_path()}
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items


@plugin.route('/musicvideos/search/artist')
def musicvideos_search_artist():
    term = plugin.keyboard(heading=_("Enter search string"))
    return musicvideos_search_artist_term(term, 1)

@plugin.route('/musicvideos/search/album')
def musicvideos_search_album():
    term = plugin.keyboard(heading=_("Enter search string"))
    return musicvideos_search_album_term(term)

@plugin.route('/musicvideos/search/track')
def musicvideos_search_track():
    term = plugin.keyboard(heading=_("Enter search string"))
    return musicvideos_search_track_term(term, 1)

@plugin.route('/musicvideos/top_artists/<page>', options={'page': "1"})
def musicvideos_top_artists(page):
    results = lastfm.get_top_artists(page)
    artists = results["artists"]["artist"]
    items = []
    for artist in artists:
        large_image = artist["image"][-1]["#text"]
        name = to_utf8(artist["name"])
        context_menu = [
            (
                _("Scan item to library"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_add_artist_to_library", artist_name=name))
            )
        ]
        item = {
            'label': name,
            'path': plugin.url_for("musicvideos_artist_albums", artist_name=name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': name,
            },
            'info_type': 'music',
            'context_menu': context_menu
        }
        items.append(item)
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items



@plugin.route('/musicvideos/top_tracks/<page>', options={'page': "1"})
def musicvideos_top_tracks(page):
    results = lastfm.get_top_tracks(page)
    tracks = results["tracks"]["track"]
    items = []
    for track in tracks:
        large_image = track["image"][-1]["#text"]
        track_name = to_utf8(track["name"])
        artist_name = to_utf8(track["artist"]["name"])
        path = plugin.url_for("musicvideos_play_video", artist_name=artist_name, track_name=track_name)
        icon = "DefaultMusicVideo.png"
        info_type = "musicvideos"
        context_menu = [
            (
                "{0} {1} {2}...".format(_("Select"), _("Video").lower(), _("Stream").lower()),
                "PlayMedia({0})".format(plugin.url_for("musicvideos_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            ),
            (
                _("Scan item to library"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_add_to_library", artist_name=artist_name,
                                                       track_name=track_name))
            ),
            (
                _("Music"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            )
        ]
        item = {
            'label': "{0} - {1}".format(artist_name, track_name),
            'path': path,
            'thumbnail': large_image,
            'icon': icon,
            'poster': large_image,
            'info': {
                'artist': artist_name,
            },
            'info_type': info_type,
            'context_menu': context_menu
        }
        items.append(item)
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items


@plugin.route('/musicvideos/top_artists_by_country/<country>/<page>', options={'page': "1"})
def musicvideos_top_artists_by_country(country, page):
    results = lastfm.get_top_artists_by_country(country, page)
    artists = results["topartists"]["artist"]
    items = []
    for artist in artists:
        large_image = artist["image"][-1]["#text"]
        name = to_utf8(artist["name"])
        context_menu = [
            (
                _("Scan item to library"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_add_artist_to_library", artist_name=name))
            )
        ]
        item = {
            'label': name,
            'path': plugin.url_for("musicvideos_artist_albums", artist_name=name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': name,
            },
            'info_type': 'music',
            'context_menu': context_menu
        }
        items.append(item)
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items


@plugin.route('/musicvideos/top_tracks_by_country/<country>/<page>', options={'page': "1"})
def musicvideos_top_tracks_by_country(country, page):
    results = lastfm.get_top_tracks_by_country(country, page)
    tracks = results["tracks"]["track"]
    items = []
    for track in tracks:
        large_image = track["image"][-1]["#text"]
        track_name = to_utf8(track["name"])
        artist_name = to_utf8(track["artist"]["name"])
        context_menu = [
            (
                "{0} {1}...".format(_("Select"), _("Stream").lower()),
                "PlayMedia({0})".format(plugin.url_for("musicvideos_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            ),
            (
                _("Scan item to library"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_add_to_library", artist_name=artist_name,
                                                       track_name=track_name))
            )#,
#            (
#                _("Music video"),
#                "RunPlugin({0})".format(plugin.url_for("musicvideos_play_video", artist_name=artist_name,
#                                                       track_name=track_name, mode='context'))
#            )
        ]
        item = {
            'label': "{0} - {1}".format(artist_name, track_name),
            'path': plugin.url_for("musicvideos_play_video", artist_name=artist_name, track_name=track_name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': artist_name,
            },
            'info_type': 'music',
            'context_menu': context_menu
        }

        items.append(item)
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items


@plugin.route('/musicvideos/search_artist_term/<term>/')
def musicvideos_search_artist_term(term):
    search_results = audiodb.search("search", term)
    artists = search_results["artists"]
    total_results = len(artists)
    items = []
    for artist in artists:
        image = artist["strArtistThumb"]
        logo = artist["strArtistLogo"]
        name = to_utf8(artist["strArtist"])
        namelist = [to_utf8(artist["strArtist"])]
        try:
            rplot = artist["strBiography{}".format(LANG.upper())]
        except:
            rplot = artist["strBiographyEN"]
        if rplot is None:
            rplot = artist["strBiographyEN"]
        plot = rplot
        genres = []
        if "/" in artist["strStyle"]:
            to_add = artist["strStyle"].split("/")
            for a in to_add:
                genres.append(a)
        else:
            genres.append(artist["strStyle"])
        if artist["strGenre"] not in genres:
            genres.append(artist["strGenre"])
        genre = " / ".join(genres)
        context_menu = [
            (
                _("Scan item to library"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_add_artist_to_library", artist_name=name))
            )
        ]
        item = {
            'label': name,
            'path': plugin.url_for("musicvideos_artist_albums", artist_name=name),
            'thumbnail': image,
            'icon': image,
            'banner': logo,
            'poster': image,
            'info': {
                'artist': namelist,
                'cast': namelist,
                'year': artist["intFormedYear"],
                'genre': genre,
                'plot': plot,
            },
            'info_type': 'video',
            'context_menu': context_menu
        }

        items.append(item)
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items

@plugin.route('/musicvideos/search_album_term/<term>')
def musicvideos_search_album_term(term):
    search_results = audiodb.search("searchalbum", "", term)
    xbmc.log("{}".format(search_results), xbmc.LOGNOTICE)
    albums = search_results["album"]
    total_results = len(albums)
    items = []
    for album in albums:
        artist = to_utf8(album["strArtist"])
        image = album["strAlbumThumb"]
        logo = album["strAlbumCDart"]
        name = to_utf8(album["strAlbum"])
        namelist = [to_utf8(album["strAlbum"])]
        try:
            rplot = album["strDescription{}".format(LANG.upper())]
        except:
            rplot = album["strDescriptionEN"]
        if rplot is None:
            try:
                rplot = album["strDescriptionEN"]
            except:
                rplot = ""
        plot = rplot
        genres = []
        if "/" in album["strStyle"]:
            to_add = album["strStyle"].split("/")
            for a in to_add:
                genres.append(a)
        else:
            genres.append(album["strStyle"])
        if album["strGenre"] not in genres:
            genres.append(album["strGenre"])
        genre = " / ".join(genres)
        context_menu = [
            (
                _("Scan item to library"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_add_album_to_library", album_name=name, artist_name=artist))
            )
        ]
        item = {
            'label': "{0} - {1}".format(name, artist),
            'path': plugin.url_for("musicvideos_artist_album_tracks", artist_name=artist, album_name=name),
            'thumbnail': image,
            'icon': image,
            'banner': logo,
            'poster': image,
            'info': {
                'artist': namelist,
                'cast': namelist,
                'year': album["intYearReleased"],
                'genre': genre,
                'plot': plot,
            },
            'info_type': 'video',
            'context_menu': context_menu
        }

        items.append(item)
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items


@plugin.route('/musicvideos/search_track_term/<term>/<page>')
def musicvideos_search_track_term(term, page):
    search_results = lastfm.search_track(term, page)
    tracks = search_results["trackmatches"]["track"]
    items_per_page = search_results["opensearch:itemsPerPage"]
    start_index = search_results["opensearch:startIndex"]
    total_results = search_results["opensearch:totalResults"]
    items = []
    for track in tracks:
        large_image = track["image"][-1]["#text"]
        track_name = to_utf8(track["name"])
        artist_name = to_utf8(track["artist"])
        context_menu = [
            (
                "{0} {1} {2}...".format(_("Select"), _("Audio").lower(), _("Stream").lower()),
                "PlayMedia({0})".format(plugin.url_for("musicvideos_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            ),
            (
                _("Scan item to library"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_add_to_library", artist_name=artist_name,
                                                       track_name=track_name))
            ),
            (
                "{0} {1} {2}...".format(_("Select"), _("Video").lower(), _("Stream").lower()),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            )
        ]
        item = {
            'label': "{0} - {1}".format(artist_name, track_name),
            'path': plugin.url_for("musicvideos_play_video", artist_name=artist_name, track_name=track_name),
            'thumbnail': large_image,
            'icon': "DefaultMusic.png",
            'poster': large_image,
            'info': {
                'artist': artist_name,
            },
            'info_type': 'music',
            'context_menu': context_menu
        }

        items.append(item)
    if start_index + items_per_page < total_results:
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for("musicvideos_search_track_term", term=term, page=int(page) + 1)
        })
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items


@plugin.route('/musicvideos/artist/<name>')
def musicvideos_artist(name):
    name = to_utf8(name)
    items = [
        {
            'label': _("Tracks"),
            'path': plugin.url_for("musicvideos_artist_tracks", artist_name=name),
            'icon': get_icon_path("music")
        },
        {
            'label': _("Albums"),
            'path': plugin.url_for("musicvideos_artist_albums", artist_name=name),
            'icon': get_icon_path("music")
        },
    ]
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items


@plugin.route('/musicvideos/artist/<artist_name>/tracks/<page>', options={'page': "1"})
def musicvideos_artist_tracks(artist_name, page):
    artist_name = to_utf8(artist_name)
    results = lastfm.get_artist_top_tracks(artist_name, page)
    items = []
    for track in results["track"]:
        large_image = track["image"][-1]["#text"]
        track_name = to_utf8(track["name"])
        context_menu = [
            (
                _("Context player"),
                "PlayMedia({0})".format(plugin.url_for("musicvideos_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            ),
            (
                _("Scan item to library"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_add_to_library", artist_name=artist_name,
                                                       track_name=track_name))
            ),
            (
                _("Musicvideo"),
                "PlayMedia({0})".format(plugin.url_for("musicvideos_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='default'))
            )
        ]
        if plugin.get_setting(SETTING_PREFERRED_musicvideos_TYPE, unicode) == "audio":
            item = {
                'label': track_name,
                'path': plugin.url_for("musicvideos_play_video", artist_name=artist_name, track_name=track_name),
                'thumbnail': large_image,
                'icon': "DefaultMusic.png",
                'poster': large_image,
                'info_type': 'music',
                'context_menu': context_menu,
            }
        else:
            item = {
                'label': track_name,
                'path': plugin.url_for("musicvideos_play_video", artist_name=artist_name, track_name=track_name),
                'thumbnail': large_image,
                'icon': "DefaultMusicVideo.png",
                'poster': large_image,
                'info_type': 'music',
                'context_menu': context_menu,
            }
        items.append(item)
    if results["@attr"]["totalPages"] > page:
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for("musicvideos_artist_tracks", artist_name=artist_name, page=int(page) + 1)
        })
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items


@plugin.route('/musicvideos/artist/<artist_name>/albums/<page>', options={'page': "1"})
def musicvideos_artist_albums(artist_name, page):
    artist_name = to_utf8(artist_name)
    results = lastfm.get_artist_top_albums(artist_name, page)
    items = [
        {
            'label': _("All Tracks"),
            'path': plugin.url_for("musicvideos_artist_tracks", artist_name=artist_name),
            'icon': get_icon_path("music")
        }
    ]
    for album in results["album"]:
        album_name = to_utf8(album["name"])
        image = album['image'][-1]['#text']
        artist_album_name = to_utf8(album['artist']['name'])
        context_menu = [
            (
                _("Scan item to library"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_add_album_to_library", artist_name=artist_album_name,
                                                       album_name=album_name))
            )
        ]
        item = {
            'thumbnail': image,
            'label': "{0}".format(album_name),
            'info': {
                'title': album_name,
                'artist': [artist_album_name],
            },
            'info_type': 'music',
            'path': plugin.url_for("musicvideos_artist_album_tracks", artist_name=artist_name, album_name=album_name),
            'context_menu': context_menu
        }
        items.append(item)
    if results["@attr"]["totalPages"] > page:
        next_page = int(page) + 1
        items.append({
            'label': _("Next >>"),
            'icon': get_icon_path("item_next"),
            'path': plugin.url_for("musicvideos_artist_albums", artist_name=artist_name, page=next_page)
        })
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items


@plugin.route('/musicvideos/artist/<artist_name>/album/<album_name>/tracks')
def musicvideos_artist_album_tracks(artist_name, album_name):
    artist_name = to_utf8(artist_name)
    album_name = to_utf8(album_name)
    results = lastfm.get_album_info(artist_name, album_name)
    items = []
    for track in results["tracks"]["track"]:
        track_name = to_utf8(track["name"])
        track_number = track["@attr"]["rank"]
        image = results["image"][-1]["#text"]
        context_menu = [
            (
                "{0} {1} {2}...".format(_("Select"), _("Audio").lower(), _("Stream").lower()),
                "PlayMedia({0})".format(plugin.url_for("musicvideos_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='context'))
            ),
            (
                _("Scan item to library"),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_add_to_library", artist_name=artist_name,
                                                       track_name=track_name, album_name=album_name))
            ),
            (
                "{0} {1} {2}...".format(_("Select"), _("Video").lower(), _("Stream").lower()),
                "RunPlugin({0})".format(plugin.url_for("musicvideos_play_video", artist_name=artist_name,
                                                       track_name=track_name, mode='default'))
            )
        ]
        item = {
            'label': "{0}. {1}".format(track_number, track_name),
            'path': plugin.url_for("musicvideos_play_video", artist_name=artist_name, album_name=album_name, track_name=track_name),
            'thumbnail': image,
            'icon': "DefaultMusicVideo.png",
            'poster': image,
            'info_type': 'music',
            'context_menu': context_menu,
        }
        items.append(item)
    if FORCE == True: plugin.set_view_mode(VIEW); return items
    else: return items


@plugin.route('/musicvideos/play/<artist_name>/<track_name>/<album_name>/<mode>', options={'album_name': "None",
                                                                                     'mode': 'default'})
def musicvideos_play(artist_name, track_name, album_name, mode):
    items = [
        {
            'label': "{0} {1}".format(_("Play"), _("Audio").lower()),
            'path': plugin.url_for("musicvideos_play_video", artist_name=artist_name, track_name=track_name,
                                   album_name=album_name, mode=mode)
        },
        {
            'label': "{0} {1}".format(_("Play"), _("Video").lower()),
            'path': plugin.url_for("musicvideos_play_video", artist_name=artist_name, track_name=track_name,
                                   album_name=album_name, mode=mode)
        }
    ]
    musicvideos_play_video(artist_name, track_name, album_name, mode)

@plugin.route('/musicvideos/play_video/<artist_name>/<track_name>/<album_name>/<mode>', options={'album_name': "None",
                                                                                           'mode': 'default'})
def musicvideos_play_video(artist_name, track_name, album_name, mode):
    if album_name == "None":
        track_info = lastfm.get_track_info(artist_name, track_name)
        if track_info and "album" in track_info:
            album_name = track_info["album"]["title"]
    play_musicvideo(artist_name, track_name, album_name, mode)

@plugin.route('/musicvideos/add_to_library/<artist_name>/<track_name>/<album_name>', options={'album_name': "None"})
def musicvideos_add_to_library(artist_name, track_name, album_name):
    if album_name == "None":
        album_name = lastfm.get_track_info(artist_name, track_name)["album"]["title"]

    library_folder = setup_library(plugin.get_setting(SETTING_MUSICVIDEOS_LIBRARY_FOLDER, unicode))

    add_musicvideos_to_library(library_folder, artist_name, album_name, track_name)
    scan_library(type="video", path=plugin.get_setting(SETTING_MUSICVIDEOS_LIBRARY_FOLDER, unicode))

@plugin.route('/musicvideos/add_album_to_library/<artist_name>/<album_name>')
def musicvideos_add_album_to_library(artist_name, album_name):
    library_folder = setup_library(plugin.get_setting(SETTING_MUSICVIDEOS_LIBRARY_FOLDER, unicode))
    results = lastfm.get_album_info(artist_name, album_name)
    for track in results["tracks"]["track"]:
        track_name = to_utf8(track["name"])
        add_musicvideos_to_library(library_folder, artist_name, album_name, track_name)
    scan_library(type="video", path=plugin.get_setting(SETTING_MUSICVIDEOS_LIBRARY_FOLDER, unicode))

@plugin.route('/musicvideos/add_artist_to_library/<artist_name>')
def musicvideos_add_artist_to_library(artist_name):
    import math
    library_folder = setup_library(plugin.get_setting(SETTING_MUSICVIDEOS_LIBRARY_FOLDER, unicode))
    album_results = lastfm.get_artist_top_albums(artist_name)
    total_albums = len(album_results)
    index = 0
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('MetalliQ', _("{0} {1} {2}").format(_("Adding"), artist_name, _("to library")))
    for album in album_results["album"]:
        album_name = to_utf8(album["name"])
        percent_done = int(math.floor((float(index) / total_albums) * 100))
        pDialog.update(percent_done, _("{0} {1} - {2} {3}").format(_("Adding"), artist_name,
                                                                   album_name, _("to library")))
        track_results = lastfm.get_album_info(artist_name, album_name)
        for track in track_results["tracks"]["track"]:
            if pDialog.iscanceled():
                pDialog.update(0)
                return
            track_name = to_utf8(track["name"])
            add_musicvideos_to_library(library_folder, artist_name, album_name, track_name)
        index += 1
        pDialog.update(0)
    scan_library(type="video", path=plugin.get_setting(SETTING_MUSICVIDEOS_LIBRARY_FOLDER, unicode))