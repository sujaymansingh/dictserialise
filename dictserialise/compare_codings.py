"""Try different encoders and decoders.

Usage:
    compare_codings.py [--length=n]
    compare_codings.py (-h | --help)

Options:
    -h --help        Show this screen
    --length=n       The number of objects to put in a list [Default: 1000]
"""
import sys
import timeit
import zlib

import docopt

import dictserialise


class TestPoint(object):

    def __init__(self, **kwargs):
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)

    def to_dict(self):
        return {"x": self.x, "y": self.y}

    def from_dict(self, d):
        self.x = d["x"]
        self.y = d["y"]
        return self


def get_large_object(length):
    first_dict = {}
    first_dict["name"] = "Some dict"
    first_dict["points"] = []

    for i in range(length):
        first_dict["points"].append(TestPoint(x=i, y=2 * i))
    return first_dict


if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    length = int(args.get("--length"))

    obj = get_large_object(length)

    print u"Length of obj['points'] = {0}".format(length)
    print u"Size of obj = {0}b".format(sys.getsizeof(obj))

    # Just run these first to ensure all lazy-inits etc are run.
    dictserialise.dumps(obj, encoder="json")
    dictserialise.dumps(obj, encoder="msgpack")

    for (coding, compress) in [
        ("json", False),
        ("json", True),
        ("msgpack", False),
        ("msgpack", True),
    ]:
        start_time = timeit.default_timer()
        encoded = dictserialise.dumps(obj, encoder=coding)
        if compress:
            encoded = zlib.compress(encoded)
        time_taken = 1000 * (timeit.default_timer() - start_time)
        title = "{0} (zipped)".format(coding) if compress else coding
        print u"{0:20s} {1:12d} {2:9.3f}ms".format(
            title, len(encoded), time_taken)
        del encoded
