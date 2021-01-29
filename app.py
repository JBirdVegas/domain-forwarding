#!/usr/bin/env python3

from aws_cdk import core

from forwarding.forwarding_stack import ForwardingStack, Config

the_stanford_girls = core.App()
wall_street_betz = core.App()

ForwardingStack(the_stanford_girls, "theStanfordGirlsForwarding", Config(
    domain_name='thestanfordgirls.com',
    zone_id='Z0681220185CG6SLGWTT7',
    redirect_url='https://poshmark.com/closet/hbstanford'
))
ForwardingStack(wall_street_betz, "wallstreetbetzForwarding", Config(
    domain_name='wallstreetbetz.com',
    zone_id='Z02346722ZLQ8556O63VJ',
    redirect_url='https://www.reddit.com/r/wallstreetbets/'
))

the_stanford_girls.synth()
wall_street_betz.synth()
