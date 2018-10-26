# Cisco Spark Helper

There are three security related gotchas that I've discovered when developing Cisco Teams Bots.  First, needing to authenticate webhook requests from the Cisco Spark Infrastructure.  Secondly, making sure that your bot isn't being used by other organizations.  While both are super important, the latter probably more so because you don't want data leakage outside of your company.

Spark Helper provides three python functions to help alleviate these two problems.  The first function basically checks all the participants in a room to see if they are in an allowed organization.  

```python
def membership_check(room_Id, bot_token, allowed_person_Org_Id):
    date_time = dt.datetime.now()
    print("{}, membership_check starting".format(date_time))
    the_url = 'https://api.ciscospark.com/v1/memberships?roomId={}'.format(room_Id)
    room_member_orgs_allowed = False

    get_request_headers = {"Authorization": "Bearer {}".format(bot_token)}

    message_response = requests.get(the_url, verify=True, headers=get_request_headers)
    if message_response.status_code == 200:

        message_json = json.loads(message_response.text)

        room_member_orgs_allowed = orgs_are_in_allowed_org_list(allowed_person_Org_Id, message_json)

    else:
        print("{},   membership check failed: {}".format(date_time, message_response))

    print("{}, membership_check ending".format(date_time))
    return room_member_orgs_allowed

```

If a participant in a Spark Space is not in an allowed organization, it returns *False* and you can decide how to proceed.  For example, ignore the request or potentially boot the person from the space.

The second function provides a function where you can periodically check which spaces your bot are in and remove them in case there are people outside of your organization.  This way, prying eyes are less likely to see sensitive information.
```python
def check_and_delete_membership(bot_token, allowed_person_Org_Id):
    membership_url = "https://api.ciscospark.com/v1/memberships"
    membership_message_response = requests.get(membership_url, verify=True, headers={'Authorization': 'Bearer {}'.format(bot_token)})

    response_json = json.loads(membership_message_response.text)
    print(response_json, membership_message_response.status_code)
    if membership_message_response.status_code != 200:
        return
    memberships = response_json['items']
    # print(memberships)

    bad_memberships = []
    for membership_item in memberships:
        roomId = membership_item['roomId']
        membership_id = membership_item['id']

        allowed_membership = membership_check(roomId, bot_token, allowed_person_Org_Id)

        if allowed_membership == False:
            bad_memberships.append(membership_id)

            print("   Found Membership to delete:\n   ...roomId: {}\n   ...membershipId:  {}\n".format(roomId,
                                                                                                       membership_id))

    if len(bad_memberships) > 0:
        for bad_membership_id in bad_memberships:
            print("   ...deleting membership:  {}".format(bad_membership_id))
            delete_url = "https://api.ciscospark.com/v1/memberships/{}".format(bad_membership_id)
            delete_message_response = requests.delete(delete_url, verify=True,
                                               headers={'Authorization': 'Bearer {}'.format(bot_token)})
            if delete_message_response.status_code != 204:
                print("!!!***...unable to delete membership.  Rerun audit to delete")
            else:
                print("   ...delete membership status code: {}".format(delete_message_response.status_code))

    else:
        print("...no memberships to delete")

```


The third function will verify the signature sent by the Cisco Spark webhook request.  As with the membership organization check above, if it returns *False*, you can just throw away the request.  Conceivably you could have a cron job periodically call this function with the appropriate bot token and org ID.

```python
def verify_signature(key, raw_request_data, request_headers):
    date_time = dt.datetime.now()
    print("{}: verify_signature: start".format(date_time))
    signature_verified = False
    # Let's create the SHA1 signature
    # based on the request body JSON (raw) and our passphrase (key)
    hashed = hmac.new(key, raw_request_data, hashlib.sha1)
    validated_signature = hashed.hexdigest()

    if validated_signature == request_headers.get('X-Spark-Signature'):
        signature_verified = True
        print("{}:   verify_signature: webhook signature is valid".format(dt.datetime.now()))
    else:
        print("{}.   verify_signature: webhook signature is NOT valid".format(dt.datetime.now()))

    print("{}: verify_signature: end".format(date_time))
    return signature_verified

```

In a Flask type of application, this is how I typically use them:

```python
@app.route('/yourApp',methods =['POST'])
def handle_request():
    request_json = request.json
    
    # You don't want to store this stuff in your source
    bot_token = os.environ.get('YOUR_APP_SPARK_BOT_TOKEN')
    allowed_person_Org_Id = os.environ.get('YOUR_APP_SPARK_ORG_ID')
    key = str.encode(os.environ.get('YOUR_APP_SPARK_BOT_WEBHOOK_SECRET'))
  
    # Perform the membership check
    if not sparkhelper.membership_check(request_json['data']['roomId'], bot_token, allowed_person_Org_Id):
        return 'Ok'

    # Perform the webhook request signature authentication check
    raw = request.data
    signature_verified = sparkhelper.verify_signature(key, raw, request.headers)

    if signature_verified:
        do_stuff()

    return "Ok"

```