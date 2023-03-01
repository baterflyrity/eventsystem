# Convenient Event System

Create, subscribe and fire events with one line of code. Unlike alternative packages this one provides static typed predefined events with documented signature of event handlers.

**Both ordinary and async event handlers are supported. Both ordinary and async events are supported. Any of ordinary, async and awaited async event triggering is supported.**

# Usage examples

Briefly, you need to perform two steps:

1. decide between two options: group events in class derived from `EventDispatcher` or just define functions,
2. then decorate each event with `@event`.

----

Let's see how to use the library in more details. Imagine we write some user interface stuff for our super-duper program.

### Single event example

**Step 1: define click event.**

```python
@event
def click(x: int, y: int)->None:
	"""
	Occures when user clicks on our interface.
	
	:param x: mouse horizontal position relative to top left corner.
	:param y: mouse vertical position relative to top left corner.
	"""
	... # no implementation required
```

**Step 2: subscribe click event.**

```python
@click
def on_click(x: int, y: int)->None:
	"""
	Process mouse click.
	"""
	print(f'You have clicked at ({x}; {y}).')
```

**Step 3: fire click event.**

```python
click.trigger(12, 34) # You have clicked at (12; 34).
```

### Events group example

**Step 1: define mouse events group.**

```python
class Mouse(EventDispatcher):
	@event
	def click(x: int, y: int)->None:
		"""
		Occures when user clicks on our interface.
		
		:param x: mouse horizontal position relative to top left corner.
		:param y: mouse vertical position relative to top left corner.
		"""
		... # no implementation required
	@event
	def move(x: int, y: int)->None:
		"""
		Occures when user moves cursor over our interface.
		
		:param x: mouse horizontal position relative to top left corner.
		:param y: mouse vertical position relative to top left corner.
		"""
		...
```

**Step 2: subscribe click event.**

```python
mouse = Mouse()

@mouse.click
def on_click(x: int, y: int)->None:
	"""
	Process mouse click.
	"""
	print(f'You have clicked at ({x}; {y}).')
```

**Step 3: fire click event.**

```python
mouse.click.trigger(12, 34) # You have clicked at (12; 34).
```

# How to create events?

Event are created by using `event` decorator. It can be used with or without parameters.

The event can have arbitrary body that is not actually called. Main feature is to defined event signature hence during subscribing **developer can see help message and type hints with intended event handler signature**.

### Single event bound to default event emitter

The simplest case is to just create an event. So default event emitter is used to manage this event.

```python
@event
def click(x: int, y: int)->None:
	"""
	Occures when user clicks on our interface.
	
	:param x: mouse horizontal position relative to top left corner.
	:param y: mouse vertical position relative to top left corner.
	"""
	...
```

### Single event bound to custom event emitter

Otherwise, you can specify different event emitter passing as argument.

```python
my_event_emitter = EventEmitter()

@event(my_event_emitter)
def click(x: int, y: int)->None:
	"""
	Occures when user clicks on our interface.
	
	:param x: mouse horizontal position relative to top left corner.
	:param y: mouse vertical position relative to top left corner.
	"""
	...
```

### Events group bound to dedicated event emitter

Moreover, you can combine events in group by using classes. There are two different approaches: using default event emitter or dedicate one per each class.

**Creating dedicated event emitter per each event group is recommended.**

Considering the preferred approach you can group event in class derived from `EventDispatcher`. This ensures creation of new event emitter per each class instance.

**Notice that using `event` decorator stays the same way as for non-class functions.**

```python
class Mouse(EventDispatcher):
	@event
	def click(x: int, y: int)->None:
		"""
		Occures when user clicks on our interface.
		
		:param x: mouse horizontal position relative to top left corner.
		:param y: mouse vertical position relative to top left corner.
		"""
		... # no implementation required
	@event(my_event_emitter) # given event emitter is prior to Mouse one 
	def move(x: int, y: int)->None:
		"""
		Occures when user moves cursor over our interface.
		
		:param x: mouse horizontal position relative to top left corner.
		:param y: mouse vertical position relative to top left corner.
		"""
		...
```

Then you can instantiate `Mouse` class and access dedicated event emitter for e.g. further low-level tuning.

```python
mouse = Mouse()

mouse.emitter.max_listeners = 2 # allows up to two handlers
```

When using `event` decorator on `EventDispatcher` subclass method with specified event emitter it takes priority over the one dedicated per class instance.

### Events group bound to default event emitter

In case you do not want to create dedicated event emitter per class instance (*not recommended*) you can just omit deriving from `EventDispatcher`.

In following code default event emitter is used for all events in group.

```python
class Mouse:
	@event
	def click(x: int, y: int)->None:
		"""
		Occures when user clicks on our interface.
		
		:param x: mouse horizontal position relative to top left corner.
		:param y: mouse vertical position relative to top left corner.
		"""
		... # no implementation required
	@event(my_event_emitter) # given event emitter is prior to default one 
	def move(x: int, y: int)->None:
		"""
		Occures when user moves cursor over our interface.
		
		:param x: mouse horizontal position relative to top left corner.
		:param y: mouse vertical position relative to top left corner.
		"""
		...
```

# How to subscribe events?

Event is subscribed by decorating handler. **Handler can be any ordinary or async function (callable).** Decorator also can be used with or without parameters.

**Notice, when using event your IDE can show help message and type hints of intended handler signature.**

### Unlimited event handler

The simplest case is to just decorate handler with event. So handler will be called when event triggers.

```python
@click
def on_click(x: int, y: int)->None:
	"""
	Process mouse click.
	"""
	print(f'You have clicked at ({x}; {y}).')
```

**There is no difference between usage of single events or ones from event groups.** Hence, according to `Mouse` class example the above code can be rewritten in:

```python
@mouse.click
def on_click(x: int, y: int)->None:
	"""
	Process mouse click.
	"""
	print(f'You have clicked at ({x}; {y}).')
```

### Event handler with executions limit

Otherwise, you can specify number of times to handle event. When event fires more times, no further calls will be made to the handler.

```python
@click(2)
def on_click(x: int, y: int)->None:
	"""
	Process mouse click two first times.
	"""
	print(f'You have clicked at ({x}; {y}).')
```

In above case `on_click` will be called only for the first two times.

# How to fire events?

To fire, emit, trigger event you can use `.trigger(...)` method where should pass exactly the same arguments that are defined in event signature.

**Notice, when using event your IDE can show help message and type hints of intended arguments.**

Basically, to trigger an event you can just call `trigger` method. Each active handler will be called with given arguments. You can use any set of arguments, including positional, universal, named, packed and even named packed.

```python
click.trigger(12, 34)
```

Alternatively considering `Mouse` class example:

```python
mouse.click.trigger(12, 34)
```

### Triggering events from async loop

When event is triggered from async loop the method returns loop task of handlers dispatching. One can optionally await it to pause current async thread until dispatching will be done.

Consider example above running within asyncio loop:

```python
async def main():
	click.trigger(12, 34) # Schedule handlers execution and go to the next line without waiting.
	...
	await click.trigger(12, 34) # Wait until all handlers process before next line execution.
	...
	
asyncio.run(main())
```

*It is worth nothing that some IDEs, linters or static type checkers can warn about not awaited triggering. This is not a problem and depends only on demanded triggering behaviour.*

# Reference

**eventsystem.event(...)**

Event descriptor decorator. Can be used on functions or class methods. Can be used with or without parameters.

When used with single parameter `emitter:EventEmitter` binds given event emitter to decorated event.

When used without parameters (brackets): if method belongs to `EventDispatcher` derived class instance then uses its event emitter, else uses default emitter.

**eventsystem.EventDispatcher(emitter: EventEmitter | None = None)**

Base class to provide event group. Events are described as methods. Each event should have signature of `EventHandler` and decorated with `@event`.

Constructor parameters:

* **emitter** - event emitter to use. If not given creates a new one.

Fields:

* **emitter** - event emitter bound to dispatcher subclass instance.

**eventsystem.Event**

Event interface. Intended to be used as decorator or parametrized decorator for handlers. *Should not be instantiated directly.*

Fields:

* **name** - read only property of event name

Methods:

* **get_emitter() → EventEmitter | None** - get bound event emitter. In most cases, event will have event emitter bound. But in rare cases it can be `None` when no handler descriptor has been decorated yet.

* **trigger(...) → asyncio.Task| None** - fire the event. All arguments are passed to each handler. Signature must match handler descriptor. If event is triggered being in asyncio loop the method returns corresponding Task which can be optionally awaited to pause until all handlers are processed.

**eventsystem.emitter**

Default event emitter.

**eventsystem.dispatcher**

Default event dispatcher bound to default event emitter.

**eventsystem.EventHandler**

Base event and event handler signature (type annotations). Signature of handler must copy signature of event.

# What event emitter is?

This library us build on top of [pymitter](https://pypi.org/project/pymitter). `EventEmitter` - is a basic building block of that library which actually dispatches events, manages priority, limitations and queues.

Using `EventEmitter` directly you can unsubscribe handlers, get all active handlers or limit them. For detailed tuning read pymitter documentation.
