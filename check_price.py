import requests
import pprint
import time

IFTTT_URL = "https://maker.ifttt.com/trigger/bx/with/key/bBXzNxaTX-9C0nzRQ8f4Mj"

r = requests.get('https://bx.in.th/api/')
currency = r.json()

messages = []

## Filter only THB
c_thb = list(filter(lambda c: currency[c]['primary_currency'] == "THB", currency))
for c_id in c_thb:
	pair = currency[c_id]['primary_currency'] + currency[c_id]['secondary_currency']
	change = currency[c_id]['change']
	last_price = currency[c_id]['last_price']

	prefix = ""
	prefix_change = ""

	if change < -10:
		prefix = "[แดง] "

	if change > 20:
		prefix = "[เขียว] "
		prefix_change = "+"

	pprint.pprint("฿{:,}".format(last_price))
	if pair in ["THBETH", "THBXRP", "THBBCH", "THBOMG"]:
		messages.append(prefix + pair + " " + "฿{:,}".format(last_price) + " | " + prefix_change + str(change))

sorted_messages = sorted(list(messages), reverse=True)


for msg in sorted_messages:
	data = {
		"value1": msg
	}
	requests.post(IFTTT_URL, data)
	pprint.pprint("POST: " + msg)
	time.sleep(5)

pprint.pprint("DONE")

