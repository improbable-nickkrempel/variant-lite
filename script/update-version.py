#!/usr/bin/env python
#
# Copyright 2017-2018 by Martin Moene
#
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
# script/update-version.py
#

from __future__ import print_function

import argparse
import os
import re
import sys

import generate_header

# Configuration:

def_max_types = 16
def_max_args = 5

table = (
    # path, substitute find, substitute format
    ( 'CMakeLists.txt'
        , r'set\W+variant_lite_version\W+"([0-9]+\.[0-9]+\.[0-9]+)"\W+$'
        , 'set( variant_lite_version "{major}.{minor}.{patch}" )\n' )

#    , ( 'example/cmake-pkg/CMakeLists.txt'
#        , r'set\W+variant_lite_version\W+"([0-9]+\.[0-9]+(\.[0-9]+)?)"\W+$'
#        , 'set( variant_lite_version "{major}.{minor}" )\n' )
#
#    , ( 'script/install-xxx-pkg.py'
#        , r'\variant_lite_version\s+=\s+"([0-9]+\.[0-9]+\.[0-9]+)"\s*$'
#        , 'variant_lite_version = "{major}.{minor}.{patch}"\n' )

    , ( 'conanfile.py'
        , r'version\s+=\s+"([0-9]+\.[0-9]+\.[0-9]+)"\s*$'
        , 'version = "{major}.{minor}.{patch}"' )

    # Note: edit template:

    , ( 'template/variant.hpp'
        , r'\#define\s+variant_lite_MAJOR\s+[0-9]+\s*$'
        , '#define variant_lite_MAJOR  {major}' )

    , ( 'template/variant.hpp'
        , r'\#define\s+variant_lite_MINOR\s+[0-9]+\s*$'
        , '#define variant_lite_MINOR  {minor}' )

    , ( 'template/variant.hpp'
        , r'\#define\s+variant_lite_PATCH\s+[0-9]+\s*$'
        , '#define variant_lite_PATCH  {patch}\n' )
)

# End configuration.

def readFile( in_path ):
    """Return content of file at given path"""
    with open( in_path, 'r' ) as in_file:
        contents = in_file.read()
    return contents

def writeFile( out_path, contents ):
    """Write contents to file at given path"""
    with open( out_path, 'w' ) as out_file:
        out_file.write( contents )

def replaceFile( output_path, input_path ):
    # prevent race-condition (Python 3.3):
    if sys.version_info >= (3, 3):
        os.replace( output_path, input_path )
    else:
        os.remove( input_path )
        os.rename( output_path, input_path )

def editFileToVersion( version, info, verbose ):
    """Update version given file path, version regexp and new version format in info"""
    major, minor, patch = version.split('.')
    in_path, ver_re, ver_fmt = info
    out_path = in_path + '.tmp'
    new_text = ver_fmt.format( major=major, minor=minor, patch=patch )

    if verbose:
        print( "- {path} => '{text}':".format( path=in_path, text=new_text.strip('\n') ) )

    writeFile(
        out_path,
        re.sub(
            ver_re, new_text, readFile( in_path )
            , count=0, flags=re.MULTILINE
        )
    )
    replaceFile( out_path, in_path )

def editFilesToVersion( version, table, verbose ):
    if verbose:
        print( "Editing files to version {v}:".format(v=version) )
    for item in table:
        editFileToVersion( version, item, verbose )

def editFilesToVersionFromCommandLine():
    """Update version number given on command line in paths from configuration table."""

    parser = argparse.ArgumentParser(
        description='Update version number in files.',
        epilog="""""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'version',
        metavar='version',
        type=str,
        nargs=1,
        help='new version number, like 1.2.3')

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='report the name of the file being processed')

    parser.add_argument(
        '--max-types',
        metavar='types',
        type=int,
        default=def_max_types,
        help='number of variant types')

    parser.add_argument(
        '--max-args',
        metavar='args',
        type=int,
        default=def_max_args,
        help='number of arguments for \'visit\' methods')

    args = parser.parse_args()

    editFilesToVersion( args.version[0], table, args.verbose )
    makeVariantHeader( 'template/variant.hpp', 'include/nonstd/variant.hpp', args.max_types, args.max_args, args.verbose )

def makeVariantHeader( tpl_path, hdr_path, types, args, verbose ):
    generate_header.ProcessTemplate( tpl_path, hdr_path, types, args, verbose )


if __name__ == '__main__':
    editFilesToVersionFromCommandLine()

# end of file
