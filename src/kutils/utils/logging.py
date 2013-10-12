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
import logging
import traceback


class Logging(object):
  """ Convenience helper to get a named logger """

  @staticmethod
  def suppress_exceptions():
    """ Suppress annoying exceptions when not interested """
    ErrorTracebackHandler._suppress_exceptions = True

  @staticmethod
  def _new_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s: %(message)s (%(levelname)s)')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    tb_handler = ErrorTracebackHandler()
    logger.addHandler(tb_handler)
    return logger

  @classmethod
  def _logger(cls, name):
    try:
      cache = cls.__loggers
    except AttributeError:
      cls.__loggers = {}
    if not name in cls.__loggers:
      cls.__loggers[name] = Logging._new_logger(name)
    return cls.__loggers[name]

  @classmethod
  def get(cls, depth=1):
    import inspect
    frame = inspect.stack()[depth]
    target = frame[1]
    return Logging._logger(target)


class ErrorTracebackHandler(logging.StreamHandler):
  _suppress_exceptions = False  # Suppress by setting to True
  def emit(self, record):
    try:
        msg = traceback.format_exc()
        if msg is not None and str(msg) != "None\n" and not ErrorTracebackHandler._suppress_exceptions:
          self.stream.write(msg)
    except AttributeError:
        pass  # Fails in py3
