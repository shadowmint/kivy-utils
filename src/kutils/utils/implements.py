import inspect


def implements(*T):
  def inner(cls):
    cls.__implements = []
    for t in T:

      # Look for required methods
      t_methods = inspect.getmembers(t, predicate=lambda x: inspect.isfunction(x) or inspect.ismethod(x))
      c_methods = inspect.getmembers(cls, predicate=lambda x: inspect.isfunction(x) or inspect.ismethod(x))
      sig = {}
      for i in t_methods:
        name = 'method:%s' % i[0]
        if not name.startswith("method:__"):
          sig[name] = False
      for i in c_methods:
        name = 'method:%s' % i[0]
        if name in sig.keys():
          sig[name] = True

      # Look for required properties
      t_props = [i for i in inspect.getmembers(t) if i not in t_methods]
      c_props = [i for i in inspect.getmembers(cls) if i not in c_methods]
      for i in t_props:
        name = 'property:%s' % i[0]
        if not name.startswith("property:__"):
          sig[name] = False
      for i in c_props:
        name = 'property:%s' % i[0]
        if name in sig.keys():
          sig[name] = True

      missing = False
      for i in sig.keys():
        if not sig[i]:
          missing = True
      if missing:
        raise ImplementsException(cls, t, sig)
      cls.__implements.append(t)
    return cls
  return inner


def has_api(instance, T):
  """ Runtime check for T in type identity """
  rtn = False
  if instance is not None and T is not None:
    if inspect.isclass(instance):
      if hasattr(instance, "__implements"):
        if T in instance.__implements:
          rtn = True
    else:
      if hasattr(instance.__class__, "__implements"):
        if T in instance.__class__.__implements:
          rtn = True
  return rtn


class ImplementsException(Exception):
  def __init__(self, cls, T, signature):
    msg = "Invalid @implements decorator on '%s' for interface '%s': %r" % (cls.__name__, T.__name__, signature)
    super(ImplementsException, self).__init__(msg)
    self.signature = signature
