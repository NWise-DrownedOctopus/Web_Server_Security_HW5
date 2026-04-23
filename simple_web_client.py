import socket
import sys
import io


class SimpleWebClient:

    hostName = "localhost"
    PORT = 8080

    @staticmethod
    def main():
        try:
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.connect((SimpleWebClient.hostName, SimpleWebClient.PORT))

            out = io.TextIOWrapper(serverSocket.makefile('wb'), newline='', write_through=True)
            in_ = io.TextIOWrapper(serverSocket.makefile('rb'), newline='\n')
            stdIn = io.TextIOWrapper(sys.stdin.buffer, newline='\n')

            userInput = stdIn.readline().rstrip('\n')
            if userInput is not None and userInput != "":

                parts = userInput.split(" ")
                if parts[0] == "PUT":
                    scan = open(parts[1], 'r')
                    file = ""
                    for line in scan:
                        file += line if line.endswith('\n') else line + "\n"
                    userInput = userInput + "\n" + file
                    scan.close()

                out.write(userInput + "\n")
                out.flush()
                response = in_.readline().rstrip('\n')

                if response is not None and response != "":
                    print("Response from Server: ")
                    print(response)
                    response = in_.readline().rstrip('\n')
                    while response is not None and response != "":
                        print(response)
                        response = in_.readline().rstrip('\n')

        except socket.gaierror:
            print("Don't know about host " + SimpleWebClient.hostName, file=sys.stderr)
            sys.exit(1)
        except (ConnectionRefusedError, OSError):
            print("Couldn't get I/O for the connection to " + SimpleWebClient.hostName, file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    SimpleWebClient.main()