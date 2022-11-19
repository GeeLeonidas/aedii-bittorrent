import threading as thr
import node as nd
from time import sleep

BASE_PORT = 30000

if __name__ == "__main__":
    nodes = []
    threads = []
    for i in range(5):
        nodes.append(nd.Node(('127.0.0.1', BASE_PORT+i)))
        threads.append(thr.Thread(target=nodes[i].listen))
        threads[i].start()
    for i in range(1, len(nodes)):
        nodes[i].enter_dht(nodes[0].addr)
        sleep(1)
    
    cmd = input('>> ')
    while cmd != 'exit':
        if cmd == 'echo':
            nodes[0].echo()
        elif cmd == 'print':
            for node in nodes:
                print(f'{node.prev} (prev) - {node.addr} - {node.next} (next)')
        cmd = input('>> ')
    for node in nodes:
        node.alive = False