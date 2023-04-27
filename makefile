CC = clang
CFLAGS = -Wall -std=c99 -pedantic

all: a3 mol.o libmol.so molecule_wrap.o _molecule.so

mol.o:  mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so

molecule_wrap.c molecule.py: molecule.i
	swig -python molecule.i

molecule_wrap.o: molecule_wrap.c
	$(CC) -c -fPIC -I/Library/Frameworks/Python.framework/Versions/3.10/include/python3.10/ molecule_wrap.c -o molecule_wrap.o

_molecule.so: molecule_wrap.o
	$(CC) -shared molecule_wrap.o -o _molecule.so -L/Users/simonastamkevicius/Desktop/CIS2750/A2 -L/Library/Frameworks/Python.framework/Versions/3.10/lib -lpython3.10 -lmol -dynamiclib

a3: libmol.so
	$(CC) -L. -lm -lmol -o a3

clean:
	rm -f *.o *.so a3