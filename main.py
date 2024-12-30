import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

class ResumableHTTPRequestHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)

        # Check if the path is a directory
        if os.path.isdir(path):
            return super().send_head()  # Use default directory listing
        
        # If it's a file, proceed with resumable download handling
        if not os.path.isfile(path):
            self.send_error(404, "File not found")
            return None

        # Get the file size
        file_size = os.path.getsize(path)
        start, end = 0, file_size - 1

        # Check for Range header for resumable download
        range_header = self.headers.get('Range')
        if range_header:
            try:
                # Parse the Range header
                range_values = range_header.split('=')[1]
                start, end = range_values.split('-')
                start = int(start) if start else 0
                end = int(end) if end else file_size - 1
                self.send_response(206)
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            except ValueError:
                # If range is malformed, reset to default range
                start, end = 0, file_size - 1
                self.send_response(200)
        else:
            self.send_response(200)

        # Set headers
        self.send_header("Content-type", "application/octet-stream")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()

        # Open the file and seek to the requested start position
        file = open(path, 'rb')
        file.seek(start)
        self.wfile.write(file.read(end - start + 1))
        file.close()

# Set up and run the server
def run(server_class=HTTPServer, handler_class=ResumableHTTPRequestHandler, port=8000):
    server_address = ('0.0.0.0', port)  # Bind to all available IPs
    httpd = server_class(server_address, handler_class)
    print(f"Serving HTTP on port {port} (http://0.0.0.0:{port}) ...")
    httpd.serve_forever()

if __name__ == "__main__":
    run(port=8000)
