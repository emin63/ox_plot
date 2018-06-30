"""Tools for making bar plots for finance data.
"""

import tempfile
import os
import subprocess
import logging

import pandas
import matplotlib              # Need these lines to prevent emacs hanging or
matplotlib.interactive(False)  # exceptions when using non-GUI virtual machine
matplotlib.use('PS')           # in an interactive session 
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MonthLocator
from matplotlib.finance import candlestick_ohlc
from aocks import aocksplot


def prep_plot_data(orig_data, start_end_date=(None, None), mode=None):
    """Prepare pandas DataFrame for plotting.

    :arg orig_data:      Original pandas DataFrame.

    :arg start_end_date: Option tuple of start, end dates.

    :arg mode=None:      Optional string indicating data mode (see
                         infer_data_mode for more info).  

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    :returns:   A DataFrame with Date, Open, Close, High, Low data suitable
                for plotting. This is meant as a helper function.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:    Helper for simple_pandas_plot.

    """

    mode = mode if mode is not None else infer_data_mode(orig_data)
    data = orig_data.copy(deep=True)
    data = data.truncate(*start_end_date)
    if mode == 'pion':
        renames=dict([(item, (item[0].upper() + item[1:]))
                      for item in data if item != 'event_date'])
        data.rename(columns=renames, inplace=True)
        dateField = 'event_date'
    else:
        dateField = 'date'

    # drop the date index from the dateframe
    data.reset_index(inplace = True)

    # convert the datetime64 column in the dataframe to 'float days'
    if mode == 'pandas':
        data.date = mdates.date2num(getattr(data, dateField).dt.to_pydatetime())
    else:
        assert mode == 'pion'
        data['date'] = [thing.toordinal() for thing in getattr(data, dateField)]

    return data


def simple_pandas_plot(orig_data, output_file=None, mainTitle='', 
                       start_end_date = (None, None),
                       pltargs=(('width', .3), ('colorup', 'b'))):
    """Plot pandas DataFrame

    :arg orig_data: A pandas DataFrame containing open, high, low, close,
                    and volume data with a date.

    :arg mainTitle='':  Optional main title for the plot.      

    :arg start_end_date: Option tuple of start, end dates.

    :arg pltargs=:  Options such that dict(pltargs) can be passed to
                    candlestick_ohlc. Example keys include 'width'
                    and 'colorup'.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    :returns:   The matplotlib figure object for the plot.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:    Take pandas data and make a nice stock plot.

    """
    data = prep_plot_data(orig_data, start_end_date, mode='pandas')
    
    fig = plt.figure(figsize=(8,6))
    gs = matplotlib.gridspec.GridSpec(2,1, height_ratios=[4,1])
    ax1 = fig.add_subplot(gs[0])        
    ax_vol = fig.add_subplot(gs[1], sharex=ax1)
    axes = [ax1, ax_vol]        

    plt.setp(ax1.get_xticklabels(), visible=False)    
    plt.setp(ax_vol.get_xticklabels(), visible=True)

    plt.setp(axes, title='')
    fig.suptitle(mainTitle, size=20)

    majorFormatter = DateFormatter('%b %y')  # e.g., Jan 12

    fig.subplots_adjust(bottom=0.2)
    ax1.xaxis.set_major_locator(MonthLocator([3,6,9,12]))
    ax1.xaxis.set_major_formatter(majorFormatter)
    candlestick_ohlc(ax1, [tuple(x) for x in data[
        ['date', 'open', 'high', 'low', 'close']].to_records(index=False)],
                     **dict(pltargs))
    ax1.grid(True)
    ax1.xaxis_date()
    ax1.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45,
             horizontalalignment='right')

    # make bar plots and color differently depending on up/down for the day
    pos = list((data['open']-data['close'])<=0)
    neg = list((data['open']-data['close'])>0)
#    ax_vol.bar(list(data['date'][pos]),list(data['volume'][pos]),
#            color='b',width=.1,align='center',edgecolor='none')
#    ax_vol.bar(list(data['date'][neg]),list(data['volume'][neg]),
#            color='r',width=.1,align='center',edgecolor='none')

    #for my_ax in axes:
    #    clean_axis(my_ax) #FIXME
    
    if output_file:
        fig.savefig(output_file)

    return fig


def _regr_test_simple_pandas_plot():
    """

>>> import matplotlib              # Need these three lines to prevent emacs 
>>> matplotlib.interactive(False)  # from hanging when using matplotlib
>>> matplotlib.use('PS')           # in an interactive session
>>> import os, datetime, tempfile, pandas
>>> from ox_plot.finance import barplot
>>> start, end = datetime.date(2014, 6, 1), datetime.date(2015, 6, 30)
>>> infile = os.path.join(os.path.dirname(barplot.__file__), '_test_data.csv')
>>> data = pandas.read_csv(infile, parse_dates=[0], infer_datetime_format=True,
...     index_col=0)
>>> outfile = tempfile.mktemp(suffix='.png')
>>> plot = barplot.simple_pandas_plot(data, output_file=outfile,
... mainTitle='Testing')
>>> plot.savefig(outfile)
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
