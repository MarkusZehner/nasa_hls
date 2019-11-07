"""
still beta, not operational -- Konstantin 7.11.19
"""

datasets = get_available_datasets_from_tiles(products=["S30"],
                                             years=[2019])

print("Number of datasets: ", len(datasets))
print("First datasets:\n -", "\n - ".join(datasets[:3]))
print("Last datasets:\n -", "\n - ".join(datasets[-3:]))
