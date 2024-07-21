from __future__ import print_function, unicode_literals

import socket

import regex
import boto3
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from prompt_toolkit.validation import ValidationError
from routefinder.app import RouteFinder, RouteFindingResult
from routefinder.interfaces.config import CommandConfigFactory, CommandConfig


def validate_available_source(available_source):
    if not available_source:
        raise ValidationError(
            message="No Available Source Resource Found(Check EC2, NetworkInterface, InternetGateway)")
    return True


def validate_ip(ip: str):
    pattern_ok = regex.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip)
    if not pattern_ok:
        raise ValidationError(message='Please enter a valid IP')
    return True


def validate_fqdn(route_finder: RouteFinder, fqdn):
    try:
        host = route_finder.get_host_by_name(fqdn)
        return True
    except socket.gaierror:
        return False


def validate_registered_ip(route_finder: RouteFinder, ip: str):
    validate_ip(ip)

    is_registered_ip = route_finder.ip_map.get(ip)
    if not is_registered_ip:
        raise ValidationError(message='Not registered IP')
    return True


def validate_registered_fqdn(route_finder, fqdn):
    if validate_fqdn(route_finder=route_finder, fqdn=fqdn):
        host = route_finder.get_host_by_name(fqdn)
        return validate_registered_ip(route_finder=route_finder, ip=host)
    raise ValidationError(message='Not registered FQDN')


class RouteFinderCommand:
    def __init__(self, boto_config=None):
        client = boto3.client("ec2", config=boto_config)
        self.route_finder = RouteFinder(ec2_client=client)
        self.available_sources = self.get_available_sources()
        self.config_factory = CommandConfigFactory(command=self)

    def get_available_sources(self):
        has_instance = bool(self.route_finder.instance_map)
        has_ip = bool(self.route_finder.ip_map)

        available_sources = [
            Choice("EC2", name="Amazon EC2 Instance", enabled=not has_instance),
            Choice("IP", name="IP Address on AWS", enabled=not has_ip),
            Choice("FQDN", name="FQDN on AWS", enabled=not has_ip),
        ]
        if not has_ip and not has_instance:
            raise ValidationError(message="No Available Resources on target region")
        return available_sources

    def ask_source(self):
        source = ""
        source_type = inquirer.select(
            message="Select SourceType",
            choices=self.available_sources
        ).execute()

        if source_type == "EC2":
            source = inquirer.select(
                message="Select Target EC2",
                choices=[Choice(k, name=repr(v)) for k, v in self.route_finder.instance_map.items()]
            ).execute()
        elif source_type == "IP":
            source = inquirer.text(
                message="Input IP Address on AWS",
                validate=lambda ip: validate_registered_ip(self.route_finder, ip)
            ).execute()
        elif source_type == "FQDN":
            source = inquirer.text(
                message="FQDN on AWS",
                validate=lambda fqdn: validate_registered_fqdn(self.route_finder, fqdn)
            ).execute()
        else:
            raise ValidationError(message="source must be set")
        return source, source_type

    def ask_destination(self):
        destination_type = inquirer.select(
            message="Select DestinationType",
            choices=[
                Choice("FQDN", name="Domain Name(FQDN)"),
                Choice("EC2", name="Amazon EC2 Instance"),
                Choice("IP", name="IPv4 Address")]
        ).execute()

        if destination_type == "EC2":
            destination = inquirer.select(
                message="Select Target EC2",
                choices=[Choice(k, name=repr(v)) for k, v in self.route_finder.instance_map.items()]
            ).execute()
        elif destination_type == "FQDN":
            destination = inquirer.text(
                message="Input Domain Name",
                validate=lambda fqdn: validate_fqdn(self.route_finder, fqdn)
            ).execute()
        elif destination_type == "IP":
            destination = inquirer.text(message="Input IP Address", validate=validate_ip).execute()
        else:
            raise ValidationError(message="Destination must be set")
        return destination, destination_type

    def setup(self):
        source, source_type = self.ask_source()
        destination, destination_type = self.ask_destination()
        protocol = inquirer.select(
            message="select Protocol", choices=["tcp", "udp"]).execute()
        destination_port = inquirer.number(
            message="Input destination PortNumber",
            default=80,
            validate=lambda port: port.isnumeric() and 0 <= int(port) <= 65535
        ).execute()

        return self.config_factory.build(source_type=source_type, source=source,
                                         destination_type=destination_type, destination=destination,
                                         protocol=protocol, destination_port=destination_port)

    def run(self, config: CommandConfig, sync_flag=True) -> RouteFindingResult:
        config.is_valid()
        serialized_config = config.serialize(route_finder=self.route_finder)
        analysis_result = self.route_finder.run(
            source=serialized_config["source"],
            destination=serialized_config["destination"],
            protocol=serialized_config["protocol"],
            source_ip=serialized_config["source_ip"],
            destination_ip=serialized_config["destination_ip"],
            destination_port=serialized_config["destination_port"],
            sync_flag=sync_flag)
        return analysis_result


if __name__ == "__main__":
    command = RouteFinderCommand()
    command_config: CommandConfig = command.setup()
    result = command.run(command_config, sync_flag=True)
    print(result.get_result(detail=True))
