# -*- coding: utf-8 -*-
#    Plugin browser plugin for Gedit
#    Copyright (C) 2017 Lars Windolf <lars.windolf@gmx.de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, Gedit, Gio
from .pluginbrowser import PluginBrowser

class AppActivatable(GObject.Object, Gedit.AppActivatable):
    __gtype_name__ = "PluginBrowserAppActivatable"

    app = GObject.property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)
        self._menu_ext = None

    def do_activate(self):
        self._action = Gio.SimpleAction(name="plugin-browser")
        self._action.connect("activate", self._run)
        self.app.add_action(self._action)

        self._menu_ext = self.extend_menu("preferences-section")
        item = Gio.MenuItem.new("Install Plugins", "app.plugin-browser")
        self._menu_ext.append_menu_item(item)

    def do_deactivate(self):
        self.app.remove_action("plugin-browser")
        self._menu_ext = None
        self._action = None
        self._browser = None

    def _run(self, action, parameter, data=None):
        self._browser = PluginBrowser()
        self._browser.show_all()

