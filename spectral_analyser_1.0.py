from rtlsdr import RtlSdr
import numpy as np
import time
import scipy
import math
import matplotlib.pyplot as plt

#  zadejte prvni a posledni frekvenci pro definovani okna ktere ma byt zmereno, v MHz
f_start = input("Vloz startovni frekvenci [ MHz ] :")
print "Fstart =", f_start
f_stop = input("Vloz koncovou frekvenci [ MHz ] :")
print "Fstop =", f_stop
sirka_volba = raw_input("Vloz volbu pro rozliseni, RBW ( a = 244 Hz // b = 61 Hz // c = 15 Hz // d = 1 Hz):")
print "volba =", sirka_volba
log_volba = raw_input("Logaritmicka stupnice :  a = ano // n = ne   :")
print "volba =", log_volba
pozadi_volba = raw_input("Odecist sumove pozadi :  a = ano // n = ne   :")
print "volba =", pozadi_volba


if	sirka_volba is	'a' :
	pocet_vzorku = 8 * 512

if	sirka_volba is	'b' :
	pocet_vzorku = 32 * 512

if	sirka_volba ==	'c' :
	pocet_vzorku = 128 * 512

if	sirka_volba ==	'd' :
	pocet_vzorku = 1024 * 1024

sdr = RtlSdr()
pocet_oken = f_stop-f_start
f_start = f_start * 1e6
f_stop = f_stop * 1e6
sdr.sample_rate = 1.2e6  # Hz 
sdr.freq_correction = +30   # korekce ochylky hodin, v PPM
sdr.gain = 12

sdr.center_freq = f_start + 0.5e6    # Hz
x = np.linspace(f_start, f_stop , pocet_oken *(int(round(pocet_vzorku*(1/1.2))))) # definice velikosti pole pro vyslednou FFT - jen pro indexy

data = sdr.read_samples(pocet_vzorku) # testovaci aktivace prijimace, prvni vzorky nejsou kvalitni
provede_mereni = 1
pozadi_temp = 0
if	pozadi_volba ==	'a' :
	pozadi_temp = 1
	raw_input("Probehne mereni pozadi, pro pokracovani stiskni ENTER")

while provede_mereni==1 :  # test zda-li se provede dvakrat pro kontrolu pozadi
	fft = np.linspace(0,0,  pocet_oken *(int(round(pocet_vzorku*(1/1.2))))) # definice velikosti pole pro vyslednou FFT - zde se zapisuje
	for aktualni_okno in range(1, pocet_oken+1):
		print('Merim')
		time.sleep(0.08) # bezpecnostni prodleva pro preladeni a ustaleni
		data = sdr.read_samples(pocet_vzorku)
		sdr.center_freq = sdr.center_freq + 1e6; 
		data = abs(scipy.fft(data)) # provede se FFT 

		for index in range(-1,1): # vymaze se pripadna velika stejnosmerna hodnota
	        	data[index] = 0

		data = np.roll(data, pocet_vzorku/2) # vycentruje se	
		
		for index in range(0, int(round(pocet_vzorku*(1/1.2)))): # sklada obraz do jednoho velkeho po 1 MHz oknech, ovsem navzorkovanych je 1.2 MHz, okraje 100kHz se zahodi
		        fft[index+(int(round(pocet_vzorku*(1/1.2)))*(aktualni_okno - 1))] = data[index+int(round(pocet_vzorku*(0.1/1.2)))]
		provede_mereni = 0

	if 	pozadi_temp == 1 :      # pozadi_temp je "1" pri prvnim kole mereni pozadi, pri mereni uzitecneho signalu je "0"
		pozadi_data = fft     # zaloha pozadi
		provede_mereni = 1
		pozadi_temp = 0
		raw_input("Probehne mereni s pritomnosti uzitecneho signalu, pro pokracovani stiskni ENTER")
		for index in range(0, pocet_oken *(int(round(pocet_vzorku*(1/1.2))))):
			fft[index] = 0


max_hodnota = 0
for index in range(0, pocet_oken *(int(round(pocet_vzorku*(1/1.2))))): # proscanuje indexy vysledneho FFT okna
	if fft[index] > max_hodnota:
		max_hodnota = fft[index]
		index_max_hodnoty = index
	if	log_volba is	'a' :
		if	fft[index] < 1 :
			fft[index]= 1
		fft[index]=20*math.log10(fft[index])
	if	pozadi_volba ==	'a' :
		fft[index] = fft[index] - pozadi_data[index]

plt.close('all')
f, ax = plt.subplots()
ax.plot(x,fft )
ax.set_title('FFT')
ax.set_ylabel('Amplituda [-]')
if	log_volba is	'a' :
	ax.set_ylabel('Amplituda [dB]')
ax.set_xlabel('Frekvence [ MHz ]')

print('*********')
print('Start [ MHz ]:')
print(f_start/1e6)
print('---------')
print('Stop  [ MHz ]:')
print(f_stop/1e6)
print('---------')
print('Sirka pasma  [ MHz ]:')
print((f_stop - f_start )/1e6)
print('---------')
print('Pocet oken  [ - ]:')
print(pocet_oken)
print('---------')
print('Rozliseni, RBW :')
print(1e6/pocet_vzorku)
print('---------')
print('Dominantni frekvence:')
print(x[index_max_hodnoty])
print('*********')
plt.show()


