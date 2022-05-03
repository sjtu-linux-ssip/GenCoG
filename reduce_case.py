import os
import re
from argparse import Namespace, ArgumentParser

import numpy as np

from typefuzz.debug import ErrorKind, CompileReducer, RunReducer, ComputeReducer

options = Namespace()


def parse_args():
    global options
    p = ArgumentParser()
    p.add_argument('-d', '--directory', type=str, help='Directory for storing error cases.')
    options = p.parse_args()


def main():
    level_matcher = re.compile('opt_level=(\\d)')
    for case_id in sorted(os.listdir(options.directory), key=lambda s: int(s)):
        case_path = os.path.join(options.directory, case_id)
        with open(os.path.join(case_path, 'error.txt'), 'r') as f:
            opt_str = f.readline()
            err = f.read()
        opt_level = int(next(level_matcher.finditer(opt_str)).groups()[0])
        with open(os.path.join(case_path, 'code.txt'), 'r') as f:
            code = f.read()
        for kind, reduce_cls in zip(
                [ErrorKind.COMPILE, ErrorKind.RUN, ErrorKind.COMPUTE],
                [CompileReducer, RunReducer, ComputeReducer]
        ):
            # Check error kind
            if not os.path.exists(os.path.join(case_path, kind.name)):
                continue
            print(f'Reducing case {case_id}:')

            # Possibly load inputs and parameters
            inputs_path = os.path.join(case_path, 'inputs.npz')
            inputs = None
            if os.path.exists(inputs_path):
                with np.load(inputs_path) as f:
                    inputs = dict(f.items())
            params_path = os.path.join(case_path, 'params.npz')
            params = None
            if os.path.exists(params_path):
                with np.load(params_path) as f:
                    params = dict(f.items())

            # Reduce code
            reducer = reduce_cls(code, err, opt_level, inputs=inputs, params=params)
            reduced_code, extra = reducer.reduce()
            with open(os.path.join(case_path, 'code-reduced.txt'), 'w') as f:
                f.write(reduced_code)
            if len(extra) > 0:
                with open(os.path.join(case_path, 'extra.txt'), 'w') as f:
                    f.write(extra)


if __name__ == '__main__':
    parse_args()
    main()
