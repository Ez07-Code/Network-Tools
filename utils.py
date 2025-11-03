# utils.py - Network Tools Utilities
import json
import os
import re
import socket
import subprocess
import platform
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import ipaddress

class NetworkUtils:
    """Utilidades de red para la aplicación"""
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validar dirección IP"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_domain_name(domain: str) -> bool:
        """Validar nombre de dominio"""
        pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(pattern.match(domain)) and len(domain) <= 253
    
    @staticmethod
    def get_local_ip() -> str:
        """Obtener IP local del sistema"""
        try:
            # Conectar a un servidor externo para determinar la IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def get_default_gateway() -> Optional[str]:
        """Obtener gateway predeterminado"""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(
                    ["route", "print", "0.0.0.0"],
                    capture_output=True, text=True, timeout=10
                )
                lines = result.stdout.split('\n')
                for line in lines:
                    if '0.0.0.0' in line and 'Gateway' not in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            gateway = parts[2]
                            if NetworkUtils.validate_ip_address(gateway):
                                return gateway
            else:
                result = subprocess.run(
                    ["ip", "route", "show", "default"],
                    capture_output=True, text=True, timeout=10
                )
                match = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', result.stdout)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return None
    
    @staticmethod
    def ping_host(host: str, count: int = 4, timeout: int = 5) -> Dict:
        """Hacer ping a un host y retornar estadísticas"""
        try:
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
            else:
                cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Parsear resultados
            stats = {
                'host': host,
                'packets_sent': count,
                'packets_received': 0,
                'packet_loss': 100.0,
                'min_time': None,
                'max_time': None,
                'avg_time': None,
                'success': False
            }
            
            if result.returncode == 0:
                output = result.stdout
                
                # Buscar estadísticas de pérdida de paquetes
                if platform.system().lower() == "windows":
                    loss_match = re.search(r'\((\d+)% loss\)', output)
                    if loss_match:
                        stats['packet_loss'] = float(loss_match.group(1))
                        stats['packets_received'] = count - int(count * stats['packet_loss'] / 100)
                    
                    # Buscar tiempos
                    time_matches = re.findall(r'time[<=](\d+)ms', output)
                    if time_matches:
                        times = [int(t) for t in time_matches]
                        stats['min_time'] = min(times)
                        stats['max_time'] = max(times)
                        stats['avg_time'] = sum(times) / len(times)
                        stats['success'] = True
                
                else:  # Linux/Unix
                    loss_match = re.search(r'(\d+)% packet loss', output)
                    if loss_match:
                        stats['packet_loss'] = float(loss_match.group(1))
                        stats['packets_received'] = count - int(count * stats['packet_loss'] / 100)
                    
                    # Buscar estadísticas de tiempo
                    time_match = re.search(r'min/avg/max.*?= ([\d.]+)/([\d.]+)/([\d.]+)', output)
                    if time_match:
                        stats['min_time'] = float(time_match.group(1))
                        stats['avg_time'] = float(time_match.group(2))
                        stats['max_time'] = float(time_match.group(3))
                        stats['success'] = True
            
            return stats
            
        except Exception as e:
            return {
                'host': host,
                'error': str(e),
                'success': False
            }
    
    @staticmethod
    def resolve_hostname(hostname: str) -> Dict:
        """Resolver hostname a IP"""
        try:
            # Resolver IPv4
            ipv4_addresses = []
            try:
                result = socket.getaddrinfo(hostname, None, socket.AF_INET)
                ipv4_addresses = list(set([r[4][0] for r in result]))
            except socket.gaierror:
                pass
            
            # Resolver IPv6
            ipv6_addresses = []
            try:
                result = socket.getaddrinfo(hostname, None, socket.AF_INET6)
                ipv6_addresses = list(set([r[4][0] for r in result]))
            except socket.gaierror:
                pass
            
            return {
                'hostname': hostname,
                'ipv4_addresses': ipv4_addresses,
                'ipv6_addresses': ipv6_addresses,
                'success': bool(ipv4_addresses or ipv6_addresses)
            }
            
        except Exception as e:
            return {
                'hostname': hostname,
                'error': str(e),
                'success': False
            }

class ConfigManager:
    """Gestor de configuración de la aplicación"""
    
    def __init__(self, config_dir: str = "network_tools_config"):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "config.json")
        self.favorites_file = os.path.join(config_dir, "favorites.json")
        self.history_file = os.path.join(config_dir, "history.json")
        self.templates_file = os.path.join(config_dir, "templates.json")
        
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Asegurar que existe el directorio de configuración"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def load_config(self) -> Dict:
        """Cargar configuración principal"""
        default_config = {
            'last_tool': 'PING',
            'window_geometry': '1200x800',
            'theme': 'dark',
            'auto_save_output': False,
            'max_history_entries': 100,
            'default_timeout': 300,
            'terminal_font_size': 10,
            'show_welcome_message': True,
            'auto_scroll_output': True,
            'save_window_position': True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge con configuración por defecto
                    default_config.update(config)
        except Exception as e:
            print(f"Error cargando configuración: {e}")
        
        return default_config
    
    def save_config(self, config: Dict):
        """Guardar configuración"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def load_favorites(self) -> List[Dict]:
        """Cargar favoritos"""
        try:
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando favoritos: {e}")
        return []
    
    def save_favorites(self, favorites: List[Dict]):
        """Guardar favoritos"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(favorites, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando favoritos: {e}")
    
    def load_history(self) -> List[Dict]:
        """Cargar historial"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando historial: {e}")
        return []
    
    def save_history(self, history: List[Dict]):
        """Guardar historial"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando historial: {e}")
    
    def load_templates(self) -> List[Dict]:
        """Cargar plantillas de comandos"""
        default_templates = [
            {
                'name': 'Ping básico',
                'tool': 'PING',
                'description': 'Ping simple a Google DNS',
                'parameters': {'Host/IP Destino': '8.8.8.8', 'Número de pings': '4'}
            },
            {
                'name': 'Traceroute a Google',
                'tool': 'TRACERT',
                'description': 'Rastrear ruta a Google',
                'parameters': {'Host/IP Destino': 'google.com'}
            },
            {
                'name': 'Ver conexiones activas',
                'tool': 'NETSTAT',
                'description': 'Mostrar todas las conexiones activas',
                'parameters': {'Argumentos': '-an'}
            },
            {
                'name': 'Configuración IP completa',
                'tool': 'IPCONFIG',
                'description': 'Ver toda la configuración de red',
                'parameters': {'Argumentos (ej: /all)': '/all'}
            }
        ]
        
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando plantillas: {e}")
        
        # Guardar plantillas por defecto si no existen
        self.save_templates(default_templates)
        return default_templates
    
    def save_templates(self, templates: List[Dict]):
        """Guardar plantillas"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando plantillas: {e}")

class OutputFormatter:
    """Formateador de salida para diferentes tipos de comandos"""
    
    @staticmethod
    def format_ping_output(output: str) -> str:
        """Formatear salida de ping con colores y emojis"""
        lines = output.split('\n')
        formatted_lines = []
        
        for line in lines:
            if 'Reply from' in line or 'bytes from' in line:
                # Línea de respuesta exitosa
                formatted_lines.append(f"✅ {line}")
            elif 'Request timed out' in line or 'no answer' in line:
                # Timeout
                formatted_lines.append(f"⏱️ {line}")
            elif 'Destination host unreachable' in line:
                # Host no alcanzable
                formatted_lines.append(f"❌ {line}")
            elif 'Packets:' in line or 'packet loss' in line:
                # Estadísticas
                formatted_lines.append(f"📊 {line}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def format_tracert_output(output: str) -> str:
        """Formatear salida de traceroute"""
        lines = output.split('\n')
        formatted_lines = []
        
        for line in lines:
            if re.match(r'\s*\d+\s+', line):
                # Línea de salto
                if '*' in line:
                    formatted_lines.append(f"⏱️ {line}")
                else:
                    formatted_lines.append(f"🛤️ {line}")
            elif 'Trace complete' in line:
                formatted_lines.append(f"✅ {line}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def format_netstat_output(output: str) -> str:
        """Formatear salida de netstat"""
        lines = output.split('\n')
        formatted_lines = []
        
        for line in lines:
            if 'LISTENING' in line:
                formatted_lines.append(f"👂 {line}")
            elif 'ESTABLISHED' in line:
                formatted_lines.append(f"🔗 {line}")
            elif 'TIME_WAIT' in line:
                formatted_lines.append(f"⏳ {line}")
            elif 'CLOSE_WAIT' in line:
                formatted_lines.append(f"🔒 {line}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def format_output_by_command(command: str, output: str) -> str:
        """Formatear salida según el tipo de comando"""
        command_lower = command.lower()
        
        if 'ping' in command_lower:
            return OutputFormatter.format_ping_output(output)
        elif 'tracert' in command_lower or 'traceroute' in command_lower:
            return OutputFormatter.format_tracert_output(output)
        elif 'netstat' in command_lower:
            return OutputFormatter.format_netstat_output(output)
        else:
            return output

class SystemInfo:
    """Información del sistema y diagnósticos"""
    
    @staticmethod
    def get_system_info() -> Dict:
        """Obtener información completa del sistema"""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'local_ip': NetworkUtils.get_local_ip(),
            'default_gateway': NetworkUtils.get_default_gateway()
        }
    
    @staticmethod
    def diagnose_network() -> Dict:
        """Realizar diagnóstico básico de red"""
        results = {}
        
        # Test conectividad local
        local_ip = NetworkUtils.get_local_ip()
        results['local_connectivity'] = {
            'ip': local_ip,
            'reachable': local_ip != '127.0.0.1'
        }
        
        # Test gateway
        gateway = NetworkUtils.get_default_gateway()
        if gateway:
            ping_result = NetworkUtils.ping_host(gateway, count=2)
            results['gateway_connectivity'] = {
                'gateway': gateway,
                'reachable': ping_result.get('success', False),
                'avg_time': ping_result.get('avg_time')
            }
        
        # Test DNS
        dns_servers = ['8.8.8.8', '1.1.1.1']
        results['dns_connectivity'] = {}
        
        for dns in dns_servers:
            ping_result = NetworkUtils.ping_host(dns, count=2)
            results['dns_connectivity'][dns] = {
                'reachable': ping_result.get('success', False),
                'avg_time': ping_result.get('avg_time')
            }
        
        # Test resolución DNS
        test_domains = ['google.com', 'github.com']
        results['dns_resolution'] = {}
        
        for domain in test_domains:
            resolve_result = NetworkUtils.resolve_hostname(domain)
            results['dns_resolution'][domain] = {
                'resolvable': resolve_result.get('success', False),
                'ipv4_addresses': resolve_result.get('ipv4_addresses', [])
            }
        
        return results
    
    @staticmethod
    def generate_network_report() -> str:
        """Generar reporte completo de red"""
        system_info = SystemInfo.get_system_info()
        network_diag = SystemInfo.diagnose_network()
        
        report = f"""
🖥️ REPORTE DE DIAGNÓSTICO DE RED
{'=' * 50}

📋 INFORMACIÓN DEL SISTEMA:
• Sistema Operativo: {system_info['platform']} {system_info['platform_release']}
• Arquitectura: {system_info['architecture']}
• Hostname: {system_info['hostname']}
• IP Local: {system_info['local_ip']}
• Gateway: {system_info['default_gateway'] or 'No detectado'}

🌐 CONECTIVIDAD DE RED:
"""
        
        # Conectividad local
        local_conn = network_diag['local_connectivity']
        status = "✅ Activa" if local_conn['reachable'] else "❌ Inactiva"
        report += f"• Conectividad Local: {status} ({local_conn['ip']})\n"
        
        # Conectividad gateway
        if 'gateway_connectivity' in network_diag:
            gw_conn = network_diag['gateway_connectivity']
            status = "✅ Alcanzable" if gw_conn['reachable'] else "❌ No alcanzable"
            avg_time = f" ({gw_conn['avg_time']:.1f}ms)" if gw_conn['avg_time'] else ""
            report += f"• Gateway: {status} ({gw_conn['gateway']}){avg_time}\n"
        
        # DNS
        report += "\n🔍 SERVIDORES DNS:\n"
        for dns, info in network_diag['dns_connectivity'].items():
            status = "✅ Alcanzable" if info['reachable'] else "❌ No alcanzable"
            avg_time = f" ({info['avg_time']:.1f}ms)" if info['avg_time'] else ""
            report += f"• {dns}: {status}{avg_time}\n"
        
        # Resolución DNS
        report += "\n🌍 RESOLUCIÓN DNS:\n"
        for domain, info in network_diag['dns_resolution'].items():
            status = "✅ Funcional" if info['resolvable'] else "❌ Falla"
            ips = ", ".join(info['ipv4_addresses'][:2]) if info['ipv4_addresses'] else "No resuelto"
            report += f"• {domain}: {status} → {ips}\n"
        
        report += f"\n📅 Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report