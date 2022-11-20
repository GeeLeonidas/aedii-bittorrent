import threading as thr
import node as nd
import filechunk as fc

BASE_PORT = 30000
CMD_PREFIX = '>> '
MUSIC = ['SalmonLikeTheFish - Glacier.mp3', 'SalmonLikeTheFish - Shenandoah.mp3', 'SalmonLikeTheFish - Zion.mp3']

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
    
    cmd = input(CMD_PREFIX)
    while cmd != 'exit':
        args = cmd.split(' ')
        cmd = args.pop(0)
        if cmd == 'echo':
            nodes[0].echo()
        elif cmd == 'print':
            for node in nodes:
                print(f'{node.prev} (prev) - {node.addr} - {node.next} (next)')
        elif cmd == 'find' and len(args) == 2:
            song = MUSIC[int(args[0])]
            nodes[0].find(song, int(args[1]))
        elif cmd == 'put' and len(args) == 1:
            song = MUSIC[int(args[0])]
            fc.add_file('music', song, [node.addr for node in nodes])
        elif cmd == 'get' and len(args) == 2:
            song = MUSIC[int(args[0])]
            fc.get_file(args[1], song, [node.addr for node in nodes])
        cmd = input(CMD_PREFIX)
    for node in nodes:
        node.alive = False