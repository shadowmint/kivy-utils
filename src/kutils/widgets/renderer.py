from __future__ import absolute_import
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.core.window import Window
from kivy.graphics.transformation import Matrix
from kivy.graphics.shader import *
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.logger import Logger



class RMesh(object):
    """ A renderer mesh, containing all the rendering information
        required to render one mesh with one associated texture.

        Note that the texture here is NOT an atlas url or path,
        it must be a kivy.core.image.Image.texture.
    """

    def __init__(self, format=None, indices=None, vertices=None, texture=None, mode=None):
        """ Create a mesh.

            Notice that although you can patch the containing mesh by
            changing the ._vertices, etc. you cannot change the vertex
            buffer format; if you do it will be ignored regardless of
            calling rebuild().

            :format: The vertex format, eg. [('v_pos', 3, 'float'], ...]
            :indices: The vertex index values.
            :vertices: The actual vertex data, according to format.
            :texture: A texture reference.
            :mode: A valid rendering mode, eg. triangles, lines, etc.
        """
        self._format = format
        self._indices = indices
        self._vertices = vertices
        self._texture = texture
        self._mode = mode
        self._invalid = True
        self._mesh = None

    def touch(self):
        self._invalid = True

    @property
    def invalid(self):
        return self._invalid

    def rebuild(self):
        if self._invalid:
            if self._mesh is None:
                self._mesh = Mesh(
                    vertices=self._vertices,
                    indices=self._indices,
                    fmt=self._format,
                    mode=self._mode,
                    texture=self._texture,
                )
            else:
                self._mesh.vertices = self._vertices
                self._mesh.indices = self._indices
                self._mesh.mode = self._mode
                self._mesh.texture = self._texture
            self._invalid = False
            #Logger.info(str(self._vertices))
            #App#Logger.info(str(self._indices))
            #Logger.info(str(self._format))
            #Logger.info(str(self._mode))
            #Logger.info(str(self._texture))

class Renderer(Widget):
    """ Performs basic rendering of vertex data using a shader.

        Attached at the bottom of this file is a sample default shader;
        copy it out to the appropriate assets location and refer to it
        when using the renderer.

        The matrix param for this render should be a lambda to invoke
        once the window is open to generate a perspective matrix.

        Usage:

            matrix = lambda: Matrix().view_clip(0, Window.width, 0, Window.height, 1, 100, 0)
            r = Renderer(shader='source_file.glsl', matrix=matrix)
            r.targets.append(mesh)
            r.rebuild()
            parent.add_widget(r)
    """

    def __init__(self, shader, matrix, **kwargs):
        self.canvas = RenderContext()
        self.canvas.shader.source = shader
        super(Renderer, self).__init__(**kwargs)
        self.targets = []
        self.matrix = matrix
        self.rebuild()
        Clock.schedule_once(self.update_glsl, 1.0 / 60.0)

    def update_glsl(self, *largs):
        self.canvas['projection_mat'] = self.matrix()

    def invalid(self):
        return any(filter(lambda x: x.invalid, self.targets))

    def rebuild(self):
        if self.invalid:
            with self.canvas:
                PushMatrix()
                UpdateNormalMatrix()
                for t in self.targets:
                    if t.invalid:
                        t.rebuild()
                PopMatrix()


SHADER_SOURCE = """
---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3 v_pos;
attribute vec4 v_color;
attribute vec2 v_uv;
attribute vec3 v_rotation; // [angle, x, y]


uniform mat4 modelview_mat;
uniform mat4 projection_mat;

varying vec4 frag_color;
varying vec2 uv_vec;
varying mat4 v_rotationMatrix;

void main (void) {

    float cos = cos(v_rotation[0]);
    float sin = sin(v_rotation[0]);

    mat2 trans_rotate = mat2(
      cos, -sin,
      sin, cos
    );

    vec2 rotated = trans_rotate * vec2(v_pos[0] - v_rotation[1], v_pos[1] - v_rotation[2]);
    gl_Position = projection_mat * modelview_mat * vec4(rotated[0] + v_rotation[1], rotated[1] + v_rotation[2], 1.0, 1.0);
    frag_color = v_color;
    uv_vec = v_uv;
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

varying vec4 frag_color;
varying vec2 uv_vec;

uniform sampler2D tex;

void main (void){
    vec4 color = texture2D(tex, uv_vec) * frag_color;
    gl_FragColor = color;
}
"""
