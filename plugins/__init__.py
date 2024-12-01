import pluggy

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

hookimpl = pluggy.HookimplMarker("slideshow")
"""Marker to be imported and used in plugins (and for own implementations)"""