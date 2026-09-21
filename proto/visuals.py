"""Visible rendering on Mac.

Ursina's default GLSL 130 shaders fail on Darwin. A full-screen camera
overlay with no shader also paints the window black on GL 3.2 core.
Meshes use a color-only GLSL 150 shader (no texture sample).
"""

from __future__ import annotations

from ursina import AmbientLight, DirectionalLight, Entity, Shader, camera, color, window

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

HULL = Shader(
    name="underscore_hull",
    language=Shader.GLSL,
    vertex="""#version 150
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
out vec4 vclip;
void main() {
    vclip = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    gl_Position = vclip;
}
""",
    fragment="""#version 150
uniform vec4 p3d_ColorScale;
uniform float cut_ndc;
uniform float cut_aspect;
in vec4 vclip;
out vec4 fragColor;
void main() {
    if (cut_ndc > 0.02 && vclip.w > 0.08) {
        vec2 ndc = vclip.xy / vclip.w;
        vec2 p = vec2(ndc.x * cut_aspect, ndc.y);
        if (dot(p, p) < cut_ndc * cut_ndc) {
            discard;
        }
    }
    fragColor = p3d_ColorScale;
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
    if map_name == "ship":
        _ambient.color = color.rgb(72, 104, 148)
        _sun.color = color.rgb(186, 214, 255)
    else:
        _ambient.color = color.rgb(168, 196, 224)
        _sun.color = color.rgb(255, 236, 214)


def paint(col):
    """Ursina Color from 0–255 tuple or existing Color."""
    if hasattr(col, "r") and not isinstance(col, tuple):
        return col
    from proto.config import rgb

    return rgb(col)


def solid(col, hull=False, **kwargs):
    """Always-visible mesh: vertex color, no texture sample."""
    kwargs.pop("texture", None)
    kwargs["shader"] = HULL if hull else COLOR
    kwargs["color"] = paint(col)
    e = Entity(**kwargs)
    if hull:
        e.set_shader_input("cut_ndc", 0.0)
        e.set_shader_input("cut_aspect", 1.6)
    return e
