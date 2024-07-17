from __future__ import print_function, unicode_literals
import regex
import boto3
from PyInquirer import prompt
from prompt_toolkit.validation import Validator, ValidationError
from route_finder import RouteFinder, RouteFindingResult


class IPValidator(Validator):
    def validate(self, document):
        ok = regex.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid IP',
                cursor_position=len(document.text))  # Move cursor to end


class RouteFinderCommand:
    def __init__(self):
        client = boto3.client("ec2")
        self.route_finder = RouteFinder(ec2_client=client)
        self.run_type_map = {
            "inbound": self.run_inbound_analysis,
            "outbound": self.run_outbound_analysis,
            "between": self.run_between_analysis,
        }

    def run(self, find_type) -> RouteFindingResult:
        if find_type not in self.run_type_map:
            raise KeyError("Not supported run_type")
        return self.run_type_map[find_type]()

    def setup(self):
        setup_prompt = [
            {
                'type': 'list',
                'message': 'Select Route Finder Type(Press 1 or 2 or 3)',
                'name': 'find_type',
                'default': 'h',
                'choices': [
                    {
                        'name': 'Inbound(IGW->EC2)',
                        'value': 'inbound'
                    },
                    {
                        'name': 'Outbound(EC2->IGW)',
                        'value': 'outbound'
                    },
                    {
                        'name': 'Between EC2(EC2<->EC2)',
                        'value': 'between'
                    },
                ]
            }
        ]
        return prompt(setup_prompt)

    def run_inbound_analysis(self) -> RouteFindingResult:
        inbound_params = [
            {
                'type': 'input',
                'name': 'SourceIp',
                'message': 'Source Ip',
                "default": "0.0.0.0",
                "validate": IPValidator
            },
            {
                'type': 'list',
                'name': 'Source',
                'message': 'Select Source IGW',
                "choices": [{"name": k, "value": v} for k, v in self.route_finder.igw_map.items()],
            },
            {
                'type': 'list',
                'name': 'Destination',
                'message': 'select Target EC2',
                "choices": [{"name": k, "value": v} for k, v in self.route_finder.instance_map.items()],
            },
            {
                'type': 'input',
                'name': 'DestinationPort',
                'message': 'Destination Port(0-65535)',
                'default': "8000",
                'validate': lambda val: str(val).isnumeric() and 0 <= int(val) <= 65535
            },
            {
                'type': 'list',
                'name': 'Protocol',
                'message': 'select Protocol',
                "choices": ['tcp', 'udp']
            },
        ]
        network_insight_kwargs = prompt(questions=inbound_params)
        analysis_result = self.route_finder.run(
            source=network_insight_kwargs["Source"],
            source_ip=network_insight_kwargs["SourceIp"],
            destination=network_insight_kwargs["Destination"],
            destination_port=int(network_insight_kwargs["DestinationPort"]),
            protocol=network_insight_kwargs["Protocol"],
            sync_flag=True
        )
        return analysis_result

    def run_outbound_analysis(self) -> RouteFindingResult:
        outbound_params = [
            {
                'type': 'list',
                'name': 'Source',
                'message': 'Select Source EC2',
                "choices": [{"name": k, "value": v} for k, v in self.route_finder.instance_map.items()],
            },
            {
                'type': 'list',
                'name': 'Destination',
                'message': 'select Target IGW',
                "choices": [{"name": k, "value": v} for k, v in self.route_finder.igw_map.items()],
            },
            {
                'type': 'list',
                'name': 'Protocol',
                'message': 'select Protocol',
                "choices": ['tcp', 'udp']
            },
        ]

        network_insight_kwargs = prompt(questions=outbound_params)
        analysis_result = self.route_finder.run(
            source=network_insight_kwargs["Source"],
            source_ip=network_insight_kwargs["SourceIp"],
            destination=network_insight_kwargs["Destination"],
            destination_port=int(network_insight_kwargs["DestinationPort"]),
            protocol=network_insight_kwargs["Protocol"],
            sync_flag=True
        )
        return analysis_result

    def run_between_analysis(self):
        outbound_params = [
            {
                'type': 'list',
                'name': 'Source',
                'message': 'Select Source EC2',
                "choices": [{"name": k, "value": v} for k, v in self.route_finder.instance_map.items()],
            },
            {
                'type': 'list',
                'name': 'Destination',
                'message': 'Select Target EC2',
                "choices": [{"name": k, "value": v} for k, v in self.route_finder.instance_map.items()],
            },
            {
                'type': 'input',
                'name': 'DestinationPort',
                'message': 'Destination Port(0-65535)',
                'default': "8000",
                'validate': lambda val: str(val).isnumeric() and 0 <= int(val) <= 65535
            },
            {
                'type': 'list',
                'name': 'Protocol',
                'message': 'select Protocol',
                "choices": ['tcp', 'udp']
            },
        ]

        network_insight_kwargs = prompt(questions=outbound_params)
        analysis_result = self.route_finder.run(
            source=network_insight_kwargs["Source"],
            destination=network_insight_kwargs["Destination"],
            destination_port=int(network_insight_kwargs["DestinationPort"]),
            protocol=network_insight_kwargs["Protocol"],
            sync_flag=True
        )
        return analysis_result


if __name__ == "__main__":
    command = RouteFinderCommand()
    setup_config = command.setup()
    result = command.run_inbound_analysis()
    print(result.get_explain())
    print(result.get_explain())