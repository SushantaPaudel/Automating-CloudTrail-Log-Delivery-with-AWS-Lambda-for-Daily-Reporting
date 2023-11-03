import boto3
import logging
from datetime import datetime, timedelta

def get_cloudtrail_events():
    cloudtrail_client = boto3.client('cloudtrail', region_name='us-east-1')
    function_name = "Your Lambda Function Name"  # Replace with your Lambda function name
    now = datetime.utcnow()
    start_time = now - timedelta(days=1)  # Adjust the time window to 24 hours

    response = cloudtrail_client.lookup_events(
        StartTime=start_time,
        EndTime=now,
    )

    events = response.get('Events', [])
    
    relevant_events = []
    for event in events:
        # Check if the 'Username' field is present in the event
        if 'Username' in event:
            # You can add additional checks or filters here as needed
            if event['Username'] != function_name:
                relevant_events.append(event)

    return relevant_events

def send_email(events):
    ses_client = boto3.client('ses', region_name='us-east-1')
    from_email = 'Your From Email'  # Replace with your email
    to_email = 'Your Recipient's Email'  # Replace with recipient's email

    subject = 'CloudTrail Events Report'
    body = "\n\n".join([str(event) for event in events])

    response = ses_client.send_email(
        Source=from_email,
        Destination={'ToAddresses': [to_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )

    return response

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        events = get_cloudtrail_events()
        
        if events:
            logger.info(f"Got {len(events)} relevant CloudTrail events. Sending email.")
            response = send_email(events)
            logger.info(f"Email sent. SES response: {response}")
        else:
            logger.info("No relevant CloudTrail events found.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == '__main__':
    lambda_handler(None, None)
