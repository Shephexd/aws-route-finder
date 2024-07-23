from typing import List
from dataclasses import dataclass, field
from .formatter import AnalyzedOutputFormatter


@dataclass
class Endpoint:
    @property
    def id(self):
        raise NotImplementedError("Endpoint must have id")


@dataclass
class InternetGateways(Endpoint):
    Name: str = field(init=False, repr=True)
    VpcId: str = field(init=False, repr=True)
    InternetGatewayId: str = field(repr=True)
    OwnerId: str
    Tags: list = field(repr=False)
    Attachments: list = field(repr=False)

    def __post_init__(self):
        self.Name, self.VpcId = "", ""
        for t in self.Tags:
            if t["Key"] == "Name":
                self.Name = t["Value"]
                break

        for _attach in self.Attachments:
            if _attach["State"] == "available":
                self.VpcId = _attach["VpcId"]

    @property
    def id(self):
        return self.InternetGatewayId


@dataclass
class EC2Instance(Endpoint):
    Name: str = field(init=False, repr=True)
    ImageId: str = field(repr=False)
    InstanceId: str
    InstanceType: str = field(repr=False)
    PrivateIpAddress: str
    Tags: list = field(repr=False)
    PublicIpAddress: str = ""
    Platform: str = ""

    def __post_init__(self):
        for t in self.Tags:
            if t["Key"] == "Name":
                self.Name = t["Value"]
                break

    @property
    def id(self):
        return self.InstanceId


@dataclass
class NetworkInterface(Endpoint):
    NetworkInterfaceId: str
    InterfaceType: str
    OwnerId: str = field(repr=False)
    PrivateIpAddress: str
    PrivateIpAddresses: List[str]
    Status: str
    SubnetId: str = field(repr=False)
    VpcId: str = field(repr=False)
    AvailabilityZone: str = field(repr=False)
    SourceDestCheck: str = field(repr=False, default="")
    PrivateDnsName: str = field(repr=False, default="")
    Description: str = ""
    Groups: List[str] = field(repr=False, default=list)
    MacAddress: str = field(repr=False, default="")
    Attachment: dict = field(default_factory=dict, repr=False)
    Association: dict = field(default_factory=dict, repr=False)

    # Deny_all_igw_traffic: str

    @property
    def id(self):
        return self.NetworkInterfaceId

    @property
    def has_eip(self):
        return bool(self.Association)

    def __post_init__(self):
        _PrivateIpAddresses = [ip['PrivateIpAddress'] for ip in self.PrivateIpAddresses]
        self.PrivateIpAddresses = _PrivateIpAddresses


@dataclass
class InternetProtocolAddress(Endpoint):
    IpAddress: str

    @property
    def id(self):
        return self.IpAddress


@dataclass
class RouteFindingResult:
    network_insight_path_id: str
    network_insight_analysis_id: str
    detail: dict
    region_name: str = ""

    @property
    def status(self):
        return self.detail["NetworkInsightsAnalyses"][0]["Status"]

    @property
    def is_running(self):
        return self.status == "running"

    @property
    def is_succeed(self):
        return self.status == "succeeded"

    @property
    def is_reachable(self):
        if self.is_running:
            raise RuntimeError("RouteFinding Analysis is running")

        if self.is_succeed:
            return self.detail["NetworkInsightsAnalyses"][0]["NetworkPathFound"]

    @property
    def console_url(self):
        console_url = "https://console.aws.amazon.com/networkinsights/home"
        if self.region_name:
            console_url += f"?region_name={self.region_name}"
        console_url += f"#NetworkPath:pathId={self.network_insight_path_id}"
        return console_url

    def get_result(self, detail=False):
        headline = AnalyzedOutputFormatter.get_headline(is_reachable=self.is_reachable)
        console_url = f"console url: {self.console_url}"
        explanation = self.get_explain()

        lines = [headline, console_url, explanation]
        if detail:
            summary = self.get_forward_path_summary()
            lines.append(summary)
        return "\n".join(lines)

    def get_explain(self):
        if self.is_reachable:
            return "No Issue Found"
        return f"Reasons:\n" + AnalyzedOutputFormatter.explain(
            self.detail["NetworkInsightsAnalyses"][0]["Explanations"])

    def get_forward_path_summary(self):
        if self.is_running:
            raise RuntimeError("RouteFinding Analysis is running")

        if self.detail["NetworkInsightsAnalyses"][0]["NetworkPathFound"]:
            summary = AnalyzedOutputFormatter.summarize(
                entry=self.detail["NetworkInsightsAnalyses"][0]["ForwardPathComponents"])
        else:
            summary = "Network Path Not Found"
        return summary
