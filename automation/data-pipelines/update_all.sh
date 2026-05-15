#!/usr/bin/env sh
set -eu

python automation/data-pipelines/fetch_wid_data.py
python automation/data-pipelines/fetch_ons_housing.py
python automation/data-pipelines/fetch_ons_wealth.py
python automation/data-pipelines/fetch_hmrc_stats.py
