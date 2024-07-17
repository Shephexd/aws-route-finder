from __future__ import print_function, unicode_literals

import time
from tqdm import tqdm
from routefinder.dto import Endpoint, EC2Instance, InternetGateways, RouteFindingResult


class RouteFinder:
    def __init__(self, ec2_client):
        self._proxy = ec2_client
        self.instance_map = {}
        self.igw_map = {}
        self.register_igw()
        self.register_instances()

    @property
    def igws(self):
        return list(self.igw_map.values())

    @property
    def igw_names(self):
        return list(self.igw_map.keys())

    @property
    def instances(self):
        return list(self.instance_map.values())

    @property
    def instance_names(self):
        return list(self.instance_map.keys())

    def run(self, source: Endpoint, destination: Endpoint, protocol: str, source_ip='', destination_port=0, sync_flag=False):
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

    def register_igw(self):
        igw_response = self._proxy.describe_internet_gateways()
        for igw_kwargs in igw_response["InternetGateways"]:
            _igw = InternetGateways(**igw_kwargs)
            self.igw_map[str(_igw)] = _igw

    def register_instances(self):
        result = self._proxy.describe_instances()
        k = EC2Instance.__dataclass_fields__.keys()
        _instances = []
        try:
            for r in result["Reservations"]:
                _inst = r["Instances"][0]
                _inst_dto = EC2Instance(**{i: _inst[i] for i in set(k).intersection(_inst.keys())})
                self.instance_map[str(_inst_dto)] = _inst_dto
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

    def describe_analysis(self, network_insight_analysis_id, network_insight_path_id, sync_flag=False) -> RouteFindingResult:
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
                    NetworkInsightsAnalysisIds=[network_insight_analysis_id], NetworkInsightsPathId=network_insight_path_id
                )
                response.detail = analysis_desc
                pbar.update()
            pbar.update(20)
        return response


if __name__ == "__main__":
    import boto3

    client = boto3.client("ec2")
    route_finder = RouteFinder(client)
    res: RouteFindingResult = route_finder.run(
        source=route_finder.instances[0],
        destination=route_finder.instances[1],
        protocol='tcp',
        sync_flag=True
    )
    print(res.get_result(detail=True))
