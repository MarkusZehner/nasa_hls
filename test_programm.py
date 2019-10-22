import nasa_hls
#
# available_tiles = nasa_hls.get_available_tiles_from_url()
# print("Total number of tiles: ", len(available_tiles))
# print("First tiles: ", available_tiles[:3])
# print("Last tiles: ", available_tiles[-3:])
#
# print(type(available_tiles))


# returns dataframe
df_datasets = nasa_hls.get_available_datasets(products=["L30", "S30"],
                                              years=[2018],
                                              tiles=["32UNU", "32UPU"],
                                              return_list=False) 

print("Number of datasets: ", df_datasets.shape[0])
print(df_datasets.head(3))
print(df_datasets.tail(3))

