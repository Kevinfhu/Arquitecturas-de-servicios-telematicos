# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 16:53:56 2023

@author: kevin
"""

import socket
import struct
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as waves


def receive_file_size(sck: socket.socket):
    # Esta función se asegura de que se reciban los bytes
    # que indican el tamaño del archivo que será enviado,
    # que es codificado por el cliente vía struct.pack(),
    # función la cual genera una secuencia de bytes que
    # representan el tamaño del archivo.
    fmt = "<Q"
    expected_bytes = struct.calcsize(fmt)
    received_bytes = 0
    stream = bytes()
    while received_bytes < expected_bytes:
        chunk = sck.recv(expected_bytes - received_bytes)
        stream += chunk
        received_bytes += len(chunk)
    filesize = struct.unpack(fmt, stream)[0]
    return filesize


def receive_file(sck: socket.socket, filename):
    # Leer primero del socket la cantidad de 
    # bytes que se recibirán del archivo.
    filesize = receive_file_size(sck)
    # Abrir un nuevo archivo en donde guardar
    # los datos recibidos.
    with open(filename, "wb") as f:
        received_bytes = 0
        # Recibir los datos del archivo en bloques de
        # 1024 bytes hasta llegar a la cantidad de
        # bytes total informada por el cliente.
        while received_bytes < filesize:
            chunk = sck.recv(4096)
            if chunk:
                f.write(chunk)
                received_bytes += len(chunk)
                
def send_file(sck: socket.socket, data):
    # Codificar el tamaño del archivo en una secuencia de bytes.
    fmt = "<Q"
    filesize = len(data)
    stream = struct.pack(fmt, filesize)
    # Enviar la secuencia de bytes que representa el tamaño del archivo.
    sck.sendall(stream)
    # Enviar los datos del archivo en bloques de 1024 bytes.
    sent_bytes = 0
    while sent_bytes < filesize:
        chunk = data[sent_bytes:sent_bytes + 4096]
        sck.sendall(chunk)
        sent_bytes += len(chunk)


with socket.create_server(("localhost", 6190)) as server:
    while True: # bucle infinito para mantener la conexión
        print("Esperando al cliente...")
        conn, address = server.accept()
        print(f"{address[0]}:{address[1]} conectado.")
        print("Recibiendo archivo...")
        receive_file(conn, "muestra_Invernal01_recibida.wav")
        print("Archivo recibido.")
        
        print ("Procesando el archivo")
        archivo = 'muestra_Invernal01_recibida.wav'
        muestreo, sonido = waves.read(archivo)

        tamano=np.shape(sonido)
        canales=len(tamano)
        tipo = 'estéreo'
        if (canales<2):
            tipo = 'monofónico'
        duracion = len(sonido) /muestreo

        print('muestreo (Hz) : ',muestreo)
        print('canales: ' + str(canales) + ' tipo ' + tipo )
        print('duración (s): ',duracion)
        print('tamaño de matriz: ', tamano)
        print(sonido)

        # Generar el archivo de imagen
        plt.plot(sonido)
        plt.savefig('Figura generada.png')
        plt.show(block=False)
        
        # Enviar el archivo generado al cliente
        with open('Figura generada.png', 'rb') as f:
            data = f.read()
            send_file(conn, data)

        input("Presiona enter para cerrar la ventana de la gráfica")

        print("Esperando Nueva Conexión...")
