def boot():
  """ Kivy bootstrap
      copy this to bootstrap the app and customize.
  """
  import sys
  import os
  from os.path import dirname, abspath, join, exists
  path = abspath(join(dirname(__file__), 'eggs'))
  if exists(path):
    for folder in os.listdir(path):
      if not folder.startswith('.'):
        full_path = join(path, folder)
        sys.path.append(full_path)

  # from app.main import main
  # return main
  return lambda: raise Exception('Invalid launch script: please customize main.py')


if __name__ == '__main__':
  boot().main()
