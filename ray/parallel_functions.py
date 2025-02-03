import ray
ray.init()

@ray.remote
def f(x):
    return x * x * x

futures = [f.remote(i) for i in range(5)]
print(ray.get(futures)) # [0, 1, 8, 27, 64]