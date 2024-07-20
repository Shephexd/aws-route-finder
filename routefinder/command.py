from __future__ import print_function, unicode_literals

import socket

import regex
import boto3
from botocore.config import Config
from PyInquirer import prompt
from prompt_toolkit.validation import Validator, ValidationError
from routefinder.app import RouteFinder, RouteFindingResult, get_host_by_name
from routefinder.dto import Endpoint


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


class RouteFinderCommand:
    def __init__(self, boto_config: Config = None):
        if boto_config:
            client = boto3.client("ec2")
        else:
            client = boto3.client("ec2", config=boto_config)
        self.route_finder = RouteFinder(ec2_client=client)

    def setup(self):
        source_questions = [
            {
                'type': 'list',
                'name': 'SourceType',
                'message': 'Select SourceType',
                "choices": [
                    {"name": "Amazon EC2 Instance", "value": "EC2"},
                    {"name": "IP Address on AWS", "value": "IP"},
                    {"name": "Internet Gateway", "value": "IGW"}
                ]
            },
            {
                'type': 'list',
                'name': 'Source',
                'message': 'Select Target EC2',
                "choices": [{"name": repr(v), "value": k} for k, v in self.route_finder.instance_map.items()],
                "when": lambda answer: answer["SourceType"] == "EC2"
            },
            {
                'type': 'input',
                'name': 'Source',
                'message': 'Input IP Address on AWS',
                "validate": lambda ip: validate_registered_ip(self.route_finder, ip),
                "when": lambda answer: answer["SourceType"] == "IP"
            },
            {
                'type': 'list',
                'name': 'Source',
                'message': 'Select Internet Gateway',
                "choices": [{"name": repr(v), "value": k} for k, v in self.route_finder.igw_map.items()],
                "when": lambda answer: answer["SourceType"] == "IGW"
            },
        ]
        destination_questions = [
            {
                'type': 'list',
                'name': 'DestinationType',
                'message': 'Select DestinationType',
                "choices": lambda answer:
                [
                    {"name": "Domain Name(FQDN)", "value": "FQDN"},
                    {"name": "Amazon EC2", "value": "EC2"},
                    {"name": "IPv4 Address", "value": "IP"}
                ]
                if answer["SourceType"] == "IGW"
                else [
                    {"name": "Domain Name(FQDN)", "value": "FQDN"},
                    {"name": "IPv4 Address", "value": "IP"},
                    {"name": "Amazon EC2", "value": "EC2"},
                    {"name": "Internet Gateway", "value": "IGW"}
                ]
            },
            {
                'type': 'list',
                'name': 'Destination',
                'message': 'Select Target EC2',
                "choices": [{"name": repr(v), "value": k} for k, v in self.route_finder.instance_map.items()],
                "when": lambda answer: answer["DestinationType"] == "EC2"
            },
            {
                'type': 'input',
                'name': 'Destination',
                'message': 'Input Domain Name',
                "validate": self.validate_fqdn,
                "when": lambda answer: answer["DestinationType"] == "FQDN",
            },
            {
                'type': 'input',
                'name': 'Destination',
                'message': 'Input IPAddress',
                "validate": lambda ip: validate_ip(ip),
                "when": lambda answer: answer["DestinationType"] == "IP"
            },
            {
                'type': 'list',
                'name': 'Destination',
                'message': 'Select Internet Gateway',
                "choices": [{"name": repr(v), "value": k} for k, v in self.route_finder.igw_map.items()],
                "when": lambda answer: answer["DestinationType"] == "IGW"
            }
        ]
        packet_setup = [
            {
                'type': 'list',
                'name': 'Protocol',
                'message': 'select Protocol',
                "choices": ['tcp', 'udp']
            },
            {
                'type': 'input',
                'name': 'Port',
                'message': 'Input Destination Port Number',
                "validate": lambda port: port.isnumeric() and 0 <= int(port) <= 65535
            }
        ]
        questions = source_questions + destination_questions + packet_setup
        return prompt(questions=questions)

    def map_source(self, source_type, source, source_ip) -> (Endpoint, str):
        if source_type == "EC2":
            source = self.route_finder.instance_map[source]
        elif source_type == "IGW":
            source = self.route_finder.igw_map[source]
        elif source_type == "IP":
            source = self.route_finder.ip_map[source]
        return source, source_ip

    def map_destination(self, destination_type, destination, destination_ip) -> (Endpoint, str):
        # Analyzer based on NetworkInterface
        if destination_type in ["EC2", "IGW"]:
            return self.route_finder.endpoint_map[destination_type][destination], ""

        # Analyzer based on IP Address
        if destination_type in ["FQDN", "IP"]:
            if destination in self.route_finder.ip_map:
                destination = self.route_finder.get_eni_by_name(destination)
                return destination, ""
            else:
                destination_ip = self.route_finder.get_host_by_name(fqdn=destination)
                return None, destination_ip

    def run(self, source_type, source, destination_type, destination, protocol="tcp", source_ip="", destination_ip="",
            destination_port=0) -> RouteFindingResult:
        src_endpoint, source_ip = self.map_source(source_type=source_type,
                                                  source=source,
                                                  source_ip=source_ip)
        dest_endpoint, destination_ip = self.map_destination(destination_type=destination_type,
                                                             destination=destination,
                                                             destination_ip=destination_ip)
        analysis_result = self.route_finder.run(
            source=src_endpoint,
            source_ip=source_ip,
            destination=dest_endpoint,
            destination_ip=destination_ip,
            destination_port=destination_port,
            protocol=protocol,
            sync_flag=True
        )
        return analysis_result


if __name__ == "__main__":
    command = RouteFinderCommand()
    setup_config = command.setup()
    print(setup_config)
    result = command.run(source_type=setup_config["SourceType"],
                         source=setup_config["Source"],
                         destination_ip="",
                         destination_type=setup_config["DestinationType"],
                         destination=setup_config["Destination"],
                         protocol=setup_config["Protocol"],
                         destination_port=int(setup_config["Port"]))
    print(result)
