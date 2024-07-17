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
    InstanceType: str
    PrivateIpAddress: str
    Tags: list = field(repr=False)
    Platform: str = ""
    PublicIpAddress: str = ""

    def __post_init__(self):
        for t in self.Tags:
            if t["Key"] == "Name":
                self.Name = t["Value"]
                break

    @property
    def id(self):
        return self.InstanceId


@dataclass
class RouteFindingResult:
    network_insight_path_id: str
    network_insight_analysis_id: str
    detail: dict

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

    def get_result(self, detail=False):
        headline = AnalyzedOutputFormatter.get_headline(is_reachable=self.is_reachable)
        explanation = self.get_explain()
        lines = [headline, explanation]
        if detail:
            summary = self.get_forward_path_summary()
            lines.append(summary)

        return "\n".join(lines)

    def get_explain(self):
        if self.is_succeed:
            return ""
        return "\n".join(AnalyzedOutputFormatter.explain(self.detail["NetworkInsightsAnalyses"][0]["Explanations"]))

    def get_forward_path_summary(self):
        if self.is_running:
            raise RuntimeError("RouteFinding Analysis is running")

        summary = AnalyzedOutputFormatter.summarize(
            entry=self.detail["NetworkInsightsAnalyses"][0]["ForwardPathComponents"])
        return summary
