#!/usr/bin/env python
# File created on 09 Feb 2010
#file make_2d_plots.py

from __future__ import division

__author__ = "Jesse Stombaugh"
__copyright__ = "Copyright 2010, The QIIME project"
__credits__ = ["Jesse Stombaugh"]
__license__ = "GPL"
__version__ = "0.91"
__maintainer__ = "Jesse Stombaugh"
__email__ = "jesse.stombaugh@colorado.edu"
__status__ = "Release"
 
import matplotlib,re
from qiime.util import parse_command_line_parameters, get_options_lookup
from optparse import make_option
from qiime.make_2d_plots import generate_2d_plots
from qiime.parse import parse_map,parse_coords,group_by_field,group_by_fields
import shutil
import os
from qiime.util import get_qiime_project_dir
from qiime.make_3d_plots import combine_map_label_cols,get_map,get_coord,\
                         process_colorby,create_dir

options_lookup = get_options_lookup()

#make_2d_plots.py
script_info={}
script_info['brief_description']="""Make 2D PCoA Plots"""
script_info['script_description']="""This script generates 2D PCoA plots using the principal coordinates file generated by performing beta diversity measures of an OTU table."""
script_info['script_usage']=[]
script_info['script_usage'].append(("""Default Example:""","""If you just want to use the default output, you can supply the principal coordinates file (i.e., resulting file from principal_coordinates.py), where the default coloring will be based on the SampleID as follows:""","""%prog -i beta_div_coords.txt"""))
script_info['script_usage'].append(("""Output Directory Usage:""","""If you want to give an specific output directory (e.g. \"2d_plots\"), use the following code.""", """%prog -i beta_div_coords.txt -o 2d_plots/"""))
script_info['script_usage'].append(("""Mapping File Usage:""","""Additionally, the user can supply their mapping file ("-m") and a specific category to color by ("-b") or any combination of categories. When using the -b option, the user can specify the coloring for multiple mapping labels, where each mapping label is separated by a comma, for example: -b \'mapping_column1,mapping_column2\'. The user can also combine mapping labels and color by the combined label that is created by inserting an \'&&\' between the input columns, for example: -b \'mapping_column1&&mapping_column2\'.

If the user wants to color by specific mapping labels, they can use the following code:""","""%prog -i beta_div_coords.txt -m Mapping_file.txt -b 'mapping_column'"""))
script_info['script_usage'].append(("""""","""If the user would like to color all categories in their metadata mapping file, they can pass 'ALL' to the '-b' option, as follows:""","""%prog -i beta_div_coords.txt -m Mapping_file.txt -b ALL"""))
script_info['script_usage'].append(("""Output Directory Usage:""","""If you want to give an specific output directory (e.g. \"2d_plots\"), use the following code.""", """%prog -i beta_div_coords.txt -o 2d_plots/"""))
script_info['script_usage'].append(("""Combination of Features:""","""or use some of the suggestions from above:""", """%prog -i beta_div_coords.txt -m Mapping_file.txt -b \'mapping_column1,mapping_column1&&mapping_column2\'"""))
script_info['output_description']="""This script generates an output folder, which contains several files. To best view the 2D plots, it is recommended that the user views the _pca_2D.html file."""

script_info['required_options']=[\
make_option('-i', '--coord_fname', dest='coord_fname', \
help='This is the path to the principal coordinates file (i.e., resulting \
file from principal_coordinates.py)')
]
script_info['optional_options']=[\
make_option('-m', '--map_fname', dest='map_fname', \
     help='This is the metadata mapping file [default=%default]'),
make_option('-b', '--colorby', dest='colorby',\
     help='This is the categories to color by in the plots from the \
user-generated mapping file. The categories must match the name of a column \
header in the mapping file exactly and multiple categories can be list by comma \
separating them without spaces. The user can also combine columns in the \
mapping file by separating the categories by "&&" without spaces \
[default=%default]'),
options_lookup['output_dir']
]

script_info['version'] = __version__



def main():
    option_parser, opts, args = parse_command_line_parameters(**script_info)

    matplotlib_version = re.split("[^\d]", matplotlib.__version__)
    matplotlib_version_info = tuple([int(i) for i in matplotlib_version if \
                            i.isdigit()])

    if matplotlib_version_info != (0,98,5,3) and \
        matplotlib_version_info != (0,98,5,2):
        print "This code was only tested with Matplotlib-0.98.5.2 and \
              Matplotlib-0.98.5.3"
    data = {}

    #Open and get coord data
    data['coord'] = get_coord(opts.coord_fname)

    #Open and get mapping data, if none supplied create a pseudo mapping
    #file
    if opts.map_fname:
        mapping = get_map(opts, data)
    else:
        data['map']=(([['#SampleID','Sample']]))
        for i in range(len(data['coord'][0])):
            data['map'].append([data['coord'][0][i],'Sample'])

    #Determine which mapping headers to color by, if none given, color by
    #Sample ID's
    if opts.colorby:
        prefs,data=process_colorby(opts.colorby,data)
    else:
        prefs={}
        prefs['Sample']={}
        prefs['Sample']['column']='#SampleID'

    filepath=opts.coord_fname
    filename=filepath.strip().split('/')[-1]

    qiime_dir=get_qiime_project_dir()

    js_path=os.path.join(qiime_dir,'qiime','support_files','js')

    dir_path=opts.output_dir
    if dir_path and not dir_path.endswith("/"):
        dir_path=dir_path+"/"

    dir_path=create_dir(dir_path,'2d_plots_')

    js_dir_path = os.path.join(dir_path,'js')
    try:
        os.mkdir(js_dir_path)
    except OSError:
        pass

    shutil.copyfile(os.path.join(js_path,'overlib.js'), os.path.join(js_dir_path,'overlib.js'))

    try:
        action = generate_2d_plots
    except NameError:
        action = None
    #Place this outside try/except so we don't mask NameError in action
    if action:
        action(prefs, data, dir_path,filename)


if __name__ == "__main__":
    main()