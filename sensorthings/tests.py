from django.test import TestCase
from pydantic import BaseModel, ValidationError, validator
from .api.core.utils import whitespace_to_none, allow_partial


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
