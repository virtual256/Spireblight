import logging
import asyncio
import sys

from aiohttp import web

from webpage import webpage
from logger import logger

import server, events

from configuration import config

if config.server.debug:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="{asctime} :: {levelname}:{name} - {message}",
        datefmt="(%Y-%m-%d %H:%M:%S)",
        style="{",
    )

logger.info("Starting the bot")

async def main():
    await events.invoke("setup_init")

    tasks = set()

    if not any((config.twitch.enabled, config.discord.enabled)):
        logging.warning("None of the bots are enabled. There will be no commands on the baalorbot page.")

    if config.twitch.enabled:
        tasks.add(server.Twitch_startup())
    if config.discord.enabled:
        tasks.add(server.Discord_startup())

    tasks.add(web._run_app(webpage))

    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except (web.GracefulExit, KeyboardInterrupt):
        pass
    finally:
        logging.debug("Running cleanup...")
        if config.twitch.enabled:
            await server.Twitch_cleanup()
        if config.discord.enabled:
            await server.Discord_cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main()) # TODO: Signal handlers and stuff
    except (web.GracefulExit, KeyboardInterrupt) as e:
        if isinstance(e, web.GracefulExit):
            logging.debug("App closed gracefully")
        else:
            logging.debug(f"Received exception {repr(e)}")
