import socket
from requests import get


def ip_address_changed(combined_total: float):
    """
    Binance API will fail if current IP address
    not in whitelist.
    165.120.110.243
    """
    whitelist = ['165.120.110.243']
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    public_ip = get('https://api.ipify.org').content.decode('utf8')
    #print("Public IP address is: {public_ip}")

    if public_ip not in whitelist:
        return [f"Current public IP address: {public_ip}"]

    return []


if __name__ == "__main__":
    print(ip_address_changed(0))
