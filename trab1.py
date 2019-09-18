from array import *
# from easysnmp import Session
import time
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import threading

# Cria sessao SNMP conforme os dados passados de parametro
def createSessionV3(hostname, commnity, securityUsername, authProtocol, authPassword, sucurityLevel, privacyProtocol, privacyPass):
    from easysnmp import Session
    session = Session(hostname=hostname, community=commnity, security_username=securityUsername, auth_protocol=authProtocol, auth_password=authPassword, security_level=sucurityLevel, privacy_protocol = privacyProtocol, privacy_password = privacyPass, version=3)
    return session;

def getInterfacesNumber(session):
    # Faz request para obter o numero de interfaces de rede
    ifNumber = session.get('ifNumber.0')
    numInterfaces = int(ifNumber.value)
    return numInterfaces

def getInterfacesState(session, nInterfaces):
    numInterfaces = nInterfaces
    countBulk = session.get_bulk(['ifOperStatus'], 0, numInterfaces)
    states = []
    for i in range(numInterfaces):
        ifStatus = countBulk[i]
        states.append(int(ifStatus.value))
    return states

def getInterfacesName(session, nInterfaces):
    numInterfaces = nInterfaces
    countBulk = session.get_bulk(['ifDescr'], 0, numInterfaces)
    names = []
    for i in range(numInterfaces):
        ifName = countBulk[i]
        names.append(ifName.value)
    return names

# Retorna um vetor de erors [entrada, saida] em numero de ocorrencias
def getErrors(session, nInterfaces):
    numInterfaces = nInterfaces
    # Faz uma requisicao bulk com dois contadores in/out das interfaces de uma vez para obter os erros de entrada e saida
    countBulk = session.get_bulk(['ifInErrors', 'ifOutErrors'], 0, numInterfaces)
    # Define variavel de trafego momentaneo
    errors = []
    inErrors_ = 0
    outErrors_ = 0
    # Loop pelas interfaces
    for i in range(numInterfaces):
        # Os contadores in/out da interface i estarao na lista um apos o outro (posicoes i e i+1)
        ifInErrors = countBulk[i]
        ifOutErrors = countBulk[i+1]
        # Convertendo os valores para inteiro
        inErrors_ = inErrors_ + int(ifInErrors.value)
        outErrors_ = outErrors_ + int(ifOutErrors.value)
    errors.append(inErrors_)
    errors.append(outErrors_)
    return errors

# Retorna um vetor de trafego [entrada, saida] em bytes
def getTraffic(session, nInterfaces):
    numInterfaces = nInterfaces
    # Faz uma requisicao bulk com dois contadores in/out das interfaces de uma vez para obter o trafego de entrada e saida
    countBulk = session.get_bulk(['ifInOctets', 'ifOutOctets'], 0, numInterfaces)
    # Define variavel de trafego momentaneo
    traffic = []
    inTraffic_ = 0
    outTraffic_ = 0
    # Loop pelas interfaces
    for i in range(numInterfaces):
        # Os contadores in/out da interface i estarao na lista um apos o outro (posicoes i e i+1)
        ifInOctets = countBulk[i]
        ifOutOctets = countBulk[i+1]
        # Convertendo os valores para inteiro
        inTraffic_ = inTraffic_ + int(ifInOctets.value)
        outTraffic_ = outTraffic_ + int(ifOutOctets.value)
    traffic.append(inTraffic_)
    traffic.append(outTraffic_)
    return traffic

# TODO: Le da interface valores
host = 'localhost'
commnity = 'public'
snmpUser = 'MD5User'
authProtocol = 'MD5' # deve poder deixar escolher entre MD5 e SHA
authPass = 'The Net-SNMP Demo Password'
securityLevel = 'auth_without_privacy' # pode ser nos valores 'auth_without_privacy', 'no_auth_or_privacy', 'auth_with_privacy'
privacyProtocol = 'DEFAULT' # Pode permitir 'DEFAULT', 'DES', 'AES'
privacyPass = ''
maxTraffic = 5 * pow(10,6) #10^6 eh mega

# Cria sessao SNMP v3 sem inicio
session = False

lock = threading.Lock()
inTraffic = 0
lastInOctets = 0
outTraffic = 0
lastOutOctets = 0
inErrors = 0
outErrors = 0
interfaces = []


def updateVariables():

    while (True):
        lock.acquire()
        global inTraffic
        global outTraffic
        global inErrors
        global outErrors
        global interfaces
        global session
        global lastInOctets
        global lastOutOctets

        if session is not False:
            interfaces = []
            # Le numero de interfaces ativas
            nInterfaces = getInterfacesNumber(session)
            # Le trafego geral de entrada e saida
            traffic = getTraffic(session, nInterfaces)
            #Calcula trafego tido nos 5 segundos
            if lastInOctets != 0 and lastOutOctets != 0:
                inTraffic = int((traffic[0] - lastInOctets)/5)
                outTraffic = int((traffic[1] - lastOutOctets)/5)
                if inTraffic < 0:
                    inTraffic = inTraffic*(-1)
                if outTraffic < 0:
                    outTraffic = outTraffic*(-1)
            lastInOctets = traffic[0]
            lastOutOctets = traffic[1]
            print "Trafego de entrada: " , inTraffic , " bytes/s"
            print "Trafego de saida: " , outTraffic , " bytes/s"
            # Emite alerta de trafego acima do definido
            if inTraffic > maxTraffic:
                print "->Trafego execido na entrada!"
            if outTraffic > maxTraffic:
                print "->Trafego execido na saida!"
            # Le erros em geral de entrada e saida
            errors = getErrors(session, nInterfaces)
            inErrors = errors[0]
            outErrors = errors[1]
            print "Erros na entrada: " , inErrors
            print "Erros na saida: " , outErrors
            # Le os estados das interfaces de rede e seus nomes
            states = getInterfacesState(session, nInterfaces)
            names = getInterfacesName(session,nInterfaces)
            for i in range(len(states)):
                state = states[i]
                stateString = ''
                if state == 1:
                    stateString = 'Up'
                elif state == 2:
                    stateString = 'Down'
                elif state == 3:
                    stateString = 'Testing'
                elif state == 4:
                    stateString = 'Unknow'
                elif state == 5:
                    stateString = 'Dormant'
                elif state == 6:
                    stateString = 'NotPresent'
                elif state == 7:
                    stateString = 'LowerLayerDown'
                print "Status: " , names[i] , " - " , stateString 
                interfaces.append({ "name": names[i], "state": stateString })
        lock.release()
        time.sleep(5)

updateVariablesThread = threading.Thread(target=updateVariables)
updateVariablesThread.start()

app = Flask(__name__)

cors = CORS(app)

@app.route("/trafego", methods=['GET'])
@cross_origin(origin='127.0.0.1')
def Trafego():
    global inTraffic
    global outTraffic
    global inErrors
    global outErrors
    global interfaces
    return {'trafego-entrada':  inTraffic, 'trafego-saida': outTraffic, 'erros-entrada': inErrors, 'errors-saida': outErrors, "interfaces": interfaces }

@app.route("/change-params", methods=['POST'])
@cross_origin(origin='127.0.0.1')
def ChangeParams():
    lock.acquire()
    global session
    req_data = request.get_json()['data']
    host = req_data['host']
    commnity = req_data['commnity']
    snmpUser = req_data['snmpUser']
    authProtocol = req_data['authProtocol']
    authPass = req_data['authPass']
    securityLevel = req_data['securityLevel']
    privacyProtocol = req_data['privacyProtocol']
    privacyPass = req_data['privacyPass']

    print("SET", host, commnity, snmpUser, authProtocol, authPass, securityLevel, privacyProtocol, privacyPass)
    try:
        session = createSessionV3(host, commnity, snmpUser, authProtocol, authPass, securityLevel, privacyProtocol, privacyPass)
    except:
        print("ERROR - SNMP error:")
        session = False
    lock.release()

    return { "ok": True }


app.run(port='5002')


updateVariablesThread.join()