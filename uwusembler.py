'''*******************************************************************************
 * Name          : uwusembler.py
 * Author        : John Graham & Emma Hodor
 * Pledge        : I pledge my honor that I have abided by the Stevens Honor System.
 * Date          : 12/05/22
 * Description   : Assembles a program.txt file according to the uwusembly language.
 ******************************************************************************'''

import os

def extend(str, n):
    '''extends a string with 0's so that it is of n length'''
    while(len(str)<n):
        str="0"+str
    return str

labels={}
current_address=0x00

def instruction(instr):
    '''sets the machine code for instructions instructions'''
    machine_code=0b00000000000000000000000000000000 #32-bit instructions

    mnemonic=instr[1] #mnemonic is at the 2nd position in instr list
    if mnemonic=="add":
        machine_code+=0b000<<7 #Op = 000 = ADD
        machine_code+=0b1<<31 #Write
    elif mnemonic=="sub":
        machine_code+=0b001<<7 #Op = 001 = SUB
        machine_code+=0b1<<31 #Write
    elif mnemonic=="mul":
        machine_code+=0b010<<7 #Op = 010 = MUL
        machine_code+=0b1<<31 #Write
    elif mnemonic=="div":
        machine_code+=0b011<<7 #Op = 011 = DIV
        machine_code+=0b1<<31 #Write
    elif mnemonic=="load":
        machine_code+=0b1<<6 #MemR
        machine_code+=0b1<<31 #Write
    elif mnemonic=="store":
        machine_code+=0b1<<5 #MemW
    elif mnemonic=="and":
        machine_code+=0b100<<7 #Op = 100 = AND
        machine_code+=0b1<<31 #Write
    elif mnemonic=="or":
        machine_code+=0b101<<7 #Op = 101 = ORR
        machine_code+=0b1<<31 #Write
    elif mnemonic=="not":
        machine_code+=0b110<<7 #Op = 110 = NOT
        machine_code+=0b1<<31 #Write
    elif mnemonic=="xor":
        machine_code+=0b111<<7 #Op = 111 = XOR
        machine_code+=0b1<<31 #Write
    elif mnemonic=="move":
        machine_code+=0b1<<31 #Write
    elif mnemonic=="print":
        machine_code+=0b1<<4 #print
    elif mnemonic=="jump":
        machine_code+=0b1<<3 #jump
    elif mnemonic=="zero":
        machine_code+=0b1<<3 #jump
        machine_code+=0b1<<2 #compare


    dst=instr[0] #dst is at the 1st position in instr list
    if(mnemonic=="store"):
        machine_code+=int(dst[1])<<15 #setting first register as the source to be written to memory (RegData2) (instead of a destination to be written to)
    elif(mnemonic=="print"):
        if(dst[0]=='u'):
            machine_code+=int(dst[1])<<24
        else:
            machine_code+=0b1<<27 #imm1
            machine_code+=int(dst)<<19
        return machine_code #no other processing needed for print
    elif(mnemonic=="jump" or mnemonic=="zero"):
        machine_code+=0b1<<27 #imm1
        machine_code+=labels[dst]<<19
        if(mnemonic=="jump"):
            return machine_code
    else:
        machine_code+=int(dst[1])<<28

    src1=instr[2]
    if(src1[0]=='u'):
        if(mnemonic=="zero"):
            machine_code+=int(src1[1])<<15
            return machine_code #no other processing needed for this instruction
        else:
            machine_code+=int(src1[1])<<24
    else:
        machine_code+=0b1<<27 #imm1
        machine_code+=int(src1)<<19

    if(mnemonic=="move"): #no third arg for moving
        machine_code+=0b1<<18 #imm2 (will be 0, so that ALUout is just the move value)
        return machine_code
    elif(mnemonic=="load" or mnemonic=="store" or mnemonic=="not" or mnemonic=="zero"): #no third arg for these instructions
        return machine_code

    src2=instr[3]
    if(src2[0]=='u'):
        machine_code+=int(src2[1])<<15
    else:
        machine_code+=0b1<<18 #imm2
        machine_code+=int(src2)<<10

    return machine_code
    

if __name__=="__main__":
    if os.path.exists("instr"): #removes any current instr image file, if one exists
        os.remove("instr")
    if os.path.exists("data"): #removes any current data image file, if one exists
        os.remove("data")
    
    program=open("program.txt", 'r') #reading from the program

    instructions=open("instr", 'w') #writing to a new instr file (will overwrite any current instr file)
    instructions.write("v3.0 hex words addressed\n") #header
    data_write=False #no .data segment needed yet

    address_line=0x00 #for labeling each address line in the instr file
    instructions.write((hex(address_line))[2:]+"0: ")

    data_address_line=0x00 #for labeling each address line in the data file

    counter=0 #counts the number of entries in each line for the instr file
    data_counter=0 #counts the number of entries in each line for the data file

    program_check=open("program.txt", 'r')
    for line in program_check:
        if(line=="" or line=="\n" or line.startswith(".text") or line.startswith("//")):
            continue #nothing to process for empty lines
        if "//" in line: #removes comments
            line=line[:line.find("//")]
        instr=line.split() #makes a list of all items in the instruction (removes whitespace and makes it easier to process)
        if(len(instr)>1 and instr[1]=="label"):
            machine_code=0b0
            labels[instr[0]]=current_address
        current_address+=0x1


    for line in program: #runs for every line in the program.txt file
        line=" ".join(line.split()) #removes duplicate whitespace
        if(line=="" or line=="\n" or line.startswith(".text") or line.startswith("//")):
            continue #no instruction/data to process for this line
        elif(line.startswith(".data")): #start of the data segment, so we start writing to new data file
            data=open("data", 'w')
            data.write("v3.0 hex words addressed\n")
            data.write((hex(data_address_line))[2:]+"0: ")
            data_write=True #for processing each data provided, and filling the data file
            continue #no instruction/data to process for this line

        if "//" in line: #removes comments
            line=line[:line.find("//")]
        
        if(data_write): #runs if we have a .data segment
            data.write(extend(hex(int(line))[2:], 2)+" ")
            data_counter+=1
            if(data_counter==16): #we need to start a new line in the data file
                data_counter=0
                data.write('\n')
                data_address_line+=0x10 #adjusting address label
                if(data_address_line>0xf0): #end of file
                    break
                data.write(hex(data_address_line)[:2]+": ") #write new address label
            continue #continue bc we have finished processing data, no instruction to process

        instr=line.split() #makes a list of all items in the instruction (removes whitespace and makes it easier to process)
        if instr[1]=="label":
            machine_code=0b0
        else:
            machine_code=instruction(instr) #setting the machine code!
        
        instructions.write((extend(hex(machine_code)[2:], 8))+" ") #writes hex version of the machine code to the file (with proper format)
        counter+=1
        if counter==8: #we need to start a new line in the instr file
            counter=0
            instructions.write("\n")
            address_line+=0x08 #adjusting the address label
            if address_line>0xf8: #end of file
                break
            instructions.write(extend(hex(address_line)[2:], 2)+": ") #write new address label
    

    while(True): #fills out the rest of the instr file with 0's, according to the required format
        instructions.write("00000000 ")
        counter+=1
        if counter==8:
            counter=0
            instructions.write("\n")
            address_line+=0x08
            if address_line>0xf8:
                break
            instructions.write(extend(hex(address_line)[2:], 2)+": ")
    
    while(True and data_write): #fills out the rest of the data file with 0's, according to the required format (if we have a data file)
        data.write("00 ")
        data_counter+=1
        if data_counter==16:
            data_counter=0
            data.write("\n")
            data_address_line+=0x10
            if data_address_line>0xf0:
                break
            data.write((hex(data_address_line))[2:]+": ")
    
    program.close() #close all of the files
    program_check.close()
    instructions.close()
    if data_write:
        data.close()