#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import csv
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from copy import deepcopy

# Path for saving output images, set to None if you do not want to save
save_dir = "figures"
# Attempt to show interactive figures, may not work in some environments
show_plots = True
# Path were the csv files with the input data are located
data_dir = "COVID-19/csse_covid_19_data/csse_covid_19_time_series"
# Filename pattern, placeholder {} is replaced by confirmed, recovered or deaths
filename_pattern_global = "time_series_covid19_{}_global.csv"
filename_pattern_US = "time_series_covid19_{}_US.csv"
# Countries to show by default if none are given on the command line
default_countries = ["Germany"]

class Country:
    def __init__(self, data_tuple):
        self.province, self.name = data_tuple[:2]
        self.latitude = float(data_tuple[2])
        self.longitude = float(data_tuple[3])
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
        # When running on US data: Use City+State instead of State+Country
        target_columns = ["Admin2", "Province_State", "Lat", "Long_"]
    else:
        target_columns = ["Province/State", "Country/Region", "Lat", "Long"]
    # Use first date with available data as marker
    target_columns.append("1/22/20")
    format_info = tuple(row.index(col) for col in target_columns)
    data_start = format_info[4]
    dates = [dt.datetime.strptime(date, '%m/%d/%y').date() for date in row[data_start:]]
    return dates, format_info


def process_row(row, format_info):
    country_info = tuple(row[index] for index in format_info[:4])
    c = Country(country_info)
    data_start = format_info[4]
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
        "ylim": (0.9, 1e7),
        "xlim": (date_start, date_end + dt.timedelta(5)),
    }

    for country in countries:
        if not country in all_countries:
            # Try to expand name if there is a matching state/province
            selected = next((c.full_name for c in all_countries.values() if c.province == country), None)
            if selected is None:
                print("Country '{}' not found.".format(country))
                continue
            country = selected
        fig, ax = plt.subplots()
        title = "{} up to {}".format(all_countries[country].full_name, date_end)
        ax.set(title=title, **options)
        ax.grid(b=True, which='major')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
        for entry in entries:
            try:
                dataset = datasets[entry.tag]
            except KeyError:
                continue
            data_x = np.array(dataset.dates) + dt.timedelta(entry.date_offset)
            data_y = dataset.values[country] * entry.scale
            ax.scatter(data_x, data_y, label=entry.label, color=entry.color)
        legend = ax.legend(loc='upper left', shadow=True, fontsize='x-large')
        legend.get_frame().set_facecolor('C4')
        fig.autofmt_xdate()
        if save_dir is not None:
            os.makedirs(save_dir, exist_ok=True)
            filename = os.path.join(save_dir, "{}.png".format(country))
            fig.savefig(filename)
            print("Plot for {} saved to {}".format(country, filename))

    if show_plots:
        plt.show()


if __name__ == "__main__":
    country_names = []
    us_mode = False
    for token in sys.argv[1:]:
        if token.startswith("-") and token.lower().replace("-", "") == "us":
            us_mode = True
        else:
            country_names.append(token)
    if len(country_names) == 0:
        country_names = ["US"] if us_mode else default_countries

    pattern = filename_pattern_US if us_mode else filename_pattern_global
    main(country_names, pattern)
