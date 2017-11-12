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
import os, sys, shutil, subprocess
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

class PluginBrowser(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Plugin Browser")

        self.target_dir = os.path.expanduser("~/.local/share/gedit/plugins/")

        self.set_border_width(10)
        self.set_default_size(600,300)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self._liststore = Gtk.ListStore(bool, str, str, str, str)
        self._plugin_list = self.fetch_list()
        for ref in self._plugin_list['plugins']:
            try:
                name = next(iter(ref))
                installed = False
                if os.path.isfile('%s%s.plugin' % (self.target_dir, ref[name]['module'])):
                   installed = True
                if not 'icon' in ref[name]:
                   ref[name]['icon'] = 'libpeas-plugin'

                self._liststore.append((installed, ref[name]['icon'], name, ref[name]['category'], ref[name]['description']))
            except:
                print("Bad fields for plugin entry %s" % name)

        self.current_filter_category = None
        self.category_filter = self._liststore.filter_new()
        self.category_filter.set_visible_func(self.category_filter_func)

        #creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.category_filter)
        self.treeview.connect("row-activated", self.on_row_activated)
        for i, column_title in enumerate(["Inst.", "Icon", "Name", "Category", "Description"]):
            if column_title == 'Inst.':
                renderer = Gtk.CellRendererToggle()
                column = Gtk.TreeViewColumn(column_title, renderer, active=i)
            elif column_title == 'Icon':
                renderer = Gtk.CellRendererPixbuf()
                column = Gtk.TreeViewColumn(column_title, renderer, icon_name=i)
            else:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)
            column.set_sort_column_id(i)

        self._categories = Gtk.ListStore(str)
        for category in ["All", "Linter", "IDE", "Completion"]:
            self._categories.append([category])

        self._catcombo = Gtk.ComboBox.new_with_model(self._categories)
        renderer_text = Gtk.CellRendererText()
        self._catcombo.pack_start(renderer_text, True)
        self._catcombo.add_attribute(renderer_text, "text", 0)
        self._catcombo.connect("changed", self.on_catcombo_changed)
        self._catlabel = Gtk.Label("Filter by category")

        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        self.grid.attach_next_to(self._catlabel, self.scrollable_treelist, Gtk.PositionType.TOP, 1, 1)
        self.grid.attach_next_to(self._catcombo, self._catlabel, Gtk.PositionType.RIGHT, 2, 1)

        self.scrollable_treelist.add(self.treeview)

        self.show_all()

    def fetch_list(self):
        """Fetch list from github project repo and parse JSON"""
        list_url = "https://raw.githubusercontent.com/lwindolf/gedit-pluginbrowser/master/plugin-list.json"
        data = None
        req = urllib.request.Request(list_url)
        resp = urllib.request.urlopen(req).read()
        return json.loads(resp.decode('utf-8'))

    def category_filter_func(self, model, iter, data):
        """Tests if the category in the row is the one in the filter"""
        if self.current_filter_category is None or self.current_filter_category == "All":
            return True
        else:
            return model[iter][3] == self.current_filter_category

    def on_catcombo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            self.current_filter_category = model[tree_iter][0]
        else:
            self.current_filter_category = None
        self.category_filter.refilter()

    def on_row_activated(self, path, column, user_data):
        selection = self.treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter != None:
            plugin = model[treeiter][2]

            # Get infos on selected plugin
            for ref in self._plugin_list['plugins']:
                if plugin == next(iter(ref)):
                    model[treeiter][0] = self.install_plugin(ref[plugin])
                    return

            if plugin_info == None:
                print("Failed to get plugin infos for git fetch!")
                return

    def show_message(self, message, error = False):
        dialog = Gtk.MessageDialog(self, Gtk.DialogFlags.DESTROY_WITH_PARENT, (Gtk.MessageType.ERROR if error else Gtk.MessageType.INFO), Gtk.ButtonsType.CLOSE, message)
        Gtk.Dialog.run(dialog)
        Gtk.Widget.destroy(dialog)
 
    def install_plugin(self, plugin_info):
        """Fetches github repo for a plugin and tries to install the plugin"""
        DIR_NAME = "/tmp/gedit-pluginbrowser-%s" % plugin_info['module']
        if os.path.isdir(DIR_NAME):
            shutil.rmtree(DIR_NAME)
        os.mkdir(DIR_NAME)
        os.chdir(DIR_NAME)

        # Git checkout
        p = subprocess.Popen(["git", "clone", "https://github.com/%s" % plugin_info['source'], "."])
        p.wait()
        # FIXME: error checking

        # Now copy the plugin source, there are 2 variants:
        # - either there is a subdir named after the module   <module>/
        # - or there is a module file with language extension <module>.py
        try:
            src_dir = '%s/%s' % (DIR_NAME, plugin_info['module'])
            if os.path.isdir(src_dir):
                print("Copying %s to %s" % (src_dir, self.target_dir))
                shutil.copytree(src_dir, "%s/%s" % (self.target_dir, plugin_info['module']))
        except:
            self.show_message("Failed to copy plugin directory (%s)!" % sys.exc_info()[0], True)
            return False

        # FIXME: support other plugin languages besides Python
        try:
            src_file = '%s/%s.py' % (DIR_NAME, plugin_info['module'])
            if os.path.isfile(src_file):
                shutil.copy(src_file, self.target_dir)
        except:
            self.show_message("Failed to copy plugin .py file (%s)!" % sys.exc_info()[0], True)
            return False

        # Copy .plugin file
        try:
            shutil.copy('%s/%s.plugin' % (DIR_NAME, plugin_info['module']), self.target_dir)
        except:
            self.show_message("Failed to copy .plugin file (%s)!" % sys.exc_info()[0], True)
            return False

        # Cleanup
        shutil.rmtree(DIR_NAME)

        self.show_message("Plugin '%s' is now installed. Ensure to restart Gedit and enable it in the plugin preferences!" % plugin_info['module'])
        return True

