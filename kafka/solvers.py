#!/usr/bin/env python
"""Some solvers"""

# KaFKA A fast Kalman filter implementation for raster based datasets.
# Copyright (c) 2017 J Gomez-Dans. All rights reserved.
#
# This file is part of KaFKA.
#
# KaFKA is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KaFKA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with KaFKA.  If not, see <http://www.gnu.org/licenses/>.

from collections import namedtuple
import numpy as np
import scipy.sparse as sp

from utils import  matrix_squeeze, spsolve2, reconstruct_array

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


__author__ = "J Gomez-Dans"
__copyright__ = "Copyright 2017 J Gomez-Dans"
__version__ = "1.0 (09.03.2017)"
__license__ = "GPLv3"
__email__ = "j.gomez-dans@ucl.ac.uk"


def linear_diagonal_solver ( observations, mask, H_matrix,
            x_forecast, P_forecast, R_mat, the_metadata, approx_diagonal=True):
    LOG.info("Squeezing prior covariance...")
                                  n_params=self.n_params)
    P_forecast_prime = np.array(P_forecast.diagonal()).squeeze()[mask.ravel()]
                

    # At this stage, we have a forecast (prior), the observations
    # and the observation operator, so we proceed with the
    # assimilation
    if approx_diagonal:
        # We approximate the inverse matrix by a division assuming
        # P_forecast is diagonal
        LOG.info("Diagonal approximation")
        R_mat_prime = np.array(R_mat.diagonal()).squeeze()
        S = H_matrix.dot(H_matrix.T)*P_forecast_prime + R_mat_prime
        nn1 = R_mat_prime.shape[0]
        LOG.info("About to calculate approx KGain")
        kalman_gain = P_forecast_prime*np.array(H_matrix.diagonal()).squeeze()
        LOG.info("About to calculate approx KGain")
        kalman_gain = kalman_gain/S
    LOG.info("Squeeze x_forecast")
    x_forecast_prime = matrix_squeeze(x_forecast, mask=mask.ravel(),
                                                          n_params=self.n_params)
    LOG.info("Calculating innovations")
    innovations_prime = (observations.ravel()[mask.ravel()] -
                                             H_matrix.dot(x_forecast_prime))
    LOG.info("Calculating analysis state")
    x_analysis_prime = x_forecast_prime + \
                                           kalman_gain*innovations_prime
    LOG.info("Calculating analysis covariance")
    P_analysis_prime = ((sp.eye(kalman_gain.shape[0],
                                                    kalman_gain.shape[0])
                                       - kalman_gain*H_matrix)*P_forecast_prime)
    # Now move
    LOG.info("Inflating analysis state")
    x_analysis = reconstruct_array ( x_analysis_prime, x_forecast,
                                        mask.ravel(), n_params=self.n_params)
    LOG.info("Analsysis smalld diagonal, useful as preconditioner")
    small_diagonal = np.array(P_analysis_prime.diagonal()).squeeze()
    big_diagonal = np.array(P_forecast.diagonal()).squeeze()
    LOG.info("Inflate analysis covariance")
    P_analysis_diag = reconstruct_array(small_diagonal, big_diagonal,
                                    mask, n_params=self.n_params)
    P_analysis = sp.dia_matrix ( (P_analysis_diag, 0),
                                    shape=P_forecast.shape)
    return x_analysis, P_analysis
