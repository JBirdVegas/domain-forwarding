#!/usr/bin/env python3
import json

from aws_cdk import core

from forwarding.forwarding_stack import ForwardingStack, Config

with open('configuration.json', 'r') as _configs:
    forwards = json.loads(_configs.read())

for domain_forward in forwards:
    app = core.App(auto_synth=True)
    ForwardingStack(app, domain_forward.get("app_name"), Config(
        domain_name=domain_forward.get('domain_name'),
        zone_id=domain_forward.get('zone_id'),
        redirect_url=domain_forward.get('redirect_url')
    ))
    app.synth()
