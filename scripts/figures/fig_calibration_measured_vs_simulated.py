"""
Figure 7: measured vs simulated indoor temperature of the monitored classroom after the tuning,
one figure per building: (a–d) hourly time series of one representative week per season;
(e) hourly measured vs simulated values over the year; (f) daily mean and range of the hourly
residuals; (g) distribution of the hourly residuals.

Input: results/calibration/<building>_hourly_temperature_comparison.csv (02_bem_calibration).
Output: figures/calibration_measured_vs_simulated_<building>.png|pdf|svg
"""

import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from figure_style import config, CM, MEASURED, SIMULATED, NAVY, BUILDING_TITLES, save

OCCUPIED, SELECTED_WEEK, BAND = '#e3e6ec', '#ffe08a', '#eeeeee'
STATS_BOX = dict(fc='white', ec='#b8c2d6', lw=0.5, alpha=0.75, boxstyle='round,pad=0.25')
# Representative weeks (Monday 01:00 -> following Monday 00:00), as in Table 3
WEEKS = [('Winter', '2024-01-22', '22–28 Jan'), ('Spring', '2024-05-27', '27 May–2 Jun'),
         ('Summer', '2024-06-17', '17–23 Jun'), ('Autumn', '2024-11-25', '25 Nov–1 Dec')]


def week(df, start):
    start = pd.Timestamp(start)
    return df[(df.index > start) & (df.index <= start + pd.Timedelta(days=7))]


def shade_occupied_hours(ax, df):
    occupied, times, i = (df['occupants'] > 0).values, df.index, 0
    while i < len(times):
        if occupied[i]:
            j = i
            while j + 1 < len(times) and occupied[j + 1]:
                j += 1
            ax.axvspan(times[i] - pd.Timedelta(hours=1), times[j], color=OCCUPIED, lw=0, zorder=0.5)
            i = j + 1
        else:
            i += 1


def statistics(ax, text):
    ax.text(0.0, 1.03, text, transform=ax.transAxes, ha='left', va='bottom', fontsize=5.6, bbox=STATS_BOX, zorder=10)


def figure_of(building):
    df = pd.read_csv(config.CALIBRATION_RESULTS_DIR / f'{building}_hourly_temperature_comparison.csv',
                     parse_dates=['timestamp']).set_index('timestamp')
    df = df.rename(columns={'tuned': 'simulated'})
    df['residual'] = df['measured'] - df['simulated']
    rmse = np.sqrt((df['residual'] ** 2).mean())
    r2 = 1 - (df['residual'] ** 2).sum() / ((df['measured'] - df['measured'].mean()) ** 2).sum()

    fig = plt.figure(figsize=(17.4 * CM, 11.6 * CM))
    grid = GridSpec(2, 4, figure=fig, left=0.065, right=0.99, top=0.835, bottom=0.085, hspace=0.62, wspace=0.42, height_ratios=[1, 1.15])
    fig.text(0.01, 0.975, BUILDING_TITLES[building], fontsize=8.5, fontweight='bold', color=NAVY, ha='left', va='top')
    fig.legend(handles=[Line2D([], [], color=MEASURED, lw=1.8, label='Measured'), Line2D([], [], color=SIMULATED, lw=1.8, label='Simulated'),
                        Patch(fc=OCCUPIED, label='Occupied hours'), Patch(fc=SELECTED_WEEK, label='Selected weeks'),
                        Line2D([], [], ls='', marker='o', ms=3, color=NAVY, alpha=0.6, label='Hourly pair'),
                        Line2D([], [], color='black', lw=0.8, label='1:1 line'), Line2D([], [], color='black', lw=0.5, ls='--', label='±2 °C')],
               loc='upper right', bbox_to_anchor=(0.99, 0.995), ncol=7, frameon=False, fontsize=6.2, handlelength=1.8, columnspacing=1.1)
    letters = iter('abcdefg')

    # (a–d) representative weeks
    weeks = [week(df, start) for _, start, _ in WEEKS]
    y_min = np.floor(min(w[['measured', 'simulated']].min().min() for w in weeks)) - 1
    y_max = np.ceil(max(w[['measured', 'simulated']].max().max() for w in weeks)) + 1
    for j, ((season, start, label), w) in enumerate(zip(WEEKS, weeks)):
        ax = fig.add_subplot(grid[0, j])
        shade_occupied_hours(ax, w)
        ax.plot(w.index, w['measured'], color=MEASURED, lw=0.9)
        ax.plot(w.index, w['simulated'], color=SIMULATED, lw=0.9)
        ax.set_title(f'({next(letters)}) {season}, {label}', loc='left', pad=15)
        statistics(ax, f"RMSE {np.sqrt((w['residual'] ** 2).mean()):.1f} °C   MTDW {round(w['residual'].mean(), 1) + 0:+.1f} °C")
        ax.set_ylim(y_min, y_max)
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True, nbins=6))
        ax.set_xlim(w.index[0] - pd.Timedelta(hours=1), w.index[-1])
        ax.set_xticks([pd.Timestamp(start) + pd.Timedelta(days=d) for d in (0, 2, 4, 6)])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %d'))
        if j == 0:
            ax.set_ylabel('Temperature (°C)')

    # (e) hourly pairs over the year
    ax = fig.add_subplot(grid[1, 0])
    low, high = np.floor(df[['measured', 'simulated']].min().min()) - 1, np.ceil(df[['measured', 'simulated']].max().max()) + 1
    ax.fill_between([low, high], [low - 2, high - 2], [low + 2, high + 2], color=BAND, lw=0, zorder=1)
    ax.scatter(df['measured'], df['simulated'], s=1.2, color=NAVY, alpha=0.15, lw=0, rasterized=True, zorder=2)
    ax.plot([low, high], [low, high], color='black', lw=0.8, zorder=3)
    for offset in (-2, 2):
        ax.plot([low, high], [low + offset, high + offset], color='black', lw=0.5, ls='--', zorder=3)
    ax.set_xlim(low, high); ax.set_ylim(low, high); ax.set_aspect('equal')
    ax.set_xlabel('Measured (°C)'); ax.set_ylabel('Simulated (°C)')
    ax.set_title(f'({next(letters)}) Hourly values, full year', loc='left', pad=22)
    statistics(ax, f"n = {len(df):,}   R² = {r2:.2f}   RMSE = {rmse:.1f} °C\n"
                   f"MBE = {round(-df['residual'].mean(), 1) + 0:+.1f} °C   |res.| ≤ 2 °C: {(df['residual'].abs() <= 2).mean() * 100:.0f}%")

    # (f) daily residuals over the year
    ax = fig.add_subplot(grid[1, 1:3])
    daily = df['residual'].resample('D')
    daily_mean, daily_min, daily_max = daily.mean(), daily.min(), daily.max()
    for _, start, _ in WEEKS:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(start) + pd.Timedelta(days=7), color=SELECTED_WEEK, lw=0, zorder=0.5)
    ax.axhspan(-2, 2, color=BAND, alpha=0.8, lw=0, zorder=0.6)
    ax.fill_between(daily_mean.index, daily_min, daily_max, color=MEASURED, alpha=0.22, lw=0)
    ax.plot(daily_mean.index, daily_mean, color=MEASURED, lw=0.8)
    ax.axhline(0, color='black', lw=0.7)
    for y in (-2, 2):
        ax.axhline(y, color='black', lw=0.5, ls='--')
    ax.set_ylabel('Residual, meas. − sim. (°C)')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.set_xlim(pd.Timestamp('2024-01-01'), pd.Timestamp('2025-01-01'))
    limit = np.ceil(max(abs(daily_min.min()), abs(daily_max.max())))
    ax.set_ylim(-limit, limit)
    ax.set_title(f'({next(letters)}) Residuals over the year', loc='left', pad=15)
    statistics(ax, 'Line: daily mean of hourly residuals   Band: daily min–max')

    # (g) residual distribution
    ax = fig.add_subplot(grid[1, 3])
    bins = np.arange(np.floor(df['residual'].min()), np.ceil(df['residual'].max()) + 0.5, 0.5)
    ax.hist(df['residual'], bins=bins, color=MEASURED, alpha=0.85, lw=0)
    ax.axvline(0, color='black', lw=0.7)
    ax.axvline(df['residual'].mean(), color=NAVY, lw=0.9, ls='--')
    ax.set_xlabel('Residual, meas. − sim. (°C)'); ax.set_ylabel('Hours')
    ax.set_title(f'({next(letters)}) Residual distribution', loc='left', pad=15)
    statistics(ax, f"mean {round(df['residual'].mean(), 1) + 0:+.1f} °C   SD {df['residual'].std():.1f} °C")
    save(fig, f'calibration_measured_vs_simulated_{building}')


if __name__ == '__main__':
    for building in ('building10', 'building09'):
        figure_of(building)
