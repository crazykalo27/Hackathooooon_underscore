"""Bootstrap Ursina and start the game."""

from __future__ import annotations


def run():
    from panda3d.core import loadPrcFileData

    loadPrcFileData("", "win-size 1280 720")
    loadPrcFileData("", "gl-version 3 2")

    from ursina import Ursina, window

    from proto import visuals
    from proto.game import Game

    app = Ursina()
    visuals.apply()
    window.title = "UNDERSCORE"
    window.borderless = False
    window.exit_button.visible = False
    window.fps_counter.enabled = False

    Game()
    app.run()


if __name__ == "__main__":
    run()
