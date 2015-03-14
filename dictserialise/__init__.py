"""Use this to dump and load arbitrary objects to strings.
The objects __must__ support `to_dict` and `from_dict` methods.

e.g.
class Point(object):
    def __init__(self, **kwargs):
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)

    def to_dict(self):
        return {"x": self.x, "y": self.y}

    def from_dict(self, d):
        self.x = d["x"]
        self.y = d["y"]
        return self
"""
import json
import pydoc

import msgpack


class InvalidCoding(Exception):
    pass


def dumps(some_object, **kwargs):
    """Write an object to a string.
    First the object(s) are converted to dicts as appropriate.
    Then the intermediate dicts are encoded as a dict using the given encoding.
    TODO: Use other encoders than json.
    """
    escaped_dict = escape(some_object)
    encoder = kwargs.get("encoder", "json")
    if encoder == "json":
        return json.dumps(escaped_dict)
    elif encoder == "msgpack":
        return msgpack.packb(escaped_dict, encoding="utf-8")
    else:
        raise InvalidCoding("invalid encoder: {0}".format(encoder))


def loads(serialised_string, **kwargs):
    """Read an object from a string.
    First the string is converted to a dict using the given encoder.
    Then the dict is simply converted to objects.
    """
    decoder = kwargs.get("decoder", "json")
    if decoder == "json":
        loaded_dict = json.loads(serialised_string)
    elif decoder == "msgpack":
        loaded_dict = msgpack.unpackb(serialised_string, encoding="utf-8")
    else:
        raise InvalidCoding("invalid decoder: {0}".format(decoder))
    return unescape(loaded_dict)


def unescape(item):
    """Given an object, look (recursively) for any dicts that have a
    __classname__ key.
    For those that do, convert them to an object.
    """
    if isinstance(item, list):
        return [unescape(sub_item) for sub_item in item]
    elif isinstance(item, dict):
        if "__classname__" not in item:
            # This is a simple dict, but its key/values may not be.
            return {
                unescape(key): unescape(value)
                for (key, value) in item.iteritems()
            }
        else:
            klass = pydoc.locate(item.pop("__classname__"))
            loaded_object = klass()
            unescaped_dict = {
                unescape(key): unescape(value)
                for (key, value) in item.iteritems()
            }
            loaded_object.from_dict(unescaped_dict)
            return loaded_object
    else:
        return item


def escape(item):
    """Escape all objects that have to_dict and from_dict functions into dicts.
    """
    if isinstance(item, list):
        return [escape(sub_item) for sub_item in item]
    elif isinstance(item, dict):
        return {
            escape(key): escape(value)
            for (key, value) in item.iteritems()
        }
    elif hasattr(item, "to_dict"):
        escaped_dict = {"__classname__": u"{0}.{1}".format(
            item.__module__, item.__class__.__name__)}
        for (key, value) in item.to_dict().iteritems():
            escaped_dict[escape(key)] = escape(value)
        return escaped_dict
    else:
        return item
