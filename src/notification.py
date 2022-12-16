import boto3
import requests
import json
import os
AWSRegion = "us-east-1"


class SNSHandler:
    sns_client = None

    def __init__(self):
        pass

    @classmethod
    def get_sns_client(cls):
        if SNSHandler.sns_client is None:
            SNSHandler.sns_client = sns = boto3.client("sns",
                                                      aws_access_key_id=os.getenv("AWSAccessKeyId"),
                                                      aws_secret_access_key=os.getenv("AWSSecretKey"),
                                                      region_name=AWSRegion
                                                      )
        return SNSHandler.sns_client


    @classmethod
    def get_sns_topics(cls):
        s_client = SNSHandler.get_sns_client()
        result = response = s_client.list_topics()
        topics = result["Topics"]
        return topics

    @classmethod
    def send_sns_message(cls, sns_topic, message):
        s_client = SNSHandler.get_sns_client()
        response = s_client.publish(
            TargetArn=sns_topic,
            Message=json.dumps({'default': json.dumps(message)}),
            MessageStructure='json'
        )
        print("Publish response = ", json.dumps(response, indent=2))