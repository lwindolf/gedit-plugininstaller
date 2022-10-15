# gedit-plugininstaller

Easy to use plugin installer for GNOME Gedit. Supports installing plugins and their dependencies from a curated list of plugins. For now it supports only plugins hosted on github.

Tested to work with Gedit 3.14 - 41.0

Might work with newer version too!

![Plugin Installer Screenshot](https://lzone.de/images/gedit-plugininstaller.png)

Plugins are installed using "git clone" and then installed into ~/.local/share/gedit/plugins.

## Installation

### Linux

You need to copy the plugin like this

    git clone https://github.com/lwindolf/gedit-plugininstaller.git
    mkdir -p ~/.local/share/gedit/plugins/
    cp -r gedit-plugininstaller/plugininstaller.plugin gedit-plugininstaller/plugininstaller/ ~/.local/share/gedit/plugins/

Finally start Gedit and enable the plugin installer under Preferences / Plugins.

### Windows

The plugin is [known](https://github.com/lwindolf/gedit-plugininstaller/issues/5) to work with MSYS2 installed Gedit. For this installation type download all files into your MSYS installation directory, e.g.

    C:\msys64\mingw64\lib\gedit\plugins

## Adding Plugins

If you want to add another plugin please add it to plugin-list.json and make a pull request.

## Dependencies

* Gedit 3.14+
* Requires git installed
* Some plugins require pip3 to install further Python modules
