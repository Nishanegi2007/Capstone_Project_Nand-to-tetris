import sys
import os

# Predefined Hack symbols
PREDEFINED_SYMBOLS = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, 
    "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9, 
    "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15,
    "SCREEN": 16384, "KBD": 24576
}

# Translation tables for C-instructions
COMP_TABLE = {
    "0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100", "A": "0110000",
    "!D": "0001101", "!A": "0110001", "-D": "0001111", "-A": "0110011",
    "D+1": "0011111", "A+1": "0110111", "D-1": "0001110", "A-1": "0110010",
    "D+A": "0000010", "D-A": "0010011", "A-D": "0000111",
    "D&A": "0000000", "D|A": "0010101",
    # a = 1 cases
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101"
}

DEST_TABLE = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111"
}

JUMP_TABLE = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
}

class Assembler:
    def __init__(self, filepath, K=0):
        self.filepath = filepath
        self.K = K
        self.symbol_table = PREDEFINED_SYMBOLS.copy()
        self.rom_address = 0
        self.ram_address = 16
        self.clean_instructions = [] # Stores (original_line_num, instruction_text)

    def clean_and_parse_pass1(self):
        """First pass: remove comments/whitespace, record labels, and index ROM lines."""
        if not os.path.exists(self.filepath):
            print(f"Error: File '{self.filepath}' not found.")
            sys.exit(1)

        with open(self.filepath, 'r') as f:
            raw_lines = f.readlines()

        extra_feature_mode = self.K % 3

        for line_num, raw_line in enumerate(raw_lines, start=1):
            # Strip comments and whitespace
            line = raw_line.split('//')[0].strip()
            if not line:
                continue

            # Check for label declaration: (LABEL)
            if line.startswith('(') and line.endswith(')'):
                label = line[1:-1].strip()
                if label in self.symbol_table:
                    if extra_feature_mode == 2:
                        print(f"Warning: Label '{label}' defined twice (Line {line_num}).")
                self.symbol_table[label] = self.rom_address
            else:
                self.clean_instructions.append((line_num, line))
                self.rom_address += 1

    def assemble(self):
        self.clean_and_parse_pass1()
        extra_feature_mode = self.K % 3
        binary_output = []

        for line_num, line in self.clean_instructions:
            try:
                if line.startswith('@'):
                    # A-Instruction
                    symbol = line[1:]
                    if symbol.isdigit():
                        address = int(symbol)
                    else:
                        if symbol not in self.symbol_table:
                            self.symbol_table[symbol] = self.ram_address
                            self.ram_address += 1
                        address = self.symbol_table[symbol]
                    
                    bin_code = format(address, '016b')
                else:
                    # C-Instruction
                    dest, comp, jump = "", "", ""
                    if '=' in line:
                        dest_part, rest = line.split('=')
                        dest = dest_part.strip()
                    else:
                        rest = line

                    if ';' in rest:
                        comp_part, jump_part = rest.split(';')
                        comp = comp_part.strip()
                        jump = jump_part.strip()
                    else:
                        comp = rest.strip()

                    if comp not in COMP_TABLE or dest not in DEST_TABLE or jump not in JUMP_TABLE:
                        raise ValueError("Invalid instruction components")

                    bin_code = "111" + COMP_TABLE[comp] + DEST_TABLE[dest] + JUMP_TABLE[jump]

                binary_output.append(bin_code)

            except Exception as e:
                if extra_feature_mode == 1:
                    print(f"Line {line_num}: invalid instruction ('{line}')")
                    sys.exit(1)
                else:
                    raise ValueError(f"Line {line_num}: invalid instruction '{line}' -> {e}")

        # Extra feature K mod 3 == 0: Save all labels and variables into symbols.txt
        if extra_feature_mode == 0:
            with open("symbols.txt", "w") as sym_file:
                for sym, addr in sorted(self.symbol_table.items(), key=lambda x: x[1]):
                    sym_file.write(f"{sym}: {addr}\n")

        return binary_output

def main():
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <filename.asm> [K_value]")
        sys.exit(1)

    filepath = sys.argv[1]
    K_val = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    assembler = Assembler(filepath, K=K_val)
    binary_lines = assembler.assemble()

    output_path = filepath.rsplit('.', 1)[0] + '.hack'
    with open(output_path, 'w') as out_f:
        out_f.write('\n'.join(binary_lines) + '\n')
    
    print(f"Successfully assembled {filepath} -> {output_path} (K mod 3 = {K_val % 3})")

if __name__ == "__main__":
    main()