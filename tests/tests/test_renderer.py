from __future__ import absolute_import
import unittest

# Test imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Kivy setup
from kivy.config import Config
Config.set('graphics', 'width', '200')
Config.set('graphics', 'height', '200')

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
from kutils.widgets.sprites import Sprites, Sprite
from random import random
import os


def resolve(*args):
  rtn = os.path.abspath(os.path.join(os.getcwd(), 'assets', *args))
  print rtn
  return rtn

class RendererApp(App):

    SPRITE_COUNT = 100

    def __init__(self, **kwargs):
        super(RendererApp, self).__init__(**kwargs)
        self.create_sprites()
        Clock.schedule_interval(self.update_sprites, 1.0 / 25.0)
        Clock.schedule_once(self.shutdown, 5.0)

    def build(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.floatlayout import FloatLayout
        from kivy.uix.label import Label

        root = FloatLayout()
        ui = BoxLayout(orientation='vertical')
        root.add_widget(self.sprites)
        self.sprites.rebuild()

        root.add_widget(ui)
        ui.add_widget(Label(text="Hello World 1"))
        ui.add_widget(Label(text="Hello World 2"))
        return root

    def create_sprites(self):
        self.sprites = Sprites(shader=resolve('simple.glsl'))
        self.texture = Image(resolve('texture.png'))
        for i in range(self.SPRITE_COUNT):
            s = Sprite()
            s.texture = self.texture.texture
            s.pos = [100, 100]
            s.size = [10, 10]
            s.color = [1.0, 1.0, 1.0, 1.0]
            s.rebuild()
            self.sprites.targets.append(s)

    def update_sprites(self, *largs):
        for i in range(self.SPRITE_COUNT):
            self.sprites.targets[i].pos[0] += 10 * (random() - 0.5)
            self.sprites.targets[i].pos[1] += 10 * (random() - 0.5)
            for j in range(4):
                self.sprites.targets[i].color[j] += 0.01 * (random() - 0.5)
                if self.sprites.targets[i].color[j] < 0.0:
                    self.sprites.targets[i].color[j] = 0
                if self.sprites.targets[i].color[j] > 1.0:
                    self.sprites.targets[i].color[j] = 1.0
            self.sprites.targets[i].rotation += 0.05 * random()
            self.sprites.targets[i].rebuild()
        self.sprites.rebuild()

    def shutdown(self, *largs):
        self.stop()


class Tests(unittest.TestCase):
  def test_renderer(self):
    RendererApp().run()


if __name__ == '__main__':
  unittest.main()
