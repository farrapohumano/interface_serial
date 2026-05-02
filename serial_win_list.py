import time

import serial
from serial.tools import list_ports

class SerialController:
    def __init__(self, port: str, name: str, baudrate: int = 9600, timeout: int = 10, break_point: str = None):
        self.port = port
        self.name = name
        self.baud = baudrate
        self.timeout = timeout
        self.break_point = break_point
        self.comm = None

        self.serial_connect()

    def send_data(self, data, type_of_text, wait=True):
        data_to_send = self.encode_data(data)

        try:
            if self.comm is None:
                ok = self.serial_connect()
                if not ok or self.comm is None:
                    raise RuntimeError("Serial did not connect (self.comm == None!).")

            self.comm.write(data_to_send)

            if wait:
                return (self.serial_read_data_until(self.break_point)
                        if self.break_point else self.read_data())

        except serial.SerialException as e:
            return e

    # def send_data(self, data, type_of_text, wait=True):
    #     data_to_send = self.encode_data(data)
    #     print(data)
    #     print(data_to_send)
    #
    #     try:
    #         if self.comm is None:
    #             self.serial_connect()
    #         if wait:
    #             self.comm.write(data_to_send)
    #             response = self.serial_read_data_until(self.break_point) if self.break_point else self.read_data()
    #             return response
    #         else:
    #             self.comm.write(data_to_send)
    #
    #     except serial.SerialException as e:
    #         return e


    def read_data(self):
        return self.decode_data(self.comm.read(), type_decode="utf-8")

    def serial_read_data_until(self, break_point):
        while True:
            pass

    def serial_connect(self):
        try:
            self.comm = serial.Serial(self.port, self.baud, timeout=1)
            return True
        except Exception as e:
            self.comm = None
            return False

    # def serial_connect(self):
    #     if self.comm is not None:
    #         try:
    #             self.comm = self.__serial_connection()
    #         except serial.serialutil.SerialException as e:
    #             raise Exception(f"Error connecting to serial port: {e}.")

    def serial_disconnect(self):
        if self.comm is not None:
            try:
                self.comm.close()
            except serial.serialutil.SerialException as e:
                raise Exception(f"Error disconnecting to serial port: {e}.")

    def encode_data(self, data):
        return data.encode()

    def decode_data(self, data, type_decode):
        return data.decode(type_decode)

    def __serial_connection(self):
        return serial.Serial(self.port, self.baud, timeout=self.timeout)


def get_serial_comm_ports():
    try:
        return list_ports.comports() if list_ports.comports() else []
    except serial.serialutil.SerialException as e:
        raise Exception(f"Error connecting to serial port: {e}.")



if __name__ == '__main__':
    ports = get_serial_comm_ports()
    print(ports)