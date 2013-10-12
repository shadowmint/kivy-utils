'''
So the scene manager is responsible for looking after a specific set of things:

1) The set of UI overlays

2) The eeeeeeee

nstlal cython3) The set of currently rendering content

So broadly, we have a set of ui's which can overlay any content

and a renderer that contains sprites, which can exist under any ui

And the manager looks after transitioning and mainting state between those.

Then on top of that we have a
'''
from kutils.utils import Dynamic


class SceneWidget(object):
  pass


class SceneManager(object):
  """
      Usage:

      def setup(self, m):
        m.shared.renderer = Renderer() # <--- Shared is made available to all widget factories
        m.scenes.loading = LoadingScene()
        m.scenes.game = GameScene()
        m.load(m.scenes.loading)

      def build(self):
        m = SceneManager()
        self.setup(m)
        return m

  """

  def __init__(self):
    """
    """
    self.shared = Dynamic()
    self.scenes = Dynamic()
    self.active = None

  def clear(self, scene):
    """ Clear all loaded scenes """
    pass

  def load(self, scene):
    """ Add a single scene """
    pass

  def unload(self, scene):
    """ Remove a single scene """
    pass

  @property
  def widget(self):
    """ Returns the top level widget for this manager, which changes content when the manager does """
    pass
