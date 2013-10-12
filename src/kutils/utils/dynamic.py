# Copyright 2013 Douglas Linder
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class Dynamic(object):
  """ Dynamic reflective dictionary.

      It's often useful to use a more terse form of the
      syntax dict_instance["Key"]; this object allows the
      use of chained invokation like a class instance:

      i = Dyanmic()
      i.x.y = "X"
      i.y = 10

      v = getattr(i, key)

      You can interate over the object:

      for k, v in i:
        pass

      And immediately convert into a dictionary if required:

      d = dict(iter(i))

      You can also convert a dictionary instance into a dynamic,
      which is especially useful for json processing:

      d = {"x" : { "y" : { "z" : 1, "z2" : 2 } } }
      i = Dynamic(d)

      z = i.x.y.z
      z2 = i.x.y.z2

      Obviously you are limited to python variable name compliant
      keys using this object.
  """

  def __init__(self, src=None):
    if src is not None:
      for k in src.keys():
        value = src[k]
        if isinstance(value, dict):
          value = Dynamic(value)
        setattr(self, k, value)

  def __getattr__(self, key):
    if key not in self.__dict__.keys():
      self.__dict__[key] = Dynamic()
    return self.__dict__[key]

  def __setattr__(self, key, value):
    self.__dict__[key] = value

  def __iter__(self):
    for k in self.__dict__.keys():
      value = self.__dict__[k]
      if isinstance(value, Dynamic):
        yield k, dict(iter(value))
      else:
        yield k, value

  def __contains__(self, key):
    return key in self.__dict__

  def keys(self):
    try:
      return self.__dict__.viewkeys()
    except:  # python 3
      return self.__dict__.keys()

  def values(self):
    try:
      return self.__dict__.viewvalues()
    except:  # python 3
      return self.__dict__.values()
