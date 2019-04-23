import json
import requests
import datetime
import hashlib
import hmac
import base64
import time
import sys
import random 
import concurrent.futures



# Update the customer ID to your Log Analytics workspace ID
customer_id = 'XXXXXXXXX-xxxx-xxxx-xxxx-XXXXXXXXXXXXXX'

# For the shared key, use either the primary or the secondary Connected Sources client authentication key   
shared_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxxxxxxxxxxxxxxxx=="

# The log type is the name of the event that is being submitted
log_type = 'WebMonitorTest'

# An example JSON web monitor object
json_data = [{
   "StoreID": "S1001",
    "IsActive": "true"
}]
body = json.dumps(json_data)

#####################
######Functions######  
#####################

# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(
        hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
    ).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

# Build and send a request to the POST API
def post_data(rfc1123date,customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    response = requests.post(uri,data=body, headers=headers)
    return response.status_code 

# Build Heart Beat
def build_heartbeat(storeid,signal):
    hb_json_data = [{
        "Store_ID": storeid,
        "IsActive:" : signal
    }]
    #print(json.dumps(hb_json_data))
    return json.dumps(hb_json_data)

#Loop through the Minutes
#How do we generate store down....
#Signal is input to suggest how often to skip
#If signal = x, every x minutes, skip for x

def genstoreheartbeat(store,numofminutes,signal ): 
    for runminutes in range (0,numofminutes):
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        if signal == True:
            hb = build_heartbeat(store,signal)
            respcode = post_data(rfc1123date,customer_id, shared_key, hb, log_type)
            print(rfc1123date + "-" + store  + "-" + str(respcode) )
        time.sleep(60)


#Arguments
#LogAnalytics.py <minutes> <storeprefix> <storenumstart>  <maxstores>
if len(sys.argv) < 3:
    numofminutes = 5
    store = "Store"
    storecounter = 1000
    maxstores = 20
    signal = True
else:
    numofminutes = int(sys.argv[1])
    store = sys.argv[2]
    storecounter = int(sys.argv[3])
    maxstores = int(sys.argv[4])
    if sys.argv[4] == "0":
        signal = False
    else:
        signal = True

stores = []
for x in range(maxstores):
    stores.append(store+str(storecounter+x))


print(str(numofminutes) + " " + store + " " + str(stores.count)+ " " + str(maxstores) + " " + str(signal))

threadid = 1000
future_to_stores = []
# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    # Start the load operations and mark each future with its StoreID
    future_to_store = {executor.submit(genstoreheartbeat, store, numofminutes, bool(signal)): store for store in stores}
    for future in concurrent.futures.as_completed(future_to_store):
        store = future_to_store[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (store, exc))
        else:
            print('%r done' % (store))



