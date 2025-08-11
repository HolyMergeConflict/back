# app/metrics_utils.py
import time
import inspect
from contextlib import contextmanager
from functools import wraps

def _maybe_labels(label_fn, *args, **kwargs):
    return (label_fn(*args, **kwargs) if label_fn else {}) or {}

def _wrap(fn, before=None, after=None, on_error=None, get_labels=None):
    is_coro = inspect.iscoroutinefunction(fn)

    @wraps(fn)
    async def aw(*args, **kwargs):
        labels = _maybe_labels(get_labels, *args, **kwargs)
        if before: before(labels)
        try:
            t0 = time.perf_counter()
            res = await fn(*args, **kwargs)
            if after: after(labels, time.perf_counter() - t0)
            return res
        except Exception as e:
            if on_error: on_error(labels, e)
            raise

    @wraps(fn)
    def sw(*args, **kwargs):
        labels = _maybe_labels(get_labels, *args, **kwargs)
        if before: before(labels)
        try:
            t0 = time.perf_counter()
            res = fn(*args, **kwargs)
            if after: after(labels, time.perf_counter() - t0)
            return res
        except Exception as e:
            if on_error: on_error(labels, e)
            raise

    return aw if is_coro else sw

def count(counter, labels=None):
    def deco(fn):
        return _wrap(fn, before=lambda l: counter.labels(**l).inc(), get_labels=labels)
    return deco

def count_success_failure(counter, labels=None, label_name="result"):
    def deco(fn):
        def after(l, _dt): counter.labels(**{**l, label_name: "success"}).inc()
        def on_err(l, _e): counter.labels(**{**l, label_name: "failed"}).inc()
        return _wrap(fn, after=after, on_error=on_err, get_labels=labels)
    return deco

def observe_latency(hist, labels=None):
    def deco(fn):
        def after(l, dt): hist.labels(**l).observe(dt)
        return _wrap(fn, after=after, get_labels=labels)
    return deco

@contextmanager
def latency_cm(hist, **labels):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        hist.labels(**labels).observe(time.perf_counter() - t0)
