import json

from aws_cdk import (core,
                     aws_apigateway,
                     aws_certificatemanager as cert_manager,
                     aws_route53_targets as targets,
                     aws_route53 as route53)


class Config:
    def __init__(self, domain_name, zone_id, redirect_url):
        self.domain_name = domain_name
        self.zone_id = zone_id
        self.redirect_url = redirect_url


class ForwardingStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, config: Config, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, "hostedZoneForApiGateway",
                                                                     hosted_zone_id=config.zone_id,
                                                                     zone_name=config.domain_name)
        cors_options = aws_apigateway.CorsOptions(allow_headers=['*'],
                                                  allow_methods=['*'],
                                                  allow_origins=['*'])
        certificate = cert_manager.DnsValidatedCertificate(
            self,
            f'domain_cert_for_{config.domain_name.split(".")[0]}',
            domain_name=config.domain_name,
            hosted_zone=hosted_zone,
            validation_method=cert_manager.ValidationMethod.DNS)
        domain_name_options = aws_apigateway.DomainNameOptions(certificate=certificate,
                                                               domain_name=config.domain_name,
                                                               security_policy=aws_apigateway.SecurityPolicy.TLS_1_2)
        api = aws_apigateway.RestApi(self, "restapi",
                                     rest_api_name='rest-forwarder',
                                     domain_name=domain_name_options,
                                     deploy=True,
                                     default_cors_preflight_options=cors_options,
                                     deploy_options=aws_apigateway.StageOptions(cache_data_encrypted=True,
                                                                                stage_name='prod'))
        response = aws_apigateway.IntegrationResponse(
            status_code="302",
            response_parameters={
                'method.response.header.location': f"'{config.redirect_url}'"
            },
            response_templates={

            })
        api.root.add_method(
            "ANY",
            aws_apigateway.MockIntegration(
                integration_responses=[response],
                passthrough_behavior=aws_apigateway.PassthroughBehavior.WHEN_NO_MATCH,
                request_templates={
                    "application/json": json.dumps({
                        "statusCode": 302,
                        "headers": {
                            "location": config.redirect_url
                        }
                    })
                }
            ),
            method_responses=[
                aws_apigateway.MethodResponse(
                    response_models={
                        "application/json": aws_apigateway.Model.EMPTY_MODEL
                    },
                    status_code="302",
                    response_parameters={
                        'method.response.header.location': True
                    },
                )
            ]
        )
        # noinspection PyTypeChecker
        api_domain_target = route53.RecordTarget.from_alias(targets.ApiGatewayDomain(api.domain_name))
        route53.ARecord(self, 'arecord',
                        target=api_domain_target,
                        zone=hosted_zone,
                        record_name=config.domain_name)
