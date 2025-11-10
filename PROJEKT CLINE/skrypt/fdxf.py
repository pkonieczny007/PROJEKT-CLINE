def sze(filename):
    with open(filename, mode='r', encoding='utf-8', errors='ignore') as file_obj:
        file = file_obj.read()
        lista = file.split()

    try:
        min_index = lista.index('$EXTMIN')
        max_index = lista.index('$EXTMAX')

        minx_index = min_index + 2
        maxx_index = max_index + 2

        minX = float(lista[minx_index])
        maxX = float(lista[maxx_index])

        szerokosc = int(maxX) - int(minX)
        return szerokosc
    except (ValueError, IndexError) as e:
        print(f"Błąd w pliku {filename}: {e}")
        return 0


def wys(filename):
    with open(filename, mode='r', encoding='utf-8', errors='ignore') as file_obj:
        file = file_obj.read()
        lista = file.split()

    try:
        min_index = lista.index('$EXTMIN')
        max_index = lista.index('$EXTMAX')

        miny_index = min_index + 4
        maxy_index = max_index + 4

        minY = float(lista[miny_index])
        maxY = float(lista[maxy_index])

        wysokosc = int(maxY) - int(minY)
        return wysokosc
    except (ValueError, IndexError) as e:
        print(f"Błąd w pliku {filename}: {e}")
        return 0

