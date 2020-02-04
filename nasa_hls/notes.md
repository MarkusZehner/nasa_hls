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

## Tasks

7. API development for download of Sentinel-2 and Landsat-8 data
Contact: john.truckenbrodt@uni-jena.de
Data:
- NASA harmonized Sentinel-2 and Landsat-8 data (https://hls.gsfc.nasa.gov/)
Software:
- nasa-hls: https://github.com/benmack/nasa_hls
### Task:
- extension of the nasa-hls download tool with spatial querying: which tiles are (1) needed and
which (2) available for own study area?
- option to export a mosaic with custom extent (e.g. via shapefile) as GeoTiff making use of GDAL’s
VRT file format
- computation of at least three different spectral indices (e.g. NDVI, EVI, SAVI, ...)
- visualization of mosaics in Jupyter overlaid on top of Open Street Map (see packages ipyleaflet and
folium)