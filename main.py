import socket
import os
import io
import mimetypes


class HTTPResponse(object):
    def __init__(self, version, status_code, headers=None, body=''):
        if headers is None:
            headers = {}
        self.version = version
        self.status_code = status_code
        self.headers = headers
        self.body = body

    @staticmethod
    def status_code_as_str(status_code):
        if status_code == 200:
            return "200 OK"
        elif status_code == 302:
            return "302 Moved Temporarily"
        elif status_code == 404:
            return "404 Not Found"
        else:
            raise Exception('status code is unreachable')

    def __str__(self):
        str_io = io.StringIO()
        str_io.write('{} {}\n'.format(self.version, HTTPResponse.status_code_as_str(self.status_code)))
        if len(self.headers) == 0:
            str_io.write('\n')
        else:
            str_io.write('\n'.join(['{}: {}'.format(k, v) for k, v in self.headers.items()]) + '\n\n')
        str_io.write(self.body)
        return str_io.getvalue()

    def to_bytes(self):
        return bytes(str(self), 'utf-8')


class HTTPRequest(object):
    def __init__(self, str_rqst):
        rqst_elements = str_rqst.split("\r\n")
        rqst_el = [x for x in rqst_elements if len(x) != 0]
        first_line = rqst_elements[0].split(" ")
        self.method = first_line[0]
        self.route = first_line[1]
        self.http_version = first_line[2]
        self.headers = {i[0]: i[1] for i in [line.split(": ") for line in rqst_el[1:]]}


def send_response(request_path):
    if http_request.method == "GET":
        print("request_path = " + request_path)
        html_resp = io.StringIO()
        if os.path.isdir(request_path):
            if not http_request.route.endswith('/'):
                con.sendall(
                    HTTPResponse(
                        http_request.http_version,
                        302,
                        {'Location': 'http://{}'.format(http_request.headers['Host'] + http_request.route + '/')},
                        'Moved Permanently'
                    ).to_bytes()
                )
            else:
                # html_resp.write(b"%s 200 OK\n\n" % bytes(http_request.http_version, 'utf-8'))
                list_d = os.listdir(path=request_path)
                if "index.html" in list_d:
                    with open(os.path.join(request_path, "index.html"), 'rb') as file:
                        html_resp.write(str(file.read(), 'utf-8'))
                    con.sendall(HTTPResponse(http_request.http_version, 200, body=html_resp.getvalue()).to_bytes())
                else:
                    html_resp.write("<html>\n<body>\n<ul>\n")
                    for name in list_d:
                        html_resp.write("<li><a href={}>{}</a>\n".format(os.path.join(http_request.route, name), name))
                    html_resp.write("</ul>\n</body>\n</html>\n")
                    con.sendall(HTTPResponse(http_request.http_version, 200, body=html_resp.getvalue()).to_bytes())
        elif os.path.isfile(request_path):
            base_name = os.path.basename(request_path)
            cont_type = mimetypes.guess_type(base_name)[0]
            if cont_type is None:
                cont_type = "application/octet-stream"
            print(cont_type)
            # html_resp.write(b"%s 200 OK\n" % bytes(http_request.http_version, 'utf-8'))
            # html_resp.write(b"Content-Type: %s\n" % bytes(cont_type, 'utf-8'))
            # html_resp.write(b"Content-length: %s\n\n" % bytes(str(os.path.getsize(request_path)), 'utf-8'))
            con.sendall(
                HTTPResponse(
                    http_request.http_version,
                    200,
                    {'Content-Type': '{}'.format(cont_type),
                     'Content-length': '{}'.format(str(os.path.getsize(request_path)))},
                    html_resp.getvalue()
                ).to_bytes()
            )

            with open(request_path, 'rb') as file_to_send:
                con.sendall(file_to_send.read())
        else:
            con.sendall(
                HTTPResponse(
                    http_request.http_version,
                    404,
                    body='404 Not Found'
                ).to_bytes()
            )
    else:
        con.sendall(
            HTTPResponse(
                http_request.http_version,
                404,
                body='404 Not Found'
            ).to_bytes()
        )
    con.close()


# def not_found():
#     return \
#         b"%s 404 Not Found \n\n 404 Not Found" % bytes(http_request.http_version, 'utf-8')


HOST, PORT = 'localhost', 8888

listen_socket = socket.socket()
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(5)
print('Serving HTTP on port %s ...' % PORT)
while True:
    # try:
    con, client_address = listen_socket.accept()
    request = con.recv(1024)
    if request != b'':
        print(request)

        http_request = HTTPRequest(request.decode("utf-8"))
        current_directory = os.getcwd()
        send_response(os.path.join(current_directory, http_request.route[1:]))
        print("------------------------------------------------------------------------------------ \n")
    # except Exception:
    #     print('exception')
