from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

#untuk menggunakan processpoolexecutor, karena tidak mendukung subclassing pada process,
#maka class ProcessTheClient dirubah dulu menjadi function, tanpda memodifikasi behaviour didalamnya

def ProcessTheClient(connection,address):
		rcv=""
		while True:
			try:
				data = connection.recv(1024)
				if not data:
					break
				rcv += data.decode()
				if '\r\n\r\n' in rcv:
						break
			except OSError:
				break

		try:
			header_part, body_part = rcv.split('\r\n\r\n', 1)
		except ValueError:
			connection.close()
			return

		headers = header_part.split('\r\n')
		content_length = 0
		for line in headers:
			if line.lower().startswith("content-length:"):
				content_length = int(line.split(":")[1].strip())

		while len(body_part.encode()) < content_length:
			try:
				data = connection.recv(1024)
				if not data:
					break
				body_part += data.decode()
			except OSError:
				break

		full_request = header_part + '\r\n\r\n' + body_part
		hasil = httpserver.proses(full_request)
		hasil = hasil + b"\r\n\r\n"
		connection.sendall(hasil)
		connection.close()



def Server():
	the_clients = []
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	my_socket.bind(('0.0.0.0', 8889))
	my_socket.listen(1)

	with ProcessPoolExecutor(20) as executor:
		while True:
				connection, client_address = my_socket.accept()
				#logging.warning("connection from {}".format(client_address))
				p = executor.submit(ProcessTheClient, connection, client_address)
				the_clients.append(p)
				#menampilkan jumlah process yang sedang aktif
				jumlah = ['x' for i in the_clients if i.running()==True]
				print(jumlah)





def main():
	Server()

if __name__=="__main__":
	main()
