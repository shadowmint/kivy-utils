from __future__ import absolute_import
import unittest

from kutils.assets.collada import load_collada
from os.path import dirname, abspath, join


class Tests(unittest.TestCase):

  def _path(self, *args):
    path = dirname(__file__)
    output = join(path, *args)
    return abspath(output)

  def test_loads_raw_collada(self):
    path = self._path('assets', '3d', 'models', 'model.dae')
    record = load_collada(path)
    print record
    assert record is not None

  def test_loads_zipped_collada(self):
    path = self._path('assets', '3d', 'models', 'model.dae.zip')
    record = load_collada(path)
    print record
    assert record is not None


if __name__ == '__main__':
  unittest.main()
