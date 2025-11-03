# tool_definitions.py
import platform

# Determina el sistema operativo para ajustar los comandos
OS_TYPE = platform.system().lower()

# --- Definiciones de las Herramientas ---

TOOLS = {
    "PING": {
        "description": (
            "Utilidad: Envía paquetes ICMP ECHO_REQUEST a un host de red para verificar si está activo y medir el tiempo de respuesta.\n"
            "Funcionamiento: Especifica un host (IP o dominio) y opcionalmente el número de pings a enviar."
        ),
        "parameters": [
            {"name": "Host/IP", "type": "entry", "required": True, "arg": None},
            {"name": "Número de pings", "type": "entry", "required": False, "arg": "-n" if OS_TYPE == "windows" else "-c", "default": "4"}
        ],
        "command": ["ping"]
    },
    "TRACERT": {
        "description": (
            "Utilidad: Muestra la ruta (los 'saltos' a través de routers) que toman los paquetes para llegar a un host de red.\n"
            "Funcionamiento: Introduce la IP o el nombre de dominio del destino."
        ),
        "parameters": [
            {"name": "Host/IP", "type": "entry", "required": True, "arg": None}
        ],
        "command": ["tracert"] if OS_TYPE == "windows" else ["traceroute"]
    },
    "PATHPING": {
        "description": (
            "Utilidad: Combina la funcionalidad de PING y TRACERT. Proporciona información sobre la latencia de red y la pérdida de paquetes en cada salto intermedio.\n"
            "Funcionamiento: Introduce la IP o el nombre de dominio del destino. Puede tardar varios minutos en completarse."
        ),
        "parameters": [
            {"name": "Host/IP", "type": "entry", "required": True, "arg": None}
        ],
        "command": ["pathping"]
    },
    "NSLOOKUP": {
        "description": (
            "Utilidad: Consulta los servidores de nombres de dominio (DNS) para obtener información de un dominio, como su dirección IP, o viceversa.\n"
            "Funcionamiento: Introduce un dominio o una dirección IP."
        ),
        "parameters": [
            {"name": "Dominio/IP", "type": "entry", "required": True, "arg": None}
        ],
        "command": ["nslookup"]
    },
    "NETSTAT": {
        "description": (
            "Utilidad: Muestra las conexiones de red activas (entrantes y salientes), tablas de enrutamiento y estadísticas de interfaces de red.\n"
            "Funcionamiento: Selecciona los argumentos a ejecutar. '-an' es una opción común para ver todas las conexiones y puertos."
        ),
        "parameters": [
            {"name": "Argumentos", "type": "entry", "required": True, "arg": None, "default": "-an"}
        ],
        "command": ["netstat"]
    },
    "IPCONFIG": {
        "description": (
            "Utilidad: Muestra la configuración de red TCP/IP actual de todas las interfaces de red del equipo.\n"
            "Funcionamiento: El comando se ejecuta sin parámetros adicionales por defecto, pero puedes agregar otros como '/all'."
        ),
        "parameters": [
            {"name": "Argumentos (ej: /all)", "type": "entry", "required": False, "arg": None, "default": "/all" if OS_TYPE == "windows" else "-a"}
        ],
        "command": ["ipconfig"] if OS_TYPE == "windows" else ["ifconfig"]
    },
    "ARP": {
        "description": (
            "Utilidad: Muestra y modifica las entradas en la caché del Protocolo de resolución de direcciones (ARP), que relaciona direcciones IP con direcciones MAC.\n"
            "Funcionamiento: El argumento '-a' muestra la tabla ARP actual."
        ),
        "parameters": [
            {"name": "Argumentos", "type": "entry", "required": True, "arg": None, "default": "-a"}
        ],
        "command": ["arp"]
    },
    "NETSH": {
        "description": (
            "Utilidad: Herramienta de scripting de línea de comandos que permite mostrar o modificar la configuración de red de un equipo.\n"
            "Funcionamiento: Introduce el contexto y el comando de netsh que deseas ejecutar (ej: 'interface ip show config')."
        ),
        "parameters": [
            {"name": "Contexto y Comando", "type": "entry", "required": True, "arg": None, "default": "interface ip show config"}
        ],
        "command": ["netsh"]
    },
    "ROUTE": {
        "description": (
            "Utilidad: Muestra y manipula las entradas en la tabla de enrutamiento de IP local.\n"
            "Funcionamiento: El comando 'print' muestra la tabla de enrutamiento."
        ),
        "parameters": [
             {"name": "Comando (ej: print)", "type": "entry", "required": True, "arg": None, "default": "print" if OS_TYPE == "windows" else "-n"}
        ],
        # CORRECCIÓN: Usar 'route' en ambos sistemas para consistencia del nombre de la herramienta.
        # Los parámetros ya se encargan de la diferencia ('print' vs '-n').
        "command": ["route"]
    },
    "SCANNER": {
        "description": "Escanea puertos abiertos en un host.",
        "parameters": [
            {"name": "Host", "type": "entry", "required": True, "arg": "host"},
            {"name": "Puertos", "type": "entry", "required": True, "arg": "ports", "default": "22,80,443"}
        ],
        "command": "internal_port_scanner",
        "internal": True
    },
    "SUBNET": {
        "description": "Calcula detalles de una subred.",
        "parameters": [
            {"name": "Red (ej: 192.168.1.0/24)", "type": "entry", "required": True, "arg": "network"}
        ],
        "command": "internal_subnet_calculator",
        "internal": True
    },
    "WOL": {
        "description": "Despierta un equipo en la red local.",
        "parameters": [
            {"name": "MAC Address", "type": "entry", "required": True, "arg": "mac"}
        ],
        "command": "internal_wol",
        "internal": True
    },
    "WHOIS": {
        "description": "Consulta información de un dominio.",
        "parameters": [
            {"name": "Dominio", "type": "entry", "required": True, "arg": "domain"}
        ],
        "command": "internal_whois",
        "internal": True
    }
}

# Deshabilitar herramientas no disponibles en el SO actual
if OS_TYPE != "windows":
    if "PATHPING" in TOOLS: del TOOLS["PATHPING"]
    if "NETSH" in TOOLS: del TOOLS["NETSH"]
    if "TRACERT" in TOOLS:
        pass
