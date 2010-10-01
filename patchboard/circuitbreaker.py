import datetime
from threading import Lock

class CircuitOpen(Exception):
    pass

class CircuitBreaker(object):
    def __init__(self, threshold, timeout):
        self.failures = 0
        if isinstance(timeout, int):
            timeout = datetime.timedelta(seconds=timeout)
        self.threshold = threshold
        self.timeout = timeout
        self.closed = True
        self.error_expiration = datetime.datetime.now()
        self.circuit_lock = Lock()
    
    def __call__(self, *args, **kwargs):
        self.check_circuit()
        try:
            ret = self.run(*args, **kwargs)
        except Exception, exception:
            self.register_failure(exception)
            raise
        else:
            self.close_circuit()
            return ret
    
    def check_circuit(self):
        if not self.is_ready():
            raise CircuitOpen
    
    def is_ready(self):
        #ATOMIC
        self.circuit_lock.acquire()
        if not self.closed:
            if self.error_expiration <= datetime.datetime.now():
                self.open_circuit()
            else:
                self.circuit_lock.release()
                return False
        self.circuit_lock.release()
        return True
    
    def register_failure(self, exception):
        #ATOMIC
        self.circuit_lock.acquire()
        self.failures += 1
        if self.failures >= self.threshold:
            self.open_circuit()
        self.circuit_lock.release()
    
    def open_circuit(self):
        self.closed = False
        self.error_expiration = datetime.datetime.now() + self.timeout
    
    def close_circuit(self):
        #ATOMIC
        self.circuit_lock.acquire()
        self.failures = 0
        self.closed = True
        self.circuit_lock.release()
    
    def run(self):
        raise NotImplementedError

def circuit_breaker(func, threshold, timeout, default=None):
    class Breaker(object):
        def run(self, *args, **kwargs):
            return func(*args, **kwargs)
    breaker = Breaker(threshold, timeout)
    def wrapper(*args, **kwargs):
        try:
            return breaker(*args, **kwargs)
        except:
            if callable(default):
                return default()
            raise
    return wrapper
