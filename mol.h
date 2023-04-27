#ifndef _myheader_h
#define _myheader_h

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#define M_PI 3.141592653589793238462643383279502884

typedef struct atom
{
char element[3]; //null terminated string representing the atom's name
double x, y, z; //floating point numbers representing the position of the atoms
} atom;

typedef struct bond
{
unsigned short a1, a2; //indices of the two atoms in the array with address atoms
unsigned char epairs; //number of electron pairs in the bond
atom *atoms; // the array of atom pointers
double x1, x2, y1, y2, z, len, dx, dy; //x1 and y1 are the x and y coordinates of the first atom, same for second.
// z stores the average z value of the two atoms. len stores the distance between the two atoms. dx and dy stores the difference in x and y values between a2 and a1 divided by the length of the bond.
} bond;

typedef struct molecule //molecule which has zero or more atoms and zero or more bonds
{
unsigned short atom_max, atom_no; //atom_max is never negative and represents the dimentionality of the array while atom_no is the number of atoms currently stored in the array
atom *atoms, **atom_ptrs; //atom_ptrs and bond_ptrs are arrays of pointers
unsigned short bond_max, bond_no; //same as for atom_max and atom_no
bond *bonds, **bond_ptrs;
} molecule;

typedef double xform_matrix[3][3];

typedef struct mx_wrapper
{
  xform_matrix xform_matrix;
} mx_wrapper;

void atomset (atom *atom, char element[3], double *x, double *y, double *z);
void atomget (atom *atom, char element[3], double *x, double *y, double *z);
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs );
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs );
void compute_coords( bond *bond );
molecule *molmalloc (unsigned short atom_max, unsigned short bond_max);
molecule *molcopy (molecule *src);
void molfree (molecule *ptr);
void molappend_atom (molecule *molecule, atom *atom);
void molappend_bond (molecule *molecule, bond *bond);
void molsort (molecule *molecule);
void xrotation (xform_matrix xform_matrix, unsigned short deg);
void yrotation (xform_matrix xform_matrix, unsigned short deg);
void zrotation (xform_matrix xform_matrix, unsigned short deg);
void mol_xform (molecule *molecule, xform_matrix matrix);
int atomcmp (const void *a, const void *b);
int bondcmp (const void *a, const void *b);

/*typedef struct rotations
{
  molecule *x[72];
  molecule *y[72];
  molecule *z[72];
} rotations;

rotations *spin( molecule *mol );
void rotationsfree( rotations *rotations );*/

#endif
