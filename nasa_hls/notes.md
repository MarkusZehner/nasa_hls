# Notes
User interface for `download_tiles:
1. `make_tiles_dataset()` -> dict (gefiltert nach Wünschen in Zeiträumen)
2. `download_tiles(dict, dstdir)` -> none (calls download_batch)

## Development

**<ins> For Landsat-Scenes </ins>**

1. `ds = gdal.Open("HLS.L30.T34JDN.2018014.v1.4.hdf")`

2. `ds.GetMetadataItem("SENSING_TIME")[0:10]`

**<ins> For Sentinel-Scenes </ins>**


## Documentation

1. define make_tiles_dataset. Functionality:
+ download utm.kml to auxil path
+ intersect user shape with nasa tiles
+ extract for the given date