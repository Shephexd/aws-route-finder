import argparse
from botocore.config import Config
from routefinder.interfaces.cli import RouteFinderCommand


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
        print("Target Region:", args.region)

    try:
        command = RouteFinderCommand(boto_config=boto_config)
        setup_config = command.setup()
        setup_config.summarize()
        result = command.run(config=setup_config)
        print(result.get_result(detail=True))

    except KeyboardInterrupt as e:
        print("Exit RouteFinder")
        exit(0)
