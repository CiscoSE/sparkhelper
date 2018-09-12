"""

Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""
from __future__ import absolute_import, division, print_function

import sparkhelper


__author__ = "Tim Taylor <timtayl@cisco.com>"
__contributors__ = []
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

bot_tokens = {'bot_1_key': "bot_auth_token_1",
              'bot_2_key': "bot_auth_token_2"}

allowed_person_Org_Id = ['yourOrgsWebexTeamsIDHere']


if __name__ == "__main__":
    for key, bot_token in bot_tokens.items():
        print("searching for memberships for {}".format(key))
        sparkhelper.check_and_delete_membership(bot_token, allowed_person_Org_Id)

        print("")
