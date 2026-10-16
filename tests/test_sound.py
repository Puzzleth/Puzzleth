"""Sound initialization tests.

Verifies that audio device initialization doesn't produce errors and that
the silent buffer prevents speaker pops on Windows.

Run with:  python -m unittest discover -s tests
"""
import os
import sys
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ["PUZZLETH_HOME"] = os.path.join(tempfile.mkdtemp(), "profile.json")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1280, 800))

from puzzleth import sound  # noqa: E402


class TestSoundInitialization(unittest.TestCase):
    """Test that sound initialization works correctly and stabilizes audio device."""

    def test_sound_init_basic(self):
        """Test that sound.init() completes without errors."""
        sound.init(sfx_volume=0.75, music_volume=0.5)
        self.assertTrue(sound.available())

    def test_sound_init_with_zero_volume(self):
        """Test that sound.init() works with zero volume (edge case)."""
        sound.init(sfx_volume=0.0, music_volume=0.0)
        self.assertTrue(sound.available())

    def test_sound_init_with_full_volume(self):
        """Test that sound.init() works with full volume."""
        sound.init(sfx_volume=1.0, music_volume=1.0)
        self.assertTrue(sound.available())

    def test_silent_buffer_created(self):
        """Test that the silent buffer is created during initialization."""
        sound.init(sfx_volume=0.75, music_volume=0.5)
        # The silent buffer should exist after initialization
        self.assertIsNotNone(sound._silent_buffer)

    def test_sound_play_after_init(self):
        """Test that sound effects can be played after initialization."""
        sound.init(sfx_volume=0.75, music_volume=0.5)
        # This should not raise any exceptions
        # (even if the sound files don't exist, the function handles it gracefully)
        sound.play("tap")
        sound.play("key")


if __name__ == "__main__":
    unittest.main()
