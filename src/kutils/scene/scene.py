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
from __future__ import absolute_import
from datetime import datetime
import os.path

from kutils.utils import Factory, Dynamic


class Scene(object):
  """ Managed scene data object.

      The 'widget' property of this class returns the current widget
      associated with it; if watch() is called, it attempts to watch
      the source file and reload the module if it changes.

      To dynamically update a displayed ui, something needs to periodically
      query the widget and timestamp objects on this module, and update
      accordingly.
  """

  def __init__(self):
    self._wpath = None
    self._widget = None
    self._wfactory = None
    self._factory = None
    self.data = Dynamic()
    self.timestamp = 0

  def watch(self):
    if os.path.exists(self._wpath):
      self._factory = Factory()
      self._factory.load(self._wpath)
      self._factory.watch(True)

  @property
  def widget(self):
    if self._factory is not None:
      rtn, reloaded = self._factory.prop('widget')
      if reloaded:
        self._widget = None
        self._wfactory = rtn
    if self._widget is None:
      self._widget = self._wfactory()
      self.rebuild(self._widget, self.data)
      self.timestamp = datetime.now()
    return self._widget

  @property
  def path(self):
    """ Return the path being used here for tests and retrospection """
    return self._wpath

  def rebuild(self, widget):
    """ Override this to map data -> widgets """
    pass
