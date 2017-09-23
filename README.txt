1) To run the server:
python server.py port_number

for example:
python server.py 13000

2) To run the client:
python client.py server_host server_port filename command(GET\HEAD)

for example:
python client.py localhost 13000 web_image.jpg get

In this case, the file web_image.jpg will be stored in the Download folder and the following headers will be printed to the terminal.
HTTP/1.0 200 OK
Date: Mon, 18 Sep 2017 22:55:50 GMT
Server: Apache/1.3.27 (Unix)
MIME-version: 1.0
Last-Modified: Tue, 12 Sep 2017 17:25:12 GMT
Content-Type: image/jpg
Content-Length: 27535

Note that, the files are located in the Upload folder on the server.

3) To run the client to retrieve index.html either type:
python client.py localhost 13000 index.html get

or type:
python client.py localhost 13000 get

4) In case of head command, a file named filename_HEAD will be stored in the Download folder containing the response
and the headers will be printed in the terminal.
For example:
python client.py localhost 13000 lion.png head

After executing the previous command, file lion.png_HEAD will be stored in the Download containing the following headers:
HTTP/1.0 200 OK
Date: Mon, 18 Sep 2017 23:00:12 GMT
Server: Apache/1.3.27 (Unix)
MIME-version: 1.0
Last-Modified: Sun, 17 Sep 2017 23:08:15 GMT
Content-Type: image/png
Content-Length: 1581953

Also, the headers will be shown in the terminal.

5) If the request is a bad request, file not found, or forbidden,
then the server returns the corresponding error headers and a simple HTML page containing the error message to be displayed nicely by the browser.

6) The server supports the following file content types:
- HTML
- txt
- png
- jpg
- jpeg
- gif
- x-xbitmap
- ico
Otherwise, if the server receives a file content type that is not supported,
then the server will return 400 bad request message and won't return the file.

7) To run from the browser, type the following:
http://localhost:13000/
http://localhost:13000/index.html
http://localhost:13000/web_image.jpg

Note that, the files are located in the Upload folder on the server.

8) If we get multiple HEAD requests for the same file, then I append the HEAD response to the file.
