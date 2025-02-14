import types


class IdioticTrigger:
    """Used by a routine to subscribe to an attribute's value

    Triggers are used to alert routines of state change within the system. Each
    routine uses a trigger to “subscribe” to a device driver’s attribute’s
    changes. Whenever the subscribed-to attribute’s updater function is called,
    the trigger is alerted so that it can execute its routine.

    However, a trigger does not simply execute its routine blindly on any change
    with the attribute’s value. A trigger is tied to a specific value
    transition. For example, a trigger for a thermostat changing routine would
    subscribe to a temperature sensor’s temperature attribute, but only when the
    temperature transitions from less than 70°F to greater than 70°F. A trigger
    is instantiated with the desired attribute, its routine, and what state
    change the routine should be interested in.

    Note that triggers are edge triggered. In the previous temperature based
    example, the trigger would not be executed if the temperature stay above
    70°F, only if it dipped below and than again performed the upward
    transition.
    """

    def __init__(self, routine, attr, check, value):
        """
        :param attr:   Attribute to subscribe to
        """
        # Allows for both str and class function to be passed
        # TODO: This feels clunky
        if isinstance(check, str):
            self.check = getattr(self, check)
        else:
            self.check = types.MethodType(check, self)

        self.value = value

        self.routine = routine
        self.routine.trigger = self

        self.attr = attr
        self.subscribe(attr)

        self.name = None

        self.active = False

    def subscribe(self, attr) -> None:
        """Subscribe to attribute for state changes"""
        print(f"Subscribed to {attr}")
        attr.subscribe(self)

    def alert(self, value) -> None:
        """Called when attr's state changes

        Calls self.trigger() if self.check [conditional] is True

        :param value: value of attr after state change
        """
        print(f"Checking {value}")
        check = self.check(value)
        if check != self.active:
            if check:
                print(f"Triggered {value}")
                self.trigger()
                self.active = True
            else:
                self.active = False

    def trigger(self) -> None:
        """Call parent IotRoutine"""
        self.routine()

    def check_eq(self, attr_value):
        """attr_value == value"""
        return attr_value == self.value

    def check_neq(self, attr_value):
        """attr_value != value"""
        return attr_value != self.value

    def check_gt(self, attr_value):
        """attr_value > value"""
        return attr_value > self.value

    def check_gte(self, attr_value):
        """attr_value >= value"""
        return attr_value >= self.value

    def check_lt(self, attr_value):
        """attr_value < value"""
        return attr_value < self.value

    def check_lte(self, attr_value):
        """attr_value <= value"""
        return attr_value <= self.value

    def check_true(self, attr_value):
        """attr_value == bool(True)"""
        return bool(attr_value)

    def check_false(self, attr_value):
        """attr_value == bool(False)"""
        return not bool(attr_value)
