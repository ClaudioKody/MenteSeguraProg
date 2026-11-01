import socket
from pathlib import Path


try:
    import qrcode
except ImportError:
    raise SystemExit('Falta qrcode. Ejecutá: python -m pip install "qrcode[pil]"')


try:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    probe.connect(("8.8.8.8", 80))
    local_ip = probe.getsockname()[0]
    probe.close()
except OSError:
    local_ip = socket.gethostbyname(socket.gethostname())
url = f'http://{local_ip}:5000'
output = Path(__file__).with_name('qr-mentesegura.png')
qrcode.make(url).save(output)
print(f'URL para el celular: {url}')
print(f'QR guardado en: {output}')
print('Abrí qr-mentesegura.png y escanealo con el celular.')
