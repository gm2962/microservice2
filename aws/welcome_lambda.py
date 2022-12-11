import json
import boto3
import os


def lambda_handler(event, context):
    payload = json.loads(event['Records'][0]['Sns']['Message'])
    email_added = payload["send_email"]

    admin_email = os.environ['ADMIN_EMAIL']
    ses = boto3.client('ses')

    body = f"""
		Welcome {email_added}. We hope you have a great shopping experience! 
	"""

    ses.send_email(
        Source=admin_email,
        Destination={'ToAddresses': [email_added]},
        Message={
            'Subject': {
                'Data': 'Welcome to our store',
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
