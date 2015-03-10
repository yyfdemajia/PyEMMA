__author__ = 'noe'

import numpy as np
from pyemma.coordinates.io.reader import ChunkedReader
from pyemma.util.log import getLogger

logger = getLogger('DataInMemory')


class DataInMemory(ChunkedReader):

    """
    multi-dimensional multi-trajectory data fully stored in memory
    """

    def __init__(self, _data):
        """

        :param data:
            ndarray of shape (nframe, ndim) or
            list of ndarrays, each of shape (nframe_i, ndim)
        """
        ChunkedReader.__init__(self)

        if isinstance(_data, np.ndarray):
            self.data = [_data]
            self.ntraj = 1
            if _data.ndim == 1:
                self.ndim = np.shape(_data)[0]
            else:
                self.ndim = np.shape(_data)[1]
            self._lengths = [np.shape(_data)[0]]
        elif isinstance(_data, list):
            # TODO: consider having a list of filenames here and lazy load them into memory
            self.data = _data
            self.ntraj = len(_data)
            # ensure all trajs have same dim
            ndims = np.fromiter(([np.shape(_data[i])[1]
                                  for i in xrange(len(_data))]), dtype=int)
            ndim_eq = ndims == np.shape(_data[0][1])
            if not np.all(ndim_eq):
                raise ValueError("input data has different dimensions!"
                                 " Indices not matching: %s"
                                 % np.where(ndim_eq == False))
            self.ndim = ndims[0]

            self._lengths = [np.shape(_data[i])[0] for i in range(len(_data))]
        else:
            raise ValueError('input data is neither an ndarray '
                             'nor a list of ndarrays!')

        self.t = 0
        self.itraj = 0
        self._chunksize = 0

    @property
    def chunksize(self):
        return self._chunksize

    @chunksize.setter
    def chunksize(self, x):
        # chunksize setting is forbidden, since we are operating in memory
        pass

    def number_of_trajectories(self):
        """
        Returns the number of trajectories

        :return:
            number of trajectories
        """
        return self.ntraj

    def trajectory_length(self, itraj):
        """
        Returns the length of trajectory

        :param itraj:
            trajectory index

        :return:
            length of trajectory
        """
        return self._lengths[itraj]

    def trajectory_lengths(self):
        """
        Returns the length of each trajectory

        :return:
            length of each trajectory
        """
        return self._lengths

    def n_frames_total(self):
        """
        Returns the total number of frames, over all trajectories

        :return:
            the total number of frames, over all trajectories
        """
        return np.sum(self._lengths)

    def dimension(self):
        """
        Returns the number of output dimensions

        :return:
        """
        return self.ndim

    def reset(self):
        """Resets the data producer
        """
        self.itraj = 0
        self.t = 0

    def next_chunk(self, lag=0):
        """

        :param lag:
        :return:
        """
        # finished once with all trajectories? so reset the pointer to allow
        # multi-pass
        if self.itraj >= self.ntraj:
            self.reset()

        traj_len = self._lengths[self.itraj]
        traj = self.data[self.itraj]

        # complete trajectory mode
        if self._chunksize == 0:
            if lag == 0:
                X = traj
                self.itraj += 1
                return X
            else:
                X = traj[: -lag]
                Y = traj[lag:traj_len]
                self.itraj += 1
                return (X, Y)

    @staticmethod
    def distance(x, y):
        """

        :param x:
        :param y:
        :return:
        """
        return np.linalg.norm(x - y, 2)

    @staticmethod
    def distances(x, Y):
        """

        :param x: ndarray (n)
        :param y: ndarray (Nxn)
        :return:
        """
        return np.linalg.norm(Y - x, 2, axis=1)