### Class for creating random strings #########################
#
# NOTE! 
#
###############################################################

import string
import random

class RandomStringGenerator(object):

    def __init__(self):
        self.CHARS = string.ascii_letters
        self.CHARS = self.CHARS + string.digits
        # self.CHARS = self.CHARS + string.punctuation
    
    
    def get_random_str(self, length):
        length = int(length)
        try:
            length = length + 1 - 1
        except TypeError:
            print("Provided value '{0}' is not integer, returning empty string.".format(length))
            length = 0
        rnd = ""
        while len(rnd) < length:
            rnd = rnd + random.choice(self.CHARS)
        # print("Created random string: '{0}'".format(rnd))
        return rnd

def main():
    rnd = RandomStringGenerator()
    print("10 random chars: "+ rnd.get_random_str(10))

if __name__ == "__main__":
    main()

