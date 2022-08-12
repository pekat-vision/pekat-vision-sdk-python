# PEKAT VISION api
#
# A Python module for communication with PEKAT VISION 3.10.2 and higher
#
# Author: developers@pekatvision.com
# Date:   11 August 2022
# Web:    https://github.com/pekat-vision

import json
import os
import platform
import random
import socket
import string
import sys
import subprocess
import atexit
import base64

import numpy as np
import requests


__version__ = '1.3.3'


class DistNotFound(Exception):
    def __str__(self):
        return "PEKAT VISION dist not found"


class DistNotExists(Exception):
    def __str__(self):
        return "PEKAT VISION dist not exists"


class PortIsAllocated(Exception):
    def __str__(self):
        return "Port is allocated"


class InvalidData(Exception):
    def __str__(self):
        return "Invalid input data. Allowed types are the file path (string) or image in numpy array"


class InvalidResponseType(Exception):
    def __str__(self):
        return "Invalid response type (context, image, annotated_image)"


class CannotBeTerminated(Exception):
    def __str__(self):
        return "Already running instance cannot be terminated"


class ProjectNotFound(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "Project not found. Check path {}.".format(self.path)


class PekatNotStarted(Exception):
    def __str__(self):
        return "Pekat not started from unknown reason"


class OpenCVImportError(Exception):
    def __str__(self):
        return "You need opencv-python installed for this type of response_type"

class NoConnection(Exception):
    def __str__(self):
        return "Could not establish connection with running instance."


class Instance:
    def __init__(
            self,
            project_path=None,
            dist_path=None,
            port=None,
            host='127.0.0.1',
            already_running=False,
            password=None,
            api_key=None,
            disable_code=None,
            tutorial_only=None,
            context_in_body=False,
            wait_for_init_model=False,
            ping=True,
            gpu=0,
    ):
        """
        Create instance of interface for communication

        :param project_path: Path to project. It is ignored is already_running=True
        :type project_path: str
        :param dist_path: path to PEKAT VISION binaries. It is ignored is already_running=True
        :type dist_path: str
        :param port:
        :type port: int
        :param host:
        :type host: str
        :param already_running: Instance will not be created. It joins to existing one. Raises NoConnection if ping fails.
        :type already_running: bool
        :param password: access to client gui
        :type password: str
        :param api_key: api key - more in PEKAT VISION doc
        :type api_key: str
        :param disable_code: disable module code
        :type disable_code: bool
        :param tutorial_only: allow only Anomoly of Surface tutorial
        :type tutorial_only: bool
        :param context_in_body: receive context in body instead of header
        :type context_in_body: bool
        :param wait_for_init_model: wait for all models to load before returning the Instance object
        :type wait_for_init_model: bool
        :param ping: ping the address to check whether the Instance is running
        :type ping: bool
        :param gpu: which GPU to start project on. It is ignored is already_running=True
        :type gpu: int
        """
        self.project_path = project_path
        self.dist_path = dist_path

        self.host = host
        self.already_running = already_running
        self.password = password
        self.api_key = api_key
        self.disable_code = disable_code
        self.tutorial_only = tutorial_only
        self.context_in_body = context_in_body
        self.wait_for_init_model = wait_for_init_model
        self.gpu = gpu

        if port is None:
            self.port = self.__find_free_ports()
            self.port_is_defined = False
        else:
            self.port = port
            self.port_is_defined = True

        if not already_running:
            self.__start_instance()
            atexit.register(self.stop)

        if ping:
            self.ping()

        self.__stopping = False

    def analyze(self, image, response_type='context', data=None, timeout=20):
        """
        Send image to PEKAT VISION. PEKAT VISION return result of recognition.
        :param image: numpy image or path to image file
        :type image: numpy, str
        :param response_type: more in PEKAT VISION doc
        :type response_type: str
        :param data: adds data to the query - more in PEKAT VISION doc
        :type data: str
        :param timeout: Timeout to request
        :type timeout: int
        :return: results of recognition based on response_type
        :rtype: (numpy, object), object
        """
        image_path = None
        numpy_image = None

        if isinstance(image, str):
            image_path = image
        elif isinstance(image, (np.ndarray, np.generic)):
            numpy_image = image
        else:
            raise InvalidData()

        if response_type not in ['annotated_image', 'context', 'heatmap']:
            raise InvalidResponseType

        query = 'response_type={}'.format(response_type)
        url = 'http://{}:{}'.format(self.host, self.port)

        if self.api_key:
            query += '&api_key={}'.format(self.api_key)

        if data:
            query += '&data={}'.format(data)

        if self.context_in_body:
            query += '&context_in_body'

        if image_path:
            with open(image_path, 'rb') as data:
                response = requests.post(
                    url='{}/analyze_image?{}'.format(url, query),
                    data=data.read(),
                    timeout=timeout,
                    headers={'Content-Type': 'application/octet-stream'}
                )
        else:
            shape = numpy_image.shape
            response = requests.post(
                url='{}/analyze_raw_image?width={}&height={}&{}'.format(url, shape[1], shape[0], query),
                data=numpy_image.tobytes(),
                headers={'Content-Type': 'application/octet-stream'},
                timeout=timeout
            )

        if response_type in ['heatmap', 'annotated_image']:
            if self.context_in_body:
                image_len = int(response.headers.get('ImageLen'))
                if not image_len:
                    return response.json()
                np_arr = np.frombuffer(response.content[:image_len], np.uint8)
                context_json = response.content[image_len:].decode('utf-8')
            else:
                np_arr = np.frombuffer(response.content, np.uint8)
                context_base64 = response.headers.get('ContextBase64utf')
                if context_base64 is None:
                    return response.json()
                context_json = base64.b64decode(context_base64)
            try:
                import cv2
                return cv2.imdecode(np_arr, 1), json.loads(context_json)
            except ImportError:
                raise OpenCVImportError()
        else:
            return response.json()

    def __get_dist_path(self):
        if self.dist_path:
            if os.path.exists(self.dist_path):
                return self.dist_path
            else:
                raise DistNotExists()
        elif platform.system() == "Windows":
            program_files_path = "{}\\Program Files".format(os.environ['systemdrive'])
            for i in os.listdir(program_files_path):
                if i.startswith("PEKAT VISION "):
                    return os.path.join(program_files_path, i)

        raise DistNotFound()

    @staticmethod
    def __find_free_ports():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', 0))
        _, port = s.getsockname()
        s.close()
        return port

    def __random_string(self, string_length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(string_length))

    def __check_project(self):
        return os.path.exists(os.path.join(self.project_path, 'pekat_package.json'))

    def __start_instance(self):
        if not self.__check_project():
            raise ProjectNotFound(self.project_path)

        dist_path = self.__get_dist_path()
        server_path = os.path.join(dist_path, "pekat_vision/pekat_vision")
        self.stop_key = self.__random_string(10)

        params = [
            server_path,
            "-data",
            self.project_path,
            "-port",
            str(self.port),
            "-host",
            self.host,
            "-stop_key",
            self.stop_key,
        ]
        
        if self.gpu:
            params += ["-gpu", str(self.gpu)]

        # add other arguments
        if self.api_key:
            params += ["-api_key", self.api_key]
        if self.password:
            params += ["-password", self.password]
        if self.disable_code:
            params += ["-disable_code", self.disable_code]
        if self.tutorial_only:
            params += ["-tutorial_only", self.tutorial_only]

        self.process = subprocess.Popen(
            params,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        stop_init_model = not self.wait_for_init_model
        server_running = False

        # wait for start
        while True:
            next_line = self.process.stdout.readline().decode()
            if next_line == '' and self.process.poll() is not None:
                break
            sys.stdout.flush()
            
            if next_line.find("__SERVER_RUNNING__") != -1:
                server_running = True
            if next_line.find("STOP_INIT_MODEL") != -1:
                stop_init_model = True
            if server_running and stop_init_model:
                return
            
            if next_line.find("OSError: [Errno 48] Address already in use") != -1:

                if self.port_is_defined:
                    raise PortIsAllocated()
                else:
                    self.port = self.__find_free_ports()
                    return self.__start_instance()
        raise PekatNotStarted()

    def stop(self, timeout=5):
        """
        Stop running instance
        :param timeout: Timeout to kill process
        :type timeout: int
        """
        # only own subprocess (PEKAT) can be stopped
        if not self.process or self.__stopping:
            return

        self.__stopping = True

        requests.get(
            url='http://{}:{}/stop?key={}'.format(self.host, self.port, self.stop_key),
            timeout=timeout
        )
    
    def ping(self, timeout=5):
        """
        Ping Pekat server.
        :param timeout: Timeout to ping
        :type timeout: int
        :return: ping response
        :rtype: requests.Response
        """
        try:
            return requests.get(
                url='http://{}:{}/ping'.format(self.host, self.port),
                timeout=timeout
            )
        except requests.exceptions.Timeout as e:
            raise NoConnection()
        except Exception as e:
            raise e
