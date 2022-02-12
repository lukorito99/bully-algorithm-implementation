import socket
import threading

port = 1250
header = 64

#server = '192.168.175.1'
s = socket.gethostbyname(socket.gethostname())
addr = (s, port)

disconnect_message = 'DISCONNECTING!'

n = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(7)]
election='Search For New Coordinator.'

Higher_IDs=dict()
Lower_IDs=dict()

x=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
this_ID=dict()

this_ID[4]=['alive',x,'']

#key is process Id
Higher_IDs[5]=['alive',n[4]]
Higher_IDs[6]=['alive',n[5]]
Higher_IDs[7]=['crushed',n[6]]

Lower_IDs[0]=['alive',n[0]]
Lower_IDs[1]=['alive',n[1]]
Lower_IDs[2]=['alive',n[2]]
Lower_IDs[3]=['alive',n[3]]

Node_responses=['Ok','iWoN!']

def inform(msg,z):

    message=msg.encode('utf-8')

    msg_len = len(message)
    send_len=str(msg_len).encode('utf-8')

    send_len += b' ' * (header - len(send_len))

    z.sendall(send_len)
    z.sendall(message)

check=['AYA','IAA','NA']

def failedCoordinator():
    this_ID[4][1]=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
       this_ID[4][1].connect(addr)

       inform(check[0],this_ID[4][1])

       inform(disconnect_message,this_ID[4][1])
    except socket.error as e:
         pass


    this_ID[4][1].close()


def node_sending(f,y):

    f=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    f.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
       f.connect(addr)

       inform(y,f)
       inform(disconnect_message,f)

    except socket.error as e:
         pass

    f.close()



def node_recv(j):
    j=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    j.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    m=''
    try:

        j.connect(addr)
        m=j.recv(4096).decode('utf-8')

        # inform(disconnect_message,j)
    except socket.error as e:
        pass

    j.close()
    return m


def receiving_node_status():
    elect='No'
    Higher_IDs[7][1]=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:

        Higher_IDs[7][1].connect(addr)
        m=Higher_IDs[7][1].recv(4096).decode('utf-8')

        if m == check[0]:
           #process 7 was intial coordinator
           if Higher_IDs[7][0] == 'alive':
               inform(check[1],Higher_IDs[7][1])
               elect='No'
           else:
               elect='Yes'
               inform(check[2],Higher_IDs[7][1])


        if m == check[1]:
            elect='No'
            inform(check[1],Higher_IDs[7][1])
            # print('\nContinuing Detection!\n')

        inform(disconnect_message,Higher_IDs[7][1])
    except socket.error as e:
        pass

    Higher_IDs[7][1].close()
    return [elect,7]



def node_election():
    IDs_to_send_to=list()
    result=receiving_node_status()
    if result[0] == 'No':
        print('\nContinuing Detection!\n')
    else:
        print('Intiating election...\n')
        for i in list(Higher_IDs.keys()):
            if i != result[1] and max(i,4) == i:#node 7 is down communication not possible
                IDs_to_send_to.append(i)

        round=1

        print('Round: ',round,' sending election message.\n')

        for  b in range(len(IDs_to_send_to)):
           node_sending(this_ID[4][1],election)
           if node_recv(IDs_to_send_to[b]) == election:
               node_sending(Higher_IDs[IDs_to_send_to[b]][1],Node_responses[0])
               if node_recv(this_ID[4][1]) == Node_responses[0]:
                   print('Process 4 handing over leader election to higher process.\n')

                   break


        z=0
        # from itertools import cycle
        # l=cycle(IDs_to_send_to)
        while z !=len(IDs_to_send_to)-1:
            round+=1
            print('Round: ',round,' sending election message.\n')

            node_sending(Higher_IDs[IDs_to_send_to[z]][1], election)

            if node_recv(IDs_to_send_to[z+1]) == election:
                node_sending(Higher_IDs[IDs_to_send_to[z+1]][1],Node_responses[0])

                if node_recv(Higher_IDs[IDs_to_send_to[z]][1]) == Node_responses[0]:
                    print('Process ',IDs_to_send_to[z],' handing over leader election to higher process.\n')

            z+=1

        new_coordinator=max(IDs_to_send_to)
        IDs_to_send_to.remove(new_coordinator)

        IDs_to_send_to.append(4)
        for k in Lower_IDs.keys():
            IDs_to_send_to.append(k)

        for j in IDs_to_send_to:
             node_sending(Higher_IDs[new_coordinator][1],Node_responses[1])
             if j == 4:
                print(node_recv(this_ID[j][1]))
             else:
                if j in Lower_IDs.keys():
                  print(node_recv(Lower_IDs[j][1]))
                else:
                    print(node_recv(Higher_IDs[j][1]))


        print('\nElection done new coordinator is Process:',new_coordinator,'\n')



failedCoordinator()

node_election()
