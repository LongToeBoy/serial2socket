import usb2soc

"""
ავტომატურად იქმნება ახალი ნაკადი როგორც კი გამოვაცხადებთ კლიენტს
სერიული ტაიმაუტი ძირითადად 0.05 ზე მიყენია დანარჩენი მარტივი მისახვედრია რა არის

new thread is created once client is declared.
i keep serial timeout at 0.05sec, it works for me. rest is pretty straightforward

string serialPort, hostIP
int baudRate, hostPort
float serialtimeOut
"""
client=usb2soc.asClient(serialPort, baudRate, serialtimeOut,hostIP,hostPort)
while True:
	g=raw_input("Type 'Start' or 'Stop': ")
	if g=="start":
		client.start()
	elif g=="stop":
		client.stop()
