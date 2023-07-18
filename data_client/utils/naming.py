#
# Created on Tue Jul 18 2023
#
# Copyright (c) 2023 Company-placeholder. All rights reserved.
#
# Author Yubinlv.
#

import re


# define a function to convert camelCase to under_score
def camel_to_under(camel_string):
    # use a regular expression to match all capital letters
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    # use the sub() method to replace capital letters with an underscore followed by the lowercase letter
    under_string = pattern.sub('_', camel_string).lower()
    return under_string
