def fromArrayToString(array):
    algo = ""
    for i in array:
        algo += i+","

    algo = algo[:-1]
    return algo

def checkWinner(dic):

    stri = "pos"
    arra = []
    for i in range(0,9):
        arra += [dic[stri+str(i)]]

    arra2 = [arra[0:3],arra[3:6],arra[6:]]

    for i in arra2:
        if i[0] == i[1] == i[2] and i[0] != "  ":
            return (True,i[0])

    for i in range(0,3):
        if arra[i] == arra[i+3] == arra[i+6] and arra[i] != "  ":
            return (True,arra[i])

    if (arra2[0][0] != "  " and arra2[0][0] == arra2[1][1] == arra2[2][2]) or (arra2[0][2] != "  " and arra2[0][2] == arra2[1][1] == arra2[2][0]):
        return (True,arra2[1][1])

    if "  " not in arra:
        return (True,'velha')
    return (False,"  ")
