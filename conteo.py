from typing import Any, List, Tuple
import cv2
import numpy as np
from random import randrange

class Stack():
    def __init__(self) -> None:
        self.list = []

    def append(self, item: Any) -> None:
        self.list.append(item)

    def pop(self) -> Any:
        if(len(self.list) != 0):
            return self.list.pop()
        else:
            raise IndexError()

    def peek(self) -> Any:
        if(len(self.list) != 0):
            return self.list[-1]
        else:
            raise IndexError()

    def __len__(self) -> int:
        return len(self.list)

def ObtenerVecindad(coordenadas: List, resolucion: Tuple) -> List:
    vecinos = []
    i = coordenadas[0]
    j = coordenadas[1]

    for fila in range(-1,2):
        fila_vecino = i + fila
        
        if((fila_vecino >= 0) and (fila_vecino < resolucion[0])):
            vecinos.append([i + fila, j])

    for columna in range(-1,2):
        columna_vecino = j + columna

        if((columna_vecino >= 0) and (columna_vecino < resolucion[1])):
            vecinos.append([i, j + columna])

    vecinos.remove([i,j])

    return vecinos


imagen = cv2.imread("D:\\raulg\\Desktop\\Imagen.png")
grises = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
_, binaria = cv2.threshold(grises, 100, 200, cv2.THRESH_BINARY)

imagen_salida = np.zeros(binaria.shape, dtype = np.int32)

objetos = 0
pila = Stack()

for fila in range(binaria.shape[0]):
    for columna in range(binaria.shape[1]):
        if binaria[fila][columna] != 0:
            objetos += 1
            pila.append([fila, columna])

            binaria[fila][columna] = 0
            imagen_salida[fila][columna] = objetos

            while (not len(pila) == 0):
                coordenadas = pila.pop()
                vecinos = ObtenerVecindad(coordenadas, binaria.shape)

                for vecino in vecinos:
                    if binaria[vecino[0], vecino[1]] != 0:
                        pila.append([vecino[0], vecino[1]])
                        binaria[vecino[0]][vecino[1]] = 0
                        imagen_salida[vecino[0]][vecino[1]] = objetos

# cv2.imshow('Imagen 1', binaria)
# cv2.waitKey()
# cv2.imshow('Imagen 2', imagen_salida)
# cv2.waitKey()
colores = []

for i in range(objetos + 1):
    colores.append([randrange(255), randrange(255), randrange(255)])

for fila in range(imagen.shape[0]):
    for columna in range(imagen.shape[1]):
        if(imagen_salida[fila][columna] != 0):
            imagen[fila][columna] = colores[imagen_salida[fila][columna]]
cv2.imshow('Imagen 1', imagen)
cv2.waitKey()
print(imagen_salida)