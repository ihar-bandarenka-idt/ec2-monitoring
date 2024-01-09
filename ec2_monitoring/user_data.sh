#!/bin/bash
InstanceId=$(ec2-metadata -i |gawk '{ print $2 }')
wget https://s3.eu-central-1.amazonaws.com/amazoncloudwatch-agent-eu-central-1/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm
cat << EOF > /opt/aws/amazon-cloudwatch-agent/bin/config.json
{
  "agent": {
    "metrics_collection_interval": 60,
    "aws_sdk_log_level": "LogDebugWithEventStreamBody"
  },
  "metrics": {
    "append_dimensions": {
      "InstanceId": "${InstanceId}"
    },
    "namespace": "myspace1",
    "metrics_collected": {
      "cpu": {
        "append_dimensions": {
          "InstanceId": "${InstanceId}"
        },
        "measurement": [
          {
            "name": "cpu_usage_idle",
            "unit": "Percent"
          },
          {
            "name": "cpu_usage_nice",
            "unit": "Percent"
          }
        ],
        "totalcpu": true
      }
    }
  }
}
EOF
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json -s
