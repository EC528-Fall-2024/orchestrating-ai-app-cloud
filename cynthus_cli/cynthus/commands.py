import argparse

import requests

def ping_intel():
    
    try:
        # Make a GET request to the API endpoint using requests.get()
        r = requests.get('https://compute-us-region-1-api.cloud.intel.com/openapiv2/#/v1/ping')

        # Check if the request was successful (status code 200)
        if r.status_code == 200:
            print('Received response')
            return None
        else:
            print('Error:', r.status_code)
            return None
        
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def handle_print():
    print('For more info, type -h or --help.')

def give_info():
    print('The VM package info can be found below: ')

def cli_entry_point():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    parser_request = subparsers.add_parser('ping', help='ping Intel site')
    
    parser_print = subparsers.add_parser('print', help='print help message')

    parser_info = subparsers.add_parser('info', help='Get VM package info')

    args = parser.parse_args()

    if args.command == 'ping':
        ping_intel()
    elif args.command == 'print':
        handle_print()
    elif args.command == 'info':
        give_info()
    else:
        parser.print_help()