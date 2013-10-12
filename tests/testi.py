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

import re
import os
import sys
import time
import logging
import subprocess
import platform as _platform
from os.path import expanduser, join
import time
from os.path import expanduser, join, abspath, dirname


## Config

# logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Each item is expanded to [Existing, Content, PATH_TO_TEST] and invoked.
# eg. [['nosetests', '--verbose'], ['python3.3']]
test_runners = [['Python2.7'], ['Python3.3']] #, ['pypy']]

# Special runner for windows, because windows is 'special'
test_runners_win32 = [[sys.executable]]

# How to match a test file
test_patterns = ['.*test.*.py$']
test_excludes = ['.*testi.py$']

# The folder that has all tests in it
test_folders = ['tests']

# The folders to watch for changes
watch_folders = ['src', 'tests']

# Watch any changes on files that match these patterns
watch_patterns = ['.*\.py$']

# Run tests at most this often
minimum_test_interval = 30

# Use growl to notify of test failures
use_growl = True
use_growl_path = '/usr/local/bin/growlnotify'

# growl icons
success_icon = join(expanduser('~'), '.testi', 'success.png')
failure_icon = join(expanduser('~'), '.testi', 'fail.png')

# Use pep8 to check fileS?
use_pep8 = True
use_pep8_path = 'pep8'
use_pep8_flags = ['--ignore', 'E711,E712,E111']


## Impl

class FileWatcher(object):
  """
      Typical usage:

      def process_file(path):
        if re.match(".*\.py", path):
          ... # Do things
          return True

      observer = FileWatcher('.', action=process_file)
      while True:
        observer.poll()
        time.sleep(1)
  """

  def __init__(self, path=os.getcwd(), since=0, action=None):
    self.path = path
    self.since = since
    self.action = action

  def _updates(self):
    """ Yield files that are update/new until action accepts one """
    for root,dirs,files in os.walk(self.path):
      for filename in files:
        path = os.path.join(root, filename)
        stats = os.stat(path)
        if stats.st_mtime > self.since or stats.st_ctime > self.since:
          yield path

  def run(self):
    updated = False
    for path in  self._updates():
      if self.action is not None:
        if self.action(path):
            updated = True
    if updated:
        self.since = time.time()


class TestRunnerFactory(object):
  ''' Creates test runners as required '''

  def __init__(self, runners, patterns, excludes, folders):
    self.runners = runners
    self.patterns = patterns
    self.excludes = excludes
    self.folders = []
    for path in folders:
      fullpath = os.path.abspath(path)
      if os.path.exists(fullpath):
        self.folders.append(fullpath)
      else:
        logging.info('Unable to find requested tests folder: %s' % fullpath)
    if not len(self.folders):
      raise Exception('Invalid test folders: no matches')

  def build(self, last_result, pep_targets):
    ''' Make a new runner '''
    return TestRunner(self.runners, self.patterns, self.excludes, self.folders, last_result, pep_targets)


class Color(object):
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'


class TestRunner(object):
  ''' Find all tests and run them '''
  def __init__(self, runners, patterns, excludes, folders, last_result, pep_targets):
    self.runners = runners
    self.patterns = patterns
    self.excludes = excludes
    self.folders = folders
    self.last_result = last_result
    self.pep_targets = pep_targets

  def run(self):
    ''' Run the tests '''
    for path in self.folders:
      logging.info('Running tests in: {0}'.format(path))
      self.results = {}
      def err(error):
        logging.error(error)
      for root, dirs, files in os.walk(path, onerror=err):
        for fpath in files:
          self.run_test(fpath, root)
    return self.render()

  def run_test(self, filename, path):
    ''' Run a single test file, in the given directory '''
    for pattern in self.patterns:
      if re.match(pattern, filename):

        # Exclude specific targets
        exclude = False
        for e in self.excludes:
          if re.match(e, filename):
            exclude = True
            break
        if exclude:
          continue

        for inv in self.runners:
          os.chdir(path)
          request = []
          count = 0
          failures = 0
          request.extend(inv)
          request.append(filename)
          key = 'cd {0}; {1}'.format(path, ' '.join(request))
          logging.info('Running: {0}'.format(key))
          try:
            output = subprocess.check_output(request, stderr=subprocess.STDOUT)
            result = True
          except subprocess.CalledProcessError as e:
            print(e.output)
            output = e.output
            result = False
          except OSError as e:
            print(e)
            output = str(e)
            result = False

          # Parse output from unittest
          m = re.search('Ran ([0-9]+) test', output, flags=re.MULTILINE)
          if m:
            count += int(m.group(1))
          else:
            count += 1
          if not result:
            m = re.match('failures=([0-9]+)', output, flags=re.MULTILINE)
            if m:
              failures += int(m.group(1))
            else:
              failures += 1

          self.results[key] = (result, count, failures)
        break # Don't match multiple patterns

  def render(self):
    ''' Display the results '''
    total = 0
    passed = 0
    for r in self.results:
      out = self.results[r]
      total += out[1]
      if out[0]:
        passed += out[1]
        logging.info(Color.OKGREEN + 'PASSED' + Color.ENDC + ': {0}/{1} OK: {2}'.format(out[1], out[1], r))
    for r in self.results:
      out = self.results[r]
      if not out[0]:
        logging.info(Color.FAIL + 'FAILED' + Color.ENDC + ': {0}/{1} OK: {2}'.format(out[1] - out[2], out[1], r))
    if passed == total:
      logging.info(Color.OKBLUE + 'PASSED' + Color.ENDC + ': {0} tests passed'.format(passed, total))
    else:
      logging.info(Color.FAIL + 'FAILED' + Color.ENDC + ': {0} / {1} tests passed'.format(passed, total))
    result = passed == total
    self.growl(result, passed, total)
    for target in self.pep_targets:
        self.pep8(target)
    return result

  def growl(self, result, passed, total):
    ''' growl hacks '''
    global use_growl
    global use_growl_path
    global success_icon
    global failure_icon
    if use_growl:
      try:
        command = None
        if not result and result != self.last_result:
          command = [use_growl_path, "-s", "-m", "Test targets: {0} / {1} passed.\nTESTS FAILED.".format(passed, total), "--image", failure_icon]
        elif result and result != self.last_result:
          command = [use_growl_path, "-s", "-m", "Passed {0} test targets\nTests are happy again.".format(passed), "--image", success_icon]
        if command:
          subprocess.check_call(command)
      except subprocess.CalledProcessError as e:
        logging.info('Failed to dispatch growl notification. No growlnotify? %r' % e)

  def pep8(self, target):
    ''' pep8 hacks '''
    global use_pep8
    global use_pep8_path
    global use_pep8_flags
    if use_pep8:
      try:
        command = [use_pep8_path, target]
        command.extend(use_pep8_flags)
        subprocess.check_call(command)
      except subprocess.CalledProcessError as e:
        pass  # pep8 errors cause return code 1
      except OSError as e:
        print('No pep8? Command failed: %r' % e)


class EventHandler(object):
  ''' Handles incoming fs changes '''

  def __init__(self, factory, folders, patterns, min_interval):
    self.factory = factory
    self.folders = watch_folders
    self.patterns = watch_patterns
    self.min_interval = min_interval
    self.last_time = 0
    self.last_notice = 0
    self.run_test = True
    self.last_run_passed = True
    self.pep_targets = []

  def on_any_event(self, path):
    ''' Process tests '''
    for p in self.patterns:
      if re.match(p, path):
        if not self.run_test:
          logging.info('Changed detected in: %r' % path)
          logging.info('Scheduled new test run')
        self.run_test = True
        self.pep_targets.append(path)
        return True

  def poll(self):
    ''' Check if we have a pending event test to run '''
    for o in self.observers:
      o.run()
    if self.run_test:
      delta = time.time() - self.last_time
      if delta > self.min_interval:
        self.last_time = time.time()
        runner = self.factory.build(self.last_run_passed, self.pep_targets)
        self.last_run_passed = runner.run()
        self.last_time = time.time()
        self.run_test = False
        self.pep_targets = []
      else:
        if (time.time() - self.last_notice) > 5:
          logging.info('Next test run in {0:.2f} seconds'.format(self.min_interval - delta))
          self.last_notice = time.time()

  def listen(self):
    ''' Start watchdog '''
    self.observers = []
    for path in self.folders:
      fullpath = os.path.abspath(path)
      if os.path.exists(fullpath):
        logging.info('Watching: %s' % fullpath)
        self.observers.append(FileWatcher(path=fullpath, action=self.on_any_event))
      else:
        logging.info('Unable to find requested watch folder: %s' % fullpath)


class Color(object):
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'


class Platforms(object):
  ''' Stupid simple os detection '''
  WINDOWS="windows"
  CYGWIN="cygwin"
  LINUX="linux"
  MAC="darwin"
  UNKNOWN='wtf'

  @staticmethod
  def platform():
    name = str(_platform.system()).strip().lower()
    if Platforms.WINDOWS in name or Platforms.CYGWIN in name:
      return Platforms.WINDOWS
    elif Platforms.LINUX in name:
      return Platforms.LINUX
    elif Platforms.MAC in name:
      return Platforms.MAC
    else:
      return Platforms.UNKNOWN


if __name__ == '__main__':
  if Platforms.platform() == Platforms.WINDOWS:
    test_runners = test_runners_win32
  factory = TestRunnerFactory(test_runners, test_patterns, test_excludes, test_folders)
  event_handler = EventHandler(factory, watch_folders, watch_patterns, minimum_test_interval)
  event_handler.listen()
  try:
    while True:
      time.sleep(0.5)
      event_handler.poll()
  except KeyboardInterrupt as e:
    pass  # Shutdown
