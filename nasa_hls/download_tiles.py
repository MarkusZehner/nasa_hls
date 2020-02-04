import os
import urllib
import geopandas as gp
from nasa_hls.utils import get_available_datasets
from nasa_hls.download_hls_dataset import download_batch
import pandas as pd

path_data_win_konsti = os.path.join("D:", os.sep, "Geodaten", "#Jupiter", "GEO419", "data" + os.sep)
path_data_lin_konsti = os.path.join(os.path.expanduser('~'), 'Dokumente', 'nasa_hls', 'data' + os.sep)

path_data_lin_robin = os.path.join(os.path.expanduser('~'), 'python_projects', 'data', 'nasa_hls', 'hdf_tiles' + os.sep)
path_shape_robin = os.path.join("/home/robin/python_projects/data/nasa_hls/test_shape/dummy_region.shp")

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

    if years is None:
        years = [2018]

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
                       date=None, # TODO: read year as int
                       year=None,
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

    try:
     # convert given dates to pd.timestampe
        if date:
            date_timestamp = pd.Timestamp(date).date()
        if start_date:
            start_date = pd.Timestamp(start_date).date()
        if end_date:
            end_date = pd.Timestamp(end_date).date()
    except ValueError:
        print("provide a string in the format 'yyyy-mm-dd'") # if this error is raised, all the rest should not even be evaluated

    # still needs a little description about whats happening here
    # while True:
    #     try:

    shape = gp.read_file(shape)
    print("valid shape, process continues\n")

    if products is None:
        products = ["S30"]
    if date:
        print("single date: {date}\n ".format(date = date))
    if start_date:
        print("starting date: {date}\n ".format(date = start_date))
    if end_date:
        print("end date: {date}\n ".format(date = end_date))
    if year:
        print("year: {year}".format(year = year))


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

        
    # # Zeiraum
    elif start_date is not None and end_date is not None:
        for key in dictionary.keys():
            if key >= start_date and key <= end_date:
                dataframes.append(dictionary[key])
            else:
                pass

    # Zeitraum mit nur Ende oder Anfang 
    elif start_date is not None or end_date is not None:
        
        
        if start_date is not None and end_date is None:
            for key in dictionary.keys():
                if key >= start_date:
                    dataframes.append(dictionary[key])
        elif start_date is None and end_date is not None:
            for key in dictionary.keys():
                if key <= end_date:
                    dataframes.append(dictionary[key])

    # # year
    elif year is not None:
        for key in dictionary.keys():
            dataframes.append(dictionary[key])
    
    else:
        print("Something is wrong with your dates")
    
        #break

        #except:
        #    print("something is wrong with your shapefile. This will not work\n\n")
        #    return None

    return dataframes

def download_tiles(dstdir = path_data_lin_robin + "hdf/", datasets = None):
    """
    Download from download_batch.
    Calls datasets from make_tiles_dataset and transfers it in a manner to be digested by
    download_hls_dataset.download_batch.
    A specific date, a date range with start and end date or a range number of file can be selected to be downloaded.
    Iteration over dict

    :param: dictonary, dstdir

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

    for df in datasets:
        download_batch(dstdir = dstdir, datasets = df)


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


######################################################
# deprecated
######################################################

def show_available_dates(df):
    print("\n\n", type(df))
    df_sorted = df.sort_values(by=["date"])
    df_grouped = df_sorted.groupby(['date'], as_index=False).count()
    df_selected = df_grouped[["date", "product"]]

    return df_selected


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
