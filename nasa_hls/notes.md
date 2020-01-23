@robin: Mit PyCharm Professional kannst du einfach ein Notebook in der repo dir 
erstellen (so wie ich jetzt test.ipynb). Dann einfach die Datei in PCh öffnen und, rechts
erscheint die Code Chunk Struktur :D So können wir auch den Report machen, denke ich. Fände 
ich besser als in Rmd... Es sein denn, es will tatsächliche Seiten haben. Dann würde ich 
Rmd mit Python chunks verwenden. (?)


## Get date-metadate from file

**<ins> For Landsat-Scenes </ins>**

1. `ds = gdal.Open("HLS.L30.T34JDN.2018014.v1.4.hdf")`

2. `ds.GetMetadataItem("SENSING_TIME")[0:10]`

**<ins> For Sentinel-Scenes </ins>**

## Don't set date-column to index in `extract-date()`

## [download_tiles.py]

1. define make_tiles_dataset. Functionality:
+ download utm.kml to auxil path
+ intersect user shape with nasa tiles
+ extract for the given date

<br> 
resolved get_available_datasets_from_ulr into get_available_datasets_from_tiles``