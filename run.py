import argparse
from routefinder.command import RouteFinderCommand


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='AWSRouteFinder',
        description='AWS Reachability Analyzer CLI Tool',
        epilog='Text at the bottom of help')
    parser.add_argument('-v', '--verbose',
                        action='store_true')
    args = parser.parse_args()

    command = RouteFinderCommand()
    setup_config = command.setup()
    result = command.run(**setup_config)
    print(result.get_result(detail=args.verbose))
