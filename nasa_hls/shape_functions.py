import zipfile
import requests
import geopandas as gp
import io
import matplotlib.pyplot as plt


def download_hls_s2_tiles():
    """
    Docstring
    ----------------------------
    input:
    ----------------------------
    returns: 
        path to shapefile with nasa hls test sites

    """

    url = "https://hls.gsfc.nasa.gov/wp-content/uploads/2018/10/hls_s2_tiles.zip"
    local_path = "ignored/test_tiles/"

    print(f"Downloading shapefile from url {url}...")
    request = requests.get(url)
    zip = zipfile.ZipFile(io.BytesIO(request.content))
    print("DONE")
    zip.extractall(path=local_path)

    path_to_test_tiles = local_path + "hls_s2_tiles.shp"

    return path_to_test_tiles

def get_tiles_from_shape(user_polygon):

    # performing geometric intersection
    intersections = gp.sjoin(user_polygon, test_tiles, how="inner", op='intersects')

    # write UTM-codes in list
    names = intersections["Name"].tolist()
    print(f"The following UTM-tiles are intersecting with the input geometry:\n"
          f"{names}")

    return names

path_to_user_polygon = "/home/aleko-kon/projects/geo419/nasa-hls/ignored/user_shape/dummy_region.shp"
user_polygon = gp.GeoDataFrame.from_file(path_to_user_polygon)
test_tiles = gp.GeoDataFrame.from_file(download_hls_s2_tiles())


get_tiles_from_shape(user_polygon)

# # Plot the data
# fig, ax = plt.subplots(figsize=(12, 8))
# user_poly.plot(alpha=.5, ax=ax)
# plt.show()
