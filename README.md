# GPS Telemetry Analysis

This takes GPS points from the trucks and turns them into status, time, distance and speed. There is no real telemetry in the repo. The Excel files are fake, and the API address and garage coordinates are left blank on purpose.

## Files

`GPS-GET-DATA.ipynb` pulls raw points from the tracker API. It keeps one row per 5-minute group and drops `0,0` coordinates.

`mtrans-gps2-analiz.py` reads the raw Excel and writes the status and km result.

`dummy_muqayise2.xlsx` is the raw table shape, with 5 fake rows. `dummy_muqayise3.xlsx` is the output shape, also 5 fake rows.

The real `muqayise2.xlsx`, `muqayise3.xlsx`, any CSV and any database stay out of git. See `.gitignore`.

## Before you run it

In the notebook, put your own values in:

- `API_URL` is `http://YOUR_HOST:PORT/api.php`
- `X-API-Key` is `YOUR_API_KEY`
- `QARAJ_LAT` and `QARAJ_LON` are `0.0000`

The analysis script has the same `0.0000` coordinates. If you leave them like that, nothing falls inside the 100 m garage radius, so you will not get a `Qarajda` status.

If you point the script at your own file, change `dummy_muqayise2.xlsx` and `dummy_muqayise3.xlsx` in the code. Do not commit the output.

```
pip install -r requirements.txt
python mtrans-gps2-analiz.py
```

The script overwrites `dummy_muqayise3.xlsx`.

## Raw columns

`vehicle_id`, `timestamp`, `latitude`, `longitude`, `speed`, `speed2`, `engine_speed`, `distance`.

`distance` is the cumulative odometer in km. `engine_speed` is engine RPM.

## What the script calculates

`final_speed` is `speed2`, cut at 120. Anything above 120 becomes 120. The `speed` column is not used here.

`Ay` is the month from `timestamp`.

`Müddət (saat)` is the time until the next point of the same truck, in hours. The last row of a truck has no next point, so it gets 0.

`Məsafə (km)` is the next odometer reading minus the current one. If the difference is negative, or if it is faster than `120 km/h + 5 km` for that gap, it is written as 0.

Status is the first rule that matches:

1. Gap longer than 2 hours, and the point starts between 23:00 and 07:00 — `Gecə Parklaması`
2. Gap longer than 2 hours — `Siqnal itən ərazi`
3. `final_speed > 0` — `Hərəkətdə`
4. Speed is 0 and `engine_speed > 0` — `Boşda işləmə`
5. Speed is 0 and the point is within 100 m of the garage — `Qarajda`
6. Speed is 0 and the point is away from the garage — `Yolda parklama`

If a `Yolda parklama` block is 5 minutes or shorter, it becomes `Svetofor / Qısa dayanma`.

`Məkan_Koordinatı` shows where the signal dropped and where it came back. For parking, a short stop, night parking and idling it shows that point. Moving and garage rows are just `-`.

`Maşın_Vəziyyəti` counts how many different days that truck has in that month. 20 or more means `Analizə Uyğundur`. Fewer than that means the month is incomplete (workshop, new truck, or a dead GPS).

The status text stays in Azerbaijani because that is what the output file uses.

## Excel reports

The pivots sit on top of the output table. Every one of them is filtered to `Maşın_Vəziyyəti = Analizə Uyğundur`, so a half-empty month does not bend the result.

Monthly working time: rows are `Ay` + `vehicle_id`, columns are `status`, values are `Müddət (saat)` as a percent of the row. That number is a share of the month, not hours.

Hourly working time: same percent, rows are `Hour` + `vehicle_id`. `Hour` is not in the script. It is an Excel formula, `HOUR(timestamp)`, from 0 to 23. The duration is counted on the hour the point started.

Average speed: average of `final_speed`, and only on `Hərəkətdə` rows. Parked and idling rows are 0, so they are left out.

Monthly km: sum of `Məsafə (km)`, again only `Hərəkətdə`. This is not the raw odometer. It is the cleaned gap between readings.

Those pivots live in the real workbook. They are not in this sample repo.
