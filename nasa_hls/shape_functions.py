import zipfile
import requests
import geopandas as gp
import io
from pathlib import Path
import nasa_hls


# def download_hls_s2_tiles():
#     """
#     Brauchen wir diese Funktion eigentlich noch?
#     ----------------------------
#     input:
#     ----------------------------
#     returns:
#         path to shapefile with nasa hls test sites
#
#     """
#
#     url = "https://hls.gsfc.nasa.gov/wp-content/uploads/2018/10/hls_s2_tiles.zip"
#     local_path = "ignored/test_tiles/"
#
#     print(f"Downloading shapefile from url {url}...")
#     request = requests.get(url)
#     zip = zipfile.ZipFile(io.BytesIO(request.content))
#     print("DONE")
#     zip.extractall(path=local_path)
#
#     path_to_test_tiles = local_path + "hls_s2_tiles.shp"
#
#     return path_to_test_tiles

def get_required_tiles_from_UTM(path_to_utm_file="/home/aleko-kon/projects/geo419/nasa-hls/ignored/UTM_tiles.kml",
                                user_shape="/home/aleko-kon/projects/geo419/nasa-hls/ignored/user_shape/dummy_region.shp"):
    """
    :param path_to_utm_file: requires the path where the Nasa's world-covering UTM.kml file is stored.
    Do this manually by calling function 'download_utm_tiles'.

    :return: list of tile name [str of 5 digits starting with two numbers] which geographically intersect the user
    shape and the UTM tiles.
    """

    path_to_utm_file = Path(path_to_utm_file)
    Path.exists(path_to_utm_file)
    path_to_user_polygon = Path(user_shape)

    # Enable fiona driver, then read kml-file
    gp.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    UTM_tiles = gp.read_file(path_to_utm_file, driver='KML')


    # convert user_polygon into Gdf
    user_polygon = gp.GeoDataFrame.from_file(path_to_user_polygon)

    # perform intersection
    intersections = gp.sjoin(user_polygon, UTM_tiles, how="inner", op='intersects')

    # write UTM-codes in lis
    tiles = intersections["Name"].tolist()
    print(tiles)

    return tiles

def get_available_datasets_from_tiles(products=["S30"],
                                     years=[2018],
                                     user_shape="/home/aleko-kon/projects/geo419/nasa-hls/ignored/user_shape/dummy_region.shp"):

    # retrieve required tiles from the function above
    tiles = get_required_tiles_from_UTM(user_shape=user_shape)
    datasets = nasa_hls.get_available_datasets(products=products, years=years, tiles=tiles)

    return datasets



# testing zone
datasets = get_available_datasets_from_tiles(products=["S30"],
                                             years=[2019])

print("Number of datasets: ", len(datasets))
print("First datasets:\n -", "\n - ".join(datasets[:3]))
print("Last datasets:\n -", "\n - ".join(datasets[-3:]))

# # Plot the data
# fig, ax = plt.subplots(figsize=(12, 8))
# user_poly.plot(alpha=.5, ax=ax)
# plt.show()
