import os
import urllib
from pathlib import Path
import geopandas as gp
from nasa_hls.utils import get_available_datasets
import pandas as pd

path_data_win_konsti = os.path.join("D:", os.sep, "Geodaten", "#Jupiter", "GEO419", "data" + os.sep)
path_data_lin_konsti = os.path.join(os.path.expanduser('~'), 'Dokumente', 'nasa_hls', 'data' + os.sep)

path_data_lin_robin = os.path.join(os.path.expanduser('~'), 'python_projects', 'data', 'nasa_hls', 'hdf_tiles' + os.sep)

path_auxil = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.auxdata' + os.sep)


def download_kml():
    """
    Download the necessary .kml-file
    :param dst: desired destination
    :return: destination of the .kml-file

    """

    path = path_auxil + "utm.kml"

    if not os.path.exists(path):
        print(f"Creating new world UTM gird file in", path)
        src = (
            "https://hls.gsfc.nasa.gov/wp-content/uploads/2016/03/S2A_OPER_GIP_TILPAR_MPC__"
            "20151209T095117_V20150622T000000_21000101T000000_B00.kml")
        urllib.request.urlretrieve(src, path)
    else:
        print(f"UTM tiles already successfully downloaded to:\n", path, "\n")
    return path


def get_available_datasets_from_shape(products=None,
                                      years=None,
                                      shape=None):
    """
    Calls the Nasa's world-covering UTM.kml file being stored. Do this manually by calling function 'download_kml'.

    :param shape -> shape of the region of interest (ROI)
    :param years -> required years to be checked for
    :param products -> either "L30" or "S30", the Landsat 8 or Sentinel 2 product, respectively

    :return: list of tile name [str of 5 digits starting with two numbers] which geographically intersect the user
    shape and the UTM tiles.
    """

    # not needed here as we give it a valid shape from the "make_tiles_dataset"-function
    # try:
    #     shape = gp.read_file(shape)
    #     print("shape read")
    # except CPLE_OpenFailedError:
    #     print("thats not a the path to a vector geometry")
    # except DriverError:
    #     print("thats not a valid vector geometry")

    # define defaults
    # if shape is None:
    #    # print("no shape given") # raise error here
    # if products is None:
    #     products = ["S30"]

    if years is None:
        years = [2018]

    gp.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'  # Enable fiona driver, read in utm grid from kml
    utm_tiles = gp.read_file(download_kml(), driver='KML')

    # convert user_polygon into Gdf -> perform intersection
    # user_polygon = gp.GeoDataFrame.from_file(shape)
    match = gp.sjoin(shape, utm_tiles, how="inner", op='intersects')

    # write UTM-codes in list
    tiles = match["Name"].tolist()

    print("getting available datasets . . .")
    datasets = get_available_datasets(products=products, years=years, tiles=tiles, return_list=False)

    return datasets


def make_tiles_dataset(shape=None,
                       products=None,
                       date="2018-01-08",
                       start_date=None,
                       end_date=None):
    """
    :param: shape, date, start_date, end_date, product
    :return: dataset(s). contains date specific tiles in the spatial extent of the input shape.
    can be ingested by download_batch. Returns list when time span is specified

    is
    1. df -> when there is only a single date
    2. list of df -> when time span is specified (iterable)
    """

    # das muss in eine if-else schleife
    # if try works --> continue
    # if except --> break, da eh kein shapefile
    while True:
        try:
            shape = gp.read_file(shape)
            print("valid shape, process continues")

            # except CPLE_OpenFailedError:
            #     print("thats not a the path to a vector geometry")
            # except DriverError:
            #     print("thats not a valid vector geometry")

            # if shape is None:
            #     print("please specify a shape..!") # raise an error here!

            if products is None:
                products = ["S30"]

            if date:
                print(f"single date information: ", date)
            if start_date:
                print(f"starting date: ", start_date)
            if end_date:
                print(f"end date: ", end_date)

            datasets = None
            yyyy = [date[0:4]]
            print(f"year: ", yyyy)

            # SINGLE YEAR INPUT parse year from date input
            if not start_date:
                df = get_available_datasets_from_tiles(products=products, shape=shape, years=yyyy)
                # datasets = extract_date(df, datum = date)
                # datasets = show_available_dates(df)
                datasets = dates_to_dict(df)
<<<<<<< HEAD
            # TIME SPAN INPUT
            # yet to be developed!
=======

>>>>>>> 15ea0de73641eb85f9daef0debe878ed461752d4
            break


        except:
            print("something is wrong with your shapefile. This will not work\n\n")
            return None

    return datasets


def download_tiles(datasets = None,
                   dstdir = path_data_win_konsti + "hdf/",
                   date="2018-01-08",
                   start_date=None,
                   end_date=None):
    """
    Download from download_batch.
    Calls datasets from make_tiles_dataset and transfers it in a manner to be digested by
    download_hls_dataset.download_batch.
    A specific date, a date range with start and end date or a range number of file can be selected to be downloaded.

    :param: datasets, dstdir

    :returns: none
    """

    # TIME SPAN INPUT
    # yet to be developed!
    # if start_date:
    #     print(f"starting date: ", start_date)
    # if end_date:
    #     print(f"end date: ", end_date)
    # get_tiles()
    # dstdir = [mit der endung der tiles]
    #
    # if länge df == 1 -> download_batch()
    # else:
    #     for i in df:
    #         download_batch(dstdir = dstdir)

def show_available_dates(df):
    print("\n\n", type(df))
    df_sorted = df.sort_values(by=["date"])
    df_grouped = df_sorted.groupby(['date'], as_index=False).count()
    df_selected = df_grouped[["date", "product"]]

    return df_selected


def dates_to_dict(df):
    # sort dataframe by date
    df_sorted = df.sort_values(by=["date"])

    # make numpy array of unique dates
    unique_dates = df_sorted.date.unique()

    # create dictionary with keys being the unique dates
    dataframe_dict = {date: pd.DataFrame for date in unique_dates}

    # add rows of orignial dataframe as values
    for key in dataframe_dict.keys():
        dataframe_dict[key] = df[:][df.date == key]

    return dataframe_dict


######################################################
# specify date and date range in a this function here
######################################################

def extract_date(df, datum="2018-01-01", start_date=None, end_date=None):
    """
    expected Params
    :param date: date in the format "yyyy-mm-dd"
    :param df: dataframe-object returned by the "get_available_datasets_from_shape"-function
    --------
    returns:
    dataframe with scenes from the scpecified date
    """

    # set the date column to timestamp
    df["date"] = pd.Timestamp()

    # create logival vector for indexing later
    sel = df.date == pd.Timestamp(datum)

    if sel.any() == False:
        print("not data avaible at that date")
    else:
        df = df[sel]

    # check if specified date is in date column
    # if date not in df["date"]:
    #    print("\n \n For the tiles in your shapefile is no data at this date available")
    #    return None
    # else:
    #    df = df.loc[df["date"] == date]
    #    print("\n \n There are {nrows} scenes available for the specified date and location".format(nrows=df.shape[0]))

    return df
