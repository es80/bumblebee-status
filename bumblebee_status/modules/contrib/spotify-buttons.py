import sys
import dbus

import core.module
import core.widget
import core.input
import core.decorators
"""Displays the current song being played and allows pausing, skipping ahead, and skipping back.

Requires the following library:
    * python-dbus

Parameters:
    * spotify-buttons.format:   Format string (defaults to '{artist} - {title}')
      Available values are: {album}, {title}, {artist}, {trackNumber}
"""

class Module(core.module.Module):
    def __init__(self, config, theme):
        super().__init__(config, theme, [])

        self.__layout = self.parameter("layout", "spotify-buttons.song spotify-buttons.prev spotify-buttons.pause spotify-buttons.next")

        self.__song = ""
        self.__pause = ""
        self.__format = self.parameter("format", "{artist} - {title}")

        self.__cmd = "dbus-send --session --type=method_call --dest=org.mpris.MediaPlayer2.spotify \
                /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player."

    def hidden(self):
        return self.string_song == ""

    def update(self):
        try:
            self.clear_widgets()
            bus = dbus.SessionBus()
            spotify = bus.get_object(
                "org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2"
            )
            spotify_iface = dbus.Interface(spotify, "org.freedesktop.DBus.Properties")
            props = spotify_iface.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            playback_status = str(
                spotify_iface.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
            )
            if playback_status == "Playing":
                self.__pause = "\u25B6"
            else:
                self.__pause = "\u258D\u258D"
            self.__song = self.__format.format(
                album=str(props.get("xesam:album")),
                title=str(props.get("xesam:title")),
                artist=",".join(props.get("xesam:artist")),
                trackNumber=str(props.get("xesam:trackNumber")),
            )
            #this feels like a stupid way to do this but its all i can think of
            widget_map = {}
            for widget_name in self.__layout.split():
                widget = self.add_widget(name = widget_name)
                if widget_name == "spotify-buttons.prev":
                    widget_map[widget] = {
                        "button": core.input.LEFT_MOUSE,
                        "cmd": self.__cmd + "Previous",
                        }
                    widget.full_text("\u258F\u25C0")
                elif widget_name == "spotify-buttons.pause":
                    widget_map[widget] = {
                        "button": core.input.LEFT_MOUSE,
                        "cmd": self.__cmd + "PlayPause",
                        }
                    widget.full_text(self.__pause)
                elif widget_name == "spotify-buttons.next":
                    widget_map[widget] = {
                        "button": core.input.LEFT_MOUSE,
                        "cmd": self.__cmd + "Next",
                        }
                    widget.full_text("\u25B6\u2595")
                elif widget_name == "spotify-buttons.song":
                    widget.full_text(self.__song)
                else:
                    raise KeyError(
                        "The spotify-buttons module does not have a {widget_name!r} widget".format(widget_name=widget_name)
                        )
            for widget, callback_options in widget_map.items():
                core.input.register(widget, **callback_options)

        except Exception:
            self.__song = ""

    @property
    def string_song(self):
        if sys.version_info.major < 3:
            return unicode(self.__song)
        return str(self.__song)
