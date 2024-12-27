import sys
import os
import inspect
import pluggy
import logging as LOGGER

from types import ModuleType
from plugins import hookspecs
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
__version__ = "1.0.0"

hookimpl = pluggy.HookimplMarker("slideshow")
"""Marker to be imported and used in plugins (and for own implementations)"""


# -*- coding: utf-8 -*-

def load_module(path : str) ->ModuleType:
    """Load a Python module dynamically.
    """
    if not path : raise ValueError("Invalid Python module path ")
    if not os.path.isfile(path):
        # add hookimpl.py
        if not path[-3:] == ".py":
            #try to add hookimpl.py
            path = os.path.join(path,path + "_hookimpl.py") #creates loadimgurl/loadimgurl_hookimpl.py
    
    if not os.path.isfile(path):
        # try to add absolute path
        path = os.path.join(os.path.realpath(os.path.dirname(__file__)), path)

    if not os.path.isfile(path):
        LOGGER.error( f"Invalid Python module path '{path}'")
        return

    dirname, filename = os.path.split(path)
    modname = os.path.splitext(filename)[0]

    if dirname not in sys.path:
        sys.path.append(dirname)

    for hook in sys.meta_path:
        if hasattr(hook, 'find_module'):
            # Deprecated since Python 3.4
            loader = hook.find_module(modname, [dirname])
            if loader:
                return loader.load_module(modname)
        else:
            spec = hook.find_spec(modname, [dirname])
            if spec:
                return spec.loader.load_module(modname)

    LOGGER.warning("Can not load Python module '%s' from '%s'", modname, path)


def create_plugin_manager():
    """Create plugin manager and defined hooks specification."""
    plugin_manager = FramePluginManager(hookspecs.hookspec.project_name)
    plugin_manager.add_hookspecs(hookspecs)
    return plugin_manager


class FramePluginManager(pluggy.PluginManager):
    pluginsAvailable : list[tuple[bool,str, ModuleType]] = []

    def load_all_plugins(self, paths : str, active : list[str]=None):
        """Register the core plugins, load plugins from setuptools entry points
        and the load given module/package paths.

        note:: by default hooks are called in LIFO registered order thus
               plugins register order is important.

        :param paths: list of Python module/package paths to load
        :type paths: list
        :param disabled: list of plugins name to be disabled after loaded
        :type disabled: list
        """
        # Load plugins declared by setuptools entry points
        self.load_setuptools_entrypoints(hookspecs.hookspec.project_name)

        plugins = []
        for path in paths:
            plugin = load_module(path)
            if plugin:
                LOGGER.debug("Plugin found at '%s'", path)
                plugins.append(plugin)

        for plugin in plugins:
            name = getattr(plugin, 'PLUGIN_NAME', None)
            self.register(plugin, name=name) #plugin must be registered for getting its friendly name
            if active and name in active:
                pluginIsActive = True
            else:
                pluginIsActive = False
                self.unregister(plugin)
            self.pluginsAvailable.append((pluginIsActive, plugin))

        # Check that each hookimpl is defined in the hookspec
        # except for hookimpl with kwarg 'optionalhook=True'.
        self.check_pending()


    def getAvailablePlugins(self) -> list[tuple]:
        """returns list of available plugins. For remote controller etc"""
        return self.pluginsAvailable

    def getAvailablePlugin(self, name : str) -> tuple:
        """returns available plugin regardles its registration."""
        try:
            plugin = next(p for p in self.pluginsAvailable if p[1].PLUGIN_NAME == name)
            return plugin[1]
        except StopIteration:
            return None
        


    def loadAllPluginsFromDir(self,  active : str , path : str = None):
        """Loads all plugins from the path. If path is not set then from this file directory"""
        path = os.path.realpath(os.path.dirname(__file__))
        dirs = os.listdir(path)
        dirs = filter(lambda x: os.path.isdir(os.path.join(path,x)) and x != 'plugin_template' and x[:2] != '__',dirs)
        dirs=list(dirs)
        self.load_all_plugins(dirs, active)

    def getFancyName(self, plugin, version=True):
        """Return the friendly name of the given plugin and
        optionally its version.

        :param plugin: registered plugin object
        :type plugin: object
        :param version: include the version number
        :type version: bool
        """
        name : str = None
        vNumber : str = None
        if hasattr(plugin, "PLUGIN_FANCY_NAME"):
            name = plugin.PLUGIN_FANCY_NAME
        
            # List of all setuptools registered plugins
            distinfo = dict(self.list_plugin_distinfo())

            if plugin in distinfo:
                if not name:
                    name = distinfo[plugin].project_name
                vNumber = distinfo[plugin].version
            else:
                if not name:
                    name = self.get_name(plugin)
                if not name:
                    name = getattr(plugin, '__name__', "unknown")
                vNumber = getattr(plugin, '__version__', '?.?.?')

        if version:
            name = f"{name}-{vNumber}"
        else:
            name = f"{name}"

        return name


