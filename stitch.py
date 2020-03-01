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
    fig.suptitle('Credit balance, {} to {}'.format(dates[0].date(), dates[-1].date()), color=fg)
    ax = plt.subplot(111, facecolor=bg)
    ax.tick_params(axis='y', which='both', color=fg, labelcolor=fg)
    list(map(lambda sid: ax.spines[sid].set_color(fg), ax.spines))
    list(map(lambda label: label.set_color(fg), ax.get_xticklabels()))
    list(map(lambda label: label.set_color(fg), ax.get_yticklabels()))

    plt.gca().xaxis.set_major_formatter(mpl.dates.DateFormatter('%m/%y'))
    plt.gca().xaxis.set_major_locator(mpl.dates.MonthLocator(interval=6))
    plt.ylabel('Balance', color=fg)

    blue_line, red_line = None, None
    def vlines(_dates, _curve):
        nonlocal blue_line, red_line
        mini, maxi = _curve.argmin(), _curve.argmax()
        minx, maxx = _dates[mini], _dates[maxi]
        miny, maxy = _curve[mini], _curve[maxi]
        minc, maxc = 'lime', 'red'
        if red_line is not None:
            blue_line.remove()
            red_line.remove()
        blue_line = plt.axvline(x=minx, color=minc)
        red_line = plt.axvline(x=maxx, color=maxc)
        text = 'Low  : {} {:>6}$\nHigh : {} {:>6}$\nCurr : {} {:>6}$'.format(
            minx.date(), int(miny),
            maxx.date(), int(maxy),
            _dates[-1].date(), int(_curve[-1]))
        ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=8, fontfamily='monospace',
            verticalalignment='top', color=fg, bbox={'facecolor':'gray', 'alpha':0.95})

    progress = tqdm(len(curve))
    initial_offset = min(50, len(dates))
    update_step = 5
    p, = ax.plot([], [], 'cyan')
    def update(i, fig, ax):
        _dates = dates[:int(i * update_step) + initial_offset]
        _curve = curve[:int(i * update_step) + initial_offset]
        if i % 2 == 0:
            vlines(_dates, _curve)
        p.set_data(_dates, _curve)
        p.axes.set_xlim(_dates[0], dates[-1])
        p.axes.set_ylim(_curve.min(), _curve.max())
        progress.update(1)
        return p

    if args.video:
        frame_count = int((len(curve) - initial_offset) / update_step)
        ani = FuncAnimation(fig, update, fargs=(fig, ax), frames=frame_count, interval=100, blit=False)
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
    ap.add_argument('-b', '--balance', type=int, default=0, help='Starting balance')
    ap.add_argument('-v', '--video', action='store_true', help='Make video instead of still image')
    main(ap.parse_args())
