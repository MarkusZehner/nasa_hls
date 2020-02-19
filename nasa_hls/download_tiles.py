import os
import urllib
import geopandas as gp
import pandas as pd
import itertools
import nasa_hls
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


def get_available_datasets_from_shape(products,
                                      years,
                                      shape):
    """
    Calls the Nasa's world-covering UTM.kml file being stored. Do this manually by calling function 'download_kml'.

    Parameters
    ----------
    :param shape
        shape of the region of interest (ROI)
    :param years
        equired years to be checked for
    :param products (default = "L30")
        either "L30" or "S30", the Landsat 8 or Sentinel 2 product, respectively

    ----------
    :return: list of tile name [str of 5 digits starting with two numbers] which geographically intersect the user
    shape and the UTM tiles.
    """

    shape = gp.read_file(shape)

    print(shape.head(5))

    if "Name" in shape:
        print("name")
        shape = shape.rename(columns={"Name": "name_shape"})

    gp.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'  # Enable fiona driver, read in utm grid from kml
    utm_tiles = gp.read_file(download_kml(), driver='KML')

    # convert user_polygon into Gdf -> perform intersection
    # user_polygon = gp.GeoDataFrame.from_file(shape)
    match = gp.sjoin(shape, utm_tiles, how="inner", op='intersects')

    # write UTM-codes in list
    tiles = match["Name"].tolist()

    print(products)
    print(years)
    print(tiles)
    print("\n\n")

    print("\ngetting available datasets . . .")
    datasets = get_available_datasets(products=products, years=years, tiles=tiles, return_list=False)

    return datasets


def make_tiles_dataset(shape,
                       products=None,
                       date=None,
                       year=None,
                       start_date=None,
                       end_date=None):
    '''
    Make a list of pandas dataframaes. Each row in the dataframe is one scene and can be given to the function download_tiles
    
    :param shape
         The (ESRI-)shapefile of your AOI. Expects the full path in form of a string. Mandatory argument.
    
    :param products (optional)
         A list that contains either ["L30"] for Landsat, or ["S30"] for Sentinel, or both.
         If nothing is specified, program will search for Sentinel-2.
    
    :param date (optional)
         If you want data for only one day of the year, provide input here in the form "yyyy-mm-dd" (e.g. "2018-02-03").
         No need to futher specify any parameter.
         Default is None. If not specified, will look for next parameter: year

    :param year (optional)
         if you want the data for a whole year provide a year in the form: "yyyy".
         If provided, no need to further specify any parameter. Default is None.
    
    :param start_date (optional)
         if you are interested in data only after a certain date. Provide start_date in the form: "yyyy-mm-dd".
         If you want a certain period of the year, combine it with end_date.
         If start_date and not end_date, will look for all datasets from start_date to end of year.
    :param end_date (optional)
        If you are interested in data only before a certain date. Provide in the form: "yyyy-mm-dd".
        For a certain period combine it with start_date.
        If provided without start_date, will look for all datasets before a certain date.

    :returns list of dataframes

    Notes
    -----
    Returns list of dataframes, on df for each date (TODO: Products must be split into Landsat and Sentinel!)
    Columns covering:
    (1) Type of product
    (2) UTM tile falling into
    (3) Acquisition date
    (4) Download URL
    with as many products as fitting in the user's feature geometry and retrieved by the sensor at the respective
    date.
    You need to provide at least one of the date options (date, year, start_date, end_date).
    You can provide anyone of them in single. If you want data
    data for a certain period, work with start_date and end_date. If not provided any date-information, will take 2018.

    '''

    if not isinstance(shape, str):
        raise TypeError("parameter 'shape' must be of type str")

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
        print("\nsingle date: {date}\n ".format(date=date))
    if start_date:
        print("\nstarting date: {date}\n ".format(date=start_date))
    if end_date:
        print("\nend date: {date}\n ".format(date=end_date))
    if year:
        print("\nyear: {year}".format(year=year))

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

    # split dataframe with user date input
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
    Download Dataset from the NASA server via from `download_batch`.
    Requires list of dataframes from `make_tiles_dataset`.
    Transfers it in a manner to be digested by download_hls_dataset.download_batch.

    :param dstdir: Output destination for hdf files
    :param list of dataframes from `make_tiles_dataset`

    :returns none
    """
    for df in dataframes:
        download_batch(dstdir=dstdir, datasets=df)
    return None


def dates_to_dict(df):
    """
    Converts dataframe given by `get_available_datasets_from_shape` into an ordered (by day of year) dictionary.
    Keys are the days, values are dataframes for each day.
    Parameters
    ----------

    :param df
        Expects a dataframe in the format:
        product, tile, date, url
    :return dictionary
        keys  are of class <class 'datetime.date'>  (e.g.datetime.date(2018, 1, 1))
        values are of class <class 'pandas.core.frame.DataFrame'>

    Examples
    --------
    for accessing a certain day (key)
    import datetime
    x = datetime.datetime(2018,12,22).date()
    dic = dates_to_dict(df)
    print(dic[x])

    """
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
