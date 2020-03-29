# -*- coding: utf-8 -*-
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
    groups = [
        { "tag": "confirmed", "date_offset": 0, "scale": 1, "color": "C1" },
#        { "tag": "recovered", "date_offset": -17, "scale": 1, "color": "C2" },
#        { "tag": "deaths", "date_offset": -22, "scale": 1, "color": "C3" },
        { "tag": "recovered", "date_offset": 0, "scale": 1, "color": "C2" },
        { "tag": "deaths", "date_offset": 0, "scale": 1, "color": "C3" },        
        { "tag": "deaths", "label" : "infected (estimated)", "date_offset": -17, "scale": 100, "color": "C5" },
        ]
    datasets = {}
    for group in groups:
        file_name = pattern.format(group["tag"])
        datasets[group["tag"]] = load_data(file_name)
    # assume that dates and countries are identical among the input files
    dates = next(iter(datasets.values())).dates
    all_countries = next(iter(datasets.values())).countries

    day_one = dates[0]
    data_x = np.array(range(len(dates)))
    options = {"xlabel" : "days since {}".format(day_one),
               "ylabel" : "n",
               "yscale" :"log",
               "xlim" : (0, len(dates)),
               "ylim" :(0.9, 1e6)}
    
    for country in countries:
        if not country in all_countries:
            print("Country '{}' not found.".format(country))
            continue
        fig, ax = plt.subplots()
        ax.set(title=all_countries[country].name, **options)
        ax.grid(b=True, which='major')
        for i, group in enumerate(groups):
            tag = group["tag"]
            data_y = datasets[tag].values[country]
            offset = group["date_offset"]
            scale = group["scale"]
            auto_label = "{} shifted by {} days".format(tag, offset) if offset else tag
            ax.scatter(data_x + offset, np.array(data_y) * scale,
                       label=group["label"] if "label" in group else auto_label,
                       color=group["color"]
            )
        legend = ax.legend(loc='upper left', shadow=True, fontsize='x-large')
        legend.get_frame().set_facecolor('C4')

    plt.show()
        

if __name__ == "__main__":
    default_country = "Germany"
    countries = sys.argv[1:] if len(sys.argv) > 1 else [default_country]
    main(countries)
