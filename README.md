# Mechanical Clicker (Aplicación con Sockets TCP)

Esta aplicación es un proyecto cliente-servidor basado en sockets TCP. Consiste en un clicker donde múltiples clientes pueden conectarse a un servidor central para sincronizar y aumentar un contador de clics de forma colaborativa y en tiempo real.

## Requisitos de Instalación

- **Lenguaje y Versión:** Python 3.8 o superior.
- **Gestor de paquetes:** `pip`.

### Bibliotecas necesarias
El proyecto utiliza principalmente bibliotecas integradas en la biblioteca estándar de Python, pero requiere una biblioteca externa para la reproducción de sonidos:

- `pygame` (Externa, requerida para reproducir el efecto de sonido del clic)
- `tkinter` (Integrada, para la interfaz gráfica del cliente)
- `socket` (Integrada, para la comunicación por red)
- `threading` (Integrada, para manejar múltiples clientes y peticiones asíncronas)
- `json` (Integrada, para guardar récords locales)

Para instalar las dependencias externas (`pygame`), abre tu terminal y ejecuta:

```bash
pip install pygame
```

## Configuración de Red por Defecto

- **Protocolo:** TCP
- **Puerto:** `5050`
- **Dirección IP de escucha (Servidor):** `0.0.0.0` (El servidor escucha conexiones entrantes desde cualquier interfaz de red).
- **Dirección IP de conexión (Cliente):** `127.0.0.1` (Para pruebas locales en la misma máquina). Si pruebas en computadoras distintas, usa la IP local del servidor (ej. `192.168.1.11`).

---

## Instrucciones para ejecutar el programa

Para que el programa funcione correctamente, primero debe inicializarse el componente Servidor y posteriormente los componentes Cliente.

### 1. Iniciar el Servidor

Abre una terminal, navege hasta el directorio raíz del proyecto y ejecute:

```bash
python API/API.py
```
*(También se puede utilizar `python3` si su sistema operativo asi lo requiere).*

El servidor comenzará a ejecutarse y la consola mostrará un mensaje indicando que está escuchando:
`[INFO] Servidor TCP escuchando en 0.0.0.0:5050`

### 2. Iniciar el Cliente

Abre **otra** terminal independiente, navege a la raíz del proyecto y ejecute:

```bash
python App-Tkinter/clicker.py
```

Se abrirá una ventana gráfica (GUI) correspondiente al Mechanical Clicker.

### 3. Ejemplo Básico de Ejecución (Paso a Paso)

1. Con el **Servidor** corriendo, abre **dos ventanas del Cliente** (ejecutando el comando del cliente dos veces en terminales separadas).
2. En la parte inferior de ambas ventanas del cliente, verás campos de texto para **IP** y **Puerto**. Deja los valores por defecto (`127.0.0.1` y `5050`).
3. Haz clic en el botón verde **Conectar** en ambas ventanas.
4. El texto inferior pasará a verde indicando `Conectado a 127.0.0.1:5050`. En ese momento, ambos clientes se habrán sincronizado con el contador global del servidor.
5. Haz clic en la "tecla" de la primera ventana. Verás y escucharás el clic, y el contador subirá a `1`.
6. Sin que toques la segunda ventana, su contador también se actualizará automáticamente a `1` gracias a la sincronización en tiempo real.
7. Al finalizar, simplemente cierra las ventanas y presiona `Ctrl+C` en la terminal del servidor para apagarlo de manera segura.



# Presentacion:
https://canva.link/pptxwa3nso1ef6y