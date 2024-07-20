## AWS Route Finder

AWS Route Finder는 VPC Reachability Analyzer를 기반으로 AWS 인프라의 경로 상의 연결성을 손쉽게 테스트할 수 있는 도구입니다.   
이 도구를 사용하여 AWS 네트워크 경로를 분석하고, 인스턴스와 인터넷 게이트웨이 간의 연결성을 확인할 수 있습니다.

### 기능

- EC2 인스턴스 등록: 현재 AWS 계정의 모든 EC2 인스턴스를 등록합니다.
- 인터넷 게이트웨이 등록: 현재 AWS 계정의 모든 인터넷 게이트웨이를 등록합니다.
- 경로 분석 생성: 지정된 소스 및 대상 간의 네트워크 경로 분석을 생성합니다.
- 경로 분석 실행: 생성된 네트워크 경로 분석을 실행하고 결과를 반환합니다.
- 실시간 경로 분석 결과 확인: 경로 분석 결과를 기반으로 네트워크 연결성을 검증합니다.


## 사전 요구사항
AWS의 CloudShell에서 사용을 권장합니다.
AWS Route Finder를 사용하기 위해서는 aws-cli 도구가 설치되어 있고, 자격증명이 설정되어 있어야 합니다.


### 1. AWS CLI 설치하기
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 2. 계정 자격 증명 설정하기
```bash
$aws configure
AWS Access Key ID [None]: <AccessKeyId>
AWS Secret Access Key [None]: <위에서 발급한 Secret Access Key>
Default region name [None]: 
Default output format [None]:
```

### IAM 최소 권한 정책 예시

AWS Route Finder에서 필요한 권한은 아래와 같습니다. 

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"ec2:CreateNetworkInsightsPath",
				"ec2:StartNetworkInsightsAnalysis",
				"ec2:DescribeNetworkInsightsAnalyses",
				"ec2:DescribeNetworkInterfaces",
				"ec2:DescribeInternetGateways",
				"ec2:DescribeInstances",
				"ec2:DescribeRouteTables",
				"tiros:CreateQuery"
			],
			"Resource": "*"
		}
	]
}
```

> Tiros란?   
> Tiros는 AWS 서비스에서만 접근 가능한 서비스로, ReachabilityAnalyzer의 Finding 결과를 표시하는 서비스입니다.


```bash
$aws sts get-caller-identity
{
    "UserId": "AI******",
    "Account": "*****",
    "Arn": "arn:aws:iam::ACCOUNTID:user/USER_NAME"
}
```

**[참고자료]**
- [AWS-CLI 설치 가이드, AWS](https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/getting-started-install.html)


### 설치
AWS Route Finder를 사용하려면 boto3 라이브러리가 필요합니다. boto3를 설치하려면 다음 명령을 실행하세요:

```bash
python3 -m venv .
source bin/activate
python3 -m pip install --upgrade pip
git clone https://github.com/Shephexd/aws-route-finder/
cd aws-route-finder
pip install -r requirements.txt
alias arf="python3 $(pwd)/run.py"
arf -v
```

### 사용법

AWS Route Finder를 사용하여 경로 분석을 실행하는 방법은 다음과 같습니다:

1. Select SourceType(EC2, IP Address on AWS)
2. Select / Input Source
3. Select DestinationType(EC2, IP Address, FQDN, InternetGateway)
4. Select / Input Source
5. Select Protocol
6. Input Destination Port

```bash
arf -v # verbose mode
arf --region ap-northeast-2 # region selection
```

**output**
```bash
? Select SourceType  IP Address on AWS
? Input IP Address on AWS  10.100.30.2
? Select DestinationType  IPv4 Address
? Input IPAddress  8.8.8.8
? select Protocol  tcp
? Input Destination Port Number  80
Start Analyze from IP(10.1.154.153) to IP(8.8.8.8)
35it [00:16,  2.17it/s]                         
✅ Network Route is reachable!

Route Path Detail:
🔑 Sequence Number: 1
⚙️ Component ID: i-12312321, ...
🔗 OutboundHeader: ...
🔗 InboundHeader: ...
.
.
.
🔑 Sequence Number: 14
⚙️ Component ID: igw-0e132431, ..., Name: sample-igw
🔗 InboundHeader: ...
```


### License

이 프로젝트는 Apache 2.0 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

AWS Route Finder를 사용하여 AWS 네트워크의 경로 연결성을 손쉽게 분석하고 문제를 해결하세요!