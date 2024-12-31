from __future__ import annotations
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager

import asyncio, aiohttp, logging

logger = logging.getLogger(__name__)

CHUNK_SIZE = int(16 * 1024)

class ElevenLabsError(RuntimeError): ...

def load_api_key_from_env(env: Mapping[str, str]) -> str: return env['ELEVENLABS_API_KEY']

@asynccontextmanager
async def api_session(
  api_key: str,
  base_url: str = 'https://api.elevenlabs.io',
  **kwargs,
) -> AsyncGenerator[aiohttp.ClientSession, None, None]:
  headers = kwargs.pop('headers', {}) | {
    'xi-api-key': api_key,
  }
  session = aiohttp.ClientSession(
    base_url=base_url,
    headers=headers,
    **kwargs,
  )
  try:
    yield session
  finally:
    await session.close()

async def voices(
  session: aiohttp.ClientSession,
) -> dict[str, str]:
  """Get a List of Voices"""
  async with session.get(
    url=f'/v1/voices',
    headers={
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ) as resp:
    if resp.status // 100 != 2:
      err = await resp.json()
      logger.warning(err)
      raise RuntimeError(err)
    return {
      o['name']: o['voice_id']
      for o in (await resp.json())['voices']
    }

async def tts(
  text: str,
  voice_id: str,
  session: aiohttp.ClientSession,
  stream: bool = False,
  chunk_size: int = CHUNK_SIZE,
) -> AsyncGenerator[bytes, None]:
  """Text to Speech"""
  if stream: raise NotImplementedError('Realtime TTS')
  async with session.post(
    url=f'/v1/text-to-speech/{voice_id}',
    headers={
      'Content-Type': 'application/json',
    },
    json={
      'text': text,
      'output_format': 'mp3_44100_192',
    }
  ) as resp:
    if resp.status // 100 != 2:
      err = await resp.json()
      logger.warning(err)
      raise RuntimeError(err)
    async for c in resp.content.iter_chunked(chunk_size): yield c
    
