"""Identity filter with an execution marker, used only in disposable test repos."""
from pathlib import Path
import sys

kind, marker = sys.argv[1:]
Path(marker).write_text('filter executed\n')
if kind == 'clean':
    sys.stdout.buffer.write(sys.stdin.buffer.read())
    raise SystemExit(0)
if kind != 'process':
    raise ValueError('unsupported fixture filter')


def read_section():
    packets = []
    while True:
        header = sys.stdin.buffer.read(4)
        if not header:
            return None
        if len(header) != 4:
            raise ValueError('short packet header')
        size = int(header, 16)
        if size == 0:
            return packets
        if size < 4:
            raise ValueError('invalid packet length')
        content = sys.stdin.buffer.read(size - 4)
        if len(content) != size - 4:
            raise ValueError('short packet content')
        packets.append(content)


def write_section(packets):
    for packet in packets:
        sys.stdout.buffer.write(f'{len(packet) + 4:04x}'.encode() + packet)
    sys.stdout.buffer.write(b'0000')
    sys.stdout.buffer.flush()


hello = read_section()
assert hello == [b'git-filter-client\n', b'version=2\n'], hello
write_section([b'git-filter-server\n', b'version=2\n'])
capabilities = read_section()
assert capabilities is not None and b'capability=clean\n' in capabilities
write_section([b'capability=clean\n'])
while True:
    headers = read_section()
    if headers is None:
        break
    assert b'command=clean\n' in headers, headers
    content = read_section()
    assert content is not None
    write_section([b'status=success\n'])
    write_section(content)
    write_section([])
