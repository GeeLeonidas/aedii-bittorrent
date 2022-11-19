import threading as thr
import node as nd
from time import sleep

BASE_PORT = 30000
CMD_PREFIX = '>> '

if __name__ == "__main__":
    nodes = []
    threads = []
    node_count = int(input('Node count: '))
    for i in range(node_count):
        nodes.append(nd.Node(('127.0.0.1', BASE_PORT+i)))
        threads.append(thr.Thread(target=nodes[i].listen))
    for t in threads:
        t.start()

    for i in range(1, node_count):
        nodes[i].enter_dht(nodes[0].addr)
        sleep(1)
    
    cmd = input(CMD_PREFIX)
    while cmd != 'exit':
        if cmd == 'echo':
            nodes[0].echo()
        elif cmd == 'print':
            for node in nodes:
                print(f'{node.prev} (prev) - {node.addr} - {node.next} (next)')
        cmd = input(CMD_PREFIX)
    for node in nodes:
        node.alive = False