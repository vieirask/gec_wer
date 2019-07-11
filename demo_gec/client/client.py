import socket

from flask import Flask, render_template, request, redirect, url_for
from websocket import create_connection

import logging
import json


app = Flask(__name__)
ip = ''
port = 

ws = create_connection('ws://{}:{}/'.format(ip, port))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(' %(module)s -  %(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


@app.route('/gec_wer')
def index():
    return render_template('form.html')

@app.route('/gec_wer', methods=['GET', 'POST'])
def post():
    logger.info("post")
    if request.method == 'POST':
        logger.info("into post")
        input_str = request.form['input_str']
        send_str = input_str
        logger.info("Send '{}'".format(send_str))

        while True:
            logger.info("Send '{}'".format(send_str))
            ws.send(send_str)
            result_str = ws.recv()
            logger.info("Received '{}'".format(result_str))
            result_dict = json.loads(result_str)
            return render_template('confirm.html', input_str=input_str, result=result_dict)

if __name__ == '__main__':
    app.run(port=)
