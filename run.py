from routefinder.command import RouteFinderCommand


if __name__ == "__main__":
    command = RouteFinderCommand()
    setup_config = command.setup()
    result = command.run(**setup_config)
    print(result.get_result(detail=True))
