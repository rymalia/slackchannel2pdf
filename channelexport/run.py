# Copyright 2019 Erik Kalkoken
#
# Licensed under MIT license. See attached file for details
#
# This package contains the implementation of the command line interface
# for Channelexport
#

import os
import argparse
from datetime import datetime
from dateutil import parser
import pytz
from tzlocal import get_localzone
import locale
from channelexport import ChannelExporter

def main():
    """Implements the arg parser and starts the channelexporter with its input"""

    # main arguments
    my_arg_parser = argparse.ArgumentParser(
        description = "This program exports the text of a Slack channel to a PDF file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )    
    my_arg_parser.add_argument(        
        "channel", 
        help = "One or several: name or ID of channel to export.",
        nargs="+"
        )
    
    my_arg_parser.add_argument(
        "--token",         
        help = "Slack OAuth token"
        )

    my_arg_parser.add_argument(
        "--oldest",
        help = "don't load messages older than a date"
        )

    my_arg_parser.add_argument(
        "--latest",
        help = "don't load messages newer then a date"
        )

    # PDF file
    my_arg_parser.add_argument(        
        "-d",
        "--destination",         
        help = "Specify a destination path to store the PDF file. (TBD)",
        default = "."
        )
    
    # formatting
    my_arg_parser.add_argument(        
        "--page-orientation",         
        help = "Orientation of PDF pages",
        choices = ["portrait", "landscape"],
        default = ChannelExporter._PAGE_ORIENTATION_DEFAULT
        )
    my_arg_parser.add_argument(        
        "--page-format",         
        help = "Format of PDF pages",
        choices = ["a3", "a4", "a5", "letter", "legal"],
        default = ChannelExporter._PAGE_FORMAT_DEFAULT
        )
    my_arg_parser.add_argument(
        "--timezone",         
        help = ("Manually set the timezone to be used instead of the . "
            + "system's default timezone. e.g. 'Europe/Berlin' "
            + "Use a timezone name as defined here: "
            + "https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
        )    

    my_arg_parser.add_argument(        
        "--locale",         
        help = ("Manually set the locale to be used instead of the "
            + "system's default locale, e.g. ' de-DE' for Germany")        
        )

    # standards
    my_arg_parser.add_argument(        
        "--version",         
        help="show the program version and exit", 
        action="version", 
        version=ChannelExporter._VERSION
        )    

    # exporter config
    my_arg_parser.add_argument(        
        "--max-messages",         
        help = "max number of messages to export",
        type = int
        )

    # Developer needs
    my_arg_parser.add_argument(        
        "--write-raw-data",
        help = "will also write all raw data returned from the API to files,"\
            + " e.g. messages.json with all messages",                
        action = "store_const",
        const = True
        )    
    
    my_arg_parser.add_argument(        
        "--add-debug-info",
        help = "wether to add debug info to PDF",
        action = "store_const",
        const = True,
        default = False
        )

    start_export = True
    args = my_arg_parser.parse_args()
    
    if "version" in args:
        print(ChannelExporter._VERSION)            
        start_export = False

    # try to take slack token from optional argument or environment variable
    if args.token is None:
        if "SLACK_TOKEN" in os.environ:
            slack_token = os.environ['SLACK_TOKEN']
        else:
            print("ERROR: No slack token provided")
            start_export = False
    else:
        slack_token = args.token

    # set local timezone
    if args.timezone is not None:
        try:
            my_tz = pytz.timezone(args.timezone)
        except pytz.UnknownTimeZoneError:
            print("ERROR: Unknown timezone")
            my_tz = None
            start_export = False            
    else:
        my_tz = get_localzone() 
    
    if args.locale is not None:
        if args.locale.lower() not in locale.locale_alias.keys():
            print("ERROR: provided locale string is not valid")
            start_export = False
        else:
            my_locale = args.locale
    else:
        locale.setlocale(locale.LC_ALL, '')
        my_locale = locale.getdefaultlocale()[0]

    if start_export is not False:
        # parse oldest
        if args.oldest is not None:        
            try:
                dt = parser.parse(args.oldest)
                oldest = my_tz.localize(dt)            
            except ValueError:
                print("Invalid date input for --oldest")        
                start_export = False
        else:
            oldest = None

        # parse latest
        if args.latest is not None:        
            try:
                dt = parser.parse(args.latest)
                latest = my_tz.localize(dt)            
            except ValueError:
                print("Invalid date input for --latest")        
                start_export = False
        else:
            latest = None

    if start_export:
        exporter = ChannelExporter(
            slack_token=slack_token,             
            my_tz=my_tz,
            my_locale=my_locale,
            add_debug_info=args.add_debug_info
        )        
        exporter.run(
            channel_inputs=args.channel, 
            dest_path=args.destination,
            oldest=oldest,
            latest=latest,
            page_orientation=args.page_orientation,
            page_format=args.page_format,
            max_messages=args.max_messages, 
            write_raw_data=(args.write_raw_data == True)
        )
    

if __name__ == '__main__':
    main()