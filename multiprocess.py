from multiprocessing import Pool
from joblib import Parallel, delayed

import time

def medir_tiempo(func):
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fin = time.time()
        print(f"{func.__name__} ejecutada en: {fin - inicio:.5f} segundos")
        return resultado
    return wrapper

def process_item(item):
    # Some CPU-bound operation
    return item**2

@medir_tiempo
def heavy():
    data = range(1_000_000)
    results = Parallel(n_jobs=16)(
        delayed(process_item)(item) for item in data
    )

@medir_tiempo
def heavy2():
    data = range(1_000_000)
    with Pool(processes=16) as pool:  # Use 16 CPU cores
        results = pool.map(process_item, data)

if __name__ == "__main__":
    heavy()
    heavy2()