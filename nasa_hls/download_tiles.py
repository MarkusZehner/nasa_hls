import os
import urllib
import geopandas as gp
import pandas as pd

from nasa_hls.utils import get_available_datasets
from nasa_hls.download_hls_dataset import download_batch


# initiate auxillary file directory
path_auxil = os.path.join(os.path.expanduser('~'), '.nasa_hls', '.auxdata' + os.sep)

if not os.path.exists(path_auxil):
    os.makedirs(path_auxil)

def download_kml():
    """
    Download the necessary .kml-file
    :param dst: desired destination
    :return: destination of the .kml-file
    """

    # new path of the utm file
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

    if years is None:
        years = [2018]

    shape = gp.read_file(shape)

    if "Name" in shape:
        shape = shape.rename(columns={"Name": "name_shape"})

    gp.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'  # Enable fiona driver, read in utm grid from kml
    utm_tiles = gp.read_file(download_kml(), driver='KML')

    # convert user_polygon into Gdf -> perform intersection
    # user_polygon = gp.GeoDataFrame.from_file(shape)
    match = gp.sjoin(shape, utm_tiles, how="inner", op='intersects')

    # write UTM-codes in list
    tiles = match["Name"].tolist()

    print("\ngetting available datasets . . .")
    datasets = get_available_datasets(products=products, years=years, tiles=tiles, return_list=False)

    return datasets


def make_tiles_dataset(shape=None,
                       products=None,
                       date=None,
                       year=None,
                       start_date=None,
                       end_date=None):
    """
    :param: shape, products, date, year, start_date, end_date
    :return: dataset(s). contains date specific tiles in the spatial extent of the input shape.
    can be ingested by download_batch. Returns list when time span is specified
    """

    try:
        # convert given dates to pd.timestamp
        if date:
            date_timestamp = pd.Timestamp(date).date()
        if start_date:
            start_date = pd.Timestamp(start_date).date()
        if end_date:
            end_date = pd.Timestamp(end_date).date()
    except ValueError:
        # if this error is raised, all the rest should not even be evaluated
        print("provide a string in the format 'yyyy-mm-dd'")  # TODO: raise error

    if products is None:
        products = ["S30"]
    if date:
        print("single date: {date}\n ".format(date=date))
    if start_date:
        print("starting date: {date}\n ".format(date=start_date))
    if end_date:
        print("end date: {date}\n ".format(date=end_date))
    if year:
        print("year: {year}".format(year=year))

    # get the year (any year!!) in the format that get_available_datasets needs
    # we need a year to trigger the function of ben mack
    # we just split up the data afterwards
    if date is not None:
        # timestamp = pd.to_datetime(date)
        # year_int = timestamp.year
        yyyy = [date_timestamp.year]

    else:
        if start_date is not None:
            yyyy = [start_date.year]
        elif end_date is not None:
            yyyy = [end_date.year]
        else:
            yyyy = [year]

    # for "debugging" purposes
    # print("""the function reached this point and the parameter provided to get_available_datasets_from_shape are:
    # \n\n {products}, \n\n {shape}, "\n\n", {years}""".format(products = products, shape = shape, years = yyyy))

    df = get_available_datasets_from_shape(products=products, shape=shape, years=yyyy)
    # SPLIT DATAFRAME AS USER DATE INPUT  . . .
    dictionary = dates_to_dict(df)

    # 1 Dataframe is 1 Date and can consist of up to 4 rows(Scenes)!!!
    # make list with all the dataframe the user wants
    dataframes = []

    # # Ein Tag
    if date is not None:
        df_single_date = dictionary[date_timestamp]
        dataframes.append(df_single_date)


    # time span
    elif start_date is not None and end_date is not None:
        for key in dictionary.keys():
            if key >= start_date and key <= end_date:
                dataframes.append(dictionary[key])
            else:
                pass

    # time span with only start or end
    elif start_date is not None or end_date is not None:

        if start_date is not None and end_date is None:
            for key in dictionary.keys():
                if key >= start_date:
                    dataframes.append(dictionary[key])
        elif start_date is None and end_date is not None:
            for key in dictionary.keys():
                if key <= end_date:
                    dataframes.append(dictionary[key])

    # year
    elif year is not None:
        for key in dictionary.keys():
            dataframes.append(dictionary[key])

    else:
        print("Something is wrong with your dates")

    return dataframes


def download_tiles(dstdir=None, dataframes=None):
    """
    Download from download_batch.
    Calls datasets from make_tiles_dataset and transfers it in a manner to be digested by download_hls_dataset.download_batch.
    A specific date, a date range with start and end date or a range number of file can be selected to be downloaded.
    Iteration over dict
    :param: dictonary, dstdir
    :returns: none
    """
    for df in dataframes:
        download_batch(dstdir=dstdir, datasets=df)
    return None


def dates_to_dict(df):
    # sort dataframe by date
    df_sorted = df.sort_values(by=["date"])

    # make numpy array of unique dates
    unique_dates = df_sorted.date.unique()
    dates_ls = []

    # instead of using numpy.datetime64 use pandas.Timestamp
    for i in unique_dates:
        i = pd.Timestamp(i)
        i = i.date()
        dates_ls.append(i)

    # create dictionary with keys being the unique dates
    dataframe_dict = {date: pd.DataFrame for date in dates_ls}

    # add rows of orignial dataframe as values
    for key in dataframe_dict.keys():
        dataframe_dict[key] = df[:][df.date == key]

    return dataframe_dict