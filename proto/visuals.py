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


def apply():
    # Do NOT set Entity.default_shader — that breaks Text/font rendering.
    from proto.config import SKY

    window.color = color.rgb(*SKY)
    window.fullscreen = False
    if hasattr(window, "editor_ui") and window.editor_ui:
        window.editor_ui.enabled = False
    # Ursina's overlay is a 99x99 UI quad. Without a 150 shader it is opaque black.
    if hasattr(camera, "overlay") and camera.overlay:
        camera.overlay.enabled = False
        camera.overlay.scale = 0
        camera.overlay.color = color.clear
    AmbientLight(color=color.rgb(230, 226, 220))
    DirectionalLight(rotation=(50, -20, 0), color=color.rgb(255, 248, 236))


def paint(col):
    """Ursina Color from 0–255 tuple or existing Color."""
    if hasattr(col, "r") and not isinstance(col, tuple):
        return col
    from proto.config import rgb

    return rgb(col)


def solid(col, **kwargs):
    """Always-visible mesh: vertex color, no texture sample."""
    kwargs.pop("texture", None)
    kwargs["shader"] = COLOR
    kwargs["color"] = paint(col)
    return Entity(**kwargs)
