# Corona Log Figures

Using [COVID-19 data](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series "Github page from which tables with virus data in csv format can be downloaded") provided by the John Hopkins University, this script creates some basic figures (using *matplotlib*) using a logarithmic scale for the y-axis.

In logarithmic scale, an exponential growth appears as a straight line.  Therefore, changes in the rate of spread of the COVID-19 disease can be seen more clearly than in the commonly found diagrams in linear scale.

A simple estimate of the actual number of infected people is obtained by shifting the most reliable number (the number of deaths) back by 17 days, which is the approximate time it takes from infection to death.  It is scaled up by a factor of 100, to account for the *guessed* 1% lethality of the COVID-19 disease.  Although it is a rough approximation, comparing this line with the number of reported number of confirmed cases can be interesting.

This package contains the plotting code and a selection of example figures (in the `examples` subdirectory).  To make additional and more up-to-date figures, you need to retrieve the current data from the John Hopkins University:
```
git clone https://github.com/kiber42/corona-log-plots.git
cd corona-log-plots
git clone https://github.com/CSSEGISandData/COVID-19.git
```

The provided numbers are currently updated on a daily basis, pull the most recent data with these commands:
```
cd COVID-19
git pull
```

To generate figures, run the `time_series.py` script with one or more country names as arguments.  Without arguments, a figure for Germany (my home country) is created.
```
python3 time_series.py US "United Kingdom" Germany China
```

The figures are saved to disk as png files in a subdirectory named `figures`.  If supported by the matplotlib backend, they are also displayed on screen, hit `Ctrl+C` on the terminal to close all at once.
