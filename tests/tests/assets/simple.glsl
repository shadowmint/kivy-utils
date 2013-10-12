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
