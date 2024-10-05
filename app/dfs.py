from typing import List
from typing import List

array = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36 ]

def dfs_rec(figure, s, array):
    if figure[s]:
        return
    
    # Marcar el vértice actual como parte de la figura
    figure[s] = True

    candidates = [s-6, s+6, s-1, s+1]

    # Visitar recursivamente todos las casillas adyacentes
    for i in candidates:
        if i >= 0 and i < 36 and array[i] == array[s]:
            dfs_rec(figure, i, array)

# s sería la casilla seleccionada y array el tablero
def dfs(s, array):
    figure = [False] * len(36) # Inicializar todos los vértices como no figura
    dfs(figure, s)
    return figure

# Versión no recursiva (iterativa) del algoritmo DFS
def dfs_iter(s, array):
    figure = [False] * len(36) # Inicializar todos los vértices como no figura

    # Inicializar la pila con la casilla inicial
    stack = [s]
    while stack:
        v = stack.pop()
        if figure[v]:   # Si ya se agregó a la figura, se salta a la siguiente iteración
            continue    
        figure[v] = True
        candidates = [v-6, v+6, v-1, v+1]   # casillas adyacentes candidatas
        for i in candidates:
            if i >= 0 and i < 36 and array[i] == array[v]:  # Si la casilla es válida y tiene el mismo número
                stack.append(i)
    return figure


mov1 = { -10, -14, 10, 14 }
mov2 = { -12, 12, -2, 2 }
mov3 = { -6, 6, -1, 1 }
mov4 = { -7, -5, 7, 5 }
mov5 = { -8, 11, 8, -11 }
mov6 = { -4, -13, 4, 13 }
mov7 = { -18, -4, 18, 4 }

mov1 = { (2, -2), (-2, 2), (-2, -2), (2, 2) }
mov2 = { (2, 0), (-2, 0), (0, 2), (0, -2) }
mov3 = { (1, 0), (-1, 0), (0, 1), (0, -1) }
mov4 = { (1, 1), (-1, -1), (1, -1), (-1, 1) }
mov5 = { (-2, 1), (2, -1), (-1, -2), (1, 2) }
mov6 = { (-2, -1), (2, 1), (-1, 2), (1, -2) }
mov7 = { (4, 0), (-4, 0), (0, 4), (0, -4) }

# Definir un tipo de dato para las coordenadas x, y
class Coords:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def re_fig( coordenadas: List[Coords] ) -> List[Coords]:
    min_x = min([x for (x, y) in coordenadas])
    min_y = min([y for (x, y) in coordenadas])
    return [(x - min_x, y - min_y) for (x, y) in coordenadas]

    
def is_isomorphic(mat_a, mat_b):
    """Verifica si dos matrices son isomorfas (idénticas)."""
    if len(mat_a) != len(mat_b) or len(mat_a[0]) != len(mat_b[0]):
        return False
    
    # Verificar si todas las casillas son iguales
    for i in range(len(mat_a)): # Recorrer todas las filas
        for j in range(len(mat_a[0])): # Recorrer todas las columnas
            if mat_a[i][j] != mat_b[i][j]:
                return False
    return True