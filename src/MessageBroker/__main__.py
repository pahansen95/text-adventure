from __future__ import annotations
from hashlib import md5
from contextlib import contextmanager
import os, sys, asyncio, logging

from MessageBroker import MessageBroker, AddrPath

logger = logging.getLogger(__name__)

async def peer_leader(broker: MessageBroker):
  PEER_ID = md5(b'leader').hexdigest()
  
  ### Connect to the Broker

  logger.info(f'Peer {PEER_ID}: Connecting to Broker')
  peer_session = await broker.connect(
    peer_id=PEER_ID,
  )

  ### Setup the Topics the peer will publish & subscribe on

  logger.info(f'Peer {PEER_ID}: Publishing to `/Foo/Bar/1`')
  await peer_session.publish(
    '/Foo/Bar/1'
  )

  ### Exchange Messages with a Peer

  logger.info(f'Peer {PEER_ID}: Broadcasting Message on `/Foo/Bar/1`')
  await peer_session.put(
    topic='/Foo/Bar/1',
    dst=AddrPath.broadcast(),
    payload=b'Hello, World!',
  )
  logger.info(f'Peer {PEER_ID}: Message Broadcasted on `/Foo/Bar/1`')

  ### Teardown the Client

  logger.info(f'Peer {PEER_ID}: Disconnecting from Broker')
  await peer_session.disconnect()

async def peer_follower(broker: MessageBroker, idx: int):
  PEER_ID = md5(f'follower_{idx}'.encode()).hexdigest()

  ### Connect to the Broker

  logger.info(f'Peer {PEER_ID}: Connecting to Broker')
  peer_session = await broker.connect(
    peer_id=PEER_ID,
  )

  ### Setup the Topics the peer will publish & subscribe on

  logger.info(f'Peer {PEER_ID}: Subscribing to `/Foo/Bar/1`')
  await peer_session.subscribe(
    '/Foo/Bar/1',
  )

  ### Exchange Messages with a Peer

  logger.info(f'Peer {PEER_ID}: Receiving Message on `/Foo/Bar/1`')
  msg = await peer_session.get(
    topic='/Foo/Bar/1',
  )
  logger.info(f'Peer {PEER_ID}: Message Recieved on `/Foo/Bar/1`: {msg}')
  assert msg.payload == b'Hello, World!'

  ### Teardown the Client

  logger.info(f'Peer {PEER_ID}: Disconnecting from Broker')
  await peer_session.disconnect()

async def broker_cloop(broker: MessageBroker):
  """Conducts Evaluation of the Broker"""
  await broker.topics._wait_for_topic('/Foo/Bar/1')
  assert '/Foo/Bar/1' in broker.topics._gens
  listener = broker.topics._gens['/Foo/Bar/1']['listener']
  router = broker.topics._gens['/Foo/Bar/1']['router']

  # Initialize the Broker
  await asyncio.gather(*map(
    anext,
    (
      listener,
      router
    )
  ))

  # Evaluate all Broker Components
  while True:
    # Evaluate Listeners
    await anext(listener)
    # Evaluate Routing
    await anext(router)

async def main(argv: list[str], env: dict[str, str]) -> int:

  broker = MessageBroker(
    # ...
  )
  broker_eval = asyncio.create_task(broker_cloop(broker))
  async with asyncio.TaskGroup() as tg:
    for idx in range(10): tg.create_task(peer_follower(broker, idx))
    tg.create_task(peer_leader(broker))
  broker_eval.cancel()
  try: await broker_eval
  except asyncio.CancelledError: pass

if __name__ == '__main__':

  @contextmanager
  def cli_resources():
    try:
      log_level = os.environ.get('LOG_LEVEL', 'INFO')
      logging.basicConfig(stream=sys.stderr, level=log_level)
      yield log_level.upper() in ('DEBUG', 'TRACE')
    finally:
      logging.shutdown()
      sys.stderr.flush()
      sys.stdout.flush()

  RC = 127
  with cli_resources() as debug:
    try: RC = asyncio.run(main(sys.argv[1:], dict(os.environ)), debug=debug)
    except: logger.critical('Unhandled Exception', exc_info=True)
  raise SystemExit(RC)
