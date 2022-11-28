10 LET CAR = {"brand": "Ford", "model": "Mustang", "year": 1964, "power": 4.0}
11 PRINT CAR
12 LET A = CAR["model"]
13 PRINT A
14 PRINT A.KEYS
15 LET X = A.VALUES
20 END

10 LET CAR = {"brand": "Ford", "model": "Mustang", "year": 1964, "power": 4.0}
11 LET CAR["brand"] = "Toyota"
12 LET CAR["color"] = "red"
13 PRINT CAR
14 POP CAR["brand"]
15 PRINT CAR
20 END
