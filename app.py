#!/usr/bin/env python3
import os

import aws_cdk as cdk

from ec2_monitoring.ec2_monitoring_stack import Ec2MonitoringStack


app = cdk.App()
env = cdk.Environment(region="eu-central-1", account="542258342574")
Ec2MonitoringStack(app, "Ec2MonitoringStack", env=env)

app.synth()
