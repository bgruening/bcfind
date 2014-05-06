"""
Invoke this script to find minimum number of nearest neighbors for a connected graph and to find seeds
for the subsequent step of creating patches of the data
"""

import sys
import numpy as np
import graph_utils
from scipy.spatial import cKDTree
import pandas as pd
import utils
import parameters


def usage():
    print "python " + sys.argv[0] + " data_file outdir"
    print "data_file: path to the markers file"
    print "outdir: where to save minimum nearest neighbors and seeds"

if len(sys.argv) != 3:
    usage()
    sys.exit(1)

data_file = sys.argv[1]
outdir = utils.add_trailing_slash(sys.argv[2])

outdir_seeds = outdir + 'seeds/'
outdir_nn = outdir + 'nn/'

utils.make_dir(outdir)
utils.make_dir(outdir_seeds)
utils.make_dir(outdir_nn)

for folder in xrange(parameters.slurm_jobs):
    utils.make_dir(outdir_seeds + repr(folder))

data_frame = pd.read_csv(data_file)

points_matrix = data_frame.as_matrix([parameters.x_col, parameters.y_col, parameters.z_col])
name = data_frame[parameters.name_col]

data_substacks = utils.points_to_substack(points_matrix, name)

seeds = list()
global_kdtree = cKDTree(points_matrix)
for substack, data in data_substacks.iteritems():
    X = np.vstack(data)
    X = np.float64(X)
    kdtree = cKDTree(X)
    _, index = kdtree.query(np.mean(X, axis=0))
    _, centroid = global_kdtree.query(X[index, :])
    seeds.append(centroid)

n_neighbors = graph_utils.compute_minimum_nearest_neighbors(points_matrix)

with open(outdir_nn + repr(n_neighbors), 'w') as nn_file:
    nn_file.close()

folder = 0
while len(seeds) > 0:
    seed = seeds.pop()
    with open(outdir_seeds + repr(folder) + '/' + repr(seed), 'w') as seed_file:
        seed_file.close()
    folder = (folder + 1) % parameters.slurm_jobs
