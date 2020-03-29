#!/usr/bin/env python3
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt

class Country:
    def __init__(self, data_tuple):
        self.province, self.name = data_tuple[:2]
        self.latitude = float(data_tuple[2])
        self.longitude = float(data_tuple[3])
        self.id = self.name
        if self.province:
            self.id += " " + self.province
        
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
    

def load_data(filename):
    countries = {}
    values = {}
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        fieldnames = reader.__next__()
        assert(fieldnames[:4] == ['Province/State', 'Country/Region', 'Lat', 'Long'])        
        dates = fieldnames[4:]
        for row in reader:
            c = Country(tuple(row[:4]))
            countries[c.id] = c
            values[c.id] = tuple(int(item) for item in row[4:])            
    return Dataset(countries, dates, values)


def main(countries):
    pattern = "time_series_data/time_series_covid19_{}_global.csv"
    groups = ["confirmed", "deaths", "recovered"]
    date_offsets = [0, -22, -17]
    datasets = {}
    for group in groups:
        file_name = pattern.format(group)
#        print("Loading data for {} from {}".format(group, file_name))
        datasets[group] = load_data(file_name)
    # assume that dates and countries are identical among the input files
    dates = next(iter(datasets.values())).dates
    all_countries = next(iter(datasets.values())).countries

    day_one = dates[0]
    data_x = np.array(range(len(dates)))
    options = {"xlabel" : "days since {}".format(day_one),
               "ylabel" : "n",
               "yscale" :"log",
               "ylim" :(0.9, 1e6)}
    
    for country in countries:
        if not country in all_countries:
            print("Country '{}' not found.".format(country))
            continue
        fig, ax = plt.subplots()
        for i,g in enumerate(groups):
            data_y = datasets[g].values[country]
            offset = date_offsets[i]
            ax.scatter(data_x + offset, data_y,
                       label="{} shifted by {} days".format(g, offset) if offset else g)
            ax.set(title=all_countries[country].name, **options)
            ax.grid()
        legend = ax.legend(loc='upper left', shadow=True, fontsize='x-large')
        legend.get_frame().set_facecolor('C4')

    plt.show()
        

if __name__ == "__main__":
    default_country = "Germany"
    countries = sys.argv[1:] if len(sys.argv) > 1 else [default_country]
    main(countries)
