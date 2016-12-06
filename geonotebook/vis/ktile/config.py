import TileStache as ts
from collections import OrderedDict, MutableMapping

# class KtileLayerConfig
# Eventually will need to support configuration of the following sections:
#
# provider: Refers to a Provider, explained in detail under Providers.
# metatile Optionally makes it possible for multiple individual tiles to be
#          rendered at one time, for greater speed and efficiency. This is
#          commonly used for bitmap providers such as Mapnik. See Metatiles
#          for more information.
# preview: Optionally overrides the starting point for the built-in per-layer
#          slippy map preview, useful for image-based layers where appropriate.
#          See Preview for more information.
# projection: Names a geographic projection, explained in Projections.
#             If omitted, defaults to "spherical mercator".
# stale lock timeout: An optional number of seconds to wait before forcing a
#                     lock that might be stuck. This is defined on a per-layer
#                     basis, rather than for an entire cache at one time,
#                     because you may have different expectations for the
#                     rendering speeds of different layer configurations.
#                     Defaults to 15.
# cache lifespan: An optional number of seconds that cached tiles should be
#                 stored. This is defined on a per-layer basis. Defaults to
#                 forever if None, 0 or omitted.
# write cache: An optional boolean value to allow skipping cache write
#              altogether. This is defined on a per-layer basis. Defaults to
#              true if omitted.
# bounds: An optional dictionary of six tile boundaries to limit the rendered
#         area: low (lowest zoom level), high (highest zoom level), north,
#         west, south, and east (all in degrees). When any of these are
#         omitted, default values are north=89, west=-180, south=-89, east=180,
#         low=0, and high=31. A list of dictionaries will also be accepted,
#         indicating a set of possible bounding boxes any one of which
#         includes possible tiles.
# allowed origin: An optional string that shows up in the response HTTP header
#                 Access-Control-Allow-Origin, useful for when you need to
#                 provide javascript direct access to response data such as
#                 GeoJSON or pixel values. The header is part of a W3C working
#                 draft. Pro-tip: if you want to allow maximum permissions and
#                 minimal security headache, use a value of "*" for this.
# maximum cache age: An optional number of seconds used to control behavior of
#                    downstream caches. Causes TileStache responses to include
#                    Cache-Control and Expires HTTP response headers. Useful
#                    when TileStache is itself hosted behind an HTTP cache
#                    such as Squid, Cloudfront, or Akamai.
# redirects: An optional dictionary of per-extension HTTP redirects, treated
#            as lowercase. Useful in cases where your tile provider can
#            support many formats but you want to enforce limits to save on
#            cache usage. If a request is made for a tile with an extension in
#            the dictionary keys, a response can be generated that redirects
#            the client to the same tile with another extension. For example,
#            use the setting {"jpg": "png"} to force all requests for JPEG
#            tiles to be redirected to PNG tiles.
# tile height: An optional integer gives the height of the image tile in
#              pixels. You almost always want to leave this at the default
#              value of 256, but you can use a value of 512 to create
#              double-size, double-resolution tiles for high-density phone
#              screens.
# jpeg options: An optional dictionary of JPEG creation options, passed
#               through to PIL. Valid options include quality (integer),
#               progressive (boolean), and optimize (boolean).
# png options: An optional dictionary of PNG creation options, passed through
#              to PIL. Valid options include palette (URL or filename),
#              palette256 (boolean) and optimize (boolean).
# pixel effect: An optional dictionary that defines an effect to be applied
#               for all tiles of this layer. Pixel effect can be any of these:
#               blackwhite, greyscale, desaturate, pixelate, halftone, or blur.

class KtileLayerConfig(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.config = kwargs


class MutDict(MutableMapping):
    def __init__(self, **kwargs):
        self._dict = OrderedDict(kwargs)
        self.dirty = True

    def __getitem__(self, *args, **kwargs):
        return self._dict.__getitem__(*args, **kwargs)

    def __setitem__(self, _id, value):
        self._dict.__setitem__(_id, value)
        self.dirty = True

    def __delitem__(self, *args, **kwargs):
        self._dict.__delitem__(*args, **kwargs)
        self.dirty = True

    def __iter__(self, *args, **kwargs):
        return self._dict.__iter__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self._dict.__len__(*args, **kwargs)


# Manages the KtileConfig object for a particular Kernel.  This includes the
# actual configuration dictionary as well as styling paramaters that are made
# available from The users.
class KtileConfig(MutableMapping):
    def __init__(self, *args, **kwargs):

        self._config = None
        self._cache = None
        self._layers = None

        if "cache" in kwargs:
            self.cache = kwargs["cache"]

        self.layers = {}

    def __getitem__(self, *args, **kwargs):
        return self._layers.__getitem__(*args, **kwargs)

    def __setitem__(self, _id, value):
        if not isinstance(value, KtileLayerConfig):
            raise RuntimeError(
                "{} only accepts objects of type {}".format(
                    self.__class__.__name__, KtileLayerConfig.__class__.__name__))

        self._layers.__setitem__(_id, value)

    def __delitem__(self, *args, **kwargs):
        return self._layers.__delitem__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self._layers.__iter__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self._layers.__len__(*args, **kwargs)

    @property
    def dirty(self):
        return self._cache.dirty or self._layers.dirty

    @dirty.setter
    def dirty(self, val):
        self._cache.dirty = val
        self._layers.dirty = val

    @property
    def cache(self):
        return self._cache

    @cache.setter
    def cache(self, val):
        if not isinstance(val, MutDict):
            val = MutDict(**val)
        self._cache = val

    @property
    def layers(self):
        return {k : l.config for k, l in self._layers.items()}

    @layers.setter
    def layers(self, val):
        if not isinstance(val, MutDict):
            val = MutDict(**val)
        self._layers = val

    def as_dict(self):
        return {"cache": dict(self.cache),
                "layers": dict(self.layers)}

    @property
    def config(self):
        if self.dirty:
            self._config = ts.parseConfig(self.as_dict())
            self.dirty = False

        return self._config
