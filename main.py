import client.Client
import sys

if __name__ == '__main__':
    print("Starting")

    thisPID = int(sys.argv[1])
    nodes = int(sys.argv[2])

    theClient = client.Client.Client(pID=thisPID, N=nodes, hostFile='./hostslocal.info')

    theClient.execClient()