# Network Tools

Network Tools Pro es un conjunto completo de herramientas de diagnóstico y utilidades de red, diseñado con una interfaz gráfica moderna y fácil de usar. Esta aplicación proporciona una solución integral para profesionales y entusiastas de las redes que necesitan realizar tareas comunes de red de manera eficiente.

![Captura de pantalla de Network Tools Pro](hub.png)

## Características

Network Tools Pro incluye una variedad de herramientas, tanto para diagnóstico como para gestión de redes:

### Herramientas de Diagnóstico

- **Ping:** Envía paquetes ICMP ECHO_REQUEST a un host para comprobar su disponibilidad y tiempo de respuesta.
- **Traceroute:** Muestra la ruta y mide los retardos de tránsito de los paquetes a través de una red de Protocolo de Internet (IP).
- **PathPing:** Una combinación de Ping y Traceroute, que proporciona información más detallada sobre la latencia de la red y la pérdida de paquetes en cada salto.
- **NSLookup:** Consulta el Sistema de Nombres de Dominio (DNS) para obtener el mapeo de nombre de dominio o dirección IP, o cualquier otro registro DNS específico.
- **Netstat:** Muestra las conexiones de red para TCP (tanto entrantes como salientes), tablas de enrutamiento y una serie de estadísticas de interfaz de red y protocolo de red.
- **ARP:** Muestra y modifica la caché del Protocolo de Resolución de Direcciones (ARP).
- **Escáner de Puertos:** Escanea los puertos TCP abiertos en un host objetivo.

### Herramientas de Utilidad

- **IPConfig:** Muestra los valores de configuración actuales de la red TCP/IP.
- **Calculadora de Subredes:** Calcula los detalles de la subred, incluyendo la dirección de red, la dirección de broadcast, la máscara de red y el rango de hosts.
- **Wake-on-LAN (WOL):** Envía un paquete mágico para encender un equipo en la red local.
- **Consulta Whois:** Consulta los servidores WHOIS para obtener información sobre un nombre de dominio.

### Otras Características

- **Interfaz de Usuario Moderna:** Una interfaz de usuario intuitiva, con un tema oscuro y limpio.
- **Historial de Comandos:** Mantiene un historial de todos los comandos ejecutados para una fácil referencia.
- **Salida en Tiempo Real:** La salida de los comandos se transmite en tiempo real a la ventana de terminal.
- **Multiplataforma:** Aunque algunas herramientas son específicas del sistema operativo, la aplicación está diseñada para ser multiplataforma, con soporte para Windows, macOS y Linux.

## Tecnologías Utilizadas

- **Python:** La aplicación principal está construida con Python 3.
- **Tkinter:** La interfaz gráfica de usuario está construida usando el paquete GUI estándar de Python, Tkinter.
- **Matplotlib:** Se utiliza para trazar gráficos en tiempo real (en las características que lo utilizan).
- **psutil:** Una librería multiplataforma para recuperar información sobre procesos en ejecución y utilización del sistema.

## Instalación y Configuración

1.  **Clona el repositorio:**

    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  **Crea un entorno virtual (recomendado):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows, usa `venv\Scripts\activate`
    ```

3.  **Instala las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

## Uso

Para ejecutar la aplicación, simplemente ejecuta el script `main.py`:

```bash
python main.py
```

Crear un Ejecutable

Para crear un ejecutable independiente (.exe para Windows), puedes usar pyinstaller.

    Asegúrate de que pyinstaller está instalado:
    
```bash
pip install pyinstaller
```

Ejecuta el comando pyinstaller:

El siguiente comando creará un único archivo ejecutable en el directorio dist. El flag --noconsole evita que aparezca la ventana de comandos cuando ejecutes el ejecutable, y el flag --onefile empaqueta todo en un solo archivo. El flag --icon establece el icono de la aplicación.

```bash
pyinstaller --name "Network Tools Pro" --onefile --windowed --icon="hub.ico" main.py
```

    Encuentra el ejecutable:

    El ejecutable se ubicará en la carpeta dist.

Autor

Creado por: Ez07-Code


    GitHub: https://github.com/Ez07-Code
