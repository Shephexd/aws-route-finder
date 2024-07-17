import emoji


def summarize_component(component):
    return f"Component ID: {component['Id']}, ARN: {component['Arn']}, Name: {component.get('Name', 'N/A')}"

# Explanation codes (https://docs.aws.amazon.com/vpc/latest/reachability/explanation-codes.html)
EXPLANATION_CODE_MAP = {
  "BAD_STATE": "This component is not in a functional state.",
  "BAD_STATE_ATTACHMENT": "The attachment between these components is not in a functional state.",
  "BAD_STATE_ROUTE": "This route is not in a functional state.",
  "BAD_STATE_VPN": "This VPN connection is not in a functional state.",
  "CANNOT_ROUTE": "This route can't transmit traffic because its destination CIDR or prefix list does not match the destination address of the packet.",
  "ELB_ACL_RESTRICTION": "Classic Load Balancers apply network ACLs to outbound traffic, even if it's destined for a target in the same subnet as the load balancer.",
  "ELB_INSTALLED_AZ_RESTRICTION": "This load balancer can send traffic only to targets in Availability Zones that are enabled for the load balancer.",
  "ELB_LISTENER_PORT_RESTRICTION": "This Classic Load Balancer listener allows only inbound traffic destined for the specified port, and outbound traffic with the specified destination port.",
  "ELB_LISTENERS_MISMATCH": "This Classic Load Balancer does not have a listener that accepts the traffic.",
  "ELB_NOT_CROSSZONE": "This load balancer can't send traffic to some targets because cross-zone load balancing is disabled.",
  "ELBV2_LISTENER_HAS_NO_TG": "This listener is associated with target groups that have no targets.",
  "ELBV2_LISTENER_PORT_RESTRICTION": "This listener does not accept traffic unless it has the specified destination port.",
  "ELBV2_LISTENER_REQUIRES_TG_ACCEPT": "This listener does not have a target group that accepts the traffic.",
  "ELBV2_LISTENERS_MISMATCH": "This load balancer does not have a listener that accepts the traffic.",
  "ELBV2_NO_TARGETS_IN_AZ": "The load balancer does not have targets in the specified Availability Zones.",
  "ELBV2_SOURCE_ADDRESS_PRESERVATION": "If source address preservation is enabled, the outgoing source address is unaltered while traversing the Network Load Balancer.",
  "ENI_ADDRESS_RESTRICTION": "This network interface does not allow inbound or outbound traffic unless the source or destination address matches its private IP address.",
  "ENI_SG_RULES_MISMATCH": "This security group has no inbound or outbound rules that apply.",
  "ENI_SOURCE_DEST_CHECK_RESTRICTION": "Network interfaces with source/destination check enabled reject inbound traffic if the destination address does not match one of its private IP addresses, and reject outbound traffic if the source address does not match one of their private IP addresses.",
  "FIREWALL_RULES_RESTRICTION": "The traffic is blocked by a matching Network Firewall firewall rule.",
  "GATEWAY_REJECTS_SPOOFED_TRAFFIC": "Gateways reject traffic with spoofed addresses from the VPC.",
  "GWLB_DESTINATION_PORT_RESTRICTION": "Traffic between a Gateway Load Balancer and its targets must use port 6081 as the destination port. To analyze connectivity through a Gateway Load Balancer, specify port 6081 in the path definition.",
  "GWLB_PROTOCOL_RESTRICTION": "Traffic between a Gateway Load Balancer and its targets must use the GENEVE protocol, which is UDP-based. To analyze connectivity through a Gateway Load Balancer, specify the UDP protocol in the path definition.",
  "HIGHER_PRIORITY_ROUTE": "This route table contains a route to the destination that can't be used because there is a higher priority route with the same destination CIDR.",
  "IGW_DESTINATION_ADDRESS_IN_VPC_CIDRS": "Internet gateways accept traffic only if the destination address is within the VPC CIDR block.",
  "IGW_DESTINATION_ADDRESS_NOT_IN_RFC1918_EGRESS": "Internet gateways reject outbound traffic with destination addresses in the private IP address range (see RFC1918).",
  "IGW_DESTINATION_ADDRESS_NOT_IN_RFC6598_EGRESS": "Internet gateways reject outbound traffic with destination addresses in the shared IP address range (see RFC6598).",
  "IGW_NAT_REFLECTION": "The path has an internet gateway as an intermediate component, which Reachability Analyzer does not support. Instead, analyze the path from the source to the internet gateway and then analyze the path from the internet gateway to the destination.",
  "IGW_PRIVATE_IP_ASSOCIATION_FOR_INGRESS": "Internet gateways reject inbound traffic with a destination address that is not the public IP address of a network interface in the VPC with an available attachment.",
  "IGW_PUBLIC_IP_ASSOCIATION_FOR_EGRESS": "Traffic can't reach the internet through the internet gateway if the source address is not paired with a public IP address or if the source address does not belong to a network interface in the VPC with an available attachment.",
  "IGW_SOURCE_ADDRESS_NOT_IN_RFC1918_INGRESS": "Internet gateways reject inbound traffic with source addresses in the private IP address range (see RFC1918).",
  "IGW_SOURCE_ADDRESS_NOT_IN_RFC6598_INGRESS": "Internet gateways reject inbound traffic with source addresses in the shared IP address range (see RFC6598).",
  "INGRESS_RTB_NO_PUBLIC_IP": "A middlebox appliance can't receive traffic from the internet through an ingress route table if it does not have a public IP address.",
  "INGRESS_RTB_TRAFFIC_REDIRECTION": "Subnets whose traffic is redirected to a middlebox appliance can't use a direct route to the internet gateway even when the subnet route table provides one.",
  "MORE_SPECIFIC_ROUTE": "The specified route can't be used to transmit traffic because there is a more specific route that matches. You can use filters to require that a path include a specific intermediate component.",
  "NGW_DEST_ADDRESS_PRESERVATION": "NAT gateways do not alter destination addresses.",
  "NGW_REQUIRES_SOURCE_IN_VPC": "NAT gateways can only transmit traffic that originates from network interfaces within the same VPC. NAT gateways can't transmit traffic that originates from peering connections, VPN connections, or AWS Direct Connect.",
  "NGW_SOURCE_ADDRESS_REASSIGN": "NAT gateways transform the source's addresses in outbound traffic to match its private IP address.",
  "NO_POSSIBLE_DESTINATION": "The network component can't deliver the packet to any possible destination, or the network component sent traffic to a destination in another account or Region. If the destination is in another account, enable cross-account analyses.",
  "NO_ROUTE_TO_DESTINATION": "The route table does not have an applicable route to the destination resource.",
  "PCX_REQUIRES_ADDRESS_IN_VPC_CIDR": "Traffic can traverse this peering connection only if the destination or source address is within the CIDR block of the destination VPC.",
  "PROTOCOL_RESTRICTION": "This component only accepts traffic with specific protocols.",
  "REMAP_EPHEMERAL_PORT": "Outbound traffic from a NAT gateway or load balancer has the source port remapped to an ephemeral port in the range [1024–65535].",
  "SG_HAS_NO_RULES": "This security group has no inbound or outbound rules.",
  "SG_REFERENCES_NOT_PRESERVED": "The network component discards security group information about forwarded traffic. This prevents traffic from being accepted by security group rules that accept traffic only from a source or destination that belongs to a security group.",
  "SG_REFERENCING_SUPPORT": "The transit gateway VPC attachment does not have security group referencing support enabled. Therefore, we discard security group information about forwarded traffic.",
  "SUBNET_ACL_RESTRICTION": "Inbound or outbound traffic for a subnet must be admitted by the network ACL for the subnet.",
  "TARGET_ADDRESS_RESTRICTION": "A load balancer can only route traffic that is destined for the address of one of its targets.",
  "TARGET_PORT_RESTRICTION": "A load balancer can only route traffic to a target using its registered port.",
  "TGW_ATTACH_MISSING_TGW_RTB_ASSOCIATION": "This transit gateway attachment doesn't have a valid transit gateway route table association.",
  "TGW_ATTACH_VPC_AZ_RESTRICTION": "Traffic from a VPC attachment in the default mode can't be forwarded to the network interface in this Availability Zone because it comes from an Availability Zone where the attachment has a different network interface. Traffic from a VPC attachment in appliance mode can't be forwarded to the network interface in this Availability Zone because on the forward path it used a different Availability Zone.",
  "TGW_BAD_STATE_VPN": "This VPN connection is in a non-functional state.",
  "TGW_ROUTE_AZ_RESTRICTION": "This transit gateway is not registered in the Availability Zone where the traffic originates. The VPC attachment must have a subnet association in the Availability Zone.",
  "TGW_RTB_BAD_STATE_ROUTE": "This transit gateway route table has a route to the destination that is in a bad state.",
  "TGW_RTB_CANNOT_ROUTE": "This transit gateway route table has a route to the intended destination, but the route does not match the package destination address.",
  "TGW_RTB_HIGHER_PRIORITY_ROUTE": "This transit gateway route table contains a route to the intended destination that can't be used because there is a higher-priority route with the same destination CIDR.",
  "TGW_RTB_MORE_SPECIFIC_ROUTE": "This transit gateway route table has a route to the destination, but there is a more specific route.",
  "TGW_RTB_NO_ROUTE_TO_TGW_ATTACHMENT": "This transit gateway route table has no route to this transit gateway attachment.",
  "TGW_RTB_ROUTES_ARE_UNKNOWN": "The routes of this transit gateway route table are not known. This might be due to an internal error or because the transit gateway route table does not belong to the account running the analysis.",
  "UNKNOWN_DESTINATION": "The path can't be extended because the information about the destination is insufficient.",
  "UNKNOWN_PEERED_SGS": "One of the VPCs in the VPC peering connection is unknown. This is typically because the VPC is in a different account. Access controls referencing security groups are treated as inaccessible and deny traffic crossing this peering connection.",
  "VGW_PRIVATE_IP_ASSOCIATION_FOR_EGRESS": "Virtual private gateways can't accept outbound traffic if the source address does not belong to a network interface in the VPC with an available attachment.",
  "VGW_PRIVATE_IP_ASSOCIATION_FOR_INGRESS": "Virtual private gateways can't accept inbound traffic if the destination address is not the private IP address of a network interface in the VPC with an available attachment.",
  "VPC_LOCAL_ROUTE_CIDR_RESTRICTION": "Local routes apply only to packets with a destination address within the VPC CIDR block.",
  "VPCE_GATEWAY_EGRESS_SOURCE_ADDRESS_RESTRICTION": "VPC gateway endpoints emit only traffic with source addresses within the CIDRs of their corresponding prefix lists.",
  "VPCE_GATEWAY_PROTOCOL_RESTRICTION": "VPC gateway endpoints accept only TCP or ICMP ECHO traffic, and emit only TCP or ICMP ECHO reply traffic.",
  "VPCE_SERVICE_NOT_INSTALLED_IN_AZ": "The VPC endpoint service is not installed in the specified Availability Zone.",

  #Addtional Detail Codes(https://docs.aws.amazon.com/vpc/latest/reachability/additional-detail-codes.html)
  "ASSUMPTION_PRESERVE_CLIENT_IP_IS_DISABLED": "The analysis could not describe target group attributes for the target group, so the network path is based on the assumption that client IP preservation is disabled on the target group. You should verify this assumption.",
  "ASSUMPTION_PRESERVE_CLIENT_IP_IS_ENABLED": "The analysis could not describe target group attributes for the target group, so the network path is based on the assumption that client IP preservation is enabled on the target group. You should verify this assumption.",
  "AVAILABILITY_ZONE_CROSSED": "The network path crosses Availability Zones.",
  "FIREWALL_UNSUPPORTED_HIGHER_PRIORITY_RULE_GROUP_TYPE": "There is at least one higher priority rule that could match the traffic in this path, but we ignored because it contains an unsupported rule type. Verify that the result of the analysis matches the behavior of AWS Network Firewall in your network.",
  "FIREWALL_UNSUPPORTED_HIGHER_PRIORITY_RULES": "There is at least one higher priority rule that could match the traffic in this path, but we ignored because it contains an unsupported rule option. Verify that the result of the analysis matches the behavior of AWS Network Firewall in your network.",
  "FIREWALL_UNSUPPORTED_RULE_OPTIONS": "The matching firewall rule contains an unsupported rule option. Verify that the result of the analysis matches the behavior of AWS Network Firewall in your network.",
  "MISSING_TARGET_GROUP_ATTRIBUTES": "The target group attributes for the target were missing, so the analysis could not consider them.",
  "PATH_THROUGH_GWLB_NOT_CHECKED": "The analysis does not consider that traffic entering the VPC endpoint is forwarded to a Gateway Load Balancer for inspection before exiting the VPC endpoint.",
  "RESPONSE_RTB_HAS_NO_ROUTE_TO_TRANSIT_GATEWAY": "Traffic is routed from the transit gateway to the VPC endpoint. However, there is no route from the VPC endpoint to the transit gateway, so the network might drop the response traffic.",
  "TRANSIT_GATEWAY_APPLIANCE_MODE_RECOMMENDED": "The transit gateway VPC attachment has appliance mode disabled, but traffic is inspected through a Network Firewall. We recommend that you enable appliance mode for the VPC attachment.",
  "UNIDIRECTIONAL_PATH_ANALYSIS_ONLY": "The results include forward path analysis from the source to the destination. There might be a blocking configuration in the reverse path, which could not be analyzed."
}


class AnalyzedOutputFormatter:
    @classmethod
    def get_headline(cls, is_reachable: bool):
        if is_reachable:
            head_line = f"{emoji.emojize(':check_mark_button:')} Network Route is reachable!\n"
        else:
            head_line = f"{emoji.emojize(':cross_mark:')} No Network Route Found....\n"
        return head_line

    @classmethod
    def summarize(cls, entry):
        summary = [
            "Route Path Detail:"
        ]
        for item in entry:
            sequence_number = item.pop('SequenceNumber')
            component = item.pop('Component')
            summary.append(emoji.emojize(f":key: Sequence Number: {sequence_number}"))
            if component:
                summary.append(emoji.emojize(f":gear: {summarize_component(component)}"))
            for k in list(item.keys()):
                summary.append(
                    emoji.emojize(f":link: {k}: {item.pop(k)}")
                )
            summary.append("\n")
        return "\n".join(summary)

    @classmethod
    def explain(cls, explanations):
        messages = []
        for item in explanations:
            explanation_code = item.pop("ExplanationCode")
            message = f"[{explanation_code}] - "
            message += EXPLANATION_CODE_MAP.get(explanation_code, "Unknown issue.")
            message += f"\nContext: {item}\n"
            messages.append(message)
        messages.append("\n")
        return "\n".join(messages)
