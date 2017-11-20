# gedit-plugininstaller

Easy to use plugin installer for Gedit3. Supports installing plugins and their dependencies from a curated list of Gedit 3.14+ plugins. For now support only plugins hosted on github.

![Plugin Installer Screenshot](https://lzone.de/images/gedit-plugininstaller.png)

Plugins are installed using "git clone" and then installed into ~/.local/share/gedit/plugins.

## Installation

Sadly the installer cannot install itself :-)

    git clone https://github.com/lwindolf/gedit-plugininstaller.git
    mkdir -p ~/.local/share/gedit/plugins/
    cp -r gedit-plugininstaller/plugininstaller.plugin gedit-plugininstaller/plugininstaller/ ~/.local/share/gedit/plugins/

## Adding Plugins

If you want to add another plugin please add it to plugin-list.json and make a pull request.

## Dependencies

* Gedit 3
* Requires git installed
