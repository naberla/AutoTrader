#app.py

from flask import Flask, request #import main Flask class and request object
import json, sys
import datetime
import logging

# Import ibapi deps
from ibapi import wrapper
from ibapi.client import EClient
from ibapi.contract import *
from threading import Thread

from datetime import datetime
from time import sleep

try:
        logging.basicConfig(filename=sys.argv[-1],level=logging.INFO)
        logging.info("Starting logging...")
except Exception as e:
        print(e)
        sys.exit(0)


MARKET_ID = 19004

class Wrapper(wrapper.EWrapper):
    def __init__(self):
        wrapper.EWrapper.__init__(self)

    def tickByTickMidPoint(self, reqId: int, time: int, midPoint: float):
        """returns tick-by-tick data for tickType = "MidPoint" """

        logging.info("Midpoint. ReqId: " + str(reqId) +
              " Time: " + datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S") +
              " MidPoint: " + str(midPoint))
        self.cancelTickByTickData(reqId)

class Client(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

    def get_marketData(self, contract, reqId = MARKET_ID):

        # Here we are requesting tickdata for the EUR.GBP Contract.
        self.reqTickByTickData(reqId, contract, "MidPoint", 0, False)

        MAX_WAITED_SECONDS = 5
        logging.info("Getting tick data from the server... can take %d second to complete" % MAX_WAITED_SECONDS)

        sleep(MAX_WAITED_SECONDS)

class TestApp(Wrapper, Client):
    def __init__(self, ipaddress, portid, clientid):
        Wrapper.__init__(self)
        Client.__init__(self, wrapper=self)

        self.connect(ipaddress, portid, clientid)

        thread = Thread(target=self.run)
        thread.start()

        setattr(self, "_thread", thread)

lynx_app = TestApp("localhost", 7496, clientid = 0)
logging.info("serverVersion:%s connectionTime:%s" % (lynx_app.serverVersion(),
                                              lynx_app.twsConnectionTime()))

contract_nq = Contract()
contract_nq.localSymbol = "NQZ0"
contract_nq.secType = "FUT"
contract_nq.currency = "USD"
contract_nq.exchange = "GLOBEX"

contract_es = Contract()
contract_es.localSymbol = "ESZ0"
contract_es.secType = "FUT"
contract_es.currency = "USD"
contract_es.exchange = "GLOBEX"

app = Flask(__name__) #create the Flask app

@app.route('/query-example')
def query_example():
    language = request.args.get('language') #if key doesn't exist, returns None

    return '''<h1>The language value is: {}</h1>'''.format(language)

@app.route('/form-example', methods=['GET', 'POST']) #allow both GET and POST requests
def form_example():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        language = request.form.get('language')
        framework = request.form['framework']

        return '''<h1>The language value is: {}</h1>
                  <h1>The framework value is: {}</h1>'''.format(language, framework)

    return '''<form method="POST">
                  Language: <input type="text" name="language"><br>
                  Framework: <input type="text" name="framework"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''

@app.route('/json-example', methods=['POST']) #GET requests will be blocked
def json_example():
    req_data = request.get_json()
    logging.info(req_data['text'])
    if "NQ1!" in req_data['text']:
      lynx_app.get_marketData(contract_nq)
    else:
      lynx_app.get_marketData(contract_es)
#    print(req_data['text'] + "  /  " + str(datetime.datetime.now()))
#    pretty_json = json.loads(req_data)
#    print (json.dumps(pretty_json, indent=2))

    return 'Alert received' 


if __name__ == '__main__':
    #app.run(debug=True, port=5000)
    if sys.argv[-2] == "prod":
        from waitress import serve
        serve(app, host="0.0.0.0", port=80)
    else:
        app.run(host='0.0.0.0', port=80) #run app in debug mode on port 5000
