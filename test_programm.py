import nasa_hls
#
# available_tiles = nasa_hls.get_available_tiles_from_url()
# print("Total number of tiles: ", len(available_tiles))
# print("First tiles: ", available_tiles[:3])
# print("Last tiles: ", available_tiles[-3:])
#
# print(type(available_tiles))

# returns list
urls_datasets = nasa_hls.get_available_datasets(products=["L30", "S30"],
                                                years=[2018],
                                                tiles=["32UNU", "32UPU"])  # here to be prompted a shape
print("Number of datasets: ", len(urls_datasets))
print("First datasets:\n -", "\n - ".join(urls_datasets[:3]))
print("Last datasets:\n -", "\n - ".join(urls_datasets[-3:]))

#das ist meine Version. Raus Hier!!!



