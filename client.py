from socket import *
import sys, os, inspect

# Get the content length value.
# meta_data: the meta data in the response message.
def get_content_length(meta_data):
   content_length = ''
   meta_data_len = len(meta_data)
   # According to how my server constructs the headers, the last field before
   # the data is the content length field.
   for i in range(0, meta_data_len):
      if meta_data[meta_data_len - i - 1] == ':':
         break
      content_length = meta_data[meta_data_len - i - 1] + content_length
   return int(content_length.strip())

# Parse the response message.
# response: response message.
# filename: name of the file sent.
# command: either get or head.
def parse_response(response, filename, command):
   BUFFER_SIZE = 1024
   command = command.lower()
   tokens = response.split()
   status_code = tokens[1]
   # Make sure filename is correct!
   if filename == '':
         filename = 'index.html'
   # Get filename path to save in the downloads.
   base_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
   filename = os.path.join(base_dir, 'Download', filename)
   # Get file content.
   data_list = response.split('\r\n\r\n')
   if len(data_list) > 1: # File contains data!
	   data = data_list[1]
	   for i in range(2, len(data_list)):
		  data = data + '\r\n\r\n' + data_list[i]
	   # Check if there is more data to add!
	   if status_code == '200' and command == 'get':
		  content_length = get_content_length(data_list[0])
		  # Write data to the output file.
		  file_handler = open(filename,'wb')
		  file_handler.write(data)
		  recv_data_len = len(data)
		  while recv_data_len < content_length: # More data to write.
			 data = clientSocket.recv(BUFFER_SIZE)
			 file_handler.write(data)
			 recv_data_len = recv_data_len + len(data)
		  file_handler.close()
   if command == 'head': # Write meta-data to the file.
	  file_handler = open(filename + '_HEAD','ab')
	  file_handler.write(response)
	  file_handler.close()
   # Output the headers of the response message to the user terminal.
   header = data_list[0]
   print header


# Get args from the commandline.
filename = ''
command = ''
if len(sys.argv) == 5:
   filename = sys.argv[3]
   command = sys.argv[4]
elif len(sys.argv) == 4: # filename not specified.
   command = sys.argv[3]
else:
   print 'commandline not correct!'
   exit(0)
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
request = command + ' /' + filename + ' HTTP/1.0'
clientSocket.send(request.encode())
response = clientSocket.recv(1024)
# Parse server response and save the file.
parse_response(response, filename, command)
clientSocket.close()

