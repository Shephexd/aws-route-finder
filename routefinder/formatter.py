import emoji


def summarize_component(component):
    return f"Component ID: {component['Id']}, ARN: {component['Arn']}, Name: {component.get('Name', 'N/A')}"


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
            explanation_code = item.get("ExplanationCode")
            message = f"ExplanationCode: {explanation_code}"

            if explanation_code == "NO_ROUTE_TO_DESTINATION":
                destination_id = item.get("Destination", {}).get("Id")
                route_table_id = item.get("RouteTable", {}).get("Id")
                vpc_id = item.get("Vpc", {}).get("Id")
                message += f" - No route to destination {destination_id} in route table {route_table_id} of VPC {vpc_id}."

            elif explanation_code == "TGW_RTB_CANNOT_ROUTE":
                tgw_id = item.get("TransitGateway", {}).get("Id")
                tgw_route_table_id = item.get("TransitGatewayRouteTable", {}).get("Id")
                destination_cidr = item.get("TransitGatewayRouteTableRoute", {}).get("DestinationCidr")
                attachment_id = item.get("TransitGatewayRouteTableRoute", {}).get("AttachmentId")
                resource_id = item.get("TransitGatewayRouteTableRoute", {}).get("ResourceId")
                resource_type = item.get("TransitGatewayRouteTableRoute", {}).get("ResourceType")
                message += (f" - Transit Gateway Route Table {tgw_route_table_id} cannot route to {destination_cidr}. "
                            f"Attachment {attachment_id} for {resource_type} {resource_id} on TGW {tgw_id}.")

            elif explanation_code == "IGW_PUBLIC_IP_ASSOCIATION_FOR_EGRESS":
                igw_id = item.get("InternetGateway", {}).get("Id")
                vpc_id = item.get("Vpc", {}).get("Id")
                message += f" - Internet Gateway {igw_id} requires a public IP association for egress traffic in VPC {vpc_id}."

            elif explanation_code == "IGW_REJECTS_SPOOFED_TRAFFIC":
                igw_id = item.get("InternetGateway", {}).get("Id")
                vpc_id = item.get("Vpc", {}).get("Id")
                message += f" - Internet Gateway {igw_id} rejects spoofed traffic in VPC {vpc_id}."

            else:
                message += " - Unknown issue."

            messages.append(message)
        messages.append("\n")
        return "\n".join(messages)

