from django.test import TestCase
from pydantic import BaseModel, ValidationError, validator
from sensorthings.api.components import ThingPostBody, LocationPostBody
from sensorthings.api.core.utils import whitespace_to_none, allow_partial
from sensorthings.api.core.iso_types import ISOInterval, ISOTime


class AllowPartialDecorator(TestCase):

    def setUp(self):
        """
        Defines a simple class with some required fields to test the allow_partial class decorator on.
        """

        class Thing(BaseModel):
            id: int
            name: str
            description: str = None

        self.Thing = Thing

    def test_all_optional(self):
        """
        Initializes the test class with the allow_partial decorator and passing no required values. If allow_partial
        is working correctly, the class should initialize with no field values and without raising a ValidationError.
        """

        @allow_partial
        class OptionalThing(self.Thing):
            pass

        thing = OptionalThing()

        self.assertEqual(thing.dict(exclude_unset=True), {})

    def test_some_optional(self):
        """
        Initializes the test class with an allow_partial decorator specifying the 'name' field and passing a value for
        'id'. If allow_partial is working correctly, the class should initialize with only a value for 'id' and
        without raising a ValidationError.
        """

        @allow_partial('name')
        class OptionalThing(self.Thing):
            pass

        thing = OptionalThing(id=1)

        self.assertEqual(thing.dict(exclude_unset=True), {'id': 1})

    def test_validate_none(self):
        """
        Initializes the test class with an allow_partial decorator explicitly passing a value of None to the 'id' field.
        If allow_partial is working correctly, the class should fail to initialize and raise a ValidationError.
        """

        @allow_partial
        class OptionalThing(self.Thing):
            pass

        self.assertRaises(ValidationError, OptionalThing, id=None)


class WhitespaceValidator(TestCase):

    def setUp(self):
        """
        Defines a simple class with the whitespace_to_none included.
        """

        class Thing(BaseModel):
            name: str

            _whitespace_validator = validator('name', allow_reuse=True, pre=True)(whitespace_to_none)

        self.Thing = Thing

    def test_empty_string(self):
        """
        Initializes the test class passing a value of '' to the 'name' field. If whitespace_to_none is working
        correctly, the class should fail to initialize and raise a ValidationError.
        """

        self.assertRaises(ValidationError, self.Thing, name='')

    def test_whitespace_string(self):
        """
        Initializes the test class passing a value of '  	' to the 'name' field. If whitespace_to_none is working
        correctly, the class should fail to initialize and raise a ValidationError.
        """

        self.assertRaises(ValidationError, self.Thing, name='  	')


class NestedEntityValidator(TestCase):

    def setUp(self):
        """
        Defines test data for creating nested instances of Things and Locations.
        """

        self.thing_data = [
            {
                'name': 'test_sensor',
                'description': 'A test sensor.'
            }
        ]

        self.location_data = [
            {
                'name': 'logan',
                'description': 'Logan, UT',
                'encodingType': 'application/geo+json',
                'location': {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [41.74, -111.83]
                    }
                }
            }
        ]

    def test_single_depth_entity(self):
        """
        Initializes a Thing with one related Location. Tests whether the nested_entities_check finds the nested
        Location object and converts it to a LocationPostBody type.
        """

        thing = ThingPostBody(
            **self.thing_data[0],
            Locations=[
                self.location_data[0]
            ]
        )

        self.assertIsInstance(thing.locations[0], LocationPostBody)

    def test_double_depth_entity(self):
        """
        Initializes a Thing with one related Location, which has one related Thing. Tests whether the
        nested_entities_check finds the nested Location object and its related Thing and converts it to a
        ThingPostBody type.
        """

        thing = ThingPostBody(
            **self.thing_data[0],
            Locations=[
                {
                    **self.location_data[0],
                    'Things': [
                        self.thing_data[0]
                    ]
                }
            ]
        )

        self.assertIsInstance(getattr(thing.locations[0], 'things')[0], ThingPostBody)


class ISOTimeValidation(TestCase):

    def setUp(self):
        """
        Sets up a TestModel class for testing ISOTime validation.
        """

        class TestModel(BaseModel):
            iso_time: ISOTime

        self.TestModel = TestModel

    def test_iso_time_value(self):
        """
        Tests the ISOTime type with a valid input value. No exceptions should be raised.
        """

        test_value = '2023-01-01T11:11:11+00:00'

        test_instance = self.TestModel(
            iso_time=test_value
        )

        self.assertEqual(
            test_instance.iso_time,
            test_value
        )

    def test_non_string_value(self):
        """
        Tests the ISOTime type with a non-string value. A ValueError should be raised.
        """

        test_value = 123

        self.assertRaises(ValueError, self.TestModel, iso_time=test_value)

    def test_non_iso_value(self):
        """
        Tests the ISOTime type with a non-ISO value. A ValueError should be raised.
        """

        test_value = 'Jan 1, 2023'

        self.assertRaises(ValueError, self.TestModel, iso_time=test_value)


class ISOIntervalType(TestCase):

    def setUp(self):
        """
        Sets up a TestModel class for testing ISOInterval validation.
        """

        class TestModel(BaseModel):
            iso_interval: ISOInterval

        self.TestModel = TestModel

    def test_iso_interval_value(self):
        """
        Tests the ISOInterval type with a valid input value. No exceptions should be raised.
        """

        test_value = '2023-01-01T11:11:11+00:00/2023-01-02T11:11:11+00:00'

        test_instance = self.TestModel(
            iso_interval=test_value
        )

        self.assertEqual(
            test_instance.iso_interval,
            test_value
        )

    def test_iso_time_value(self):
        """
        Tests the ISOInterval type with an ISOTime value. A ValueError should be raised.
        """

        test_value = '2023-01-01T11:11:11+00:00'

        self.assertRaises(ValueError, self.TestModel, iso_interval=test_value)

    def test_iso_too_many_values(self):
        """
        Tests the ISOInterval type with too many time values. A ValueError should be raised.
        """

        test_value = '2023-01-01T11:11:11+00:00/2023-01-02T11:11:11+00:00/2023-01-03T11:11:11+00:00'

        self.assertRaises(ValueError, self.TestModel, iso_interval=test_value)

    def test_iso_wrong_order_interval(self):
        """
        Tests the ISOInterval type with time values in the wrong order. A ValueError should be raised.
        """

        test_value = '2023-01-02T11:11:11+00:00/2023-01-01T11:11:11+00:00'

        self.assertRaises(ValueError, self.TestModel, iso_interval=test_value)

    def test_non_iso_value(self):
        """
        Tests the ISOInterval type with non-ISO values. A ValueError should be raised.
        """

        test_value = 'Jan 1, 2023/Jan 2, 2023'

        self.assertRaises(ValueError, self.TestModel, iso_interval=test_value)

    def test_non_string_value(self):
        """
        Tests the ISOInterval type with non-string values. A ValueError should be raised.
        """

        test_value = 123

        self.assertRaises(ValueError, self.TestModel, iso_interval=test_value)
