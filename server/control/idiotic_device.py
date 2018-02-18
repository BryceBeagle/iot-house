class Attribute:
    """Decorator for functions within an IdioticDevice instance

    When the set() method is called, each subscribed IdioticTrigger's alert() method is called.
    IdioticTriggers can subscribe by calling the .subscribe() method and unsubscribe by calling the .unsubscribe()
    method.

    Uses some python magic to return a descriptor. The __get__ dundie is required to set the owner post init

    TODO: Populate IdioticDevice.attributes list
    """
    def __init__(self, fget, fset=None, subscribers=set(), owner=None):

        self.fget = fget
        self.fset = fset

        self.subscribers = subscribers

        self.owner = owner

    def __get__(self, owner, obj_type=None):

        if not self.owner:

            attr_temp = type(self)(self.fget, self.fset, self.subscribers, owner=owner)
            setattr(owner, self.fget.__name__, attr_temp)

        return getattr(owner, self.fget.__name__)

    def get(self):
        return self.fget(self.owner)

    def set(self, value, notify=True):
        """Set value of attribute and notify subscribers

        A silent set can be performed by setting notify=False"""

        ret = self.fset(self.owner, value)

        if notify:
            for subscriber in self.subscribers:
                subscriber.alert(value)

        return ret

    def getter(self, fget):
        return type(self)(fget, self.fset, self.subscribers)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.subscribers)

    def subscribe(self, subscriber):
        self.subscribers.add(subscriber)

    def unsubscribe(self, subscriber):
        self.subscribers.discard(subscriber)


class Action:
    """Add function to function's class' list of Actions"""

    # test = get_class_that_defined_method(func)

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class IdioticDevice:

    def __init__(self):

        self._uuid = None
        self._name = None

    @Attribute
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, id_):
        self._uuid = id_

    @Attribute
    def name(self):
        """Device name used for external access"""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @classmethod
    def get_attributes(cls):
        attributes = set()
        for name, obj in cls.__dict__.items():
            if isinstance(obj, Attribute):
                attributes.add(name)
        return attributes

    @classmethod
    def get_actions(cls):
        actions = set()
        for name, obj in cls.__dict__.items():
            if isinstance(obj, Action):
                actions.add(name)
        return actions
