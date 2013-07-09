# Copyright (c) Matt Haggard.
# See LICENSE for details.

from twisted.trial.unittest import TestCase

from norm.porcelain import makePool
from norm.orm import Property, classInfo, objectInfo, SQLTable



class PropertyTest(TestCase):


    def test_class(self):
        """
        When accessing through a class, you should get access to the name of
        the attribute and the name of the column
        """
        class Foo(object):
            hey = Property('foo')
            how = Property()

        self.assertEqual(Foo.hey.attr_name, 'hey')
        self.assertEqual(Foo.hey.column_name, 'foo')
        self.assertEqual(Foo.how.attr_name, 'how')
        self.assertEqual(Foo.how.column_name, 'how')


    def test_instance(self):
        """
        When accessing an instance, you can assign and retrieve a value on the
        property.
        """
        class Foo(object):
            a = Property('joe')
            b = Property()


        foo = Foo()
        self.assertEqual(foo.a, None)
        self.assertEqual(foo.b, None)
        foo.a = 12
        foo.b = 'hello'
        self.assertEqual(foo.a, 12)
        self.assertEqual(foo.b, 'hello')


    def test_conversion(self):
        """
        You can specify a function to be used to convert a value from
            python-land to database-land
            and 
            database-land to python-land
        """
        def toDatabase(x):
            return x + 'db'


        def fromDatabase(x):
            return x + 'python'


        class Foo(object):
            a = Property('joe', toDatabase=toDatabase,
                         fromDatabase=fromDatabase)

        foo = Foo()
        foo.a = 'a'
        val = Foo.a.toDatabase(foo)
        self.assertEqual(val, 'adb')

        self.assertEqual(foo.a, 'a')
        Foo.a.fromDatabase(foo, 'something')
        self.assertEqual(foo.a, 'somethingpython')


    def test_fromDatabase(self):
        """
        Setting a value from the database will mark it as not changed
        """
        class Foo(object):
            a = Property()
            b = Property()

        foo = Foo()
        foo.a = 'something'
        Foo.b.fromDatabase(foo, 'something')

        info = objectInfo(foo)
        self.assertEqual(info.changed(), [Foo.a], "Foo.b should not be "
                         "considered changed because the value came from the "
                         "database")


    def test_valueOf(self):
        """
        You can get the value of a column
        """
        class Foo(object):
            a = Property()
            b = Property()
            c = Property(default_factory=lambda:10)

        foo = Foo()
        foo.b =  10
        self.assertEqual(Foo.a.valueFor(foo), None)
        self.assertEqual(Foo.b.valueFor(foo), 10)
        self.assertEqual(Foo.c.valueFor(foo), 10, "Should know about defaults")



class classInfoTest(TestCase):


    def test_properties(self):
        """
        You can list the properties on a class
        """
        class Foo(object):
            a = Property('foo')
            b = Property()


        class Bar(object):
            c = Property()
            a = Property()

        info = classInfo(Foo)
        self.assertEqual(info.columns['foo'], [Foo.a])
        self.assertEqual(info.columns['b'], [Foo.b])
        self.assertEqual(info.attributes['a'], Foo.a)
        self.assertEqual(info.attributes['b'], Foo.b)

        info = classInfo(Bar)
        self.assertEqual(info.columns['c'], [Bar.c])
        self.assertEqual(info.columns['a'], [Bar.a])
        self.assertEqual(info.attributes['c'], Bar.c)
        self.assertEqual(info.attributes['a'], Bar.a)


    def test_primary(self):
        """
        You can find primary keys
        """
        class Foo(object):
            a = Property(primary=True)
            b = Property()


        info = classInfo(Foo)
        self.assertEqual(info.primaries, [Foo.a])



    def test_multiPrimary(self):
        """
        You can find multiple primary keys
        """
        class Foo(object):
            a = Property(primary=True)
            b = Property(primary=True)
            c = Property()
            d = Property(primary=True)


        info = classInfo(Foo)
        self.assertEqual(set(info.primaries), set([Foo.a, Foo.b, Foo.d]))


    def test_table(self):
        """
        You can get the table a class maps to.
        """
        @SQLTable('foo')
        class Foo(object):
            pass


        info = classInfo(Foo)
        self.assertEqual(info.table, 'foo')



class objectInfoTest(TestCase):


    def test_changed(self):
        """
        You can list the columns that have changed on an object
        """
        class Foo(object):
            a = Property('foo')
            b = Property()

        foo = Foo()
        info = objectInfo(foo)
        changed = info.changed()
        self.assertEqual(changed, [])

        foo.a = 'something'
        self.assertEqual(info.changed(), [Foo.a])

        foo.b = 'another'
        self.assertEqual(set(info.changed()), set([Foo.a, Foo.b]))

        info.resetChangedList()
        self.assertEqual(info.changed(), [])
        
        foo.b = 'hey'
        self.assertEqual(info.changed(), [Foo.b])


    def test_changed_default(self):
        """
        Specifying a default will be included in the changes
        """
        class Foo(object):
            a = Property(default_factory=lambda:10)

        foo = Foo()
        info = objectInfo(foo)
        changed = info.changed()
        self.assertEqual(changed, [Foo.a])







