# Corona Log Figures

Using [COVID-19 data](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series "Github page from which tables with virus data in csv format can be downloaded") provided by the Johns Hopkins University, this script creates some basic figures (using *matplotlib*) using a logarithmic scale for the y-axis.

In logarithmic scale, an exponential growth appears as a straight line.  Therefore, changes in the rate of spread of the COVID-19 disease can be seen more clearly than in the commonly found diagrams in linear scale.

A simple estimate of the actual number of infected people is obtained by shifting the most reliable number (the number of deaths) back by 17 days, which is the approximate time it takes from infection to death.  It is scaled up by a factor of 100, to account for the *guessed* 1% lethality of the COVID-19 disease.  Although it is a rough approximation, comparing this line with the number of reported number of confirmed cases can be interesting.

The counts for the most recent ten days are used to compute a trend line.  The estimated duplication time derived from the slope of this trend line is shown in parentheses in the legend.

Two additional curves are generated to illustrate the current situation more clearly: 'confirmed current' and 'recent deaths'.
The 'confirmed current' curve is obtained by only taking into account the increase of the 'confirmed' data over the previous 14 days.
Similarly, the 'recent deaths' curve is derived from the increase of the 'death' data over the previous 14 days, but modified somewhat arbitrarily by shifting it 7 days to the left and scaling it up by a factor of 150.
These modifications were done to make the 'confirmed current' and 'recent deaths' curves appear close to each other in the figure for Germany during the onset of the second wave in October 2020.
From November 2020 on, a strong divergence between the two becomes visible for the Germany data.

A similar divergence is visible for many countries.
Some possible causes that may contribute to this effect are: exhausted testing capabilities (leading to an apparent stagnation of confirmed cases while actual cases are rising), an overwhelmed medical system (leading to a higher rate of deaths), or mutations of the virus that are more dangerous and/or less reliably detected by the available tests.

This package contains the plotting code and a selection of example figures (in the `examples` subdirectory).  To make additional and more up-to-date figures, you need to retrieve the current data from the Johns Hopkins University:
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

Since there is no data for China as a whole available, the sum of all available regions in China will be computed and shown.  For some countries, e.g. France, data for the whole country and for individual regions is available.  It is possible to refer to the sum of all regional data for France as `"France ALL"` (it's important to include the quotation marks on the command line).  By comparing `France` and `"France ALL"` you will see that the numbers are very different.  For the case of France, this is because `France` apparently refers to mainland France, while the regions refer to French islands such as Guadeloupe or Martinique.  Whenever you are in doubt about what is shown in the figures, it is probably a good idea to look at the original data tables.

Johns Hopkins University provides a dedicated dataset with more fine-grained information for the United States of America.  To use this dataset instead of the global one, provide the `--us` command-line switch together with the states or counties (not cities!) you are interested in.  To see data for Manhattan (New York County), you need to type `"New York New York"` if you want to see data for New York City.  Just `"New York"` will show results for New York state.
```
python3 time_series.py --us "New York New York" "Illinois Cook" Michigan California
```

The figures are saved to disk as png files in a subdirectory named `figures`.  If supported by the matplotlib backend, they are also displayed on screen, hit `Ctrl+C` on the terminal to close all at once.
