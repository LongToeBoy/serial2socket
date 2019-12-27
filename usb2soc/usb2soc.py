#-*- coding: UTF-8 -*-

import serial, socket, time, select, threading

class asClient:
	serialPort=""
	baudRate=0
	serialtimeOut=0
	hostIP=""
	hostPort=0
	networkTimeout=0
	keepMainOpen=False
	


	def IOLoop(self,s):
		self.keepOpen=True
		self.noconcount=0   #no connection counter ითვლის რამდენი ციკლი არ შედგა კონტაქტი / no connection counter, it's counting cycles of faulty communications                            
		while self.keepOpen:
			self.times=time.time()
			self.transfer=False               #ტრანსფერის მთვლელი ქვევით აღწერა აქვს / transfer counter, below has description
			try:                              
				if(self.ser.in_waiting>0):    # თუ მიიღო ინფორმაცია სერიული პორტიდან / if got data from serial port
					self.data=self.ser.read(self.ser.in_waiting)
					print("From unit to server",s.send(self.data))   #გაგზავნოს სერვერზე (აბრუნებს გაგზავნილ ბიტებს) / send to server (returns bytes written)
					#print(self.data)
					self.transfer=True
					self.keepOpen=True
				self.ready=select.select([self.s],[],[],self.networkTimeout)   #სტაკზე ვნახე. არ ვიცი როგორ მუშაობს მაგრამ ტაიმაუთს აყენებს 10 წამიანს თუ სოკეტმა არ დააბრუნა არაფერი / network timeout
				if self.ready[0]:
					self.data=s.recv(8192)
					#print(self.data)
				else:
					self.keepOpen=False
				if len(self.data)>0:
					print("From server to unit",len(self.data))
					#print(data)
					self.ser.write(self.data)
					self.transfer=True
					self.keepOpen=True
				else:
					self.keepOpen=False
					self.s.close()
			except Exception as e:
				print(e)
				self.s.close()
				self.keepOpen=False
			if not self.transfer:   #თუ კომუნიკაცია არ შემდგარა ერთი ციკლის განმავლობაში, დაელოდოს ცოტახანი / wait if no communication
				self.noconcount+=1  #კავშირი არ შედგა და გაიზარდოს / predictable
				if self.noconcount>3:  #რაღაც რაოდენობის უკონტაქტო ციკლების შემდეგ შეწყდეს ციკლი 
					self.keepOpen=False
			else:
				self.noconcount=0  #ესეიგი კავშირი შედგა და განულდეს / predictable
			
			self.serialtimeOut=time.time()-self.times
			print("send/receive time=%s sec"%self.serialtimeOut)
			time.sleep(self.serialtimeOut)

	def main(self):
		self.ser=serial.Serial(self.serialPort,self.baudRate,timeout=self.serialtimeOut)
		self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#s.setblocking(0)        #დროებით გავთიშავ არ ვიცი რას შვრება / hell knows what its doing, lets leave turned off

		self.ser.close()        #თავიდან არ დავახურინე და რაღაც პრობლემა ჰქონდა ერთხელ, სჯობს ჯერ დავხურო, მერე გავხსნა / sometimes it has problem opening so its good idea to first close
		self.ser.open()
		self.keepMainOpen=False     #ვაილ თრუს პონტია ოღონდ უფრო კონტროლირებადი
		self.keepMainOpen=True
		while self.keepMainOpen:
			if(self.ser.in_waiting>0):
				self.timeas=time.time()

				try:
					self.s.connect((self.hostIP,self.hostPort))

				except Exception as (value,msg):
					
					if value==9:
						self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM) # თუ ERRNO.EBADF ამოაგდო ესეიგი სოკეტი დახურულია და ხელახლა ვხსნით / if errno.ebadf socket is closed so we open 
						#s.setblocking(0)

					elif value==106: #თუ errno.EISCON ესეიგი კავშირი არის და ვიწყებთ გაგზავნის ციკლს / if errno.eiscon, connection is made so we start sending data
						self.IOLoop(self.s)
						self.ser.flushInput()
						print("communication time=%s sec"%(time.time()-self.timeas))
						self.s.close()
						#self.ser.flushInput()
						print("Out of IOLoop")
					else:
						print(value,msg)


			time.sleep(0.5)	
	def start(self):
		self.keepMainOpen=True
		print("Started")
	def stop(self):
		self.keepMainOpen=False
		print("Stopped")

	def __init__(self, serialPort, baudRate, serialtimeOut,hostIP,hostPort):#, serialPort, baudRate, serialtimeOut, hostIP, hostPort, networkTimeout):
		self.serialPort=serialPort
		self.baudRate=baudRate
		self.serialtimeOut=serialtimeOut
		self.hostIP=hostIP
		self.hostPort=hostPort
		self.networkTimeout=10 # დროებით არის, მაინც იცვლება მერე / temporary, it will change anyways later on
		#print("hello")
		x=threading.Thread(target=self.main)
		x.start()
	
