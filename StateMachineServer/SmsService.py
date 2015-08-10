### Class for handling sms sending and reading  ##############
#
# NOTE! Each message takes a string parameter that needs to be parsed
# as per the needs of the specific function.
#
###############################################################

from StateMachineServer.RandomStringGenerator import RandomStringGenerator 
import android # should be installed on the device beforehand!

class SmsService(object):

    def __init__(self):
        self.droid = android.Android()
        self.rand_generator = RandomStringGenerator()
        self.tracking_phone_state = False

    def send_message_str(self, num_and_message):
        """Sends a text message to the given phone number."""
        # split the number from the message, number is first element
        as_list = num_and_message.split()
        if not len(as_list) > 1:
            return "Usage: send_message [phone number] [message]"
        # TO DO: check the first value looks like a phone number!!!
        number = as_list.pop(0)
        msgStr = ' '.join(map(str, as_list))
        print("Sms send to number '{0}' with message '{1}'".format(number, msgStr))
        result = self.droid.smsSend(number,msgStr).result
        return msgStr

    def send_message(self, number):
        """Sends a random string to the provided phone number."""
        return self.send_message_str(number + " "+ self.rand_generator.get_random_str(10))

    def make_sms_message(self, length):
        """Create a random string of length length and return."""
        if length > 160:
            print("Sms can be only 160 characters long, truncating length to 160.")
            length = 160
        return self.rand_generator.get_random_str(length)
            
    def find_new_message(self, msgStr):
        """Searches all unread messages for the message that contains the given

        msgStr parameter. Returns True if message is found and False
        otherwise.
        """
        msgs = self.droid.smsGetMessages(True)[1]
        for m in msgs:
            if m["body"] == msgStr:
                return "OK - found message '{0}".format(m)
        return "find_new_message - error: Message not found."

    def delete_message(self, msgId):
        """Delete a specific sms message from the device."""
        result = self.droid.smsDeleteMessage(msgId)[1]
        return result
    
    def start_call(self, number):
        """Try to start a phone call to the given number."""
        result = self.droid.phoneCallNumber(number)[1]
        return result

    def track_phone_state(self):
        self.tracking_phone_state = True
        result = self.droid.startTrackingPhoneState()[1]
        return result

    def read_phone_state(self):
        if self.tracking_phone_state:
            try:
                result = self.droid.readPhoneState()[1]['state']
            except KeyError as e:
                print("KeyError: {0}".format(e))
                result = None
        else:
            result = "Tracking must be switched on first!"
        return result

    def stop_tracking_phone_state(self):
        if self.tracking_phone_state:
            result = self.droid.stopTrackingPhoneState()[1]
            self.tracking_phone_state = False
        else:
            result = "Tracking must be on to be able to stop it!"
        return result
    

    
