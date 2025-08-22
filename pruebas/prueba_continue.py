listado = [1,2,3,4,5,6,7,8,9,10]
lista_impares = []
for i in listado:
    if not (i % 2 == 0):
        lista_impares.append(i)
        continue
    print("Par:", i)
    
print(lista_impares)