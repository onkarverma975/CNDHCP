#This file is used to extract information from the subnets file and then pass it on back to the server
def get_info(data):
    data = data.split('\n')[0]

    temp = data.split('/')
    ip = temp[0]
    mask = int(temp[1])
    ip = ip.split('.')
    ip = list(map(int, ip))
    return ip, mask


def parse_input():
    f= open("subnets.conf","r")
    contents = f.readline()

    network, mask = get_info(contents)

    n_hosts = int(f.readline())
    names=[]
    for i in xrange(n_hosts):
        line = f.readline()
        line = line.split(':')
        temp = {'name':line[0]
        ,'number':int(line[1])
        ,'mac':''
        ,'mask':[]
        ,'NA':[]
        ,'BA':[]
        ,'first':[]
        ,'last':[]
        }
        names.append(temp)

    for i in xrange(n_hosts):
        line = f.readline()
        line = line.split(' ')
        line[1] = line[1].split('\n')[0]
        for arr in names:
            if arr['name']==line[1]:
                arr['mac']=line[0]

    f.close()

    return network, mask, names
