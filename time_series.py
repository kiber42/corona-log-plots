# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import sys, os
import csv
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

save_to_disk = True
show_plots = True

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
        return "{0} ({1:.2f}°, {2:.2f}°)".format(name, self.latitude, self.longitude)


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


def load_data(filename):
    countries = {}
    values = {}
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        fieldnames = reader.__next__()
        assert(fieldnames[:4] == ['Province/State', 'Country/Region', 'Lat', 'Long'])
        dates = [dt.datetime.strptime(d, '%m/%d/%y').date() for d in fieldnames[4:]]
        for row in reader:
            c = Country(tuple(row[:4]))
            countries[c.full_name] = c
            values[c.full_name] = tuple(int(item) for item in row[4:])
    return Dataset(countries, dates, values)


def main(countries):
    pattern = "time_series_data/time_series_covid19_{}_global.csv"
    entries = [
        Entry("confirmed", color="C1"),
        Entry("recovered", color="C2"),
        Entry("deaths", color="C3"),
        Entry("deaths", color="C5", label="infected (estimated)", date_offset=-17, scale=100),
        ]
    datasets = {}
    for entry in entries:
        file_name = pattern.format(entry.tag)
        datasets[entry.tag] = load_data(file_name)
    # assume that countries are identical among the input files
    all_countries = next(iter(datasets.values())).countries
    all_dates = [d for dataset in datasets.values() for d in dataset.dates]
    date_start = min(all_dates)
    date_end = max(all_dates) + dt.timedelta(5)
    options = {
        "yscale": "log",
        "ylim": (0.9, 1e6),
        "xlim": (date_start, date_end),
    }

    for country in countries:
        if not country in all_countries:
            # Try to find matching state/province
            country = next((c.full_name for c in all_countries.values() if c.province == country), None)
            if country is None:
                print("Country '{}' not found.".format(country))
                continue
        fig, ax = plt.subplots()
        ax.set(title=all_countries[country].full_name, **options)
        ax.grid(b=True, which='major')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
        for entry in entries:
            dataset = datasets[entry.tag]
            data_x = np.array(dataset.dates) + dt.timedelta(entry.date_offset)
            data_y = np.array(dataset.values[country]) * entry.scale
            ax.scatter(data_x, data_y, label=entry.label, color=entry.color)
        legend = ax.legend(loc='upper left', shadow=True, fontsize='x-large')
        legend.get_frame().set_facecolor('C4')
        fig.autofmt_xdate()
        if save_to_disk:
            os.makedirs("figures", exist_ok=True)
            fig.savefig("figures/{}.png".format(all_countries[country].full_name))

    if show_plots:
        plt.show()


if __name__ == "__main__":
    default_country = "Germany"
    countries = sys.argv[1:] if len(sys.argv) > 1 else [default_country]
    main(countries)
