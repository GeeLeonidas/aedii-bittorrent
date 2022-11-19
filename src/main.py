import threading as thr
import node as nd

BASE_PORT = 33333

if __name__ == "__main__":
    nodes = []
    threads = []
    for i in range(5):
        nodes.append(nd.Node('127.0.0.1', str(BASE_PORT+i)))
        threads.append(thr.Thread(target=nodes[i].listen))
        threads[i].start()
    for i in range(1, len(nodes)):
        nodes[i].enter_dht((nodes[0].host, nodes[0].port))