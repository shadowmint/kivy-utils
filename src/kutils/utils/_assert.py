# Copyright 2012 Douglas Linder
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
from __future__ import absolute_import
from .logging import Logging


class Assert:
  """ Test helper """

  def __init__(self):
    self._logger = Logging.get(2)

  def true(self, value, message):
    if not value:
      self._fail("%s (value was not True)" % (message))

  def false(self, value, message):
    if value:
      self._fail("%s (value was True)" % (message))

  def not_equal(self, v1, v2, message):
    if v1 == v2:
      self._fail("%s (%s != %s)" % (message, str(v1), str(v2)))

  def equals(self, v1, v2, message):
    if not v1 == v2:
      self._fail("%s (%s != %s)" % (message, str(v1), str(v2)))

  def null(self, value, message):
    if not value is None:
      self._fail("%s (%s was not None)" % (message, str(value)))

  def not_null(self, value, message):
    if value is None:
      self._fail("%s (value was None)" % (message, str(value)))

  def contains(self, items, item, message):
    if item not in items:
      self._fail("%s (%s was not in the list %r)" % (message, str(item), items))

  def type(self, instance, T, message):
    if T is None:
      self._fail("%s (Invalid type; T was None)")
    elif instance is None:
      self._fail("%s (Invalid instance; None is not '%s')" % T.__name__)
    elif type(instance) is not T:
      self._fail("%s (instance type '%s' is not '%s')" % (type(instance).__name__, T.__name__))

  def trace(self, message):
    self._logger.info(message)

  def _fail(self, message):
    try:
      assert False
    except Exception as err:
      self._logger.error(message + ": %s", err)
    assert False
