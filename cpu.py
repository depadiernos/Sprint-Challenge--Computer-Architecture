"""CPU functionality."""

import sys

"""Flags: Flag Bits => 00000LGE"""
EQUAL_FLAG = 0b001
GREATER_FLAG = 0b010
LESS_FLAG = 0b100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7
        self.running = True
        self.fl = 0
        self.branch_table = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100000: self.ADD,
            0b10100010: self.MUL,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100111: self.CMP,
            0b01010100: self.JMP,
            0b01010101: self.JEQ,
            0b01010110: self.JNE,
            0b10101000: self.AND,
            0b10101010: self.OR,
            0b10101011: self.XOR,
            0b01101001: self.NOT,
            0b10101100: self.SHL,
            0b10101101: self.SHR,
            0b10100100: self.MOD,
        }

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("Usage: ls8.py filename.ls8")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as file:
                for line in file:
                    split_line = line.split("#")
                    value = split_line[0].strip() 

                    if value == "":
                        continue 
                    instruction = int(value, 2)
                    self.ram[address] = instruction
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[1]}: File not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            op_a = self.reg[reg_a]
            op_b = self.reg[reg_b]
            if op_a == op_b:
                self.fl = 0b00000001
            elif op_a > op_b:
                self.fl = 0b00000010
            elif op_a < op_b:
                self.fl = 0b00000100
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == "MOD":
            try:
                self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
            except ZeroDivisionError:
                print(f"Can't divide by zero")
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def LDI(self):
        address = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[address] = value
        self.pc += 3


    def PRN(self):
        register = self.ram_read(self.pc + 1)
        value = self.reg[register]
        print(value)
        self.pc += 2

    def PUSH(self):
        register = self.ram_read(self.pc + 1)
        value = self.reg[register]
        address = self.reg[self.sp]
        self.ram_write(address, value)
        self.reg[self.sp] -= 1
        self.pc += 2

    def POP(self):
        value = self.ram_read(self.reg[self.sp])
        register = self.ram_read(self.pc + 1)
        self.reg[register] = value
        self.reg[self.sp] += 1
        self.pc += 2

    def CALL(self):
        return_address = self.pc + 2
        self.reg[6] -= 1
        self.ram[self.reg[6]] = return_address
        self.pc = self.reg[self.ram_read(self.pc + 1)]

    def RET(self):
        self.pc = self.reg[self.sp]
        self.reg[self.sp] += 1

    def CMP(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("CMP", op_a, op_b)
        self.pc += 3

    def JMP(self):
        self.pc = self.ram_read(self.pc + 1)

    def JEQ(self):
        if self.fl == EQUAL_FLAG:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2

    def JNE(self):
        if self.fl != EQUAL_FLAG:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2

    def AND(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("AND", op_a, op_b)
        self.pc += 3

    def OR(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("OR", op_a, op_b)
        self.pc += 3

    def XOR(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("XOR", op_a, op_b)
        self.pc += 3

    def NOT(self):
        op_a = self.ram_read(self.pc + 1)
        self.alu("NOT", op_a, None)
        self.pc += 2

    def SHL(self):
        value = self.ram_read(self.pc + 1)
        bits = self.ram_read(self.pc + 2)
        self.alu("SHL", value, bits)
        self.pc += 3

    def SHR(self):
        value = self.ram_read(self.pc + 1)
        bits = self.ram_read(self.pc + 2)
        self.alu("SHR", value, bits)
        self.pc += 3

    def MOD(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("MOD", op_a, op_b)
        self.pc += 3

    def ADD(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("ADD", op_a, op_b)
        self.pc += 3

    def MUL(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("MUL", op_a, op_b)
        self.pc += 3

    def HLT(self):
        self.running = False
        sys.exit()

    def run(self):
        """Run the CPU."""
        while self.running:
            instruction = self.ram[self.pc]
            if instruction in self.branch_table:
                self.branch_table[instruction]()
            else:
                sys.exit(1)