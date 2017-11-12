"""Tools for making bar plots for intraday finance data.
"""

import tempfile
import os
import subprocess
import logging

import numpy
import pandas
import matplotlib              # Need these lines to prevent emacs hanging or
matplotlib.interactive(False)  # exceptions when using non-GUI virtual machine
matplotlib.use('PS')           # in an interactive session 
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.dates import (
    DateFormatter, MonthLocator, num2date, HourLocator, MinuteLocator)
from matplotlib.finance import candlestick_ohlc

class BSizeParams:

    def __init__(self, bsize):
        self.bsize = bsize
        self.minor_loc = None
        self.major_loc = None
        self.width = 1.0
        self.formatter = DateFormatter('%H:%M')
        self.set_from_bsize(bsize)

    def set_from_bsize(self, bsize):
        func = getattr(self, 'set_from_bsize_' + bsize.lower())
        return func()

    @staticmethod
    def get_width(minutes):
        return minutes*.9*60./4.0/(3600.*6.5)

    def set_from_bsize_15min(self):
        self.width = self.get_width(15)
        self.minor_loc = MinuteLocator()
        self.major_loc = MinuteLocator(byminute=[0,30], interval = 1)
        self.formatter = DateFormatter('%H:%M')

    def set_from_bsize_5min(self):
        self.width = self.get_width(5)
        self.minor_loc = MinuteLocator()
        self.major_loc = MinuteLocator(byminute=[0,15,30,45], interval = 1)
        self.formatter = DateFormatter('%H:%M')

    def set_from_bsize_1min(self):
        self.width = self.get_width(1)
        self.minor_loc = MinuteLocator()
        self.major_loc = MinuteLocator(byminute=[0,15,30,45], interval = 1)
        self.formatter = DateFormatter('%H:%M')        

def plot(orig_data, bsize='1Min', **pltargs):

    data = orig_data.resample(bsize).agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last',
         'volume': 'sum'})
    data['date'] = mdates.date2num(data.index.to_pydatetime())
    bparams = BSizeParams(bsize)

    fig = plt.figure(figsize=(10, 5))
    # axisbg='.9' sets to a very light gray background
    ax = fig.add_axes([0.1, 0.2, 0.85, 0.7], axisbg='.9')
    # customization of the axis
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.tick_params(axis='both', direction='out', width=2, length=8,
                   labelsize=12, pad=8)
    ax.spines['left'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)
    candlestick_ohlc(ax, [tuple(x) for x in data[
        ['date', 'open', 'high', 'low', 'close']].to_records(index=False)],
                     width=bparams.width, **pltargs)
    # FIXME: could do something like the following to plot trades
    #plt.plot([data.index[3]], [41], '^')
    #plt.plot([data.index[4]], [41], 'v')
    ax.xaxis.set_major_formatter(bparams.formatter)
    ax.xaxis.set_major_locator(bparams.major_loc)
    ax.xaxis.set_minor_locator(bparams.minor_loc)
    ax.autoscale_view()
    ax.set_axisbelow(True)
    ax.yaxis.grid(color='.75', linestyle='dashed')
    ax.xaxis.grid(color='.75', linestyle='dashed')        
    plt.setp(plt.gca().get_xticklabels(), rotation=45,
             horizontalalignment='right')
    return fig

def _regr_test_simple_pandas_plot():
    """

>>> import matplotlib              # Need these three lines to prevent emacs 
>>> matplotlib.interactive(False)  # from hanging when using matplotlib
>>> matplotlib.use('PS')           # in an interactive session
>>> import os, datetime, tempfile, pandas
>>> from ox_plot.finance import intraday
>>> infile = os.path.join(os.path.dirname(intraday.__file__), '_test_data.csv')
>>> data = pandas.read_csv(infile, parse_dates=[0], infer_datetime_format=True,
...     index_col=0)
>>> outfile = tempfile.mktemp(suffix='.png')
>>> fig = intraday.plot(data)
>>> fig.savefig(outfile)
>>> os.path.exists(outfile)
True
>>> os.remove(outfile)
>>> os.path.exists(outfile)
False
"""

    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    print ('Finished tests')
