from kutils.scene import Scene


class Scene1(Scene):
  def __init__(self):
    super(Scene1, self).__init__()
    from . import widget

    self._wfactory = widget.widget
    self._wpath = widget.__file__

  def rebuild(self, w, data):
    pass
