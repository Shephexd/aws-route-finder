from __future__ import print_function, unicode_literals
import regex
import boto3
from PyInquirer import prompt
from prompt_toolkit.validation import Validator, ValidationError
from routefinder.app import RouteFinder, RouteFindingResult


class IPValidator(Validator):
    def validate(self, document):
        ok = regex.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid IP',
                cursor_position=len(document.text))  # Move cursor to end


class FQDNValidator(Validator):
    def validate(self, document):
        ok = RouteFinder.get_host_by_name(fqdn=document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid IP',
                cursor_position=len(document.text))  # Move cursor to end


class RouteFinderCommand:
    def __init__(self):
        client = boto3.client("ec2")
        self.route_finder = RouteFinder(ec2_client=client)

    def validate_ip(self, answers, ip):
        if ip not in self.route_finder.ip_map:
            raise ValidationError("")
        return True

    def validate_fqdn(self, fqdn):
        print(self, fqdn)
        host = self.route_finder.get_host_by_name(fqdn)
        if host not in self.route_finder.ip_map:
            raise ValidationError("No Host in IP List")
        return True

    def setup(self):
        source_questions = [
            {
                'type': 'list',
                'name': 'SourceType',
                'message': 'Select SourceType',
                "choices": [
                    {"name": "Amazon EC2 Instance", "value": "EC2"},
                    {"name": "IP Address", "value": "IP"},
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
                "choices": [{"name": k, "value": v} for k, v in self.route_finder.ip_map.items()],
                "validate": self.validate_ip,
                "when": lambda answer: answer["SourceType"] == "IP"
            },
            {
                'type': 'list',
                'name': 'Source',
                'message': 'Select Internet Gateway',
                "choices": [{"name": repr(v), "value": k} for k, v in self.route_finder.igw_map.items()],
                "input": IPValidator,
                "when": lambda answer: answer["SourceType"] == "IGW"
            },
        ]
        destination_questions = [
            {
                'type': 'list',
                'name': 'DestinationType',
                'message': 'Select DestinationType',
                "choices": lambda answer:
                [{"name": "Domain Name(FQDN)", "value": "FQDN"},
                 {"name": "Amazon EC2", "value": "EC2"}] if answer["SourceType"] == "IGW"
                else [
                    {"name": "Domain Name(FQDN)", "value": "FQDN"},
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
                'type': 'list',
                'name': 'Destination',
                'message': 'Input IP Address',
                "choices": [{"name": repr(v), "value": k} for k, v in self.route_finder.igw_map.items()],
                "validate": IPValidator,
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
        ]
        questions = source_questions + destination_questions + packet_setup
        return prompt(questions=questions)

    def run(self, source_type, source, destination_type, destination, protocol) -> RouteFindingResult:
        if source_type == "IP":
            source = self.route_finder.get_eni_by_ip(source)

        if destination_type == "FQDN":
            destination = self.route_finder.get_eni_by_name(destination)

        analysis_result = self.route_finder.run(
            source=source,
            # source_ip=network_insight_kwargs["SourceIp"],
            destination=destination,
            # destination_port=int(network_insight_kwargs["DestinationPort"]),
            protocol=protocol,
            sync_flag=True
        )
        return analysis_result


if __name__ == "__main__":
    command = RouteFinderCommand()
    setup_config = command.setup()
    result = command.run(source_type=setup_config["SourceType"],
                         source=setup_config["Source"],
                         destination_type=setup_config["DestinationType"],
                         destination=setup_config["Destination"],
                         protocol=setup_config["Protocol"])
    print(result)
