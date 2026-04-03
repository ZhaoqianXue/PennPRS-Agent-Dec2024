
------------------------------------------------------
50 traits, 48 prs models, 50000 validation individuals

Time:
1. PGS Download and Preproces: negligible
2. Calculate PRS Scores: 453.887005 seconds (0.13 h)
3. PRS validation: 1374.78 seconds (0.38 h). Average duration per trait per prs: 1 seconds. 
Total time = 0.13 + 0.38 ~ 0.51 h

Cost:
Persistent disk cost $200.00 per month: 5000 Disk (GB)
Compting cost $4.07 per hour: 64 CPUs, 416 RAM (GB)

1. PGS Download and Preproces: negligible
2. Calculate PRS Scores: 0.13 (time) * 4.07 (cost) = $0.529
3. PRS validation: 0.38 * 4.07 = $1.52 
Total computation cost = $1.52 + $0.529 ~ $2 
Total storage cost = $200

------------------------------------------------------
If for example we want to do: 500 traits, 1000 prs models, 50000 validation individuals (no need to do srWGS prescreening)

Time:
1. PGS Download and Preproces: negligible (~0.5 h)
2. Calculate PRS Scores: 2.6 h
3. PRS validation: 1000 * 500 = 500,000 seconds (138.8 h =  5.7 days)
Total time = 5.7 days

Cost:
Persistent disk cost $200.00 per month: 5000 Disk (GB)
Compting cost $4.07 per hour: 64 CPUs, 416 RAM (GB)

Total computation cost (Approximately) = 6 (days) * 24 * $4.07 ~ $585.41 
Total storage cost = $200

------------------------------------------------------
Storage: 5000 Disk (GB) is enough (storage cost = $200)



Finished