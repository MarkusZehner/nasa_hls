import nasa_hls

available_tiles = nasa_hls.get_available_tiles_from_url()
print("Total number of tiles: ", len(available_tiles))
print("First tiles: ", available_tiles[:3])
print("Last tiles: ", available_tiles[-3:])

print(type(available_tiles))







