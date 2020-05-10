#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
from copy import deepcopy
import csv
import datetime as dt
import math

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy import polyfit

# Path for saving output images, set to None if you do not want to save
save_dir = "figures"
# Attempt to show interactive figures, may not work in some environments
show_plots = True
# Path were the csv files with the input data are located
data_dir = "COVID-19/csse_covid_19_data/csse_covid_19_time_series"
# Filename pattern, placeholder {} is replaced by confirmed, recovered or deaths
filename_pattern_global = "time_series_covid19_{}_global.csv"
filename_pattern_US = "time_series_covid19_{}_US.csv"
# Items to show by default if none are given on the command line
default_items = ["Germany"]
default_items_US = ["New York"]

class Country:
    def __init__(self, data_tuple):
        self.province, self.name = data_tuple[:2]
        try:
            self.latitude = float(data_tuple[2])
            self.longitude = float(data_tuple[3])
        except ValueError:
            self.latitude, self.longitude = 0, 0
        self.full_name = self.name
        if self.province:
            self.full_name += " " + self.province

    def __repr__(self):
        name = self.name
        if self.province:
            name += " ({})".format(self.province)
        return "{0} ({1:.1f}°, {2:.1f}°)".format(name, self.latitude, self.longitude)


class Dataset:
    def __init__(self, countries, dates, values):
        self.countries = countries
        self.dates = dates
        self.values = values


class Entry:
    def __init__(self, tag, color, label=None, date_offset=0, scale=1):
        self.tag = tag
        if label is None:
            self.label = tag
            if date_offset:
                self.label += " shifted by {} days".format(date_offset)
            if scale != 1:
                self.label += " (x{})".format(scale)
        else:
            self.label = label
        self.color = color
        self.date_offset = date_offset
        self.scale = scale


def process_header_row(row):
    if "Admin2" in row:
        # When running on US data: Use County+State instead of State+Country
        target_columns = ["Admin2", "Province_State", "Lat", "Long_"]
    else:
        target_columns = ["Province/State", "Country/Region", "Lat", "Long"]
    # Use first date with available data as marker
    target_columns.append("1/22/20")
    format_info = tuple(row.index(col) for col in target_columns)
    data_start = format_info[-1]
    dates = [dt.datetime.strptime(date, '%m/%d/%y').date() for date in row[data_start:]]
    return dates, format_info


def process_row(row, format_info):
    country_info = tuple(row[index] for index in format_info[:4])
    c = Country(country_info)
    data_start = format_info[-1]
    row_data = np.array([int(item) for item in row[data_start:]])
    return c, row_data


def load_data(filename):
    countries = {}
    computed = {}
    values = {}
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        dates, format_info = process_header_row(reader.__next__())
        for row in reader:
            c, row_data = process_row(row, format_info)
            countries[c.full_name] = c
            values[c.full_name] = row_data
            # Compute sums for states where individual provinces are listed
            if c.province:
                placeholder = c.name + " ALL"
                if placeholder in computed:
                    values[placeholder] += row_data
                else:
                    # Create new synthetic entry; copy Country and data row to
                    # ensure that original entry is not affected!
                    c = deepcopy(c)
                    row_data = deepcopy(row_data)
                    c.full_name = c.name + " (summed from region data)"
                    computed[placeholder] = c
                    values[placeholder] = row_data
    for placeholder, c in computed.items():
        # if there is no name collision, remove the " ALL" suffix from the name
        name = placeholder[:-4]
        if not name in countries:
            countries[name] = computed[placeholder]
            values[name] = values[placeholder]
        else:
            countries[placeholder] = computed[placeholder]
    return Dataset(countries, dates, values)


def fit_log_slope(data_x, data_y, days_fit, days_extrapolate):
    slope, offset = polyfit(range(days_fit), np.log(data_y[-days_fit:]), 1)
    n_days = days_fit + days_extrapolate
    fit_x = [0, n_days]
    fit_y = np.exp(np.array(fit_x) * slope + offset)
    # Align x values to input data_x
    first_day = data_x[-days_fit]
    fit_x = [first_day + dt.timedelta(days=d) for d in fit_x]
    double_time = math.log(2) / slope
    return fit_x, fit_y, double_time


def plot_dataset_entry(axis, dates, values, entry):
    data_x = np.array(dates) + dt.timedelta(entry.date_offset)
    data_y = values * entry.scale
    # Linear fit (to log scale data) for last few days
    fit_x, fit_y, double_time = fit_log_slope(data_x, data_y, days_fit=5, days_extrapolate=10)
    label = entry.label + " ({:.1f} days)".format(double_time)
    axis.scatter(data_x, data_y, label=label, color=entry.color)
    axis.plot(fit_x, fit_y, color="black")


def auto_find_country(search_name, all_countries):
    if search_name in all_countries:
        return search_name
    # Try to expand name to see if there is a matching state/province
    selected = next((c.full_name for c in all_countries.values() if c.province == search_name), None)
    if selected is None:
        print("Country '{}' not found.".format(search_name))
        return None
    return selected


def plot_one_country(country_name, datasets, entries, title, options):
    fig, axis = plt.subplots()
    axis.set(title=title, **options)
    axis.grid(b=True, which='major')
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    axis.xaxis.set_major_locator(mdates.MonthLocator())
    axis.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    for entry in entries:
        try:
            dataset = datasets[entry.tag]
        except KeyError:
            continue
        plot_dataset_entry(axis, dataset.dates, dataset.values[country_name], entry)
    legend = axis.legend(loc='upper left', shadow=True, fontsize='x-large')
    legend.get_frame().set_facecolor('C4')
    fig.autofmt_xdate()
    return fig


def save_figure(fig, name):
    if save_dir is None:
        return
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, "{}.png".format(name))
    fig.savefig(filename)
    print("Plot for {} saved to {}".format(name, filename))


def main(countries, filename_pattern):
    pattern = os.path.join(data_dir, filename_pattern)
    entries = [
        Entry("confirmed", color="C1"),
        Entry("recovered", color="C2"),
        Entry("deaths", color="C3"),
        Entry("deaths", color="C5", label="infected (estimated)", date_offset=-17, scale=100),
        ]
    datasets = {}
    for entry in entries:
        file_name = pattern.format(entry.tag)
        try:
            datasets[entry.tag] = load_data(file_name)
        except FileNotFoundError:
            print("No data for {}".format(entry.tag))
    # assume that countries are identical among the input files
    all_countries = next(iter(datasets.values())).countries
    all_dates = [d for dataset in datasets.values() for d in dataset.dates]
    date_start = min(all_dates)
    date_end = max(all_dates)
    options = {
        "yscale": "log",
        "ylim": (0.9, 1e8),
        "xlim": (date_start, date_end + dt.timedelta(5)),
    }

    for c in countries:
        country_name = auto_find_country(c, all_countries)
        if not country_name:
            continue
        title = "{} up to {}".format(all_countries[country_name].full_name, date_end)
        fig = plot_one_country(country_name, datasets, entries, title, options)
        save_figure(fig, country_name)

    if show_plots:
        plt.show()


if __name__ == "__main__":
    item_names = []
    us_mode = False
    for token in sys.argv[1:]:
        if token.startswith("-") and token.lower().replace("-", "") == "us":
            us_mode = True
        else:
            item_names.append(token)
    if len(item_names) == 0:
        item_names = default_items_US if us_mode else default_items

    pattern = filename_pattern_US if us_mode else filename_pattern_global
    main(item_names, pattern)
