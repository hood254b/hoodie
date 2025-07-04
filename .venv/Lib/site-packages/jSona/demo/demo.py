# from jSona import save, load
from pprint import pprint as pp
from jSona import save, load

sample_data = {'hello':['world', 'everyone~']}
save("sample.json", sample_data, cry=True)

load_data = load("sample.json", cry=True)
pp(load_data)