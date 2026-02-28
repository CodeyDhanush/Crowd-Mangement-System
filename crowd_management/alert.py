from twilio.rest import Client
from twilio.bse.exceptions import TwilioRestException

class Alertmsg:
    def __init__(self):
        self.account_sid = ""
        self.auth_token = ""
        self.from_number = ''

    def send_alert(self, number, message):
        """
        Sends an SMS alert using Twilio.
        """
        try:
            client = Client(self.account_sid, self.auth_token)

            sent_message = client.messages.create(
                from_=self.from_number,
                



                
                body=message,
                to=number
            )

            print(f"Alert sent successfully to {number}! SID: {sent_message.sid}")
            return sent_message.sid

        except TwilioRestException as e:
            print(f"Twilio Error: {e}")
            return None

        except Exception as e:
            print(f"Unexpected Error: {e}")
            return None

if __name__ == "__main__":
    print("--- Twilio Alert System Test ---")
    alert_system = Alertmsg()
    recipient_number = input("Enter recipient number (): ").strip()
    alert_message = input("Enter message: ").strip()

    if recipient_number and alert_message:
        alert_system.send_alert(recipient_number, alert_message)
    else:
        print("Recipient number and message are required.")