# command_runner.py - Enhanced Version
import subprocess
import threading
import queue
import os
import psutil
from datetime import datetime
import socket
import ipaddress

class CommandRunner:
    def __init__(self, root, output_callback, finished_callback, progress_callback=None):
        self.root = root
        self.command_queue = queue.Queue()
        self.output_callback = output_callback
        self.finished_callback = finished_callback
        self.progress_callback = progress_callback
        self.current_process = None
        self.is_cancelled = False
        self.start_time = None
        
    def run_command(self, command_list, timeout=300, internal=False, params={}):
        """Ejecutar comando con timeout opcional"""
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except queue.Empty:
                break
        
        self.is_cancelled = False
        self.start_time = datetime.now()
        
        if internal:
            threading.Thread(
                target=self._run_internal_command, 
                args=(command_list, params), 
                daemon=True
            ).start()
        else:
            threading.Thread(
                target=self._execute, 
                args=(command_list, timeout), 
                daemon=True
            ).start()
        
        self._process_queue()

    def _run_internal_command(self, command, params):
        try:
            if command == "internal_port_scanner":
                self._port_scanner(params['host'], params['ports'])
            elif command == "internal_subnet_calculator":
                self._subnet_calculator(params['network'])
            elif command == "internal_wol":
                self._wake_on_lan(params['mac'])
            elif command == "internal_whois":
                self._whois_lookup(params['domain'])
        except Exception as e:
            self._handle_unexpected_error(e)

    def _port_scanner(self, host, ports_str):
        self.output_callback(f"Iniciando escaneo de puertos en {host}...\n")
        try:
            ports = [int(p.strip()) for p in ports_str.split(',')]
        except ValueError:
            self.output_callback("Error: Formato de puertos inválido. Use una lista separada por comas, ej: 80,443,8080\n")
            self.finished_callback()
            return

        for port in ports:
            if self.is_cancelled:
                break
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((host, port))
                    if result == 0:
                        self.output_callback(f"Puerto {port}: Abierto\n")
                    else:
                        self.output_callback(f"Puerto {port}: Cerrado\n")
            except socket.gaierror:
                self.output_callback(f"Error: No se pudo resolver el host {host}\n")
                break
            except Exception as e:
                self.output_callback(f"Error escaneando el puerto {port}: {e}\n")
        self.finished_callback()

    def _subnet_calculator(self, network_str):
        try:
            net = ipaddress.ip_network(network_str, strict=False)
            self.output_callback(f"Calculando detalles para la red {network_str}:\n")
            self.output_callback(f"  Dirección de red: {net.network_address}\n")
            self.output_callback(f"  Máscara de subred: {net.netmask}\n")
            self.output_callback(f"  Dirección de broadcast: {net.broadcast_address}\n")
            self.output_callback(f"  Número de hosts: {net.num_addresses - 2}\n")
            self.output_callback(f"  Rango de hosts: {net.network_address + 1} - {net.broadcast_address - 1}\n")
        except ValueError as e:
            self.output_callback(f"Error: {e}\n")
        self.finished_callback()

    def _wake_on_lan(self, mac_address):
        try:
            mac_bytes = bytes.fromhex(mac_address.replace(':', '').replace('-', ''))
            if len(mac_bytes) != 6:
                raise ValueError("Dirección MAC inválida")
            magic_packet = b'\xff' * 6 + mac_bytes * 16
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.sendto(magic_packet, ('<broadcast>', 9))
            self.output_callback(f"Paquete mágico enviado a {mac_address}\n")
        except ValueError as e:
            self.output_callback(f"Error: {e}\n")
        self.finished_callback()

    def _whois_lookup(self, domain):
        self.output_callback(f"Consultando WHOIS para {domain}...\n")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("whois.iana.org", 43))
                s.sendall(f"{domain}\r\n".encode())
                response = b""
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    response += data
                self.output_callback(response.decode(errors='ignore'))
        except Exception as e:
            self.output_callback(f"Error en la consulta WHOIS: {e}\n")
        self.finished_callback()

    def _execute(self, command_list, timeout):
        """Ejecutar comando del sistema con manejo avanzado"""
        try:
            startupinfo = None
            creationflags = 0
            env = os.environ.copy()
            
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = subprocess.CREATE_NO_WINDOW
                env['PYTHONIOENCODING'] = 'utf-8'
            
            full_command = self._prepare_command(command_list)
            
            self.command_queue.put(('info', f"🔧 Comando: {' '.join(full_command)}\n"))
            self.command_queue.put(('info', f"⏰ Iniciado: {self.start_time.strftime('%H:%M:%S')}\n"))
            
            self.current_process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=creationflags,
                env=env,
                universal_newlines=True
            )

            self._monitor_process_output(timeout)
            
        except FileNotFoundError:
            self._handle_command_not_found(command_list[0])
        except PermissionError:
            self._handle_permission_error(command_list[0])
        except subprocess.TimeoutExpired:
            self._handle_timeout(timeout)
        except Exception as e:
            self._handle_unexpected_error(e)
        finally:
            self.current_process = None

    def _handle_permission_error(self, command):
        message = (
            f"❌ ERROR DE PERMISOS: '{command}'\n\n"
            f"💡 SOLUCIONES:\n"
            f"• Ejecutar la aplicación como administrador\n"
            f"• Verificar permisos del usuario actual\n"
            f"• Comprobar restricciones de seguridad del sistema\n"
        )
        self.command_queue.put(('finished', message))

    def _handle_timeout(self, timeout):
        if self.current_process:
            self._terminate_process_tree()
        
        message = (
            f"⏱️ TIMEOUT: El comando excedió el tiempo límite de {timeout}s\n\n"
            f"💡 POSIBLES CAUSAS:\n"
            f"• El comando está esperando entrada del usuario\n"
            f"• La operación requiere más tiempo del esperado\n"
            f"• Problemas de red o conectividad\n"
        )
        self.command_queue.put(('finished', message))

    def _handle_unexpected_error(self, error):
        message = (
            f"❌ ERROR INESPERADO: {str(error)}\n\n"
            f"💡 INFORMACIÓN TÉCNICA:\n"
            f"• Tipo: {type(error).__name__}\n"
            f"• Detalles: {str(error)}\n"
        )
        self.command_queue.put(('finished', message))

    def _get_command_suggestions(self, command):
        common_commands = {
            'ping': ['ping', 'tracert', 'pathping'],
            'trace': ['tracert', 'traceroute', 'pathping'],
            'ip': ['ipconfig', 'ifconfig'],
            'net': ['netstat', 'netsh'],
            'arp': ['arp'],
            'route': ['route'],
            'dns': ['nslookup', 'dig']
        }
        
        suggestions = []
        command_lower = command.lower()
        
        for key, commands in common_commands.items():
            if key in command_lower:
                suggestions.extend(commands)
        
        return list(set(suggestions))[:3]

    def _terminate_process_tree(self):
        if not self.current_process:
            return
            
        try:
            if os.name == 'nt':
                subprocess.run([
                    'taskkill', '/F', '/T', '/PID', str(self.current_process.pid)
                ], capture_output=True, timeout=5)
            else:
                parent = psutil.Process(self.current_process.pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                
                parent.terminate()
                
                gone, alive = psutil.wait_procs(children + [parent], timeout=3)
                for p in alive:
                    try:
                        p.kill()
                    except psutil.NoSuchProcess:
                        pass
                        
        except Exception as e:
            print(f"Error terminando proceso: {e}")

    def _process_queue(self):
        processed_any = False
        
        try:
            while True:
                try:
                    msg_type, content = self.command_queue.get_nowait()
                    processed_any = True
                    
                    if msg_type == 'output':
                        self.output_callback(content)
                    elif msg_type == 'info':
                        self.output_callback(content)
                    elif msg_type == 'progress' and self.progress_callback:
                        self.progress_callback(content)
                    elif msg_type == 'finished':
                        self.output_callback(content + "\n")
                        self.finished_callback()
                        return
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"Error procesando cola: {e}")
        
        interval = 50 if processed_any else 100
        
        if self.root and self.root.winfo_exists():
            self.root.after(interval, self._process_queue)

    def cancel_command(self):
        if not self.current_process:
            return False
            
        self.is_cancelled = True
        
        try:
            self._terminate_process_tree()
            return True
        except Exception as e:
            print(f"Error cancelando comando: {e}")
            return False

    def is_running(self):
        return self.current_process is not None and self.current_process.poll() is None

    def get_process_info(self):
        if not self.current_process:
            return None
            
        try:
            process = psutil.Process(self.current_process.pid)
            return {
                'pid': process.pid,
                'name': process.name(),
                'cpu_percent': process.cpu_percent(),
                'memory_info': process.memory_info(),
                'create_time': process.create_time(),
                'status': process.status()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def get_runtime_stats(self):
        if not self.start_time:
            return None
            
        current_time = datetime.now()
        runtime = (current_time - self.start_time).total_seconds()
        
        return {
            'start_time': self.start_time,
            'current_time': current_time,
            'runtime_seconds': runtime,
            'runtime_formatted': self._format_duration(runtime)
        }

    def _format_duration(self, seconds):
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            return f"{hours}h {remaining_minutes}m"

    def _prepare_command(self, command_list):
        if not command_list:
            raise ValueError("Lista de comandos vacía")
        
        if command_list[0] == 'netsh' and len(command_list) > 1:
            return [command_list[0]] + command_list[1].split()
        
        if not self._command_exists(command_list[0]):
            raise FileNotFoundError(f"Comando '{command_list[0]}' no encontrado")
        
        return command_list

    def _command_exists(self, command):
        try:
            if os.name == 'nt':
                subprocess.run(['where', command], 
                             capture_output=True, 
                             check=True, 
                             timeout=5)
            else:
                subprocess.run(['which', command], 
                             capture_output=True, 
                             check=True, 
                             timeout=5)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _monitor_process_output(self, timeout):
        def read_stream(stream, prefix=""):
            try:
                while True:
                    if self.is_cancelled:
                        break
                    
                    line = stream.readline()
                    if not line:
                        break
                    
                    if line.strip() or prefix:
                        self.command_queue.put(('output', f"{prefix}{line}"))
                        
            except Exception as e:
                self.command_queue.put(('output', f"❌ Error leyendo salida: {e}\n"))

        stdout_thread = threading.Thread(
            target=read_stream, 
            args=(self.current_process.stdout, ""),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=read_stream, 
            args=(self.current_process.stderr, "⚠️ "),
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()

        try:
            return_code = self.current_process.wait(timeout=timeout)
            
            stdout_thread.join(timeout=2)
            stderr_thread.join(timeout=2)
            
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            
            self._send_completion_message(return_code, duration)
            
        except subprocess.TimeoutExpired:
            self._handle_timeout(timeout)

    def _send_completion_message(self, return_code, duration):
        if self.is_cancelled:
            self.command_queue.put(('finished', 
                "⚠️ Comando cancelado por el usuario"))
        elif return_code == 0:
            self.command_queue.put(('finished', 
                f"✅ Comando completado exitosamente en {duration:.2f}s (código: {return_code})"))
        else:
            self.command_queue.put(('finished', 
                f"⚠️ Comando terminado con errores en {duration:.2f}s (código: {return_code})"))

    def _handle_command_not_found(self, command):
        suggestions = self._get_command_suggestions(command)
        message = (
            f"❌ COMANDO NO ENCONTRADO: '{command}'\n\n"
            f"💡 POSIBLES SOLUCIONES:\n"
            f"• Verificar que el comando esté instalado\n"
            f"• Comprobar que esté en el PATH del sistema\n"
            f"• Ejecutar como administrador si es necesario\n"
        )
        
        if suggestions:
            message += f"\n🔍 COMANDOS SIMILARES:\n" + "\n".join(f"• {s}" for s in suggestions)
        
        self.command_queue.put(('finished', message))