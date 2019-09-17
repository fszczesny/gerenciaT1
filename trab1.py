from array import *
from easysnmp import Session
import time
from flask import Flask, request
from flask_restful import Resource, Api
import threading

# Cria sessao SNMP conforme os dados passados de parametro
def createSessionV3(hostname, commnity, securityUsername, authProtocol, authPassword, sucurityLevel, privacyProtocol, privacyPass):
    session = Session(hostname=hostname, community=commnity, security_username=securityUsername, auth_protocol=authProtocol, auth_password=authPassword, security_level=sucurityLevel, privacy_protocol = privacyProtocol, privacy_password = privacyPass, version=3)
    return session;

def createSessionV2(hostname, commnity):
    session = Session(hostname=hostname, community=commnity, version=2)
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
    inErrors = 0
    outErrors = 0
    # Loop pelas interfaces
    for i in range(numInterfaces):
        # Os contadores in/out da interface i estarao na lista um apos o outro (posicoes i e i+1)
        ifInErrors = countBulk[i]
        ifOutErrors = countBulk[i+1]
        # Convertendo os valores para inteiro
        inErrors = inErrors + int(ifInErrors.value)
        outErrors = outErrors + int(ifOutErrors.value)
    errors.append(inErrors)
    errors.append(outErrors)
    return errors

# Retorna um vetor de trafego [entrada, saida] em bytes
def getTraffic(session, nInterfaces):
    numInterfaces = nInterfaces
    # Faz uma requisicao bulk com dois contadores in/out das interfaces de uma vez para obter o trafego de entrada e saida
    countBulk = session.get_bulk(['ifInOctets', 'ifOutOctets'], 0, numInterfaces)
    # Define variavel de trafego momentaneo
    traffic = []
    inTraffic = 0
    outTraffic = 0
    # Loop pelas interfaces
    for i in range(numInterfaces):
        # Os contadores in/out da interface i estarao na lista um apos o outro (posicoes i e i+1)
        ifInOctets = countBulk[i]
        ifOutOctets = countBulk[i+1]
        # Convertendo os valores para inteiro
        inTraffic = inTraffic + int(ifInOctets.value)
        outTraffic = outTraffic + int(ifOutOctets.value)
    traffic.append(inTraffic)
    traffic.append(outTraffic)
    return traffic


# Deve Aguardar um botao de inicio de analise
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

# Cria sessao SNMP v3
session = createSessionV3(host, commnity, snmpUser, authProtocol, authPass, securityLevel, privacyProtocol, privacyPass)
# Devemos inserir um tratamanto de erro para sessao invalida (caso de valores que nao podem ser usados juntos e pah)


lock = threading.Lock()
inTraffic = 0
outTraffic = 0
inErrors = 0
outErrors = 0
interfaces = []


def updateVariables():

    while (True):
        
        global inTraffic
        global outTraffic
        global inErrors
        global outErrors
        global interfaces
        lock.acquire()
        interfaces = []
        # Deve encerrar o loop com algum comando da interface

        # Le numero de interfaces ativas
        nInterfaces = getInterfacesNumber(session)
        # Le trafego geral de entrada e saida
        traffic = getTraffic(session, nInterfaces)
        #Calcula trafego tido nos 5 segundos
        inTraffic = traffic[0] - inTraffic
        outTraffic = traffic[1] - outTraffic
        if inTraffic < 0:
            inTraffic = inTraffic*(-1)
        if outTraffic < 0:
            outTraffic = outTraffic*(-1)
        inTraffic = inTraffic/5
        outTraffic = outTraffic/5
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
        time.sleep(1)

updateVariablesThread = threading.Thread(target=updateVariables)
updateVariablesThread.start()

app = Flask(__name__)
api = Api(app)

class Trafego(Resource):
    def get(self):
        global inTraffic
        global outTraffic
        global inErrors
        global outErrors
        global interfaces
        return {'trafego-entrada':  inTraffic, 'trafego-saida': outTraffic, 'erros-entrada': inErrors, 'errors-saida': outErrors, "interfaces": interfaces }

api.add_resource(Trafego, '/trafego')


app.run(port='5002')


updateVariablesThread.join()