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
    result = command.run(source_type=setup_config["SourceType"],
                         source=setup_config["Source"],
                         destination_type=setup_config["DestinationType"],
                         destination=setup_config["Destination"],
                         protocol=setup_config["Protocol"]
                         )
    print(result.get_result(detail=args.verbose))
