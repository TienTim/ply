10 LET I = 0
20 WHILE I < 5
21 IF I > 3 THEN BREAK
30 PRINT I
40 NEXT I
50 END

1 LET I = 5
2 WHILE I >= 1
3 PRINT I
4 NEXT I
5 END

10 LET I = 0
20 WHILE TRUE
30 IF I > 5 THEN BREAK
40 PRINT I
50 LET I = I + 1
60 NEXT
70 END

5 DIM A(10,15)
10 FOR I = 1 TO 10
11 LET J = 0
20 WHILE J < 5
30   LET A(I,J) = I + J
40 NEXT J
50 NEXT I
100 FOR I = 1 TO 10
101 LET J = 1
110 WHILE J < 5
111   IF I = 3 THEN CONTINUE
120   PRINT A(I,J),
130 NEXT J
140 PRINT
150 NEXT I
999 END

20 FOR I = 0 TO 10
21 IF I > 5 THEN CONTINUE
30 PRINT I
40 NEXT I
50 END

10 LET CAR = {"brand": "Ford", "model": "Mustang", "year": 1964, "power": 4.0}
11 LET CAR["brand"] = "Toyota"
12 LET CAR["color"] = "red"
13 PRINT CAR
14 POP CAR["brand"]
15 PRINT CAR
20 END

10 LET CAR = {"brand": "Ford", "model": "Mustang", "year": 1964, "power": 4.0}
11 PRINT CAR
20 END


10 LET CAR = {"brand": "Ford", "model": "Mustang", "year": 1964, "power": 4.0}
11 PRINT CAR
12 LET A = CAR["model"]
13 PRINT A
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
