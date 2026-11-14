from dataclasses import dataclass, field
import unittest

from docker_python.core.json import json_creator, json_value
from docker_python.core.models import Model, from_wire, to_wire


@dataclass(frozen=True)
class Wrapped:
    value: str

    @classmethod
    @json_creator
    def parse(cls, value):
        return cls(value)

    @json_value
    def primitive(self):
        return self.value


@dataclass
class Envelope(Model):
    items: list[Wrapped] | None = field(default=None, metadata={'wire_name': 'Items'})


class JsonHookTests(unittest.TestCase):
    def test_nested_hooks_and_nulls(self):
        model = Envelope.from_wire({'Items': ['one', 'two']})
        self.assertEqual(model.items, [Wrapped('one'), Wrapped('two')])
        self.assertEqual(model.to_wire(), {'Items': ['one', 'two']})
        self.assertIsNone(Envelope.from_wire({'Items': None}).items)
        self.assertEqual(Envelope().to_wire(), {})

    def test_creator_can_wrap_a_staticmethod(self):
        class Value:
            @json_creator
            @staticmethod
            def parse(value):
                return Wrapped(value)
        self.assertEqual(from_wire(Value, 'hello'), Wrapped('hello'))

    def test_creator_overrides_default_model_deserialization(self):
        @dataclass
        class Custom(Model):
            value: str

            @classmethod
            @json_creator
            def parse(cls, value):
                return cls(value['custom'])

            @json_value
            def primitive(self):
                return {'custom': self.value}
        self.assertEqual(from_wire(Custom, {'custom': 'hello'}), Custom('hello'))
        self.assertEqual(to_wire(Custom('hello')), {'custom': 'hello'})

    def test_invalid_or_ambiguous_creators_fail_clearly(self):
        class Invalid:
            @json_creator
            def parse(self, value):
                pass
        with self.assertRaisesRegex(TypeError, 'classmethod or @staticmethod'):
            from_wire(Invalid, {})
        class Ambiguous:
            @classmethod
            @json_creator
            def first(cls, value):
                pass

            @classmethod
            @json_creator
            def second(cls, value):
                pass
        with self.assertRaisesRegex(TypeError, 'multiple JSON conversion methods'):
            from_wire(Ambiguous, {})


if __name__ == '__main__':
    unittest.main()
