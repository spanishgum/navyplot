import os
import csv
import argparse
import collections
from glob import glob
from datetime import datetime, timedelta
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from tqdm import tqdm

def getdate(s):
    return datetime.strptime(s, '%m/%d/%Y')

def parse_csv(columns):
    date = getdate(columns[1])
    debit = float(columns[3]) if len(columns[3]) else 0
    credit = float(columns[4]) if len(columns[4]) else 0
    return date, debit - credit

def data_from(directory):
    for f in sorted(glob(os.path.join(directory, '*.CSV'))):
        with open(f) as data:
            reader = csv.reader(data)
            next(reader, None)
            for tx in reader:
                yield parse_csv(tx)

def main(args):
    # load data into memory and buffer with a flat line
    dates, debits = map(list, zip(*data_from(args.directory)))
    dates.extend(list(dates[-1] + timedelta(days=i) for i in range(20)))
    debits.extend(list(debits[-1] for _ in range(20)))

    # transform curve into cumsum and sort
    dates = np.array(dates)
    curve = np.array(debits).cumsum() + args.balance
    order = dates.argsort()
    dates = dates[order]
    curve = curve[order]

    # print info
    print('Found {} transactions\n'.format(len(curve)),
          'Dates: {} to {}\n'.format(dates[0].date(), dates[-1].date()),
          'Remaining balance: {:.2f}\n'.format(curve[-1]))

    # style
    bg, fg = 'black', 'cyan'
    fig = plt.figure(facecolor=bg, edgecolor=fg)
    fig.patch.set_facecolor(bg)
    fig.suptitle('Credit balance since {}'.format(dates[0].date()), color=fg)
    ax = plt.subplot(111, facecolor=bg)
    ax.tick_params(axis='y', which='both', color=fg, labelcolor=fg)
    list(map(lambda sid: ax.spines[sid].set_color(fg), ax.spines))
    list(map(lambda label: label.set_color(fg), ax.get_xticklabels()))
    list(map(lambda label: label.set_color(fg), ax.get_yticklabels()))

    plt.gca().xaxis.set_major_formatter(mpl.dates.DateFormatter('%m/%y'))
    plt.gca().xaxis.set_major_locator(mpl.dates.MonthLocator(interval=6))
    plt.ylabel('Balance', color=fg)

    def vlines(_dates, _curve):
        mini, maxi = _curve.argmin(), _curve.argmax()
        minx, maxx = _dates[mini], _dates[maxi]
        minc, maxc = 'lime', 'red'
        plt.axvline(x=minx, color=minc)
        plt.axvline(x=maxx, color=maxc)
        plt.text(minx, _curve[mini], 'minimum {}'.format(minx.date()), color=minc)
        plt.text(maxx, _curve[maxi], 'maximum {}'.format(maxx.date()), color=maxc)

    progress = tqdm(len(curve))
    initial_offset = 10
    p, = ax.plot([], [], 'cyan')
    def update(i, fig, ax):
        _dates = dates[:i + initial_offset]
        _curve = curve[:i + initial_offset]
        vlines(_dates, _curve)
        p.set_data(_dates, _curve)
        p.axes.set_xlim(_dates[0], dates[-1])
        p.axes.set_ylim(_curve.min(), _curve.max())
        progress.update(1)
        return p

    if args.video:
        ani = FuncAnimation(fig, update, fargs=(fig, ax), frames=len(curve) - initial_offset, interval=100, blit=False)
        ani.save(args.output + '.avi', writer=FFMpegWriter(fps=50), savefig_kwargs={'facecolor':bg})
    else:
        plt.plot(dates, curve, color=fg)
        vlines(dates, curve)
        plt.savefig(args.output + '.png', facecolor=fig.get_facecolor())
    progress.update(len(curve))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', '--output', type=str, default='credit_balance', help='output file name')
    ap.add_argument('-d', '--directory', default='data', help='Data directory')
    ap.add_argument('-b', '--balance', type=int, default=12500, help='Starting balance')
    ap.add_argument('-v', '--video', action='store_true', help='Make video instead of still image')
    main(ap.parse_args())
