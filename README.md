# Corona Log Figures

Using [COVID-19 data](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series "Github page from which tables with virus data in csv format can be downloaded") provided by the John Hopkins University, this script creates some basic figures (using matplotlib) using a logarithmic scale for the y-axis.

In logarithmic scale, an exponential growth appears as a straight line.  Therefore, changes in the rate of spread of the COVID-19 disease can be seen more clearly than in the commonly found diagrams in linear scale.

This package contains the plotting code and a selection of figures.  To make additional figures, you need to checkout the current data from the John Hopkins University:
```
git clone https://github.com/kiber42/corona-log-plots.git
cd corona-log-plots
git clone https://github.com/CSSEGISandData/COVID-19.git
```

The numbers are currently updated on a daily basis, retrieve the current data using:
```
cd COVID-19
git pull
```

To generate figures, run the `time_series.py` script with one or more country names as arguments.  Without arguments, a figure for my home country Germany is created.
```
./time_series.py US "United Kingdom" Germany China
```
(The syntax is assuming you're on Linux.)

The figures are saved to disk as png files and displayed on screen, hit `Ctrl+C` on the terminal to close all at once.
