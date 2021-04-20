from typing import Any, List, Literal, Tuple, TypedDict
import cv2
import numpy as np
import matplotlib.pyplot as plt
from random import randrange

# Definición del tipo de diccionario que retornará ContarObjetos 
class Conteo_Objetos(TypedDict):
    imagen_marcada: np.ndarray
    imagen_binaria: np.ndarray
    matriz_objetos: np.ndarray
    objetos: int

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

def ObtenerVecindad(coordenadas: List, resolucion: Tuple, tipo_vecindad: Literal[4,8]) -> List[List[int]]:
    vecinos = []
    i = coordenadas[0]
    j = coordenadas[1]

    def ObtenerVecindadCuatro(resolucion: Tuple) -> None:
        for fila in range(-1,2):
            fila_vecino = i + fila
            
            if((fila_vecino >= 0) and (fila_vecino < resolucion[0])):
                vecinos.append([fila_vecino, j])

        for columna in range(-1,2):
            columna_vecino = j + columna

            if((columna_vecino >= 0) and (columna_vecino < resolucion[1])):
                vecinos.append([i, columna_vecino])
    
    def ObtenerVecindadOcho(resolucion: Tuple) -> None:
        for fila in range(-1,2):
            fila_vecino = i + fila
            for columna in range(-1,2):
                columna_vecino = j + columna
                
                if(((fila_vecino >= 0) and (fila_vecino < resolucion[0])) and ((columna_vecino >= 0) and (columna_vecino < resolucion[1]))):
                    vecinos.append([fila_vecino, columna_vecino])

    switch_vecinos = {
        4: lambda : ObtenerVecindadCuatro(resolucion),
        8: lambda : ObtenerVecindadOcho(resolucion)
    }

    switch_vecinos[tipo_vecindad]()
    vecinos.remove([i,j])

    return vecinos

def ContarObjetos(ruta_imagen: str, threshold: int, vecindad: Literal[4,8]) -> Conteo_Objetos:
    imagen = cv2.imread(ruta_imagen)
    
    if(not isinstance(imagen, np.ndarray)):
        raise FileNotFoundError

    if(not isinstance(threshold, int) or threshold < 0 or threshold > 255):
        raise ValueError("El valor del threshold debe ser del rango 0-255")

    grises = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    _, binaria = cv2.threshold(grises, threshold, 255, cv2.THRESH_BINARY)
    binariaCopia = np.copy(binaria)

    # Al finalizar el proceso de conteo de objetos, está variable indicará en que posiciones de la imagen se encontraron objetos.
    # Las coordenadas donde se haya encontrado el primer objeto estarán marcadas con un 1, las coordenadas donde se haya encontrado
    # el segundo objeto estarán marcadas con un 2, etc.
    matriz_objetos = np.zeros(binaria.shape, dtype = np.int32)

    objetos = 0
    pila = Stack()

    # El conteo de objetos funciona buscando un pixel blanco, al encontrarlo, busca en todos los vecinos
    # de ese pixel otros pixeles blancos hasta encontrar un pixel negro. El conjunto de pixeles blancos
    # que haya encontrado se considera como un objeto encontrado
    for fila in range(binaria.shape[0]):
        for columna in range(binaria.shape[1]):
            if binaria[fila][columna] != 0:
                objetos += 1
                pila.append([fila, columna])

                binaria[fila][columna] = 0
                matriz_objetos[fila][columna] = objetos

                while (len(pila)):
                    coordenadas = pila.pop()
                    vecinos = ObtenerVecindad(coordenadas, binaria.shape, vecindad)

                    for vecino in vecinos:
                        if binaria[vecino[0], vecino[1]] != 0:
                            pila.append([vecino[0], vecino[1]])
                            binaria[vecino[0]][vecino[1]] = 0
                            matriz_objetos[vecino[0]][vecino[1]] = objetos

    colores = []

    for i in range(objetos + 1):
        colores.append([randrange(255) + i, randrange(255) + i, randrange(255) + i])

    for fila in range(imagen.shape[0]):
        for columna in range(imagen.shape[1]):
            if(matriz_objetos[fila][columna] != 0):
                imagen[fila][columna] = colores[matriz_objetos[fila][columna]]

    return {'imagen_marcada': imagen, 'imagen_binaria': binariaCopia, 'matriz_objetos': matriz_objetos, 'objetos': objetos}

try:
    ruta = input("Ingresa la ruta de la imagen a procesar: ")
    threshold = int(input("Ingresa el threshold que utilizar en la imagen: "))
    vecindad = int(input("Ingresa el tipo de vecindad a utilizar (4 u 8): "))

    if(vecindad != 4 and vecindad != 8):
        raise ValueError("El valor de la vecindad debe ser 4 u 8")

    resultado = ContarObjetos(ruta, threshold, vecindad)

    print(f"Se encontraron: {resultado['objetos']} objetos")

    plt.subplot(2,1,1)
    plt.imshow(resultado['imagen_binaria'], 'gray')
    plt.title("Imagen Binaria")

    plt.subplot(2,1,2)
    plt.imshow(resultado['imagen_marcada'], 'gray')
    plt.title("Imagen Marcada")

    plt.figtext(0, 0, f"Threshold: {threshold}. {resultado['objetos']} objetos encontrados. Vecindad de {vecindad}", fontsize = 10)
    
    plt.show()
except FileNotFoundError:
    print("El archivo de imagen no es valido")
except ValueError as error:
    print(error)
