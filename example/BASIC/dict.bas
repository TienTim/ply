10 LET CAR = {"brand": "Ford", "model": "Mustang", "year": 1964, "power": 4.0}
11 PRINT CAR
12 LET A = CAR["model"]
13 PRINT A
20 END

10 LET CAR = {"brand": "Ford", "model": "Mustang", "year": 1964, "power": 4.0}
11 LET CAR["brand"] = "Toyota"
12 LET CAR["color"] = "red"
13 PRINT CAR
14 CAR.POP("brand")
15 PRINT CAR
20 END

10 LET CAR = {"brand": "Ford", "model": "Mustang", "year": 1964, "power": 4.0}
14 PRINT CAR.KEYS()
15 LET X = CAR.VALUES()
16 PRINT X
20 END

10 LET CAR = {"brand": "Ford", "model": "Mustang", "year": 1964}
11 PRINT CAR
15 LET X = {"seat": 5, "wheel": "sport", "power": 4.0}
20 CAR.UPDATE(X)
21 PRINT CAR
25 CAR.CLEAR()
30 PRINT CAR
40 END
