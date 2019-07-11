import json
import logging
import subprocess
from concurrent.futures import ProcessPoolExecutor

from nltk.tokenize import sent_tokenize
from websocket_server import WebsocketServer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(' %(module)s -  %(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


class RunModel:
    def __init__(self,
                 input_filename: str = 'path to input.txt',
                 input_str: str = None,
                 output_dir: str = 'path to output dir',
                 model_path: str = 'path to trained model checkpoint.pt',
                 gpu_num: str = None
                 ):
        self.input_filename = input_filename
        self.input_str = input_str
        self.output_dir = output_dir
        self.model_path = model_path
        self.token_list = ['0', '1', '2', '3', '4']
        self.token_display = ['<1>', '<2>', '<3>', '<4>', '<5>']
        self.gpu_num = gpu_num
        self.run_script = 'path to /run_trained_model_demo.sh'

    def run_gec(self):
        self.make_input_file()
        logger.info(f'input_str: {self.input_str}')
        logger.info(f'gpu: {self.gpu_num}')
        with ProcessPoolExecutor() as executor:
            for token in self.token_list:
                executor.submit(self.process, token)
        result_dict = self.load_output()
        result_str = json.dumps(result_dict)
        return result_str

    def process(self, token):
        subprocess.call(
            [self.run_script, self.input_filename, self.output_dir, self.model_path, token, self.gpu_num]
        )

    def make_input_file(self):
        with open(self.input_filename, 'w') as f:
            for sentence in sent_tokenize(self.input_str):
                print(sentence, file=f)

    def load_output(self):
        outputs = dict()
        for token, disp in zip(self.token_list, self.token_display):
            output_file = open(f'{self.output_dir}_{token}/output.tok.txt', 'r')
            outputs[disp] = output_file.read()
        logger.info(f'output: {outputs}')
        return outputs


def get_gpu_info(nvidia_smi_path='nvidia-smi', no_units=True):
    keys = ('index', 'memory.free')
    nu_opt = '' if not no_units else ',nounits'
    cmd = '%s --query-gpu=%s --format=csv,noheader%s' % (nvidia_smi_path, ','.join(keys), nu_opt)
    output = subprocess.check_output(cmd, shell=True)
    lines = output.decode().split('\n')
    lines = [line.strip() for line in lines if line.strip() != '']

    return [{k: v for k, v in zip(keys, line.split(', '))} for line in lines]


def check_gpu():
    gpu_info = get_gpu_info()
    gpu_num = ''
    for gpu in gpu_info:
        if int(gpu['memory.free']) > 5600:
            gpu_num = gpu['index']
            break
        else:
            pass
    return gpu_num


def new_client(client, server):
    logger.info('New client {}:{} has joined.'.format(client['address'][0], client['address'][1]))


def send_msg_allclient(client, server, message):
    logger.info('Message "{}" has been received from {}:{}'.format(message, client['address'][0], client['address'][1]))
    input_str = message
    gpu_num = check_gpu()
    model = RunModel(input_str=input_str, gpu_num=gpu_num)
    result = model.run_gec()
    logger.info(f'result: {result}')
    server.send_message_to_all(result)


if __name__ == '__main__':
    ip = ''
    port = 
    server = WebsocketServer(port=port, host=ip)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(send_msg_allclient)
    server.run_forever()
