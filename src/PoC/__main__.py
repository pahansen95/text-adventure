"""

The Proof of Concept Text Adventure Game

"""
from __future__ import annotations
import logging, sys, os, asyncio, traceback, threading, signal, types
from typing import NoReturn, Literal
from collections.abc import Iterable, MappingView, Coroutine, Callable
from collections import deque

### Package Imports
import PoC
###

logger = logging.getLogger(__name__)

async def run_game() -> retry_action_t:
  await PoC.run_game_engine()
  return 'stop'

### Runtime Boilerplate ###

retry_action_t = Literal['restart', 'stop']
TASK_RETRY_ACTIONS = { 'restart', 'stop' }

async def loop_entrypoint(
  teardown: asyncio.Event,
) -> None:
  """The Entrypoint of the AsyncIO Loop"""
  logger.debug(f"Entering Event Loop Entry Point")

  # ### NOTE: Debugging
  # await teardown.wait()
  # logger.debug('Loop Entrypoint Returning')
  # return
  # ###
  
  ### Schedule that Tasks
  enabled_tasks: dict[str, Callable[[], Coroutine]] = {
    '_teardown': lambda: teardown.wait(),
    'RunGame': lambda: run_game(), # TODO: Make Configurable
  }
  disabled_tasks: dict[str, Callable[[], Coroutine]] = {}
  inflight_tasks: dict[str, asyncio.Task] = {}
  def _cancel_tasks(tasks: dict[str, asyncio.Task]):
    for n, t in {
      n: t for n, t in tasks.items()
      if not (t.done() or t.cancelling())
    }.items():
      logger.debug(f'Cancelling Task {n}')
      t.cancel()
  async def _teardown():
    nonlocal disabled_tasks, enabled_tasks
    disabled_tasks |= enabled_tasks
    enabled_tasks = {}
    _cancel_tasks(inflight_tasks)
    if len(inflight_tasks.values()) > 0: await asyncio.wait(inflight_tasks.values()) # Wait for all tasks to complete
    panic = False
    for n, t in inflight_tasks.items():
      if (exc := t.exception()) is not None and not isinstance(exc, asyncio.CancelledError):
        panic = True
        logger.critical(f'Unhandled Error raised by Task {n}', exc_info=exc)
    if panic: raise RuntimeError('Unhandled Task Exceptions encountered when tearing down Event Loop')
    raise asyncio.CancelledError('Loop Entrypoint Cancelled')

  while len(enabled_tasks) > 0:
    ### Schedule the Tasks
    for name, factory in enabled_tasks.items():
      if name not in inflight_tasks:
        logger.debug(f'Scheduling Task {name}')
        inflight_tasks[name] = asyncio.create_task(
          factory(), name=name,
        )
    ### Wait for any task to complete
    logger.debug('Waiting for any scheduled task to return')
    done, _ = await asyncio.wait(inflight_tasks.values(), return_when=asyncio.FIRST_COMPLETED)
    for t in done:
      name = t.get_name()
      logger.debug(f'Task {name} returned')
      assert t.done()
      _t = inflight_tasks.pop(name)
      assert _t is t
      ### Handle the Task State
      if name == '_teardown': await _teardown()
      elif (e := t.exception()) is not None:
        logger.error(
          f'Task {name} raised an unhandled exception...\n',
          exc_info=e,
        )
        logger.info(f'Tearing down event loop in response to the unhandled error raised by Task {name}')
        await _teardown()
      else:
        assert name != '_teardown'
        if t.cancelled():
          logger.debug(f'Task {name} was cancelled')
          retry_action: retry_action_t = 'stop'
        else:
          logger.debug(f'Task {name} completed')
          retry_action: retry_action_t = t.result()
          assert retry_action in TASK_RETRY_ACTIONS
        if retry_action in {'stop', }:
          logger.debug(f'Disabling Task `{name}` b/c it returned: {retry_action}')
          disabled_tasks[name] = enabled_tasks.pop(name)
        elif retry_action in {'restart', }:
          logger.debug(f'Restarting Task `{name}` b/c it returned: {retry_action}')
        else:
          raise NotImplementedError(f'Retry Action: {retry_action}')

def main(argv: Iterable[str], env: MappingView[str, str]) -> int:
  """The Main Function"""
  args = deque(a for a in argv if not a.startswith('-'))
  logger.debug(f'{args=}')
  flags = dict(_parse_flag(f) for f in argv if f.startswith('-'))
  logger.debug(f'{flags=}')

  ### Parse Flags
  # def _parse_bind(bind: str) -> tuple[str, int]:
  #   try: addr, port = bind.split(':', maxsplit=1)
  #   except ValueError: addr = bind
  #   if not addr: addr = '127.0.0.1' # If user doesn't specify an address, then assume loopback
  #   if not port: port = '8080' # If user doesn't specify a port, then assume 8080
  #   return addr, int(port, base=10)

  ### Set the Kwargs for the AIO Loop's Entrypoint
  loop_kwargs = {
    # 'bind_addr': _parse_bind(flags.get('bind', '127.0.0.1:50080')) # Set a default
  }

  ### Setup the AsyncIO Loop in another thread
  logger.debug('Setting Up AIO Loop')
  aio_teardown = asyncio.Event()
  aio_loop: asyncio.BaseEventLoop | None = None
  thread_state = { 'status': 'pending' }
  def aio_thread_entrypoint():
    nonlocal thread_state, aio_loop
    thread_state |= { 'status': 'running' }
    logger.debug('Spawning Event Loop')
    import uvloop; asyncio.set_event_loop_policy(uvloop.EventLoopPolicy()) # Register uvloop as the Event Loop Provider
    aio_loop = asyncio.new_event_loop()
    try:
      logger.debug('Running Event Loop Entrypoint')
      aio_loop.run_until_complete(
        loop_entrypoint(
          **loop_kwargs,
          teardown=aio_teardown,
        ),
      )
      logger.debug('Event Loop Entrypoint Completed')
      thread_state |= { 'status': 'completed' }
    except asyncio.CancelledError:
      logger.debug('Event Loop Entrypoint was Cancelled')
      thread_state |= { 'status': 'cancelled' }
    except Exception as e:
      if isinstance(e, RuntimeError) and str(e) == 'Event loop stopped before Future completed.':
        logger.warning('The Event Loop was forcefully stopped')
        thread_state |= { 'status': 'killed' }
      else:
        logger.debug('Event Loop Entrypoint unexpectedly Failed')
        thread_state |= {
          'status': 'failed',
          'exc_info': sys.exc_info(),
        }
    finally:
      logger.debug('Closing Event Loop')
      aio_loop.close()
    logger.debug('Returning from AIO Thread Entrypoint')
  aio_thread = threading.Thread(
    target=aio_thread_entrypoint,
    daemon=False, # NOTE: Dameon Threads are forcibley killed; we need to cleanly exit so we can cleanup OS Resources
  )

  ### Setup Signal Handling
  logger.debug('Setting up Signal Handling')
  quit_sig_occurance = 0
  def quit_signal_handler(sig_num: int, stack_frame: None | types.FrameType):
    nonlocal quit_sig_occurance
    logger.debug(f'Quit Signal `{signal.Signals(sig_num).name}` recieved')
    quit_sig_occurance += 1
    assert quit_sig_occurance > 0
    if quit_sig_occurance == 1: # Tell the AIO Loop to Quit
      logger.info('Informing the Event Loop it needs to quit')
      if aio_loop is None: raise NotImplementedError('A Signal to Quit was recieved before the Event Loop was Spawned')
      else: aio_loop.call_soon_threadsafe(aio_teardown.set)
    elif quit_sig_occurance == 2: # Stop the Loop
      logger.warning('Forcing the Event Loop to stop')
      assert quit_sig_occurance > 1
      aio_loop.stop()
    else:
      logger.warning('Event Loop already stopped; waiting for it to complete current iteration')

  for sig in (
    signal.SIGTERM, signal.SIGQUIT, signal.SIGINT,
  ): signal.signal(sig, quit_signal_handler)

  ### Spawn the Thread & Wait for completion
  logger.debug('Starting the AIO Event Loop Thread')
  aio_thread.start()
  logger.debug('Waiting for the AIO Event Loop Thread to Complete')
  aio_thread.join()
  assert not aio_thread.is_alive()
  assert thread_state['status'] in ('completed', 'cancelled', 'killed', 'failed'), thread_state['status']

  logger.debug('Evaluating AIO Event Loop Thread State')
  if thread_state['status'] == 'failed':
    rc = 2
    logger.critical(
      '!!! The AIO Loop Raised an Unhandled Exception !!!',
      exc_info=thread_state['exc_info'],
    )
  else:
    rc = 0
    if thread_state['status'] == 'killed': logger.warning('The AIO Loop was Killed')
    elif thread_state['status'] == 'cancelled': logger.warning('The AIO Loop was Cancelled')
    elif thread_state['status'] == 'completed': logger.info('The AIO Loop Completed Execution')
    else: assert False, 'Never should have come here'
  
  logger.debug('Main Thread Returning')
  return rc

def _parse_flag(flag: str) -> tuple[str, str]:
  assert flag.startswith('-')
  if '=' in flag: return flag.lstrip('-').split('=', maxsplit=1)
  else: return flag.lstrip('-'), True

def setup():
  try: logging.basicConfig(stream=sys.stderr, level=os.environ.get('LOG_LEVEL', 'WARNING').upper())
  except:
    import traceback as tb
    print('Failed To setup Logging...\n' + tb.format_exc())
    raise

def error() -> int:
  logger.exception('Unhandled Error')
  return 2

def cleanup(exit_code: int) -> NoReturn:
  logging.shutdown()
  sys.stdout.flush()
  sys.stderr.flush()
  exit(exit_code)

if __name__ == '__main__':
  ### Setup ###
  try: setup()
  except: exit(127) # NOTE: Setup should handle it's own errors
  ### Run ###
  try: RC = main(sys.argv[1:], os.environ)
  except: RC = error()
  ### Cleanup ###
  finally: cleanup(RC)
