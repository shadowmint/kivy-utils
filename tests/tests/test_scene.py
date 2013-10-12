from __future__ import absolute_import
import sys
import os
import time
import unittest

from kutils.utils import Assert


class SceneTests(unittest.TestCase):
  def setUp(self):
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

  @staticmethod
  def test_can_load_scene():
    a = Assert()

    import scene1.scene

    s = scene1.scene.Scene1()
    w = s.widget
    a.not_null(w, 'Failed to read widget')

  @staticmethod
  def test_can_load_scene_while_watching():
    a = Assert()

    import scene1.scene

    s = scene1.scene.Scene1()
    s.watch()
    w = s.widget
    a.not_null(w, 'Failed to read widget')

  @staticmethod
  def test_can_reload_scene():
    a = Assert()

    import scene1.scene

    s = scene1.scene.Scene1()
    s.watch()

    value = s.widget
    timestamp = s.timestamp
    time.sleep(1)

    raw = """
from datetime import datetime

__core = 'Hello World' + str(datetime.now())

def widget():
  return __core
    """

    with open(s.path, 'w') as fp:
      fp.write(raw)

    value2 = s.widget
    timestamp2 = s.timestamp
    time.sleep(1)

    raw = """
from datetime import datetime

__core = str(datetime.now())

def widget():
  return __core
    """

    with open(s.path, 'w') as fp:
      fp.write(raw)

    value3 = s.widget
    timestamp3 = s.timestamp

    a.trace(value)
    a.trace(timestamp)
    a.trace(value2)
    a.trace(timestamp2)
    a.trace(value3)
    a.trace(timestamp3)

    a.false(value.startswith('Hello World'), 'Initial module state was wrong')
    a.true(value2.startswith('Hello World'), 'After change module state was wrong')
    a.false(value3.startswith('Hello World'), 'After second change, module state was wrong')

    a.true(timestamp2 > timestamp, 'Invalid timestamp after change')
    a.true(timestamp3 > timestamp2, 'Invalid timestamp after change')


if __name__ == '__main__':
  unittest.main()
