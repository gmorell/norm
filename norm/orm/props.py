# Copyright (c) Matt Haggard.
# See LICENSE for details.
from twisted.python.compat import long, unicode

from norm.orm.base import Property

from datetime import date, datetime
from datetime import time as dt_time
import time

class Int(Property):
    def _validate(self, prop, obj, value):
        if value is None:
            return value
        if type(value) not in (int, long):
            raise TypeError('%r must be an integer, not %r' % (prop, value))
        return value


class Bool(Property):
    def _validate(self, prop, obj, value):
        if value is None:
            return None
        if type(value) not in (bool, int):
            raise TypeError('%r must be a boolean, not %r' % (prop, value))
        return bool(value)


class Date(Property):
    def _validate(self, prop, obj, value):
        if type(value) not in (type(None), date):
            raise TypeError('%r must be a date, not %r' % (prop, value))
        return value


class DateTime(Property):
    def _validate(self, prop, obj, value):
        if type(value) not in (type(None), datetime):
            raise TypeError('%r must be a datetime, not %r' % (prop, value))
        return value


class Time(Property):
    def _validate(self, prop, obj, value):
        if type(value) not in (type(None), dt_time, time, str):
            raise TypeError('%r must be a time, not %r' % (prop, value))
        try:
            if type(value) == str:
                value = time.strptime(value)
        except:
            raise ValueError("%r must be in the format HH:MM not %r", prop, value)
        return value


class String(Property):
    def _validate(self, prop, obj, value):
        if type(value) not in (type(None), str):
            raise TypeError('%r must be a str, not %r' % (prop, value))
        return value


class Unicode(Property):
    def _validate(self, prop, obj, value):
        if type(value) not in (type(None), unicode):
            raise TypeError('%r must be a unicode, not %r' % (prop, value))
        return value

# Postgres DataTypes
class UUID(Property):
    def _validate(self, prop, obj, value):
        from uuid import UUID
        if type(value) not in (type(None), unicode):
            raise TypeError('%r must be a unicode, not %r' % (prop, value))
        if not value:
            return value
        try:
            UUID(value, version=4)
        except ValueError:
            raise TypeError('%r must be a uuid' % (prop))
        return value


class JSON(Property):
    def _validate(self, prop, obj, value):
        import json
        if type(value) not in (type(None), unicode, dict):
            raise TypeError('%r must be a unicode, not %r' % (prop, value))
        try:
            json.dumps(value)
        except json.decoder.JSONDecodeError:
            raise TypeError('%r must be a valid json' % (prop))
        return value


class Array(Property):
    def __init__(self, **kwargs):
        try:
            child = kwargs.pop("child")
        except:
            raise ValueError('Array must be instantiated with a `child` kwarg')
        Property.__init__(self, **kwargs)
        self.child = child

    def _validate(self, prop, obj, value):
        if type(value) not in (type(None), list):
            raise TypeError('%r must be an array, not %r' % (prop, value))

        if value:
            for o in value:
                try:
                    self.child(o)
                except:
                    raise
                # if type(o) not in (type(None), type(self.child)):
                #     raise TypeError('%r must match the declared children' % (prop))
        return value

    def toDatabase(self, obj):
        """
        Get the value of this L{Property} for the given object converted for
        a database.

        @param obj: The obj on which this descriptor lives.

        @return: A database-ready value
        """
        value = self._getValue(obj)
        as_str = str(value)
        as_ins = as_str.replace("[","{").replace("]","}")
        return self._toDatabase(as_ins)


class Enum(Property):
    def __init__(self, **kwargs):
        try:
            values = kwargs.pop("values")
        except:
            raise ValueError('Array must be instantiated with a `values` kwarg')
        Property.__init__(self, **kwargs)
        self.values = values

    def _validate(self, prop, obj, value):
        if type(value) not in (type(None), unicode):
            raise TypeError('%r must be a unicode, not %r' % (prop, value))

        if value:
            if value not in self.values:
                raise ValueError("Invalid ENUM value, must be in [%s]" % ", ".join(self.values))

        return value