# GPS Telemetry Analysis

Maşınların GPS nöqtələrindən status, müddət, məsafə və sürət çıxarılır. Repoda real telemetriya yoxdur: Excel nümunələri saxtadır, API ünvanı və qaraj koordinatı boş qoyulub.

## Fayllar

- `GPS-GET-DATA.ipynb` — tracker API-dən xam nöqtələri götürür. Hər 5 dəqiqəlik qrupdan bir sətir saxlanılır, `0,0` koordinat atılır.
- `mtrans-gps2-analiz.py` — xam Excel-i oxuyur, status və km hesabını yazır.
- `dummy_muqayise2.xlsx` — xam cədvəlin sütunları, 5 saxta sətir.
- `dummy_muqayise3.xlsx` — analiz çıxışının sütunları, 5 saxta sətir.

Real `muqayise2.xlsx`, `muqayise3.xlsx`, CSV və verilənlər bazası `.gitignore`-dadır.

## İşə salmazdan əvvəl

Notebook-da bunları öz dəyərlərinlə əvəz et:

- `API_URL` — hazırda `http://YOUR_HOST:PORT/api.php`
- `X-API-Key` — hazırda `YOUR_API_KEY`
- `QARAJ_LAT` / `QARAJ_LON` — hazırda `0.0000`

Eyni koordinatlar analiz skriptində də `0.0000`-dır. Qaraj nöqtəsini yazmasan, 100 metr radiusu heç bir real dayanacağa düşməz və `Qarajda` statusu çıxmaz.

Öz xam faylını işlədəndə skriptdəki `dummy_muqayise2.xlsx` və `dummy_muqayise3.xlsx` adlarını dəyiş. Çıxış faylını git-ə əlavə etmə.

```
pip install -r requirements.txt
python mtrans-gps2-analiz.py
```

Skript `dummy_muqayise3.xlsx` faylının üstünə yazır.

## Xam sütunlar

`vehicle_id`, `timestamp`, `latitude`, `longitude`, `speed`, `speed2`, `engine_speed`, `distance`.

`distance` kumulyativ odometrdir (km). `engine_speed` mühərrikin RPM-idir.

## Analiz nə hesablayır

`final_speed` — `speed2`, 120-dən yuxarısı 120-yə kəsilir. `speed` bu skriptdə istifadə olunmur.

`Ay` — `timestamp`-in ayı.

`Müddət (saat)` — eyni maşının növbəti nöqtəsinə qədər olan vaxt (saniyə / 3600). Son sətirdə növbəti nöqtə yoxdur, 0 yazılır.

`Məsafə (km)` — növbəti odometr minus indiki. Fərq mənfidirsə, ya da bu müddətdə `120 km/saat + 5 km` ehtiyatını keçirsə, 0 yazılır.

Status birinci uyğun gələn şərtlə seçilir:

1. Müddət 2 saatdan çoxdur və nöqtə 23:00–07:00 arasında başlayır — Gecə Parklaması
2. Müddət 2 saatdan çoxdur — Siqnal itən ərazi
3. `final_speed > 0` — Hərəkətdə
4. Sürət 0, `engine_speed > 0` — Boşda işləmə
5. Sürət 0 və qaraja 100 m-dək — Qarajda
6. Sürət 0 və qarajdan uzaq — Yolda parklama

`Yolda parklama` eyni ardıcıl blokda 5 dəqiqə və ya daha qısadırsa, `Svetofor / Qısa dayanma` olur.

`Məkan_Koordinatı` — siqnal qopmasında qopma və bərpa nöqtəsi; park, svetofor, gecə parklama və boşda işləmədə həmin nöqtə. Hərəkətdə və qarajda `-`.

`Maşın_Vəziyyəti` — həmin maşının həmin ayında fərqli günlərin sayı. 20 və daha çoxdursa `Analizə Uyğundur`, azdırsa data natamam sayılır (təmir, yeni maşın, GPS).

## Excel hesabatları

Çıxış cədvəlinin üstündə pivot qurulur. Hamısında səhifə filtri `Maşın_Vəziyyəti = Analizə Uyğundur` olur ki, yarımçıq aylar nəticəni əyməsin.

- Ay üzrə işləmə: sətir `Ay` + `vehicle_id`, sütun `status`, dəyər `Müddət (saat)` cəminin sətir faizi. Rəqəm saat deyil, həmin ayın payıdır.
- Saat üzrə işləmə: eyni faiz, sətir `Hour` + `vehicle_id`. `Hour` skriptdə yoxdur, Excel-də `HOUR(timestamp)` düsturudur (0–23). Müddət nöqtənin başladığı saata düşür.
- Ortalama sürət: yalnız `Hərəkətdə` sətirlərində `final_speed` ortası. Park və boşda 0 olduğu üçün ora qatılmır.
- Aylıq km: yalnız `Hərəkətdə`, `Məsafə (km)` cəmi. Bu, xam odometrin özü deyil, təmizlənmiş interval fərqləridir.

Bu pivotlar real faylda qalır, nümunə repoya qoyulmayıb.
