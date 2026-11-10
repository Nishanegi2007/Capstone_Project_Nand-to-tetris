
// Box.asm
// K = 15
// Starting row = 15
// Height = 20 rows
// Width = 64 pixels (4 words)

// Check keyboard
(LOOP)
@KBD
D=M
@DRAW
D;JGT

// CLEAR BOX
@SCREEN
D=A
@480
D=D+A
@addr
M=D

@20
D=A
@n
M=D

(CLEAR)
@addr
A=M
M=0

// Clear word 2
@addr
A=M
A=A+1
M=0

// Clear word 3
@addr
A=M
A=A+1
A=A+1
M=0

// Clear word 4
@addr
A=M
A=A+1
A=A+1
A=A+1
M=0

// Next row
@addr
D=M
@32
D=D+A
@addr
M=D

@n
MD=M-1
@CLEAR
D;JGT

@LOOP
0;JMP

// DRAW BLACK BOX
(DRAW)
@SCREEN
D=A
@480
D=D+A
@addr
M=D

@20
D=A
@n
M=D

(FILL)
@addr
A=M
M=-1

// Draw word 2
@addr
A=M
A=A+1
M=-1

// Draw word 3
@addr
A=M
A=A+1
A=A+1
M=-1

// Draw word 4
@addr
A=M
A=A+1
A=A+1
A=A+1
M=-1

// Next row
@addr
D=M
@32
D=D+A
@addr
M=D

@n
MD=M-1
@FILL
D;JGT

@LOOP
0;JMP
