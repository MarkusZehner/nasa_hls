import os
import sys
import argparse

#create the parser
my_parser = argparse.ArgumentParser(description="Creates Mosaic of Harmonized Landsat8/Sentinel2 - Data for the provided extent of the shapefile")

#add the arguments
my_parser.add_argument("shapefile", metavar="shape", type=str, help = "the path to the shapefile")

#execute the parse_args-method
args = my_parser.parse_args()

input_path = args.path

if not os.path.isdir(input_path):
    print('The path specified does not exist')
    sys.exit()

print('\n'.join(os.listdir(input_path)))