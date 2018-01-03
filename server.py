from application.server.server import server_main
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', help="Listen on port.", default=7777, type=int)
    args = parser.parse_args()
    server_main(args)
