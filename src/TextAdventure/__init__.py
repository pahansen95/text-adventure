"""

The Text Adventure Package

"""
import asyncio, logging
from typing import Any

logger = logging.getLogger(__name__)

async def Bar(bind_addr: Any, quit_event: asyncio.Event):
  logger.critical(f"Hello World! {bind_addr=}")
  await quit_event.wait()
  return
