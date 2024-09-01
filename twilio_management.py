import os
from twilio.rest import Client

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
number_id = os.environ["TWILIO_NUMBER_ID"]
client = Client(account_sid, auth_token)

# incoming_phone_number = client.incoming_phone_numbers(
#     number_id
# ).fetch()
client.incoming_phone_numbers(
    number_id
).update(
    sms_url="https://example.com/sms",
)
