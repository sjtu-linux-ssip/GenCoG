import time
from argparse import Namespace, ArgumentParser
from sys import stdout

import numpy as np
from numpy.random import Generator, PCG64
from tqdm import tqdm

from typefuzz.config import muffin_ops
from typefuzz.graph import GraphGenerator
from typefuzz.metric.div import EdgeDiversity, VertexDiversity
from typefuzz.spec import OpRegistry, TypeSpec

options = Namespace()


def _parse_args():
    global options
    p = ArgumentParser()
    p.add_argument('-l', '--limit', type=int, help='Limit on total number of operations.')
    p.add_argument('-s', '--seed', type=int, default=42, help='Random seed of graph generator.')
    options = p.parse_args()


def main():
    # Initialization
    TypeSpec.for_graph = True
    opr_limit = options.limit
    rng = Generator(PCG64(seed=options.seed))
    ops = [OpRegistry.get(name) for name in muffin_ops]
    gen = GraphGenerator(ops, rng)
    vert_div = VertexDiversity(ops)
    edge_div = EdgeDiversity(ops)

    # Generation loop
    opr_count = 0
    progress = tqdm(total=opr_limit, file=stdout)
    div_record = []
    record_file = 'out/typefuzz-{}.txt'.format(time.strftime("%Y%m%d-%H%M%S", time.localtime()))
    loop_idx = 0
    while True:
        # Generate graph
        graph = gen.generate()
        vert_div.evaluate(graph)
        edge_div.evaluate(graph)

        # Count operations
        opr_num = len(graph.oprs_)
        opr_count += opr_num
        progress.update(n=opr_num)

        # Write record to file
        div_record.append([opr_count, vert_div.result, edge_div.result])
        if loop_idx % 10 == 0:
            # noinspection PyTypeChecker
            np.savetxt(record_file, np.array(div_record), fmt='%.4f')

        # Stop if operation limit is reached
        if opr_count >= opr_limit:
            # noinspection PyTypeChecker
            np.savetxt(record_file, np.array(div_record), fmt='%.4f')
            break
        loop_idx += 1

    # Output diversity
    np.set_printoptions(precision=3)
    print('Operator detail:', vert_div.op_div, sep='\n')
    print('Vertex diversity:', vert_div.result)
    print('Edge diversity:', edge_div.result)


if __name__ == '__main__':
    _parse_args()
    main()

"""
penalty=4
Operator detail:
[0.237 0.229 0.147 0.146 0.142 0.14  0.145 0.048 0.245 0.235 0.219 0.239
 0.231 0.232 0.233 0.228 0.252 0.032 0.007 0.028 0.006 0.236 0.036 0.008
 0.231 0.035 0.007 0.661 0.315 0.087 0.63  0.312 0.095 0.146 0.046 0.326
 0.131 1.    0.244]
Vertex diversity: 0.20436015676193436
Edge diversity: 0.7928994082840237
"""
