from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, DataGraphPopup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread
from time import sleep
from datetime import datetime
from random import random
from timeseriesgraph import TimeSeriesGraph


class MainWidget(BoxLayout):
    """
    Widget principal
    """
    _updateThread = None
    _updateWidget = True
    _tags = {}
    _max_points = 20

    def __init__(self, **kwargs):
        """
        Construtor de Widget Principal
        """
        super().__init__()
        self._serverIP = kwargs.get('server_ip')
        self._serverPort = kwargs.get('server_port')
        self._scan_time = kwargs.get('scan_time')
        self._modbusPopup = ModbusPopup(self._serverIP, self._serverPort)
        self._scanPopup = ScanPopup(scantime=self._scan_time)
        self._modbusClient = ModbusClient(host=self._serverIP, port=self._serverPort)
        self._meas = {}
        self._meas['timestamp'] = None
        self._meas['values'] = {}
        for key,addr in kwargs.get('modbus_addrs').items():
            if key == 'fornalha':
                plot_color = (1,0,0,1)
            else:
                plot_color = (random(),random(),random(),1)
            self._tags[key] = {'addr':addr, 'color':plot_color}
        
        self._graphPopup = DataGraphPopup(self._max_points,self._tags['fornalha']['color'])

    def startDataRead(self, ip, port):
        """
        Método para configuração do IP e porta do servidor Modbus
        Inicializa uma thread para leitura dos dados e atualização da interface
        """
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._serverPort
        try:
            Window.set_system_cursor('wait')
            self._modbusClient.open()
            Window.set_system_cursor('arrow')
            if self._modbusClient.is_open:
                self._updateThread = Thread(target=self.updater)
                self._updateThread.start()
                self.ids.img_con.source = 'imgs/conectado.png'
                self._modbusPopup.dismiss()
            else:
                self._modbusPopup.setInfo('Falha na conexão com o servidor')
        except Exception as e:
            print('Erro: ', e.args)

    def readData(self):
        """
        Método para leituras das datas do servidor
        """
        self._meas['timestamp'] = datetime.now()
        for key,value in self._tags.items():
            self._meas['values'][key] = self._modbusClient.read_holding_registers(value['addr'],1)[0]

    def updateGUI(self):
        """
        Método para atualização da interface gráfica em tempo real
        """
        # Atualização dos labels das temperaturas
        for key,value in self._tags.items():
            self.ids[key].text = str(self._meas['values'][key]) + ' ºC'
        # Atualizar o nível do termôetro
        self.ids.lb_temp.size = (self.ids.lb_temp.size[0],self._meas['values']['fornalha']
                                /450*self.ids.termometro.size[1])
        # Atualização do gráfico
        self._graphPopup.ids.graph.updateGraph((self._meas['timestamp'],self._meas['values']['fornalha'])
                                                ,0)

    def updater(self):
        """
        Método que invoca as rotinas de leitura de dados, atualização da interface e
        inserção dos dados no BD
        """
        try:
            while self._updateWidget:
                # ler os dados MODBUS
                self.readData()
                # atualizar interface
                self.updateGUI()
                # inserir os dados no BD
                sleep(self._scan_time/1000)
        except Exception as e:
            self._modbusClient.close()
            print('Erro: ', e.args)
    
    
    def stopRefresh(self):
        self._updateWidget = False
    