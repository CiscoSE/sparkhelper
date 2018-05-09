# Cisco Spark Helper

There are two security related gotchas that I've discovered when developing Cisco Spark Bots.  First, needing to authenticate webhook requests from the Cisco Spark Infrastructure.  Secondly, making sure that your bot isn't being used by other organizations.  While both are super important, the latter probably more so because you don't want data leakage outside of your company.

Spark Helper provides two python functions to help alleviate these two problems.  The first function basically checks all the participants in a room to see if they are in an allowed organization.  

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

        org_id_list = [d['personOrgId'] for d in message_json['items']]

        number_orgs_not_allowed = len(set(org_id_list).symmetric_difference(allowed_person_Org_Id))
        print('{}:   membership_check: items not in allowed or list: {}'.format(date_time, number_orgs_not_allowed))

        if number_orgs_not_allowed == 0:
            room_member_orgs_allowed = True
    else:
        print("{},   membership check failed: {}".format(date_time, message_response))

    print("{}, membership_check ending".format(date_time))
    return room_member_orgs_allowed

```

If a participant in a Spark Space is not in an allowed organization, it returns *False* and you can decide how to proceed.  For example, ignore the request or potentially boot the person from the space.

The second function will verify the signature sent by the Cisco Spark webhook request.  As with the membership organization check above, if it returns *False*, you can just throw away the request.

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