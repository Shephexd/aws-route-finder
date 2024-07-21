from botocore.config import Config
from dataclasses import dataclass, field
from prompt_toolkit.validation import Validator, ValidationError

from routefinder.dto import Endpoint


@dataclass
class CommandConfig:
    source_type: str
    source: Endpoint
    destination_type: str
    destination: Endpoint = None
    source_ip: str = ""
    destination_ip: str = ""
    destination_port: int = 80
    protocol: str = "tcp"
    boto_config: Config = None
    sync_flag: bool = True

    def serialize(self, route_finder):
        src_endpoint, src_ip = self.map_source(route_finder=route_finder,
                                               source_type=self.source_type,
                                               source=self.source)
        dest_endpoint, dest_ip = self.map_destination(route_finder=route_finder,
                                                      destination_type=self.destination_type,
                                                      destination=self.destination)

        return {
            "source": src_endpoint, "source_ip": src_ip,
            "destination": dest_endpoint, "destination_ip": dest_ip,
            "destination_port": int(self.destination_port), "protocol": self.protocol
        }

    def is_valid(self):
        if self.destination is None and self.destination_ip is None:
            raise ValueError("Destination(IP or ARN) Must be Set")

        if isinstance(self.destination, Endpoint):
            if self.source.id == self.source.id:
                raise RuntimeError("Source and Destination must be different.")
        return True

    def summarize(self):
        dest = self.destination
        if dest is None:
            dest = self.destination_ip
        print(
            f"Start Analyze from {self.source_type}({self.source}) to "
            f"{self.destination_type}({dest}), {self.protocol}({self.destination_port})")

    def map_source(self, route_finder, source_type, source) -> (Endpoint, str):
        if source_type not in {"EC2", "IP"}:
            raise ValidationError(message="source_type must be EC2 or IP on AWS")
        mapped_source = route_finder.endpoint_map[source_type][source]
        return mapped_source, ""

    def map_destination(self, route_finder, destination_type, destination) -> (Endpoint, str):
        # Analyzer based on NetworkInterface
        if destination_type in ["EC2", "IGW"]:
            return route_finder.endpoint_map[destination_type][destination], ""

        # Analyzer based on IP Address
        if destination_type in ["FQDN", "IP"]:
            if destination in route_finder.ip_map:
                destination = route_finder.get_eni_by_name(destination)
                return destination, ""
            else:
                destination_ip = route_finder.get_host_by_name(fqdn=destination)
                return None, destination_ip


class CommandConfigFactory:
    def __init__(self, command):
        self.parent = command

    def build(self, source_type, source,
              destination_type, destination,
              destination_port, protocol) -> CommandConfig:
        _config = CommandConfig(
            source=source, source_type=source_type,
            destination=destination, destination_type=destination_type,
            destination_port=destination_port, protocol=protocol
        )
        return _config
