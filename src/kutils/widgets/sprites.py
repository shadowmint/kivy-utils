from __future__ import absolute_import
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.shader import *
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.logger import Logger
from .renderer import Renderer, RMesh


class Sprite(object):
    """ Renderable target

        Notice specifically that Sprite does not look after resolving a
        texture path to a texture instance; look after that manually.

        Sprite objects can contain arbitrary vertex data; to do this
        set the vertices, format, mode and indicies manually.

        If you set any of the high level properties pos, size, uv, etc.
        The low level ones will be overwritten.
    """

    def __init__(self):
        self.pos = [0, 0]
        self.size = [0, 0]
        self.uv = [0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0]
        self.rotation = 0.0
        self.color = [1.0, 1.0, 1.0, 1.0]
        self._mesh = RMesh()
        self._built = False

        # Default mesh data
        self.mode = 'triangles'
        self.indices = [0, 1, 2, 3, 0, 2]
        self.format = [
            ('v_pos', 3, 'float'),
            ('v_color', 4, 'float'),
            ('v_uv', 2, 'float'),
            ('v_rotation', 3, 'float'),
        ]
        self.vertices = [
            10.0, 10.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            10.0, 200.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0,
            200.0, 200.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0,
            200.0, 10.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0,
        ]

    def rebuild(self):
        """ Invoke this to rebuild after setting pos, size, etc.
        """
        xmin = float(self.pos[0] - self.size[0] / 2.0)
        xmax = float(self.pos[0] + self.size[0] / 2.0)
        ymin = float(self.pos[1] - self.size[1] / 2.0)
        ymax = float(self.pos[1] + self.size[1] / 2.0)

        self.vertices = [
            xmin, ymin, 1.0,
            float(self.color[0]), float(self.color[1]), float(self.color[2]), float(self.color[3]),
            float(self.uv[0]), float(self.uv[1]),
            float(self.rotation), float(self.pos[0]), float(self.pos[1]),

            xmin, ymax, 1.0,
            float(self.color[0]), float(self.color[1]), float(self.color[2]), float(self.color[3]),
            float(self.uv[2]), float(self.uv[3]),
            float(self.rotation), float(self.pos[0]), float(self.pos[1]),

            xmax, ymax, 1.0,
            float(self.color[0]), float(self.color[1]), float(self.color[2]), float(self.color[3]),
            float(self.uv[4]), float(self.uv[5]),
            float(self.rotation), float(self.pos[0]), float(self.pos[1]),

            xmax, ymin, 1.0,
            float(self.color[0]), float(self.color[1]), float(self.color[2]), float(self.color[3]),
            float(self.uv[6]), float(self.uv[7]),
            float(self.rotation), float(self.pos[0]), float(self.pos[1]),
        ]

        self.touch()
        self._built = True

    @property
    def invalid(self):
        return self._mesh.invalid

    @property
    def texture(self):
        return self._mesh._texture

    @texture.setter
    def texture(self, value):
        self._mesh._texture = value
        self._mesh.touch()

    @property
    def indices(self):
        return self._mesh._indices

    @indices.setter
    def indices(self, value):
        self._mesh._indices = value
        self._mesh.touch()

    @property
    def format(self):
        return self._mesh._format

    @format.setter
    def format(self, value):
        if not self._built:
            self._mesh._format = value
            self._mesh.touch()
        else:
            raise Exception('Cannot set format after RMesh is built')

    @property
    def vertices(self):
        return self._mesh._vertices

    @vertices.setter
    def vertices(self, value):
        self._mesh._vertices = value
        self._mesh.touch()

    @property
    def mode(self):
        return self._mesh._mode

    @mode.setter
    def mode(self, value):
        self._mesh._mode = value
        self._mesh.touch()

    def touch(self):
        """ Invalidate the held mesh """
        if self._mesh is not None:
            self._mesh.touch()

    @property
    def mesh(self):
        return self._mesh


class Sprites(Widget):
    """ Renders sprites.

        Usage:

            sprites = Sprites(shader='blah.glsl')
            root.add_widget(sprites)

            s = Sprite()
            sprites.targets.append(s)
            sprites.rebuild()
    """

    def __init__(self, shader, renderer=None, **kwargs):
        super(Sprites, self).__init__(**kwargs)
        matrix = lambda: Matrix().view_clip(0, Window.width, 0, Window.height, 1, 100, 0)
        self._renderer = Renderer(shader=shader, matrix=matrix)
        self.add_widget(self._renderer)
        self.targets = []

    def rebuild(self):
        """ Rebuild the sprite data """
        self._renderer.targets = [t.mesh for t in self.targets]
        self._renderer.rebuild()
