"""Visible rendering on Mac.

Ursina's default GLSL 130 shaders fail on Darwin. A full-screen camera
overlay with no shader also paints the window black on GL 3.2 core.
Meshes use a color-only GLSL 150 shader (no texture sample).
"""

from __future__ import annotations

from ursina import AmbientLight, DirectionalLight, Entity, Shader, camera, color, window

_LIT_FRAG = """
vec3 toy_rgb(vec4 tint, vec3 nrm) {
    vec3 n = normalize(nrm);
    vec3 key = normalize(vec3(0.42, 0.86, 0.22));
    float wrap = clamp(dot(n, key) * 0.5 + 0.5, 0.0, 1.0);
    float shade = mix(0.58, 1.08, wrap);
    return tint.rgb * shade;
}
"""

COLOR = Shader(
    name="underscore_color",
    language=Shader.GLSL,
    vertex="""#version 150
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
""",
    fragment="""#version 150
uniform vec4 p3d_ColorScale;
out vec4 fragColor;
void main() {
    fragColor = p3d_ColorScale;
}
""",
)

TOY = Shader(
    name="underscore_toy",
    language=Shader.GLSL,
    vertex="""#version 150
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
out vec3 v_n;
void main() {
    v_n = mat3(p3d_ModelMatrix) * p3d_Normal;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
""",
    fragment="""#version 150
uniform vec4 p3d_ColorScale;
in vec3 v_n;
out vec4 fragColor;
"""
    + _LIT_FRAG
    + """
void main() {
    fragColor = vec4(toy_rgb(p3d_ColorScale, v_n), p3d_ColorScale.a);
}
""",
)

HULL = Shader(
    name="underscore_hull",
    language=Shader.GLSL,
    vertex="""#version 150
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
out vec3 v_world;
out vec3 v_n;
void main() {
    vec4 w = p3d_ModelMatrix * p3d_Vertex;
    v_world = w.xyz;
    v_n = mat3(p3d_ModelMatrix) * p3d_Normal;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
""",
    fragment="""#version 150
uniform vec4 p3d_ColorScale;
uniform vec4 cut_point;
uniform vec4 cut_dir;
uniform float cut_on;
in vec3 v_world;
in vec3 v_n;
out vec4 fragColor;
"""
    + _LIT_FRAG
    + """
void main() {
    if (cut_on > 0.5) {
        vec3 away = v_world - cut_point.xyz;
        if (dot(away, cut_dir.xyz) > 0.2) {
            discard;
        }
    }
    fragColor = vec4(toy_rgb(p3d_ColorScale, v_n), p3d_ColorScale.a);
}
""",
)


_ambient = None
_sun = None


def apply():
    # Do NOT set Entity.default_shader — that breaks Text/font rendering.
    global _ambient, _sun
    from proto.config import FONT, SKY
    from ursina import Text

    Text.default_font = FONT
    Text.default_resolution = 72

    window.color = color.rgb(*SKY)
    window.fullscreen = False
    if hasattr(window, "editor_ui") and window.editor_ui:
        window.editor_ui.enabled = False
    # Ursina's overlay is a 99x99 UI quad. Without a 150 shader it is opaque black.
    if hasattr(camera, "overlay") and camera.overlay:
        camera.overlay.enabled = False
        camera.overlay.scale = 0
        camera.overlay.color = color.clear
    _ambient = AmbientLight(color=color.rgb(72, 104, 148))
    _sun = DirectionalLight(rotation=(42, -28, 0), color=color.rgb(186, 214, 255))


def mood(map_name):
    if _ambient is None:
        return
    _ambient.color = color.rgb(186, 204, 220)
    _sun.color = color.rgb(255, 236, 210)
    _sun.rotation = (48, -32, 0)


def paint(col):
    """Ursina Color from 0–255 tuple or existing Color."""
    if hasattr(col, "r") and not isinstance(col, tuple):
        return col
    from proto.config import rgb

    return rgb(col)


def solid(col, hull=False, **kwargs):
    """World mesh: soft toy light. Hull shells also clip on the camera side."""
    from ursina import Vec4

    kwargs.pop("texture", None)
    kwargs["shader"] = HULL if hull else TOY
    kwargs["color"] = paint(col)
    e = Entity(**kwargs)
    if hull:
        e.set_shader_input("cut_on", 0.0)
        e.set_shader_input("cut_point", Vec4(0, 0, 0, 0))
        e.set_shader_input("cut_dir", Vec4(0, 1, 0, 0))
    return e
