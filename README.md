# Public holidays 2026-2028 for 26 countries (CSV)

Free CSV of the public holidays of 26 countries and regions for 2026, 2027 and 2028, with observed (substitute) days and a flag on every row that says whether an independent implementation confirmed the date.

Regions: United States (`US`), United Kingdom (England) (`GB-ENG`), Canada (`CA`), Australia (New South Wales) (`AU-NSW`), Germany (`DE`), France (`FR`), Japan (`JP`), Brazil (`BR`), Mexico (`MX`), Spain (`ES`), Italy (`IT`), Ireland (`IE`), New Zealand (`NZ`), Singapore (`SG`), Sweden (`SE`), Poland (`PL`), Belgium (`BE`), Austria (`AT`), Switzerland (Zürich) (`CH-ZH`), Portugal (`PT`), Denmark (`DK`), Norway (`NO`), Finland (`FI`), Czechia (`CZ`), Chile (`CL`), Colombia (`CO`).

For federal countries the file uses one subdivision (England, New South Wales, Zurich) because their holidays differ by region; Canada (`CA`) is the five holidays the `holidays` package lists for Canada with no province (New Year's Day, Good Friday, Canada Day, Labour Day, Christmas Day); it is not the federal statutory list, and every province adds more.

## Files

`data/public_holidays_2026_2028.csv`: 941 rows, one per holiday and date.

| column | example | notes |
|---|---|---|
| region | GB-ENG | ISO 3166-1 country code, or country-subdivision |
| country_code | GB | |
| subdivision_code | ENG | empty for national calendars |
| date | 2026-12-28 | ISO date |
| weekday | Mon | |
| name | Boxing Day (observed) | English name where the source has one |
| name_local | Boxing Day (observed) | name in the main local language |
| is_observed_shift | 1 | 1 = substitute or bridge day off (for example a weekend holiday moved to Monday); not part of the base calendar |
| is_weekend | 0 | 1 = the date falls on Saturday or Sunday |
| is_estimated | 0 | 1 = the source labels the date as estimated |
| checked | 1 | 1 = a working-day date confirmed by an independent implementation (see below) |

`data/regions.csv`: region names, weekend days and which independent implementation confirmed each year.

```python
import csv
days_off = {(r["region"], r["date"]) for r in csv.DictReader(open("data/public_holidays_2026_2028.csv"))
            if r["is_weekend"] == "0"}
("GB-ENG", "2026-12-28") in days_off  # True: Boxing Day (observed)
```

```python
import pandas as pd
url = "https://raw.githubusercontent.com/plainfoldhq/world-public-holidays/main/data/public_holidays_2026_2028.csv"
df = pd.read_csv(url, dtype=str, keep_default_na=False)
df[(df.region == "DE") & (df.is_weekend == "0")]
```

```sql
-- DuckDB
SELECT date, name FROM read_csv_auto('https://raw.githubusercontent.com/plainfoldhq/world-public-holidays/main/data/public_holidays_2026_2028.csv')
WHERE region = 'JP' AND date BETWEEN '2027-01-01' AND '2027-12-31';
```

## How the data is made and checked

- Dates and names: exported from the open-source [`holidays`](https://github.com/vacanza/holidays) package (MIT), version 0.109, public holidays only (no bank-only, school or optional holidays).
- Check: for every region and year, the set of holiday dates that fall on working days must equal the set from at least one independent implementation: [`date-holidays`](https://github.com/commenthol/date-holidays) (npm) or [`workalendar`](https://github.com/workalendar/workalendar) (Python). Every region-year in this file passed; `regions.csv` names which one. The test runs in CI on every push (`tests/`). No data from those two projects is copied here; they are only used to compare.
- Holidays that fall on a weekend are listed (`is_weekend` = 1) but are not part of the check.

## Limits

- Future dates follow current law. Governments add, move or cancel holidays (one-off holidays, election days, bridge days), sometimes at short notice. Check official sources before payroll, legal or contract use.
- Regional holidays are only included for the one subdivision listed. Bank holidays that are not public holidays, and half days, are not included.

## More countries and years

The full set covers 156 countries and 60 subdivisions (UK nations, Australian states, Canadian provinces, German states, Swiss cantons), 2000-2050, wherever the same check passes, as CSV, JSON, SQLite and .ics with a business-day helper. Region-years where the implementations disagree are listed as not covered.
$19: [buy on Polar](https://buy.polar.sh/polar_cl_GyNejNT1XIOvB0AyazglLeeinrcYHfdmPngZm1qqqg0) (checkout and tax by Polar, merchant of record). Also part of the [All-Access yearly plan](https://buy.polar.sh/polar_cl_xydfuofU72fdp6xSOHFtihAuniUFagYOwR9zf2M03Gl) with all Plainfold data packs.

Readable tables, one page per country: [plainfoldhq.github.io/public-holidays](https://plainfoldhq.github.io/public-holidays/).

## License

Data in `data/`: CC0 1.0 (public domain). Tests: MIT. See LICENSE.

Made by Plainfold, an AI-run business. Issues and corrections: open an issue or email plainfoldhq@proton.me.
