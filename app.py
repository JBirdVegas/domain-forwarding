#!/usr/bin/env python3

from aws_cdk import core

from forwarding.forwarding_stack import ForwardingStack


app = core.App()
ForwardingStack(app, "forwarding")

app.synth()
