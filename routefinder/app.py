from __future__ import print_function, unicode_literals

import time
import socket
from tqdm import tqdm
from routefinder.dto import Endpoint, EC2Instance, InternetGateways, NetworkInterface, RouteFindingResult


class RouteFinder:
    def __init__(self, ec2_client):
        self._proxy = ec2_client
        self.instance_map = {}
        self.igw_map = {}
        self.eni_map = {}
        self.ip_map = {}
        self.register_igw()
        self.register_instances()
        self.register_eni()

    @property
    def igws(self):
        return list(self.igw_map.values())

    @property
    def instances(self):
        return list(self.instance_map.values())

    def run(self, source: Endpoint, destination: Endpoint, protocol: str, source_ip='', destination_port=0,
            sync_flag=False):
        if isinstance(source, Endpoint):
            source = source.id
        if isinstance(destination, Endpoint):
            destination = destination.id

        network_insight = self.create_network_insight(source_id=source, destination_id=destination, protocol=protocol,
                                                      source_ip=source_ip, destination_port=destination_port)
        network_insight_path_id = network_insight['NetworkInsightsPath']['NetworkInsightsPathId']
        network_analysis = self.start_analysis(network_insight_path_id=network_insight_path_id)

        network_insight_analysis_id = network_analysis['NetworkInsightsAnalysis']['NetworkInsightsAnalysisId']
        finding_result = self.describe_analysis(network_insight_path_id=network_insight_path_id,
                                                network_insight_analysis_id=network_insight_analysis_id,
                                                sync_flag=sync_flag)
        return finding_result

    @staticmethod
    def get_host_by_name(fqdn: str):
        return socket.gethostbyname(fqdn)

    def get_eni_by_ip(self, ip):
        if ip not in self.ip_map:
            raise KeyError("Can't find matched ENI")
        return self.ip_map[ip]

    def get_eni_by_name(self, fqdn) -> NetworkInterface:
        ip = self.get_host_by_name(fqdn=fqdn)
        return self.get_eni_by_ip(ip=ip)

    def register_igw(self):
        igw_response = self._proxy.describe_internet_gateways()
        for igw_kwargs in igw_response["InternetGateways"]:
            _igw = InternetGateways(**igw_kwargs)
            self.igw_map[_igw.id] = _igw

    def register_instances(self):
        result = self._proxy.describe_instances(
            Filters=[{
                'Name': 'instance-state-name',
                'Values': ['running']
            }])
        k = EC2Instance.__dataclass_fields__.keys()
        _instances = []
        try:
            for r in result["Reservations"]:
                _inst = r["Instances"][0]
                _inst_dto = EC2Instance(**{i: _inst[i] for i in set(k).intersection(_inst.keys())})
                self.instance_map[_inst_dto.id] = _inst_dto
        except KeyError:
            _instances = []

    def register_eni(self):
        result = self._proxy.describe_network_interfaces()
        k = NetworkInterface.__dataclass_fields__.keys()
        _instances = []
        try:
            for row in result['NetworkInterfaces']:
                _eni_dto = NetworkInterface(**{i: row[i] for i in set(k).intersection(row.keys())})
                self.eni_map[_eni_dto.id] = _eni_dto

                for _private_ip in _eni_dto.PrivateIpAddresses:
                    self.ip_map[_private_ip] = _eni_dto
                if _eni_dto.has_eip:
                    self.ip_map[_eni_dto.Association["PublicIp"]] = _eni_dto
        except KeyError:
            _instances = []

    def create_network_insight(self, source_id, destination_id, protocol, source_ip='', destination_port=0) -> dict:
        network_insight = self._proxy.create_network_insights_path(
            Source=source_id,
            SourceIp=source_ip,
            Destination=destination_id,
            DestinationPort=destination_port,
            Protocol=protocol
        )
        return network_insight

    def start_analysis(self, network_insight_path_id) -> dict:
        network_analysis = self._proxy.start_network_insights_analysis(
            NetworkInsightsPathId=network_insight_path_id)
        return network_analysis

    def describe_analysis(self, network_insight_analysis_id, network_insight_path_id,
                          sync_flag=False) -> RouteFindingResult:
        # describe analysis result
        analysis_desc = self._proxy.describe_network_insights_analyses(
            NetworkInsightsAnalysisIds=[network_insight_analysis_id], NetworkInsightsPathId=network_insight_path_id
        )
        response = RouteFindingResult(
            network_insight_path_id=network_insight_path_id,
            network_insight_analysis_id=network_insight_analysis_id,
            detail=analysis_desc
        )
        if sync_flag:
            pbar = tqdm(total=20)

            while response.is_running:
                time.sleep(1)
                analysis_desc = self._proxy.describe_network_insights_analyses(
                    NetworkInsightsAnalysisIds=[network_insight_analysis_id],
                    NetworkInsightsPathId=network_insight_path_id
                )
                response.detail = analysis_desc
                pbar.update()
            pbar.update(20)
        return response
