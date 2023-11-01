# By Pytel

import argparse
from MyBot import *

def arg_parser():
    global DEBUG
    global VERBOSE
    parser = argparse.ArgumentParser(description='Discord bot')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose mode')
    parser.add_argument('-c', '--config', action='store_true',
                        help='Create new config file')
    parser.add_argument('-p', '--pipe', action='store_true',
                        help='Start with pipe reading task')

    args = parser.parse_args()
    DEBUG = args.debug
    VERBOSE = args.verbose
    return args

if __name__ == "__main__":
    args = arg_parser()

    bot = MyBot(args=args)
    bot.run(bot.API_TOKEN)