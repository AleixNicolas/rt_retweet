# General

## Requirements

Twarc-count requires Python 3.7 or greater and pip.

## Installation

You need to clone this repository.

`git clone https://github.com/DataPolitik/rt_changes.git`

And then, move to the folder **rt_changes**. Then, install all modules required by the script:

`pip install -r requirements.txt`

## Example of use

[Crowdosourced elite during the first wave of Covid19 in Spain](https://datapolitik.medium.com/el-baile-de-las-%C3%A9lites-en-twitter-9a288fb32eb3)

################################################################################

# retweet.py

Executes elites and/or dendrogram as required.

## Usage

`retweet.py <INFILE> <OUTFILE> [-f [FIELDS] ]`

* **-i** | **- -infile**: Required. Infile with all tweets.
* **-o** | **- -outfile**: Not required. Deffault is None. If None outfile name is generated from infile.
* **-g** | **- -granularity**: The time interval. You can use any offset alias for Pandas time series.
* **-d** | **- -decay**: An inertia parameter that weighs retweets received in the previous time intervals (default = 1).
* **-a** | **- -alpha**: Polarisation sensitivity
* **-t** | **- -threshold**: Removes users whose sum of scores are below the specific threshold.
* **-i** | **- -interval**: Specify a date period to process.
* **-m** | **- -method**: Specify clustering method used.
* **-l** | **- -algorithm**: Specify clustering algorithm used.
* **--elites/--no-elites** | Determines if elites csv filed is created deffault is --elites (True)
* **--dendrogram/--no-dendrogram** | Determines if clustering and dendrograms are created deffault is --no-dendrogram (False)

 
## Interval parameter

The paramenter -i waits for two dates separated by a comma (eg: start_time,end_time) the format should be according. Only use if smaller than dataset.
YYYY-MM-DD-HH:MM:SS.

## Granularity

Some allowed values are:

* H: Hours
* Y: Years
* W: Weeks
* M: Months

A complete description of allowed aliases can be found at: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

## Decay

Allowed values from 0 to 1

## Alpha

Allowed values from 0 to 1.6

## Algorithm

Allowed values are:

* generic: faster, but only works with method "ward"
* nn_chain: slower, but works with any distance update scheme

Clustering performed only if algorithm values are one of the above

## Method

Allowed values are:

* ward: works with any algorithm
* centroid: does not work if algorithm is "nn_chain"
* poldist: does not work if algorithm is "nn_chain"

## Examples

### Computes a simple ranking

`retweet.py examples\results.json examples\elites.csv

### Computes a weekly ranking

`dendrogram.py examples\results.json examples\elites.csv -g W`

### Removes all user under 50 points

`dendrogram.py examples\results.json examples\elites.csv -t 50`

### Compute data from an specific date interval

`dendrogram.py  examples/results.json examples\elites.csv -i 2021-10-18,2022-10-18`

### Compute data with generic algorithm

`dendrogram.py  examples/results.json examples\elites.csv -l generic

### Compute data with ward method

`dendrogram.py  examples/results.json examples\elites.csv -l ward
