# Data Licences and Source Citations

Last updated: 2026-06-27

Every dataset used in WealthLens UK must document its source, licence, URL, and the date it was accessed. This file is the central reference. Static `.meta.json` sidecars live in `automation/data-pipelines/metadata/`; some pipelines (e.g. generational wealth) generate their sidecar at runtime into `data/processed/`.

## World Inequality Database (WID)

- **Dataset:** `wid_wealth_shares_gb.csv`
- **Description:** Top 1% and top 10% wealth shares in Great Britain
- **URL:** <https://wid.world/>
- **Licence:** CC-BY
- **Access date:** 2026-05-14
- **Update frequency:** Annual

## ONS — Housing Affordability

- **Dataset:** `ons_housing_affordability_by_region.csv`
- **Description:** Median house price to workplace-based earnings ratio by UK region
- **URL:** <https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/ratioofhousepricetoworkplacebasedearningslowerquartileandmedian>
- **Licence:** Open Government Licence v3.0
- **Access date:** 2026-05-14
- **Update frequency:** Annual (March)

## ONS — Wealth and Assets Survey

- **Dataset:** `ons_wealth_by_decile.csv`
- **Description:** Total net household wealth by decile in Great Britain
- **URL:** <https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/datasets/totalwealthwealthingreatbritain>
- **Licence:** Open Government Licence v3.0
- **Access date:** 2026-05-14
- **Update frequency:** Biennial

## HMRC — Capital Gains Tax Statistics

- **Dataset:** `hmrc_cgt_concentration.csv`
- **Description:** Capital gains distribution by size of gain
- **URL:** <https://www.gov.uk/government/statistics/capital-gains-tax-statistics>
- **Licence:** Open Government Licence v3.0
- **Access date:** 2026-05-14
- **Update frequency:** Annual

## Bank of England — Base Rate and CPI

- **Dataset:** `boe_rates.csv`
- **Description:** Bank of England base rate and ONS CPI annual inflation rate
- **URL (BoE):** <https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp>
- **URL (ONS CPI):** <https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/latest>
- **Licence:** Open Government Licence v3.0
- **Access date:** 2026-05-15
- **Update frequency:** Monthly (CPI), ad-hoc (base rate)

## Resolution Foundation / ONS — Generational Wealth

- **Dataset:** `generational_wealth_gap.csv`
- **Description:** Median total household wealth by generation at age milestones
- **URL:** <https://www.resolutionfoundation.org/publications/>
- **URL (ONS WAS):** <https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/latest>
- **Licence:** Resolution Foundation series: CC BY-NC-ND 4.0 (non-commercial, no-derivatives); ONS WAS: OGL v3.0
- **Access date:** 2026-05-16
- **Update frequency:** Periodic (Resolution Foundation reports)
