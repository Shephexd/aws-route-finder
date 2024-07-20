## AWS Route Finder

AWS Route Finder는 VPC Reachability Analyzer를 기반으로 AWS 인프라의 경로 상의 연결성을 손쉽게 테스트할 수 있는 도구입니다.   
이 도구를 사용하여 AWS 네트워크 경로를 분석하고, 인스턴스와 인터넷 게이트웨이 간의 연결성을 확인할 수 있습니다.

### 기능

- EC2 인스턴스 등록: 현재 AWS 계정의 모든 EC2 인스턴스를 등록합니다.
- 인터넷 게이트웨이 등록: 현재 AWS 계정의 모든 인터넷 게이트웨이를 등록합니다.
- 경로 분석 생성: 지정된 소스 및 대상 간의 네트워크 경로 분석을 생성합니다.
- 경로 분석 실행: 생성된 네트워크 경로 분석을 실행하고 결과를 반환합니다.
- 실시간 경로 분석 결과 확인: 경로 분석 결과를 기반으로 네트워크 연결성을 검증합니다.

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

1. Select SourceType(EC2, IP Address on AWS, Internet Gateway)
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