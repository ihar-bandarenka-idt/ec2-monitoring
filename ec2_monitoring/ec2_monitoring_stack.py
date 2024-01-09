import os.path

from aws_cdk import (
    aws_ec2 as ec2, Stack, Duration, aws_iam as iam

)
import aws_cdk.aws_cloudwatch as cloudwatch
import aws_cdk.aws_sns as sns
import aws_cdk.aws_cloudwatch_actions as cloudwatch_actions
import aws_cdk.aws_sns_subscriptions as subscriptions

from constructs import Construct

with open(os.path.join("ec2_monitoring", "user_data.sh")) as f:
    user_data = f.read()
print(user_data)


class Ec2MonitoringStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = iam.Role(self, "instance-role", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                        managed_policies=[
                            iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy")])

        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )
        self.vpc = ec2.Vpc.from_lookup(
            self, "VPC"
            , vpc_id="vpc-e8a9dc83"
        )

        self.instance = ec2.Instance(self, "Instance",
                                     instance_type=ec2.InstanceType("t3.small"),
                                     machine_image=amzn_linux,
                                     vpc=self.vpc,
                                     user_data=ec2.UserData.custom(user_data),
                                     role=role,
                                     key_name="test"
                                     )

        alarm = cloudwatch.Alarm(self, "CPU-IDLE",
                                 metric=cloudwatch.Metric(
                                     namespace="myspace1",
                                     metric_name="cpu_usage_idle",
                                     period=Duration.minutes(1),
                                     statistic="Average",
                                     dimensions_map=dict(InstanceId=self.instance.instance_id, cpu="cpu-total")
                                 ),
                                 comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                                 threshold=90,
                                 evaluation_periods=1,
                                 )

        topic = sns.Topic(self, "Alarm-Idle-CPU")
        topic.add_subscription(subscriptions.EmailSubscription("ihar.bandarenka@idt.net"))
        alarm.add_alarm_action(cloudwatch_actions.SnsAction(topic))
