from __future__ import annotations
from collections.abc import Mapping
from datetime import datetime
import os, sys, logging, io, pathlib, time, concurrent.futures as conc

import PerfTests as pt

logger = logging.getLogger(__name__)

def main(*argv: str) -> int:
  if not argv:
    print("Usage: python script.py COUNT", file=sys.stderr)
    return 1

  iterations = int(eval(argv[0]))
  logger.info(f'User requested {iterations:,} tests per datastructure')

  # Run all of the Benchmarks
  measurements = pt.Benchmarks.BenchmarkRegistry.run_all_benchmarks(iterations)
  # logger.debug(measurements)
  metrics = pt.Benchmarks.BenchmarkRegistry.calc_all_metrics(measurements)
  # logger.debug(metrics)
  tables = pt.Benchmarks.BenchmarkRegistry.render_all_metrics(metrics)

  ts = time.time()
  now = datetime.fromtimestamp(ts)
  buf = io.StringIO()

  for reg_name, reg in tables.items():
    print(f'### {reg_name} ###', file=buf)
    for cls, table in reg.items():
      print(f'# {cls.__qualname__} #', file=buf)
      print(table, file=buf)
  
  print(buf.getvalue(), file=sys.stdout)
  
  return 0

  ### OLD BELOW
  with conc.ProcessPoolExecutor() as pool:
    benchmark_results = pt.run_benchmarks_and_calculate_metrics(
      count, pool=pool,
    )
  # Print results for each metric type
  ts = time.time()
  now = datetime.fromtimestamp(ts)
  buf = io.StringIO()
  print((
    '### Python Datastructures Performance Tests ###\n\n'
    f'Run Time: {now.ctime()}\n'
    f'Iterations: {count:,}\n'
  ), file=buf)
  for metric_type in pt.MetricType:
    pt.print_metrics_table(benchmark_results, metric_type, file=buf)
    pt.print_relative_performance(benchmark_results, metric_type, file=buf)
  print(buf.getvalue())
  filepath_dir = pathlib.Path(os.environ.get('WORK_CACHE', './'))
  filepath_fmt = 'PerfTests_Results_{name}.txt'
  cur_filepath = filepath_dir / filepath_fmt.format(name=now.strftime("%Y%m%d-%H%M%S"))
  latest_filepath = filepath_dir / filepath_fmt.format(name='latest')
  cur_filepath.write_text(
    buf.getvalue()
  )
  latest_filepath.unlink(missing_ok=True)
  latest_filepath.symlink_to(cur_filepath)

def _cleanup():
  sys.stdout.flush()
  sys.stderr.flush()
if __name__ == '__main__':
  logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'), stream=sys.stderr)
  try: exit(main(*sys.argv[1:]))
  except Exception as exc: logger.critical('Unhandled Exception', exc_info=exc)
  finally: _cleanup()
