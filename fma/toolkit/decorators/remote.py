def model_method(func):
    func.__fma_node_method__ = True
    return func
