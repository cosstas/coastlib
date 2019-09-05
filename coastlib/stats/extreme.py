# coastlib, a coastal engineering Python library
# Copyright (C), 2019 Georgii Bocharov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import warnings

import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype


class EVA:

    def __init__(self, data, block_size=365.2425):
        """

        Parameters
        ----------
        data : pandas.Series

        block_size : float, optional
            Block size in days. Used to determine number of blocks in data (default=365.2425, one Gregorian year).
            Block size is used to estimate probabilities (return periods for observed data) for all methods
            and to extract extreme events when using the 'Block Maxima' method.
            Return periods have units of <block_size> - e.g. a for block_size=365.2425
            a return period of 100 is the same thing as a 100-year return period.
            Weekly would be <block_size=7> and monthly would be <block_size=365.2425/12>.
        """

        if not isinstance(data, pd.Series):
            raise TypeError(f'<data> must be a pandas.Series object, \'{type(data)}\' was received')

        if not isinstance(data.index, pd.DatetimeIndex):
            raise TypeError(f'index of <data> must pandas.DatetimeIndex object, \'{type(data.index)}\' was received')

        if not is_numeric_dtype(data):
            raise TypeError(f'<data> must be of numeric dtype, \'{data.dtype}\' was received')

        self.data = data
        self.data.sort_index(ascending=True, inplace=True)
        nancount = self.data.isna().sum()
        if nancount > 0:
            self.data.dropna(inplace=True)
            warnings.warn(f'{nancount:d} no-data entries were dropped')

        self.__block_size = block_size

    @property
    def block_size(self):
        """
        See <block_size> paramter in the __init__ method.
        """

        return self.__block_size

    @property
    def number_of_blocks(self):
        return (self.data.index[-1] - self.data.index[0]) / pd.to_timedelta(f'{self.block_size}D')

    def __repr__(self):
        series_length = (self.data.index[-1] - self.data.index[0]).total_seconds() / 60 / 60 / 24

        summary = [
            f'{" " * 35}Extreme Value Analysis Summary',
            f'{"=" * 100}',
            f'Analyzed parameter{self.data.name[:28]:>29}{" " * 6}Series length{series_length:29.2f} days',
        ]

        for i in range(1, int(np.ceil(len(self.data.name) / 28))):
            summary.append(f'{" " * 19}{self.data.name[i * 28:(i + 1) * 28]:<29}')

        summary.extend(
            [
                f'Block size{self.block_size:32.2f} days{" " * 6}Number of blocks{self.number_of_blocks:31.2f}',
                f'{"=" * 100}'
            ]
        )

        return '\n'.join(summary)


if __name__ == '__main__':
    import os
    ds = pd.read_csv(
        os.path.join(os.getcwd(), 'tests', '_common_data', 'wind_speed.csv'),
        index_col=0, parse_dates=True
    )['s'].rename('Wind Speed [kn]')
    self = EVA(data=ds)
