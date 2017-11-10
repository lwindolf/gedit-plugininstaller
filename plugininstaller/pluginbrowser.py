# -*- coding: utf-8 -*-
# Plugin browser plugin for Gedit
# Copyright (C) 2017 Lars Windolf <lars.windolf@gmx.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib.request, json
import os, shutil, subprocess
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

class PluginBrowser(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Plugin Browser")
        self.set_border_width(10)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self._liststore = Gtk.ListStore(str, str, str)
        self._plugin_list = self.fetch_list()
        for ref in self._plugin_list['plugins']:
            name = next(iter(ref))
            self._liststore.append((name, ref[name]['category'], ref[name]['description']))
        self.current_filter_category = None

        self.category_filter = self._liststore.filter_new()
        self.category_filter.set_visible_func(self.category_filter_func)

        #creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.category_filter)
        self.treeview.connect("row-activated", self.on_row_activated)
        for i, column_title in enumerate(["Name", "Category", "Description"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.treeview.append_column(column)

        self.buttons = list()
        for category in ["Linter", "IDE", "Completion", "None"]:
            button = Gtk.Button(category)
            self.buttons.append(button)
            button.connect("clicked", self.on_filter_button_clicked)

        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
        self.scrollable_treelist.add(self.treeview)

        self.show_all()

    def fetch_list(self):
        """Fetch list from github project repo and parse JSON"""
        list_url = "https://raw.githubusercontent.com/lwindolf/gedit-pluginbrowser/master/plugin-list.json"
        data = None
        req = urllib.request.Request(list_url)
        resp = urllib.request.urlopen(req).read()
        return json.loads(resp.decode('utf-8'))

    def install_plugin(self):
        """Fetches github repo for a plugin and tries to install the plugin"""


    def category_filter_func(self, model, iter, data):
        """Tests if the category in the row is the one in the filter"""
        if self.current_filter_category is None or self.current_filter_category == "None":
            return True
        else:
            return model[iter][1] == self.current_filter_category

    def on_filter_button_clicked(self, widget):
        self.current_filter_category = widget.get_label()
        self.category_filter.refilter()

    def on_row_activated(self, path, column, user_data):
        selection = self.treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter != None:
            plugin = model[treeiter][0]
            plugin_info = None
            # Get infos on selected plugin
            for ref in self._plugin_list['plugins']:
                if plugin == next(iter(ref)):
                    plugin_info = ref[plugin]

            if plugin_info == None:
                print("Failed to get plugin infos for git fetch!")
                return

            DIR_NAME = "/tmp/gedit-pluginbrowser-%s" % plugin_info['module']
            if os.path.isdir(DIR_NAME):
                shutil.rmtree(DIR_NAME)
            os.mkdir(DIR_NAME)
            os.chdir(DIR_NAME)

            # Git checkout
            print("git clone https://github.com/%s" % plugin_info['source'])
            p = subprocess.Popen(["git", "clone", "https://github.com/%s" % plugin_info['source'], "."])
            p.wait()
            # FIXME: error checking

            target_dir = os.path.expanduser("~/.local/share/gedit/plugins/")

            # Now copy the plugin source, there are 2 variants:
            # - either there is a subdir named after the module   <module>/
            # - or there is a module file with language extension <module>.py
            src_dir = '%s/%s' % (DIR_NAME, plugin_info['module'])
            if os.path.isfile(src_dir):
                shutil.copytree(src_dir, target_dir)

            # FIXME: support other plugin languages besides Python
            src_file = '%s/%s.py' % (DIR_NAME, plugin_info['module'])
            if os.path.isfile(src_file):
                shutil.copy(src_file, target_dir)
                # FIXME: error checking

            # Copy .plugin file
            shutil.copy('%s/%s.plugin' % (DIR_NAME, plugin_info['module']), target_dir)
            # FIXME: error checking

            # Cleanup
            shutil.rmtree(DIR_NAME)

