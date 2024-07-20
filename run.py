import argparse
from botocore.config import Config
from routefinder.command import RouteFinderCommand


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='AWSRouteFinder',
        description='AWS Reachability Analyzer CLI Tool',
        epilog='Text at the bottom of help')
    parser.add_argument('-v', '--verbose',
                        action='store_true')
    parser.add_argument('-r', '--region')
    args = parser.parse_args()

    boto_config = None
    if args.region:
        boto_config = Config(region_name=args.region)

    command = RouteFinderCommand(boto_config=boto_config)
    setup_config = command.setup()
    print("Start Analyze from {source_type}({source}) to {destination_type}({destination})".format(
        source_type=setup_config["SourceType"],
        source=setup_config["Source"],
        destination_type=setup_config["DestinationType"],
        destination=setup_config["Destination"]
    ))
    result = command.run(source_type=setup_config["SourceType"],
                         source=setup_config["Source"],
                         destination_type=setup_config["DestinationType"],
                         destination=setup_config["Destination"],
                         protocol=setup_config["Protocol"]
                         )
    print(result.get_result(detail=args.verbose))
