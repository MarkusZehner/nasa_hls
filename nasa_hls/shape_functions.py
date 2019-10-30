import zipfile
import requests
import geopandas as gp
import io
from pathlib import Path
import os
import matplotlib.pyplot as plt
import sys

def download_utm_tiles():
    """
    Function to solely download the NASA's kml file containing vectors of the global UTM grid.
    As the file needs ~100MB memory, the user is asked to download the file manually with the following code
    ----------------------------
    No input
    ----------------------------
    returns:
        0
            
    """

    import urllib
    url = "https://hls.gsfc.nasa.gov/wp-content/uploads/2016/03/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.kml"
    bool = True

    while bool == True:
        usr_inp = input("Are you sure if you want to download the NASA's global UTM-tiles?"
                     "\n~100MB memory is required"
                     "\n[y/N]")

        if usr_inp == "y":
            bool == False
            local_path = input("Location directory of file needed. Type:"
                               "")
            # local_path = os.getcwd() + "/ignored/UTM_tiles.kml"

            print(f"Downloading kml-file from url {url}...")
            urllib.request.urlretrieve(url, local_path)

        elif bool == "N":
            print("aborted."
                  "It's cleary to big for your Mac."
                  "LINUX LOVE")
            bool == False

        else:
            print("Input not readable.")

def download_hls_s2_tiles():
    """
    Brauchen wir diese Funktion eigentlich noch?
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
    pass


    ###################BAUSTELLE####################
# def get_tiles_from_UTM():
    #path_to_user_poly = os.getcwd() + "/ignored/user_shape/" + input("enter the local path to the shapefile of your
    # working area")

    UTM_tile_path = Path(input("Please input the path to the UTM-file"))

    try:
        Path.exists(UTM_tile_path)

        # wenn die UTM-tile.kml Datei schon existiert, dann nicht mehr download_utm_tiles call

    # Enable fiona driver, then read kml-file
    gp.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    df = gp.read_file(local_path, driver='KML')
    ###################BAUSTELLE####################


    path_to_user_poly = input("enter the local path to the shapefile of your working area")

    user_poly = gp.GeoDataFrame.from_file(path_to_user_poly)
    test_tiles = gp.GeoDataFrame.from_file(download_utm_tiles())
    intersections= gp.sjoin(user_poly, test_tiles, how="inner", op='intersects')

    # write id's in list
    tiles = intersections["Name"].tolist()
    print(tiles)

    return tiles


# # Plot the data
# fig, ax = plt.subplots(figsize=(12, 8))
# user_poly.plot(alpha=.5, ax=ax)
# plt.show()
