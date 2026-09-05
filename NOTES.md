# What I checked, and what the agent got wrong

## What the agent got wrong
The km-to-miles constant was the most subtle bug — the code had MILES_PER_KM = 1.609
and multiplied, which gives km² not miles. I verified this made sense: 100 km × 1.609
would be 160.9, not ~62. Once Bob renamed it KM_PER_MILE and divided instead, 100 km
correctly became 62.1 miles.

## What I checked before I accepted its work
I ran py verify.py after every round of fixes and read km_wachter.py directly to
confirm SERVICE_INTERVAL_KM is still 15000 and WARN_AT_PERCENT is still 80. I also
checked settings.cfg to make sure both values match the code.

## What the data actually said
Total mileage and age looked like the obvious predictors but turned out to have
near-zero correlation with breakdowns (r ≈ 0.002 and r ≈ -0.001). The real predictors
were km_since_service (r=0.40), avg_daily_km (r=0.25), and load_factor (r=0.22). The
risk score split the fleet into a top half with a 38% breakdown rate and a bottom half
with only 5% — a 7x separation. Four high-risk cars were not yet flagged by the 80% rule.