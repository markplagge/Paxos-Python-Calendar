import client.Client
import sys

if __name__ == '__main__':
    print("Starting")

    thisPID = sys.argv[1]
    nodes = sys.argv[2]

    theClient = client.Client.Client(pID=thisPID, N=nodes, hostFile='./hosts.info')

    theClient.execClient()