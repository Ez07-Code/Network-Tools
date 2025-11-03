# Network Tools

Network Tools is a comprehensive suite of network diagnostic and utility tools, designed with a modern and user-friendly graphical interface. This application provides a one-stop solution for network professionals and enthusiasts to perform common network tasks efficiently.

![Network Tools Pro Screenshot](hub.png)

## Features

Network Tools Pro includes a variety of tools, both for diagnostics and for network management:

### Diagnostic Tools

- **Ping:** Send ICMP ECHO_REQUEST packets to a host to check its availability and response time.
- **Traceroute:** Display the route and measure transit delays of packets across an Internet Protocol (IP) network.
- **PathPing:** A combination of Ping and Traceroute, providing more detailed information about network latency and packet loss at each hop.
- **NSLookup:** Query the Domain Name System (DNS) to obtain domain name or IP address mapping, or for any other specific DNS record.
- **Netstat:** Display network connections for TCP (both incoming and outgoing), routing tables, and a number of network interface and network protocol statistics.
- **ARP:** Display and modify the Address Resolution Protocol (ARP) cache.
- **Port Scanner:** Scan for open TCP ports on a target host.

### Utility Tools

- **IPConfig:** Display the current TCP/IP network configuration values.
- **Subnet Calculator:** Calculate subnet details, including network address, broadcast address, netmask, and host range.
- **Wake-on-LAN (WOL):** Send a magic packet to wake up a computer on the local network.
- **Whois Lookup:** Query WHOIS servers for information about a domain name.

### Other Features

- **Modern UI:** A clean, dark-themed, and intuitive user interface.
- **Command History:** Keeps a history of all executed commands for easy reference.
- **Real-time Output:** Command output is streamed in real-time to the terminal window.
- **Cross-Platform:** While some tools are OS-specific, the application is designed to be cross-platform, with support for Windows, macOS, and Linux.

## Technologies Used

- **Python:** The core application is built with Python 3.
- **Tkinter:** The graphical user interface is built using Python's standard GUI package, Tkinter.
- **Matplotlib:** Used for plotting real-time graphs (in features that use it).
- **psutil:** A cross-platform library for retrieving information on running processes and system utilization.

## Installation and Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, simply execute the `main.py` script:

```bash
python main.py
```

## Creating an Executable

To create a standalone executable (`.exe` for Windows), you can use `pyinstaller`.

1.  **Make sure `pyinstaller` is installed:**

    ```bash
    pip install pyinstaller
    ```

2.  **Run the `pyinstaller` command:**

    The following command will create a single executable file in the `dist` directory. The `--noconsole` flag prevents the command prompt from appearing when you run the executable, and the `--onefile` flag bundles everything into a single file. The `--icon` flag sets the application icon.

    ```bash
    pyinstaller --name "Network Tools Pro" --onefile --windowed --icon="hub.ico" main.py
    ```

3.  **Find the executable:**

    The executable will be located in the `dist` folder.

## Author

Created by: **Ez07-Code**

- **GitHub:** [https://github.com/Ez07-Code](https://github.com/Ez07-Code)
