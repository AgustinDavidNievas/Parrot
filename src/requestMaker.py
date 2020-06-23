import os
import time
import requests
import multiprocessing
import concurrent.futures
import matplotlib.pyplot as plt
from multiprocessing import Manager
from pandas import DataFrame

def make_a_request(url, header, cookies):
    return requests.get(url = url, headers = header, cookies = cookies)

def loop_loco(datos, numero_loco, url, header, cookies):
    pid = os.getpid()
    for numero in range(0, numero_loco):
        t0 = time.perf_counter()
        r = make_a_request(url, header, cookies)
        t1 = time.perf_counter()
        
        print(f"{numero} en el pid {pid} la respuesta fue {r} y tardo {t1 - t0} segundos")
        cargar_datos(datos, pid, numero, t1 - t0, r)
    
def cargar_datos(datos, pid, numero, tiempo, respuesta):
    #['pid' 'numero_request' 'tiempo_respuesta', 'status_code']
    datos.append([pid, numero, tiempo, respuesta.status_code])
    
def show_data_frame(datos_compartidos):
    datos = list(datos_compartidos)
    
    tiempos_de_respuesta(datos)
    status_de_respuestas(datos)
    
    
def tiempos_de_respuesta(datos):
    df = DataFrame(datos, columns = ['pid', 'numero_request', 'tiempo_respuesta', 'status_code'])
    df = df.pivot(index='numero_request', columns='pid', values='tiempo_respuesta')
    df.plot()
    plt.savefig("tiemposDeRespuesta.png")
    
def status_de_respuestas(datos):
    status_codes = [str(dato[-1]) for dato in datos]
    counts = [sum(1 for code in status_codes if '2' in code), 
              sum(1 for code in status_codes if '4' in code), 
              sum(1 for code in status_codes if '5' in code)]
              
    df = DataFrame(counts,columns=['status_code'],index = ['200','400','500'])
    df.plot.pie(y='status_code',figsize=(5, 5),autopct='%1.1f%%', startangle=90)
    plt.savefig("tortaDeRespuestas.png")

def main():
    url = ''
    header = {'X-Client': 'test','x-version-override': None}
    cookies = {'ACCESSTOKEN': ''}
    datos = Manager().list()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for cpu in range(0,multiprocessing.cpu_count()):
            executor.submit(loop_loco, datos = datos, numero_loco = 100, url = url, header = header, cookies = cookies)
            
    show_data_frame(datos)

if __name__ == '__main__':
    main()
