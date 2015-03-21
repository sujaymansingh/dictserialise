import json
import unittest

import dictserialise


class Point(object):

    """A point has x, y co-ordinates, and a list of subpoints.
    """

    def __init__(self, **kwargs):
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.subpoints = kwargs.get("subpoints", [])

    def to_dict(self):
        return {"x": self.x, "y": self.y, "subpoints": self.subpoints}

    def from_dict(self, d):
        self.x = d["x"]
        self.y = d["y"]
        self.subpoints = d["subpoints"]
        return self


class TestSerialise(unittest.TestCase):

    def test_loads(self):
        """Load a string into an object.
        """
        serialised_string = '{"__classname__": "dictserialise.tests.' + \
            'test_serialise.Point", "x": 200, "y": 100, "subpoints": []}'

        some_object = dictserialise.loads(serialised_string, decoder="json")
        self.assertTrue(isinstance(some_object, Point))

        self.assertEqual(some_object.x, 200)
        self.assertEqual(some_object.y, 100)
        self.assertEqual(some_object.subpoints, [])

    def test_nested_loads(self):
        """Load an object that itself contains other objects.
        """
        some_dict = {
            "__classname__": "dictserialise.tests.test_serialise.Point",
            "x": 1,
            "y": 2,
            "subpoints": [
                {
                    "__classname__":
                        "dictserialise.tests.test_serialise.Point",
                    "x": 10,
                    "y": 20,
                    "subpoints": [],
                },
                {
                    "__classname__":
                        "dictserialise.tests.test_serialise.Point",
                    "x": 20,
                    "y": 40,
                    "subpoints": [],
                },
            ]
        }
        serialised_string = json.dumps(some_dict)
        some_object = dictserialise.loads(serialised_string, encoder="json")
        self.assertIsInstance(some_object, Point)

        self.assertEqual(some_object.x, 1)
        self.assertEqual(some_object.y, 2)

        subpoints = some_object.subpoints
        self.assertIsInstance(subpoints, list)

        for point in subpoints:
            self.assertIsInstance(point, Point)
        self.assertEqual(subpoints[0].x, 10)
        self.assertEqual(subpoints[0].y, 20)
        self.assertEqual(subpoints[1].x, 20)
        self.assertEqual(subpoints[1].y, 40)

    def test_dumps(self):
        p = Point(x=3, y=2, points=[])
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 2)

        serialised_string = dictserialise.dumps(p, encoder="json")

        # It is easier to test a loaded dict rather than a string.
        some_dict = json.loads(serialised_string)

        self.assertEqual(
            some_dict["__classname__"],
            "dictserialise.tests.test_serialise.Point")
        self.assertEqual(some_dict["x"], 3)
        self.assertEqual(some_dict["y"], 2)

    def test_nested_dumps(self):
        p1 = Point(x=10, y=5, subpoints=[])
        p2 = Point(x=20, y=10, subpoints=[])

        p = Point(x=2, y=1, subpoints=[p1, p2])

        serialised_string = dictserialise.dumps(p, encoder="json")
        some_dict = json.loads(serialised_string)

        self.assertEqual(
            some_dict["__classname__"],
            "dictserialise.tests.test_serialise.Point")
        self.assertEqual(some_dict["x"], 2)
        self.assertEqual(some_dict["y"], 1)

        subpoints = some_dict["subpoints"]
        self.assertIsInstance(subpoints, list)
        for point in subpoints:
            self.assertEqual(
                point["__classname__"],
                "dictserialise.tests.test_serialise.Point")

        self.assertEqual(subpoints[0]["x"], 10)
        self.assertEqual(subpoints[0]["y"], 5)
        self.assertEqual(subpoints[1]["x"], 20)
        self.assertEqual(subpoints[1]["y"], 10)

    def test_lists(self):
        serialised_string = '[{"__classname__": "dictserialise.tests.' + \
            'test_serialise.Point", "x": 200, "y": 100, "subpoints": []}]'

        result = dictserialise.loads(serialised_string, decoder="json")
        self.assertTrue(isinstance(result, list))

        some_object = result[0]
        self.assertTrue(isinstance(some_object, Point))

        self.assertEqual(some_object.x, 200)
        self.assertEqual(some_object.y, 100)

    def test_custom_loader(self):
        constants = {
            "one": ObjectWithName("one"),
            "two": ObjectWithName("two"),
        }

        dictserialise.register_custom_loader(
            ObjectWithName,
            lambda x: constants[x["name"]]
        )

        item = ObjectWithName("one")
        self.assertFalse(item is constants["one"])

        loaded = dictserialise.loads(dictserialise.dumps(item))
        self.assertTrue(loaded is constants["one"])


class ObjectWithName(object):

    """This is a dummy class with just one attribute: a name.
    """

    def __init__(self, name=""):
        self.name = name

    def to_dict(self):
        return {"name": self.name}

    def from_dict(self, d):
        raise NotImplementedError()
