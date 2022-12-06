"""Convenient Event System"""
from __future__ import annotations

__version__ = "1.0.0"

from typing import Callable, overload

from pymitter import EventEmitter

EventHandler = Callable[[...], None]
"Signature of handler must copy signature of event."


class EventDispatcher:
	"""
	Base class to provide event group.

	Events are described as methods. Each event should have signature of EventHandler and decorated with @event.
	"""

	def __init__(self, emitter: EventEmitter | None = None):
		"""
		Base class to provide event group.

		Events are described as methods. Each event should have signature of EventHandler and decorated with @event.

		:param emitter: event emitter to use. If not given creates a new one.
		"""
		if emitter is None:
			emitter = EventEmitter()
		self.emitter = emitter


class Event:
	"""
	Event interface. Intended to be used as decorator or parametrized decorator for handlers.

	**name** - read only property of event name

	**get_emitter** - method to get bound event emitter.

	**trigger** - method to trigger event.
	"""

	def get_emitter(self) -> EventEmitter | None:
		"""
		Get bound event emitter.

		In most situations, event will have event emitter bound. But in rare cases it can be None when no handler descriptor has been decorated yet.
		"""
		...

	def trigger(self, *args, **kwargs):
		"""
		Fire the event. All arguments are passed to each handler.

		Signature must be the same as for handler descriptor.
		"""
		...

	@property
	def name(self) -> str:
		"""
		Name of the event.
		"""
		...

	@overload
	def __call__(self, handler: EventHandler) -> EventHandler:
		...

	@overload
	def __call__(self, times: int) -> Callable[[EventHandler], EventHandler]:
		...

	def __call__(self, arg):
		"""
		Event should be used as a decorator for corresponding event handlers.

		Using event as decorator without parameters (brackets) subscribe handler to the event.

		Using event as decorator with single parameter times:int subscribe handler to only first N times of the event. Negative values are treated as decorator without parameters.
		"""
		...  # Just for stub purpose. See actual source in EventProxy._create_proxy method.


_default_emitter = EventEmitter()
_default_dispatcher = EventDispatcher(_default_emitter)

emitter = _default_emitter
"Default event emitter."
dispatcher = _default_dispatcher
"Default event dispatcher that is bound to default event emitter."


class EventProxy(Event):


	def __init__(self, name: str):
		self._name = name
		self._emitter = None

	@property
	def name(self) -> str:
		return self._name

	def get_emitter(self) -> EventEmitter | None:
		return self._emitter

	def trigger(self, *args, **kwargs):
		if self._emitter:
			self._emitter.emit(self.name, *args, **kwargs)

	def _create_proxy(self, dispatcher: EventDispatcher | None = None) -> EventProxy:
		def proxy(*args: EventHandler | int):
			if len(args) == 2:
				given_dispatcher, arg = args
				if not isinstance(given_dispatcher, EventDispatcher):
					given_dispatcher = _default_dispatcher
			elif len(args) == 1:
				arg = args[0]
				given_dispatcher = _default_dispatcher
			else:
				raise TypeError('Wrong number of arguments was given.')
			return self._create_handler_decorator(given_dispatcher if dispatcher is None else dispatcher, arg)

		setattr(proxy, 'trigger', self.trigger)
		setattr(proxy, 'get_emitter', self.get_emitter)
		setattr(proxy, 'name', self.name)
		return proxy

	def _create_handler_decorator(self, dispatcher: EventDispatcher, arg: EventHandler | int):
		self._emitter = dispatcher.emitter

		if isinstance(arg, int):
			times = arg
			handler = None
		else:
			times = -1
			handler = arg

		def handler_decorator(event_handler: EventHandler) -> EventHandler:
			dispatcher.emitter.on(self.name, func=event_handler, ttl=times)
			return event_handler

		if handler is None:
			return handler_decorator
		else:
			return handler_decorator(handler)


@overload
def event(handler_descriptor: EventHandler) -> Event:
	...


@overload
def event(emitter: EventEmitter) -> Callable[[EventHandler], Event]:
	...


def event(arg):
	"""
	Event descriptor decorator. Can be used on functions or class methods. Can be used with or without parameters.

	When used with single parameter emitter:EventEmitter binds given event emitter to decorated event.

	When used without parameters (brackets): if method belongs to EventDispatcher derived class instance then uses its event emitter, else uses default emitter.
	"""
	is_parametrized = isinstance(arg, EventEmitter)
	dispatcher = EventDispatcher(arg) if is_parametrized else None

	def event_decorator(handler_descriptor: EventHandler) -> Event:
		event_proxy = EventProxy(handler_descriptor.__name__)
		return event_proxy._create_proxy(dispatcher)

	if is_parametrized:
		return event_decorator
	return event_decorator(arg)


if __name__ == '__main__':
	# Test some cases.
	import inspect

	emitter2 = EventEmitter()


	def callback(*args, **kwargs):
		print(inspect.getouterframes(inspect.currentframe())[1].function, args, kwargs)


	class TestDispatcher(EventDispatcher):


		@event(emitter2)
		def event1(self, text: str) -> None: ...

		@event
		def event2(self, text: str) -> None:
			pass


	class TestNotDispatcher:


		@event(emitter2)
		def event5(self, text: str) -> None: ...

		@event
		def event6(self, text: str) -> None:
			pass


	@event
	def event3(text: str) -> None:
		...


	@event(emitter2)
	def event4(text: str) -> None:
		...


	dispatcher = TestDispatcher()
	not_dispatcher = TestNotDispatcher()


	@dispatcher.event1
	def on_event1(*args, **kwargs):
		callback(*args, **kwargs)


	@dispatcher.event1(2)
	def on_event1_parametrized(*args, **kwargs):
		callback(*args, **kwargs)


	@dispatcher.event2
	def on_event2(*args, **kwargs):
		callback(*args, **kwargs)


	@dispatcher.event2(2)
	def on_event2_parametrized(*args, **kwargs):
		callback(*args, **kwargs)


	@event3
	def on_event3(*args, **kwargs):
		callback(*args, **kwargs)


	@event3(2)
	def on_event3_parametrized(*args, **kwargs):
		callback(*args, **kwargs)


	@event4
	def on_event4(*args, **kwargs):
		callback(*args, **kwargs)


	@event4(2)
	def on_event4_parametrized(*args, **kwargs):
		callback(*args, **kwargs)


	@not_dispatcher.event5
	def on_event5(*args, **kwargs):
		callback(*args, **kwargs)


	@not_dispatcher.event5(2)
	def on_event5_parametrized(*args, **kwargs):
		callback(*args, **kwargs)


	@not_dispatcher.event6
	def on_event6(*args, **kwargs):
		callback(*args, **kwargs)


	@not_dispatcher.event6(2)
	def on_event6_parametrized(*args, **kwargs):
		callback(*args, **kwargs)


	print(dispatcher.event1.name, dispatcher.event1.get_emitter())
	print(dispatcher.event2.name, dispatcher.event2.get_emitter())
	print(event3.name, event3.get_emitter())
	print(event4.name, event4.get_emitter())
	print(not_dispatcher.event5.name, not_dispatcher.event5.get_emitter())
	print(not_dispatcher.event6.name, not_dispatcher.event6.get_emitter())
	for i in range(3):
		dispatcher.event1.trigger(f'Event trigger {i}')
		dispatcher.event2.trigger(f'Event trigger {i}')
		event3.trigger(f'Event trigger {i}')
		event4.trigger(f'Event trigger {i}')
		not_dispatcher.event5.trigger(f'Event trigger {i}')
		not_dispatcher.event6.trigger(f'Event trigger {i}')
