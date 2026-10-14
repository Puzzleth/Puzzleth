#!/usr/bin/env python3
"""Puzzleth: a WAIS-style puzzle game. Desktop: ./puzzle   Browser: see tools/build_web.sh"""
import asyncio

import pygame  # noqa: F401  (imported here so the web packager bundles it)

from puzzleth.app import App


async def main():
    await App().run_async()


asyncio.run(main())
