# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 16:39:37 2023

@author: kevin
"""

import os
import socket
import struct
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from io import BytesIO
from PIL import Image, ImageTk


class FileSender:
    
    def __init__(self, root):
        self.root = root
        self.filename = ""
        self.sock = None

        # Crear widgets de la interfaz gráfica.
        self.select_button = tk.Button(root, text="Seleccionar archivo", command=self.select_file)
        self.send_button = tk.Button(root, text="Enviar archivo", command=self.send_file)
        self.close_button = tk.Button(root, text="Cerrar conexión", command=self.close_connection)
        self.status_label = tk.Label(root, text="Seleccione un archivo para enviar.")
        self.receive_button = tk.Button(root, text="Recibir imagen", command=self.receive_image)
       
      # Crear un widget de imagen para mostrar la imagen recibida.
        self.image_label = tk.Label(root)
        self.image_label.pack()
       

        # Colocar widgets en la ventana.
        self.select_button.pack()
        self.send_button.pack()
        self.close_button.pack()
        self.status_label.pack()
        self.receive_button.pack()
        

    def select_file(self):
        # Abrir diálogo para seleccionar archivo.
        self.filename = filedialog.askopenfilename()
        self.status_label.config(text=f"Archivo seleccionado: {self.filename}")

    def send_file(self):
        # Verificar si se ha seleccionado un archivo.
        if not self.filename:
            self.status_label.config(text="Seleccione un archivo para enviar.")
            return

        # Crear objeto de socket y conectar con el servidor si aún no lo hemos hecho.
        if not self.sock:
            self.sock = socket.create_connection(("localhost", 6190))
            self.status_label.config(text="Conectado al servidor.")

        try:
            # Obtener el tamaño del archivo a enviar.
            filesize = os.path.getsize(self.filename)
            # Informar primero al servidor la cantidad
            # de bytes que serán enviados.
            self.sock.sendall(struct.pack("<Q", filesize))
            # Enviar el archivo en bloques de 1024 bytes.
            with open(self.filename, "rb") as f:
                while read_bytes := f.read(4096):
                    self.sock.sendall(read_bytes)
            # Actualizar estado de la interfaz gráfica.
            self.status_label.config(text="Archivo enviado.")
        except Exception as e:
            # Actualizar estado de la interfaz gráfica si ocurre un error.
            self.status_label.config(text=f"Error al enviar archivo: {e}")
            

    def receive_image(self):
        # Crear objeto de socket y conectar con el servidor si aún no lo hemos hecho.
        if not self.sock:
            self.sock = socket.create_connection(("localhost", 6190))
            self.status_label.config(text="Conectado al servidor.")
    
        try:
            # Recibir el tamaño de la imagen.
            size_data = b""
            while len(size_data) < 8:
                size_data += self.sock.recv(8 - len(size_data))
            size = struct.unpack("<Q", size_data)[0]
    
            # Recibir la imagen.
            image_data = b""
            while len(image_data) < size:
                image_data += self.sock.recv(size - len(image_data))
            # Convertir los datos de la imagen recibida a un objeto de imagen utilizando el módulo PIL.
            image = Image.open(BytesIO(image_data))

            # Convertir el objeto de imagen a un objeto PhotoImage utilizando ImageTk.PhotoImage().
            photo_image = ImageTk.PhotoImage(image)

            # Asignar el objeto PhotoImage al widget Label que has creado para mostrar la imagen.
            self.image_label.config(image=photo_image)
            self.image_label.image = photo_image
    
            
    
            # Actualizar estado de la interfaz gráfica.
            self.status_label.config(text="Imagen recibida.")
        except Exception as e:
            # Actualizar estado de la interfaz gráfica si ocurre un error.
            self.status_label.config(text=f"Error al recibir imagen: {e}")
    






    
    def close_connection(self):
        # Cerrar la conexión.
        if self.sock:
            self.sock.close()
            self.sock = None
            self.status_label.config(text="Conexión cerrada.")
    





if __name__ == "__main__":
    # Crear la ventana principal y el objeto FileSender.
    root = tk.Tk()
    root.title("Envío de archivos")
    sender = FileSender(root)
    root.mainloop()
