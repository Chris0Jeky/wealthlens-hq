# Data Source Registry

Last updated: 2026-05-14

Track every source used by WealthLens. Do not use a dataset in a public chart unless it has a source record here.

## Required Fields

- Dataset title
- Direct URL
- Publisher
- File/API format
- Licence
- Release/update frequency
- Geographic coverage
- Known caveats

---

## Core Wealth and Income

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| Wealth and Assets Survey (WAS) | ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/latest | ONS | XLSX, HTML; microdata via UKDS (SN 7215) | OGL v3.0 (pubs); UKDS EUL (microdata) | Biennial (suspended) | GB | **Lost accredited official statistics June 2025.** Response rate collapsed 66% to 41%. Systematically undercounts top-tail wealth by ~£800bn. December 2024 DB pension methodology change cut measured wealth by ~2.3tn. |
| HBAI / Family Resources Survey | gov.uk/government/collections/households-below-average-income-hbai--2 | DWP | ODS/XLSX; CSV via Stat-Xplore; microdata via UKDS (SN 5828/4969) | OGL v3.0 | Annual (March) | UK | Series break from FYE 2022. Primary income distribution source. |
| DWP Stat-Xplore | stat-xplore.dwp.gov.uk | DWP | JSON API (SuperWEB REST) | OGL v3.0 | Per dataset | UK | Free registration + API key. |
| World Inequality Database (WID) | wid.world/country/united-kingdom/ | WID | CSV, XLSX, R/Stata packages | CC-BY | Annual (irregular) | 200+ countries | Top shares back to early 1900s. DINA methodology. gpinter package for Pareto interpolation. |
| ONS Effects of Taxes and Benefits (ETB) | ons.gov.uk/.../theeffectsoftaxesandbenefitsonhouseholdincome/latest | ONS | XLSX | OGL v3.0 | Annual (September) | UK | Since 1977. ~5,000 household sample. |
| ONS Income Bulletin | ons.gov.uk | ONS | Statistical bulletin | OGL v3.0 | Annual | UK | Latest disposable-income Gini: 32.9% FYE 2024. |
| Understanding Society (UKHLS) | understandingsociety.ac.uk | Essex/UKDS | Stata/SPSS | UKDS EUL/SL | Annual | UK | Wave 14 (2025). Panel data with intergenerational links. |
| English Longitudinal Study of Ageing (ELSA) | elsa-project.ac.uk | UCL/UKDS | Stata/SPSS | UKDS EUL | Biennial | England | Wealth in later life. |
| LIS/LWS (Luxembourg Income/Wealth Study) | lisdatacenter.org | LIS | Microdata; DART web tool; LISSY remote-execution | Free Key Figures tier | Ongoing | Cross-national | Gold-standard harmonised microdata. |

## Tax and Revenue

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| HMRC Capital Gains Tax Statistics | gov.uk/government/statistics/capital-gains-tax-statistics | HMRC | ODS/XLSX | OGL v3.0 | Annual (July/Aug) | UK | 92% of gains accrue to top 1%. |
| HMRC Inheritance Tax Statistics | gov.uk/government/statistics/inheritance-tax-liabilities-statistics | HMRC | ODS/XLSX | OGL v3.0 | Annual | UK | Only ~4-5% of estates pay IHT. |
| HMRC Personal Incomes / SPI | gov.uk/government/collections/personal-incomes-statistics | HMRC | ODS/XLSX | OGL v3.0 | Annual (~2-year lag) | UK | Percentile points; region/LA/constituency. Excludes non-taxpayers. |
| HMRC Tax Receipts & NICs | gov.uk/government/statistics/hmrc-tax-receipts-and-national-insurance-contributions-for-the-uk | HMRC | ODS, HTML | OGL v3.0 | Annual + monthly | UK | Cleanest source for tax composition chart. |
| HMRC Personal Wealth Statistics | gov.uk/government/collections/distribution-of-personal-wealth-statistics | HMRC | PDF/XLSX | OGL v3.0 | Dormant (last: Jan 2019) | UK | Effectively discontinued. |
| HMRC Non-domiciled Taxpayer Stats | Via HMRC | HMRC | ODS/PDF | OGL v3.0 | Annual (July) | UK | Non-dom regime abolished April 2025. |
| HMRC ATED Statistics | Via HMRC | HMRC | ODS | OGL v3.0 | Annual | UK | Annual Tax on Enveloped Dwellings. |
| HMRC Stamp Tax Statistics | Via HMRC | HMRC | ODS | OGL v3.0 | Annual | UK | Property type, region. |
| IFS TaxLab | ifs.org.uk/taxlab | IFS | Interactive + XLSX | Free with attribution | Rolling | UK | Tax-system explorer. |
| Wealth Tax Commission | wealthandpolicy.com | WTC | PDF + spreadsheets | Free | One-off (Dec 2020) | UK | 24 background papers. Code bundle on UKDS ReShare. |
| OBR Forecast | Via OBR | OBR | XLSX | Free | Twice yearly | UK | Full models for fiscal-impact simulators. |

## Housing and Property

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| ONS Housing Affordability | ons.gov.uk/.../housingaffordabilityinenglandandwales/latest | ONS | XLSX | OGL v3.0 | Annual | England & Wales | 1997-2024. LA/constituency/MSOA granularity. |
| ONS HPSSA (small-area prices) | ons.gov.uk/.../medianhousepricesforadministrativegeographies | ONS | XLSX, CSV | OGL v3.0 | Quarterly rolling | England & Wales | |
| UK House Price Index | gov.uk/government/statistical-data-sets/uk-house-price-index | Land Registry | CSV, SPARQL | OGL v3.0 | Monthly | UK | LA granularity. |
| Land Registry Price Paid Data | gov.uk/government/statistical-data-sets/price-paid-data-downloads | Land Registry | CSV (~5GB) | OGL v3.0 | Monthly | England & Wales | 1995-present. |
| Land Registry SPARQL | landregistry.data.gov.uk/landregistry/sparql | Land Registry | SPARQL -> JSON/CSV | OGL v3.0 | Monthly | England & Wales | 400m+ triples. |
| HMLR Overseas Companies (OCOD) | Via HMLR | Land Registry | CSV | OGL v3.0 | Monthly | England & Wales | Title-level, jurisdiction. 1999-present. |
| English Housing Survey | Via DLUHC | DLUHC | XLSX live tables | OGL v3.0 | Annual | England | Tenure, region, dwelling. Since 1967. |
| ONS Private Rents (PIPR) | Via ONS | ONS | XLSX, CSV, JSON | OGL v3.0 | Monthly | England | LA, BRMA. On Beta API. |
| Valuation Office Agency (VOA) | Via VOA | VOA | Data | OGL | Varies | England & Wales | Council tax bands, rental data. |

## Regional and Geographic

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| Regional GDHI | ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome | ONS | XLSX; CSV via Nomis | OGL v3.0 | Annual (~21-month lag) | UK | Westminster GDHI per head £79,555 vs UK avg £24,836. |
| ONS Regional GDP per Head | Via ONS | ONS | XLSX | OGL v3.0 | Annual (April) | UK | ITL1-3, LA. |
| ONS ASHE Earnings | Via ONS | ONS | XLSX | OGL v3.0 | Annual | UK | Region, occupation, age. |
| ONS Small-area Income Estimates | Via ONS | ONS | XLSX + interactive | OGL v3.0 | Annual | England & Wales | MSOA level. |
| IMD 2019 (English Indices of Deprivation) | gov.uk/government/statistics/english-indices-of-deprivation-2019 | MHCLG | CSV | OGL | Periodic | England | LSOA -> deprivation decile. Check for 2025 update. |
| ONS Life Expectancy by Deprivation | ons.gov.uk/.../healthinequalities | ONS | XLSX + HTML | OGL v3.0 | Annual/biennial | UK | IMD decile; LSOA-level. |
| Centre for Cities Data Tool | centreforcities.org/data/data-tool/ | Centre for Cities | Interactive + CSV | Free with attribution | Annual + monthly | 63 cities, 575 constituencies | Includes Gini. |
| Nomis API | nomisweb.co.uk/datasets/gdhi | ONS | REST + bulk CSV | OGL v3.0 | Annual | UK | No auth required. |

## Poverty and Living Standards

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| Children in Low Income Families | Via DWP/HMRC | DWP/HMRC | XLSX | OGL v3.0 | Annual | UK | LA, constituency, ward. |
| FCA Financial Lives Survey | Via FCA | FCA | XLSX tracker tables | OGL-style | Biennial -> annual | UK | Adults by region, age, vulnerability. |
| JRF UK Poverty Statistics | jrf.org.uk/uk-poverty-statistics | JRF | XLSX | Free with attribution | Annual | UK | Companion to annual UK Poverty report. |
| End Child Poverty constituency map | endchildpoverty.org.uk | Loughborough CRSP | Interactive | Free | Annual | England | CRSP methodology. |
| Trust for London Poverty Profile | trustforlondon.org.uk/data/ | Trust for London | Interactive + per-chart exports | Free | 2025/26 | London | 100+ indicators across 32 boroughs. Best London data. |
| Trussell Food Parcel Statistics | Via Trussell | Trussell | PDF + ODS | Free with attribution | Annual | UK | 2.89m parcels 2024/25. ~50x the 2010/11 figure. |

## Employment and Pay

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| High Pay Centre CEO Pay Report | Via HPC | High Pay Centre | PDF | Free with attribution | Annual (Aug/Sept) | UK | FTSE 100 aggregate. Manual data entry required. |

## Corporate and Financial Transparency

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| Companies House API | developer-specs.company-information.service.gov.uk | Companies House | JSON REST | Crown free reuse | Live | UK | Free API key. 600 req/5min. |
| Companies House PSC Bulk | download.companieshouse.gov.uk/en_pscdata.html | Companies House | JSON-Lines (3GB compressed) | Crown free reuse | Weekly/Daily | UK | Beneficial ownership. |
| Open Ownership BODS | bods-data.openownership.org/source/UK_PSC/ | Open Ownership | JSON-Lines | CC-BY | Weekly | UK | Cleaned PSC data. |
| Electoral Commission Donations | Via Electoral Commission | Electoral Commission | CSV | Free | Quarterly + monthly | UK | From July 2017. |
| OpenCorporates | Various | OpenCorporates | API | Free for journalists/NGOs | Live | Global | 220m+ companies. |
| ICIJ Offshore Leaks Database | Via ICIJ | ICIJ | Database | Free | Irregular | Global | |

## Rich Lists and Top-Tail Data

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| Sunday Times Rich List | thetimes.com/sunday-times-rich-list | Times | HTML | Paywalled | Annual (May) | UK | Tippet & Wildauer (PEGFA Greenwich) reconstructed 1989-2024 openly. |
| Forbes Billionaires | forbes.com/billionaires/ | Forbes | HTML/scraped | Paywalled effectively | Annual + live | Global | No official API. |
| Knight Frank Wealth Report | knightfrank.com/wealthreport | Knight Frank | PDF | Free with registration | Annual (March) | Global | Proprietary Wealth Sizing Model. |

## Widening Participation and Education

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| OfS Postcode CSV (POLAR4/TUNDRA/ABCS) | officeforstudents.org.uk/.../get-the-postcode-data/ | OfS | CSV (186 MB) | OGL v3 | Annual (Feb 2026 release) | England | POLAR4, TUNDRA, ABCS quintiles. |
| DfE LEO (Longitudinal Education Outcomes) | explore-education-statistics.service.gov.uk/.../leo-graduate-and-postgraduate-outcomes/ | DfE | CSV via EES API | OGL | Annual | England | Sector and provider level. FSM only at sector level. |
| GIAS (Get Information About Schools) | get-information-schools.service.gov.uk | DfE | Public API | OGL | Live | England | School directory with FSM%, URN lookup. |
| Discover Uni dataset | hesa.ac.uk/support/tools-and-downloads/unistats | HESA | ZIP | CC BY 4.0 | Weekly | UK | NSS, Graduate Outcomes, continuation, tariff. Course-level. |
| OfS Access & Participation Dashboard | officeforstudents.org.uk/.../get-the-data/ | OfS | CSV | OGL | Annual | England | Access, continuation, completion, attainment, progression. |
| UCAS End-of-cycle / Equality Data | Via UCAS | UCAS | CSV + dashboards | Free with attribution | Annual | UK | Applicants, school type, FSM. |
| HESA Open Data | Via HESA | HESA | CSV/XLSX | CC BY 4.0 | Annual | UK | Provider, student. |
| postcodes.io | api.postcodes.io/postcodes/{postcode} | postcodes.io | REST API | MIT | Live | UK | No API key. Self-hostable. |
| DfE WP Statistical Release | explore-education-statistics.service.gov.uk | DfE | CSV/HTML | OGL | Annual | England | Progression to HE by age 19: FSM, SEND, care, POLAR, ethnicity. |

## International Comparators

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| World Bank PIP | pip.worldbank.org | World Bank | Headcount and Gini | Free | Ongoing | Global | Harmonised household surveys. |
| OECD Income Distribution Database | stats.oecd.org | OECD | CSV/JSON/XML via SDMX | OECD terms | 2-3x/year | OECD | UK as one country. |
| OECD "Compare Your Income" | compareyourincome.org | OECD | Interactive | Free | Periodic | OECD | Best-in-class personal-comparator design. |
| US Federal Reserve DFA | federalreserve.gov/releases/z1/dataviz/dfa/ | Federal Reserve | Interactive + CSV | Free | Quarterly | US | Gold-standard wealth dashboard. No UK equivalent. |

## Bank of England

| Source | URL | Publisher | Format | Licence | Update | Coverage | Notes |
|---|---|---|---|---|---|---|---|
| BoE IADB | bankofengland.co.uk/boeapps/database/ | BoE | CSV, XLSX, XML | OGL-equivalent | Monthly/quarterly | UK | Most machine-friendly UK source. Parameterised URL pattern. |
| BoE NMG Household Survey | bankofengland.co.uk/statistics/research-datasets | BoE | XLSX + Stata .do | Free with attribution | Annual | GB | ~6,000 households per wave. |
| BoE MLAR | bankofengland.co.uk/statistics/mortgage-lenders-and-administrators | BoE | XLSX | BoE terms | Quarterly | UK | LTV/LTI risk distribution, arrears. |

## Existing Visualisation Tools (reference)

| Source | URL | Notes |
|---|---|---|
| Our World in Data | ourworldindata.org/economic-inequality | CC-BY. Per chart slug CSV available. |
| ONS Census 2021 Interactive Maps | ons.gov.uk/census/maps | Open source (Svelte Kit + Maplibre GL JS). OA-level. No wealth data. |
| ONS "Build a Custom Area Profile" | ons.gov.uk/visualisations/customprofiles | Draw polygon aggregate. Open source. |
| ONS "How Do You Compare?" | ons.gov.uk/visualisations/dvc1802/calculator/ | **Stale (March 2022)**. Not updated. Pre-pandemic data. |
| Tax Justice Network Financial Secrecy Index | fsi.taxjustice.net | v8.0 June 2025. |
| "Wealth, shown to scale" | github.com/mkorostoff/1-pixel-wealth | Open source viral scroller. |
| PolicyEngine UK | policyengine.org | Open-source UK tax-benefit microsimulation. |
