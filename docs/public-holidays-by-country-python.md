# Public holidays by country from CSV in Python

The public holidays of 26 countries and regions for 2026-2028 are in one CSV, the free [world public holidays](https://github.com/plainfoldhq/world-public-holidays) file. This guide loads it with pandas, lists a country's holidays for a year, picks a region inside a country, counts working days in a month with numpy, and compares two countries. It ends with a cross-check against the Python `holidays` package. It uses pandas 3.1, numpy 2.4 and `holidays` 0.109 (the version the data was exported from) on Python 3.11, run from the root of the repo:

```
pip install pandas numpy holidays==0.109
```

All output below was produced by running the code in this order, in one session. The file covers 2026, 2027 and 2028 only.

## Load the CSV

```python
import pandas as pd

df = pd.read_csv("data/public_holidays_2026_2028.csv", dtype=str, keep_default_na=False)
print(len(df), "rows,", df.region.nunique(), "regions")
print(df.groupby("region").size().loc[["US", "GB-ENG", "DE", "JP"]].to_dict())
```

```
941 rows, 26 regions
{'US': 39, 'GB-ENG': 28, 'DE': 27, 'JP': 51}
```

There is one row per holiday and date. `region` is the key you filter on (`US`, `DE`, `GB-ENG`). `is_weekend` is `1` when the date falls on a Saturday or Sunday. `is_observed_shift` is `1` for a substitute day off. `dtype=str` keeps the flags as text; `keep_default_na=False` keeps the empty `subdivision_code` of national calendars as an empty string.

## Holidays for one country and year

```python
us = df[(df.region == "US") & (df.date.str[:4] == "2027")]
print(us[["date", "weekday", "name", "is_observed_shift", "is_weekend"]].to_string(index=False))
```

```
      date weekday                                            name is_observed_shift is_weekend
2027-01-01     Fri                                  New Year's Day                 0          0
2027-01-18     Mon                      Martin Luther King Jr. Day                 0          0
2027-02-15     Mon                           Washington's Birthday                 0          0
2027-05-31     Mon                                    Memorial Day                 0          0
2027-06-18     Fri Juneteenth National Independence Day (observed)                 1          0
2027-06-19     Sat            Juneteenth National Independence Day                 0          1
2027-07-04     Sun                                Independence Day                 0          1
2027-07-05     Mon                     Independence Day (observed)                 1          0
2027-09-06     Mon                                       Labor Day                 0          0
2027-10-11     Mon                                    Columbus Day                 0          0
2027-11-11     Thu                                    Veterans Day                 0          0
2027-11-25     Thu                                Thanksgiving Day                 0          0
2027-12-24     Fri                        Christmas Day (observed)                 1          0
2027-12-25     Sat                                   Christmas Day                 0          1
2027-12-31     Fri                       New Year's Day (observed)                 1          0
```

Holidays on a weekend stay in the file with `is_weekend = 1`, and the day off appears as a separate "(observed)" row. To get only the days people are off work, filter on `is_weekend == "0"`. This US calendar observes a Saturday holiday on the Friday, as federal employees do (June 18, December 24 and December 31 above). The Federal Reserve does not, so for bank settlement use a banking calendar instead.

## A region inside a country

Three entries are a single subdivision, because holidays differ by region there:

```python
print(df[df.subdivision_code != ""].groupby(["region", "country_code", "subdivision_code"]).size())
reg = pd.read_csv("data/regions.csv", dtype=str, keep_default_na=False)
print(reg[reg.region.isin(["GB-ENG", "AU-NSW", "CH-ZH"])][["region", "country", "subdivision"]].to_string(index=False))
```

```
region  country_code  subdivision_code
AU-NSW  AU            NSW                 39
CH-ZH   CH            ZH                  27
GB-ENG  GB            ENG                 28
dtype: int64
region        country     subdivision
GB-ENG United Kingdom         England
AU-NSW      Australia New South Wales
 CH-ZH    Switzerland          Zürich
```

Scotland, Wales, other Australian states and other Swiss cantons are not in the free file. Canada (`CA`) has no subdivision and is only five national holidays (see Limits).

```python
e = df[(df.region == "GB-ENG") & (df.date.str[:4] == "2027") & (df.is_weekend == "0")]
print(e[["date", "weekday", "name"]].to_string(index=False))
```

```
      date weekday                     name
2027-01-01     Fri           New Year's Day
2027-03-26     Fri              Good Friday
2027-03-29     Mon            Easter Monday
2027-05-03     Mon                  May Day
2027-05-31     Mon      Spring Bank Holiday
2027-08-30     Mon Late Summer Bank Holiday
2027-12-27     Mon Christmas Day (observed)
2027-12-28     Tue    Boxing Day (observed)
```

## Working days in a month

numpy's `busday_count` counts Monday to Friday days in a half-open range and skips a list of holidays. Pass the weekday holidays of the region and year:

```python
import numpy as np

def off_days(region, year):
    x = df[(df.region == region) & (df.date.str[:4] == str(year)) & (df.is_weekend == "0")]
    return x.date.tolist()

def working_days(region, year, month):
    first = np.datetime64(f"{year}-{month:02d}", "M")
    start, end = first.astype("datetime64[D]"), (first + 1).astype("datetime64[D]")
    weekdays = int(np.busday_count(start, end))
    return weekdays, int(np.busday_count(start, end, holidays=off_days(region, year)))

for reg_, y, m in [("GB-ENG", 2027, 5), ("US", 2027, 5), ("GB-ENG", 2027, 12), ("US", 2027, 12), ("DE", 2026, 12)]:
    wd, wk = working_days(reg_, y, m)
    print(f"{reg_:7} {y}-{m:02d}  weekdays {wd}  working days {wk}")
```

```
GB-ENG  2027-05  weekdays 21  working days 19
US      2027-05  weekdays 21  working days 20
GB-ENG  2027-12  weekdays 23  working days 21
US      2027-12  weekdays 23  working days 21
DE      2026-12  weekdays 23  working days 22
```

May 2027 has two English bank holidays (May 3 and May 31) but only Memorial Day in the US. December 2027 gives 21 for both for different reasons: England loses December 27 and 28, the US loses December 24 and 31. All countries in the file have a Saturday and Sunday weekend (`weekend_days` in `regions.csv`), which is what `busday_count` assumes by default.

## Compare two countries

Which weekday holidays of 2027 are in England but not in the US:

```python
def days(region, year):
    return set(df[(df.region == region) & (df.date.str[:4] == str(year)) & (df.is_weekend == "0")].date)

only_uk = sorted(days("GB-ENG", 2027) - days("US", 2027))
only_us = sorted(days("US", 2027) - days("GB-ENG", 2027))
both = sorted(days("US", 2027) & days("GB-ENG", 2027))
print("UK only:", only_uk)
print("US only:", only_us)
print("both:", both)
nm = df.set_index(["region", "date"]).name
for d in only_uk:
    print(d, nm["GB-ENG", d])
```

```
UK only: ['2027-03-26', '2027-03-29', '2027-05-03', '2027-08-30', '2027-12-27', '2027-12-28']
US only: ['2027-01-18', '2027-02-15', '2027-06-18', '2027-07-05', '2027-09-06', '2027-10-11', '2027-11-11', '2027-11-25', '2027-12-24', '2027-12-31']
both: ['2027-01-01', '2027-05-31']
2027-03-26 Good Friday
2027-03-29 Easter Monday
2027-05-03 May Day
2027-08-30 Late Summer Bank Holiday
2027-12-27 Christmas Day (observed)
2027-12-28 Boxing Day (observed)
```

Only two weekdays are a day off in both places: New Year's Day and the last Monday of May.

## Cross-check with the `holidays` package

The dates and names in the CSV were exported from `holidays` 0.109, so this is not an independent source. It tests that the file is an unaltered export and that the code above reads it correctly. Compare every row for all 26 regions:

```python
import holidays
print(holidays.__version__)
rows = diff_dates = diff_names = 0
for r in reg.itertuples():
    pkg = holidays.country_holidays(r.country_code, subdiv=r.subdivision_code or None, years=range(2026, 2029), language="en_US")
    ours = df[df.region == r.region]
    want = {(d.isoformat(), n) for d, n in pkg.items()}
    got = set(zip(ours.date, ours.name))
    rows += len(ours)
    date_diff = len({d for d, _ in want} ^ {d for d, _ in got})
    diff_dates += date_diff
    diff_names += len(want ^ got) - date_diff
print(rows, "rows compared;", diff_dates, "date differences;", diff_names, "name-only differences")
```

```
0.109
941 rows compared; 0 date differences; 0 name-only differences
```

Now recompute the numbers stated above directly from the package, without the CSV:

```python
def pkg_days(code, subdiv, year):
    h = holidays.country_holidays(code, subdiv=subdiv, years=year)
    return {d for d in h if d.weekday() < 5}

uk, usa = pkg_days("GB", "ENG", 2027), pkg_days("US", None, 2027)
print("UK only:", sorted(d.isoformat() for d in uk - usa) == only_uk)
print("US only:", sorted(d.isoformat() for d in usa - uk) == only_us)
for code, sub, y, m in [("GB", "ENG", 2027, 5), ("US", None, 2027, 5), ("GB", "ENG", 2027, 12), ("US", None, 2027, 12), ("DE", None, 2026, 12)]:
    first = np.datetime64(f"{y}-{m:02d}", "M")
    n = int(np.busday_count(first.astype("datetime64[D]"), (first + 1).astype("datetime64[D]"),
                            holidays=[np.datetime64(d) for d in pkg_days(code, sub, y)]))
    print(code, y, m, n)
```

```
UK only: True
US only: True
GB 2027 5 19
US 2027 5 20
GB 2027 12 21
US 2027 12 21
DE 2026 12 22
```

I found no disagreement. The repo's own tests go further: they compare each region and year with `date-holidays` (npm) or `workalendar`, which I did not run for this guide.

## Limits

- Covered: 2026, 2027 and 2028. Future dates follow current law, and governments add or move holidays at short notice.
- `CA` is five national holidays (New Year's Day, Good Friday, Canada Day, Labour Day, Christmas Day), not the federal list, and every province adds more. Its three observed rows and one US row (Veterans Day observed, 2028-11-10) have `checked = 0`, meaning no independent source confirmed that substitute day.
- Singapore dates in 2028 for Chinese New Year, Eid al-Fitr, Eid al-Adha and Vesak Day are marked `is_estimated = 1`.
- Regional holidays are only included for the one subdivision listed, and bank-only holidays and half days are not included.

## More countries and years

The [World Public Holidays 2000-2050 pack](https://buy.polar.sh/polar_cl_GyNejNT1XIOvB0AyazglLeeinrcYHfdmPngZm1qqqg0?utm_source=github&utm_medium=readme&utm_campaign=H&utm_content=world-public-holidays) ($19, one-time; Polar is the merchant of record and handles sales tax) covers 156 countries and 60 subdivisions (UK nations, Australian states, Canadian provinces, German states, Swiss cantons), 2000-2050, wherever the same check passes, as CSV, JSON, SQLite and .ics with a business-day helper. Region-years where the implementations disagree are listed as not covered.

It is also in the [All-Access yearly plan](https://buy.polar.sh/polar_cl_xydfuofU72fdp6xSOHFtihAuniUFagYOwR9zf2M03Gl?utm_source=github&utm_medium=readme&utm_campaign=ALLACCESS&utm_content=world-public-holidays) with every Plainfold data pack. Details: [README](../README.md#more-countries-and-years).

---

Made by Plainfold. Written with AI assistance.

Check official government sources before relying on a date.
