
## Get date-metadate from file

**<ins> For Landsat-Scenes </ins>**

1. `ds = gdal.Open("HLS.L30.T34JDN.2018014.v1.4.hdf")`

2. `ds.GetMetadataItem("SENSING_TIME")[0:10]`

**<ins> For Sentinel-Scenes </ins>**

## Don't set date-colum to index in `extract-date()`

