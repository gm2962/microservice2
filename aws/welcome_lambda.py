import json
import boto3
import os


def lambda_handler(event, context):
    admin_email = os.environ['ADMIN_EMAIL']
    ses = boto3.client('ses')

    body = """
		A new user has been added
	"""

    ses.send_email(
        Source=admin_email,
        Destination={'ToAddresses': [admin_email]},
        Message={
            'Subject': {
                'Data': 'New User',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': 'UTF-8'
                }
            }
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully sent email from Lambda using Amazon SES')
    }
