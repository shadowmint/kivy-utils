import traceback
from kivy.logger import Logger


class DependencyError(Exception):
    """ To prevent mass dependency hell, individual utilities will load modules
        on demand; raise this error if such an import fails.

        Note that this has implementations for using packagers like pyinstaller,
        that attempt to automatically track dependencies; use buildout to overcome
        this limitation.
    """
    def __init__(self, package, e):
        super(DependencyError, self).__init__('Required dependency "{0}" is not installed'.format(package))
        trace = traceback.format_exc()
        Logger.info(trace)
        Logger.info('Dependency failure: {0}'.format(str(e)))
