import os, inspect, stat
from datetime import datetime

class Server:
	
	# Get the content type field for the file to be sent.
	# filename: name of the requested file.
    def get_content_type(self, filename):
        content_type = ''
        if filename.endswith('html'):
            content_type = 'text/html'
        elif filename.endswith('txt'):
            content_type = 'text/plain'
        elif filename.endswith('png'):
            content_type = 'image/png'
        elif filename.endswith('jpg'):
            content_type = 'image/jpg'
        elif filename.endswith('jpeg'):
            content_type = 'image/jpeg'
        elif filename.endswith('pjpeg'):
            content_type = 'image/pjpeg'
        elif filename.endswith('gif'):
            content_type = 'image/gif'
        elif filename.endswith('x-xbitmap'):
            content_type = 'image/x-xbitmap'
        elif filename.endswith('ico'):
            content_type = 'image/ico'
        else: # Invalid content type.
            content_type = '-1'
        return content_type

	# Get filename absoult path, in case the script is running from another path.
	# filename: filename to get its absoult path.
    def get_filename(self, filename):
		# Empty filename and therefore the second field has the protocl version instead of the filename.
        if filename == 'HTTP/1.0': 
            filename = '/'
        # Remove / in the start of the filename and remove any triling spaces.
        filename = filename[1:].strip()
        if filename == '': # If the filename is empty, then the client is requesting the index.html.
            filename = 'index.html'
		# Get the base directory of the source code, as the upload folder will be next to it.
        base_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
		# Get the absoult path of the filename.
        filename = os.path.join(base_dir, 'Upload', filename)
        return filename

	# Check if the file is readable by checking that Others have read access to the file.
	# filename: name of the file to check if it is readable to the public or not.
    def is_file_readable(self, filename):
      st = os.stat(filename)
      return bool(st.st_mode & stat.S_IROTH)

	# Check the header of the request to ensure that the request is well formatted.
	# sentence: the request message.
    def check_headers(self, sentence):
        # Check if headers are colon seperated.
        lines = sentence.split('\r\n');
        for i in range(1, len(lines)):
            if len(lines[i]) == 0: # empty line.
                continue
            if not (':' in lines[i]): # line i is not colon seperated.
                return False
        return True
		
	# Get http status message to be places in the response message as the first line.
	# sentence: the request message.
    def get_http_status_message(self, sentence):
	tokens = sentence.split()
        status_code = 0
        header = ''
		# Check if the request is a bad request.
        if (len(tokens) == 0) or ((tokens[0].lower() != 'get') and (tokens[0].lower() != 'head')) or (not (self.check_headers(sentence))):
            header = 'HTTP/1.0 400 Bad Request\r\n'
            status_code = 400
        else:
            header = 'HTTP/1.0 200 OK\r\n'
            status_code = 200
            filename = self.get_filename(tokens[1])
            is_file_exists = os.path.isfile(filename)
            if not is_file_exists:
                # Error file doesn't exist.
                header = 'HTTP/1.0 404 Not Found\r\n'
                status_code = 404
            elif not self.is_file_readable(filename):
                # Error file read permission is limited.
                header = 'HTTP/1.0 403 Forbidden\r\n'
                status_code = 403
            elif self.get_content_type(filename) == '-1':
                # Unsupported content type.
                header = 'HTTP/1.0 400 Bad Request\r\n'
                status_code = 400
        return [header, status_code]

	# Get file meta data and return its data as well.
	# filename: name of the file to get its meta data.
    def get_file_meta_data(self, filename):
         file_meta_data = ''
         # Add modification date.
         statbuf = os.stat(filename)
         modification_date = datetime.fromtimestamp(statbuf.st_mtime)
         modification_date_formatted = modification_date.strftime('%a, %d %b %Y %H:%M:%S GMT') 
         file_meta_data = 'Last-Modified: ' + modification_date_formatted  + '\r\n'
         # Add content type either html or image.
         file_meta_data = file_meta_data + 'Content-Type: ' + self.get_content_type(filename) + '\r\n'
         # Add content length.
         file_handler = open(filename, 'rb')
         data = file_handler.read()
         content_size= len(data)
         file_meta_data = file_meta_data + 'Content-Length: ' + str(content_size) + '\r\n'
         return [file_meta_data, data]

	# Get the data of the response, if the request is a bad request, file not found, or forbidden,
    # then the server returns a simple HTML page containing the error message to be dispalyed
	# nicely by the browser. Otherwise, the data will be the file content.
	# status_code: code of the request.
	# data: data of the file if there is no error.
    def get_data_message(self, status_code, data):
        message = ''
        if status_code == 400:
            message = '<html> <head> </head> <body> <p> 400 Bad Request </p> </body> </html>'
        elif status_code == 404:
            message = '<html> <head> </head> <body> <p> 404 File Not Found </p> </body> </html>'
        elif status_code == 403:
            message = '<html> <head> </head> <body> <p> 403 Forbidden </p> </body> </html>'
        elif status_code == 200:
            message = data
        return message

	# Construct and send the http response.
	# sentence: the request message.
	# connectionSocket: the socket to send the response through.
    def send_http_response(self, sentence, connectionSocket):
        BUFFER_SIZE = 1024
        tokens = sentence.split()
        response = ''
        #Add status message.
        states = self.get_http_status_message(sentence)
        header = states[0]
        status_code = states[1]
        response = header
        # Add date.
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        response = response + 'Date: ' + date + '\r\n'
        # Add server.
        response = response + 'Server: Apache/1.3.27 (Unix)\r\n'
        # Add MIME version.
        response = response + 'MIME-version: 1.0\r\n'
        data = ''
        if status_code == 200:
		   # Add file meta data.
           filename = self.get_filename(tokens[1])
           file_data = self.get_file_meta_data(filename)
           file_meta_data = file_data[0]
           data = file_data[1]
           response = response + file_meta_data 
        # Add blank line.
        response = response + '\r\n'
        # Add file content if the request is get or add error page.
        if len(tokens) != 0 and tokens[0].lower() == 'get':
            response = response + self.get_data_message(status_code, data)
        response_length = len(response)
        if response_length >= BUFFER_SIZE:
            # We need to chunck the file data to multiple messages!
            for index in range(0, response_length, BUFFER_SIZE):
                sub_response = response[index: index+BUFFER_SIZE]
                connectionSocket.send(sub_response)
        else:    
            connectionSocket.send(response)

