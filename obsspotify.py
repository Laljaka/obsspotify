import obspython as obs
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Spopify:
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.redirect_url = None
        self.username = None
        self.AUTH = None

        self.image_source_name = None
        self.name_source_name = None
        self.author_source_name = None

    def set_playing(self):
        results = self.AUTH.currently_playing()

        if results is None:
            settings = obs.obs_data_create()

            source = obs.obs_get_source_by_name(S.name_source_name)
            if source is not None:
                obs.obs_data_set_string(settings, "text", '')
                obs.obs_source_update(source, settings)
                obs.obs_source_release(source)

            source = obs.obs_get_source_by_name(S.author_source_name)
            if source is not None:
                obs.obs_data_set_string(settings, "text", '')
                obs.obs_source_update(source, settings)
                obs.obs_source_release(source)

            source = obs.obs_get_source_by_name(S.image_source_name)
            if source is not None:
                obs.obs_data_set_string(settings, "url", '')
                obs.obs_source_update(source, settings)
                obs.obs_source_release(source)

            obs.obs_data_release(settings)
        else:
            artists = ''
            for item in results['item']['album']['artists']:
                artists += item['name']

            settings = obs.obs_data_create()

            source = obs.obs_get_source_by_name(S.name_source_name)
            if source is not None:
                obs.obs_data_set_string(settings, "text", results['item']['name'])
                obs.obs_source_update(source, settings)
                obs.obs_source_release(source)

            source = obs.obs_get_source_by_name(S.author_source_name)
            if source is not None:
                obs.obs_data_set_string(settings, "text", artists)
                obs.obs_source_update(source, settings)
                obs.obs_source_release(source)

            source = obs.obs_get_source_by_name(S.image_source_name)
            if source is not None:
                obs.obs_data_set_string(settings, "url", results['item']['album']['images'][1]['url'])
                obs.obs_source_update(source, settings)
                obs.obs_source_release(source)

            obs.obs_data_release(settings)


S = Spopify()


def login(props, prop):
    if S.client_id is not None and S.client_secret is not None and S.redirect_url is not None and S.username is not None:
        try:
            S.AUTH = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=S.client_id, client_secret=S.client_secret, username=S.username, scope="user-read-playback-state", redirect_uri=S.redirect_url))
            print('OK')
        except Exception:
            print('ooops')


def restart(props, prop):
    obs.timer_remove(S.set_playing)
    if S.AUTH is not None:
        obs.timer_add(S.set_playing, 10 * 1000)
    else:
        print('not logged in')


def stop(props, prop):
    obs.timer_remove(S.set_playing)


def script_description():
    return "Shows which song is currently playing on spotify"


def script_update(settings):
    S.client_id = obs.obs_data_get_string(settings, "client_id")
    S.client_secret = obs.obs_data_get_string(settings, 'client_secret')
    S.username = obs.obs_data_get_string(settings, 'username')
    S.redirect_url = obs.obs_data_get_string(settings, 'redirect_url')

    S.image_source_name = obs.obs_data_get_string(settings, 'simage')
    S.name_source_name = obs.obs_data_get_string(settings, 'sname')
    S.author_source_name = obs.obs_data_get_string(settings, 'sauthor')


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "client_id", "Client ID", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "client_secret", "Client Secret", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "username", "Username", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "redirect_url", "Redirect URL", obs.OBS_TEXT_DEFAULT)

    p = obs.obs_properties_add_list(props, "simage", "Spotify image", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    k = obs.obs_properties_add_list(props, "sname", "Spotify name", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    t = obs.obs_properties_add_list(props, "sauthor", "Spotify Author", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(k, name, name)
                obs.obs_property_list_add_string(t, name, name)
            if source_id == "browser_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    obs.obs_properties_add_button(props, "button1", "Login", login)
    obs.obs_properties_add_button(props, "button2", "Start logging", restart)
    obs.obs_properties_add_button(props, "button3", "Stop logging", stop)
    return props
