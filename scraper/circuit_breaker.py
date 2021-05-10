# Circuit Breaker helper
# When ON
#  - delegates to the `on` parameter function
#  - if `on()` fails it adds the failure to its count
#  - if this count exceeds `trigger_count`, the breaker becomes OFF
#  - if `on()` succeeds, it decrements the count
# When OFF
#  - delefates to the `off` parameter function
#  - counts the numbers of times `off` is called
#  - if this counts exceeds `release_count`, the breaker becomes ON
class CircuitBreaker:
    def __init__(self, on, off=None, trigger_count=3, release_count=10, name=None):
        self.on_func = on
        self.off_func = off
        self.is_on = True
        self.off_count = 0
        self.error_count = 0
        self.release_count = release_count
        self.trigger_count = trigger_count
        self.name = name
        if name is None and off is None:
            raise Exception("You must specify a name if you don't specify a `off` for CircuitBreaker")

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def call(self, *args, **kwargs):
        if not self.is_on:
            self.off_count += 1
            if self.off_count <= self.release_count:
                return self.call_off(*args, **kwargs)
            else:
                self.is_on = True
                self.off_count = 0

        try:
            value = self.on_func(*args, **kwargs)
            if self.error_count > 0:
                self.error_count -= 1

            return value

        except Exception as e:
            self.error_count += 1
            if self.error_count >= self.trigger_count:
                self.is_on = False
                self.error_count = 0
            raise e

    def call_off(self, *args, **kwargs):
        if self.off_func is not None:
            return self.off_func(*args, **kwargs)
        else:
            raise CircuitBreakerOffException(self.name)

class CircuitBreakerOffException(RuntimeError):
    def __init__(self, name):
        msg = f"CircuitBreaker '{name}' is currently off"
        super().__init__(self, msg)
        self.message = msg