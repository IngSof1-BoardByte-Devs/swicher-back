import time
from enum import Enum

def get_figures(array):
    '''
        Función que retorna una lista de figuras y sus índices originales
    '''
    figures = []
    for i in range(36):
        if any(figure[0][i] for figure in figures):
            continue
        figure, indices = dfs_iter(i, array)
        # Si la figura tiene 4 o 5 casillas, se agrega a la lista de figuras
        if 4 <= figure.count(True) < 6:
            figures.append((figure, indices))
    return figures

def dfs_iter(s, array):
    '''
        Función que retorna una figura y sus índices originales dado un punto de inicio
    '''
    figure = [False] * 36 # Inicializar todos los vértices como no figura
    indices = []  # Lista para almacenar los índices originales

    # Inicializar la pila con la casilla inicial
    stack = [s]
    while stack:
        v = stack.pop()
        if figure[v]:   # Si ya se agregó a la figura, se salta a la siguiente iteración
            continue    
        figure[v] = True
        indices.append(v)  # Agregar el índice original
        x, y = v % 6, v // 6  # Coordenadas x e y de la celda actual
        candidates = []
        if x > 0: candidates.append(v - 1)  # Celda a la izquierda
        if x < 5: candidates.append(v + 1)  # Celda a la derecha
        if y > 0: candidates.append(v - 6)  # Celda arriba
        if y < 5: candidates.append(v + 6)  # Celda abajo
        for i in candidates:
            if array[i] == array[v]:  # Si la casilla es válida y tiene el mismo número
                stack.append(i)

    return figure, indices

def normalize_figures(figures):
    '''
        Función que normaliza las figuras (moverlas a la esquina superior izquierda)
    '''
    valid_figures = []  # Lista para almacenar las figuras válidas
    for figure, indices in figures:
        min_x = min(i % 6 for i, val in enumerate(figure) if val)
        min_y = min(i // 6 for i, val in enumerate(figure) if val)
        new_figure = [False] * 36
        for i in range(36):
            if figure[i]:
                x = i % 6
                y = i // 6
                new_figure[(x - min_x) + 6 * (y - min_y)] = True
        valid_figures.append((new_figure, indices))
    return valid_figures

def array_to_int(array):
    '''
        Función que convierte un array a un entero
    '''
    max_col = max_row = 0
    for i in range(len(array)):
        if array[i]:
            max_col = max(max_col, i % 6)
            max_row = max(max_row, i // 6)
    figure = str(max_row+1) + str(max_col+1)  # Agrega max_row y max_col al principio
    for i in range(max_row + 1):  # Cambiado a max_row + 1
        for j in range(max_col + 1):  # Cambiado a max_col + 1
            if array[i * 6 + j]:
                figure += '1'
            else:
                figure += '0'
    print(figure)
    return figure

# Diccionario de figuras
fig_values = {
    33100111100: 'fig1', 33111010010: 'fig1', 33001111001: 'fig1', 33010010111: 'fig1', 2411000111: 'fig2', 4201111010: 'fig2', 2411100011: 'fig2', 4201011110: 'fig2',
    2400111110: 'fig3', 4210101101: 'fig3', 2401111100: 'fig3', 4210110101: 'fig3', 33100110011: 'fig4', 33011110100: 'fig4', 33110011001: 'fig4', 33001011110: 'fig4',
    1511111: 'fig5', 5111111: 'fig5', 33100100111: 'fig6', 33111100100: 'fig6', 33111001001: 'fig6', 33001001111: 'fig6', 2411110001: 'fig7', 4201010111: 'fig7', 2410001111: 'fig7',
    4211101010: 'fig7', 2400011111: 'fig8', 4210101011: 'fig8', 2401111000: 'fig8', 4211010101: 'fig8', 33001111010: 'fig9', 33010110011: 'fig9', 33010111100: 'fig9',
    33110011010: 'fig9', 33001111100: 'fig10', 33110010011: 'fig10', 33100111010: 'fig11', 33011110101: 'fig11', 33010111001: 'fig11', 33010011110: 'fig11', 33100111001: 'fig12',
    33011010110: 'fig12', 2411110010: 'fig13', 4201011101: 'fig13', 2401001111: 'fig13', 4210111010: 'fig13', 2400101111: 'fig14', 4210101110: 'fig14', 2401110100: 'fig14', 
    4201110101: 'fig14', 23011111: 'fig15', 32101111: 'fig15', 23111110: 'fig15', 32111101: 'fig15', 23101111: 'fig16', 32111011: 'fig16', 23111101: 'fig16', 32110111: 'fig16',
    33010111010: 'fig17', 23111011: 'fig18', 32011111: 'fig18', 23110111: 'fig18', 32111110: 'fig18', 23011110: 'fig19', 32101101: 'fig19', 221111: 'fig20', 23110011: 'fig21', 
    32011110: 'fig21', 23010111: 'fig22', 32101110: 'fig22', 23111010: 'fig22', 32011101: 'fig22', 23111001: 'fig23', 32010111: 'fig23', 23100111: 'fig23', 32111010: 'fig23', 
    141111: 'fig24', 411111: 'fig24', 23001111: 'fig25', 32101011: 'fig25', 23111100: 'fig25', 32110101: 'fig25'}

# Función Main
if __name__ == "__main__":
    start_time = time.time()

    board =[0, 1, 2, 3, 3, 0, 
            3, 2, 3, 1, 0, 3, 
            1, 0, 3, 0, 2, 1, 
            1, 0, 3, 1, 1, 2, 
            0, 0, 3, 1, 2, 2, 
            1, 2, 3, 0, 2, 2  ]

    figures = get_figures(board)
    figures = normalize_figures(figures)
    for figure, indices in figures:
        figure_int = array_to_int(figure)
        figure_name = fig_values.get(int(figure_int), "Unknown")
        print(f"Figura: {figure_name}, Índices originales: {indices}")

    end_time = time.time()
    print("--- %s seconds ---" % (time.time() - start_time))

    0, 1, 2, 3, 3, 0, 
    3, 2, 1, 3, 0, 3, 
    1, 0, 3, 0, 2, 1, 
    1, 0, 3, 1, 1, 2, 
    0, 3, 0, 1, 2, 2, 
    1, 3, 2, 0, 2, 2    