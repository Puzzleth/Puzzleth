#!/usr/bin/env python3
"""Puzzleth: a cognitive puzzle training game. Desktop: ./puzzle   Browser: see tools/build_web.sh"""
import asyncio
import traceback

import pygame  # noqa: F401  (imported here so the web packager bundles it)

from puzzleth import web
from puzzleth.app import App, show_error


async def main():
    try:
        app = App()
    except Exception:
        if not web.IS_WEB:
            raise
        await show_error(traceback.format_exc())   # rather than leave the page blank
        return
    await app.run_async()


asyncio.run(main())
