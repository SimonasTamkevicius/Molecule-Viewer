#include "mol.h"

// Sets the atom's name and x, y, and z values
void atomset (atom *atom, char element[3], double *x, double *y, double *z){
	strcpy (atom->element, element);
	atom->x = *x;
	atom->y = *y;
	atom->z = *z;
}

// Copies the values of the atom
void atomget (atom *atom, char element[3], double *x, double *y, double *z){
	strcpy (element, atom->element);
	*x = atom->x;
	*y = atom->y;
	*z = atom->z;
}

// Sets the bonds two atoms and the number of electorn pairs
void bondset (bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs){
	bond->a1 = *a1;
	bond->a2 = *a2;
	bond->epairs = *epairs;
	bond->atoms = *atoms;

	compute_coords (bond);
}

// Copies the values of the bond
void bondget (bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs){
	*epairs = bond->epairs;
	*a1 = bond->a1;
	*a2 = bond->a2;
	*atoms = bond->atoms;
}

// computes the required values for the bond structure
void compute_coords (bond *bond){
	bond->x1 = bond->atoms[bond->a1].x;
	bond->y1 = bond->atoms[bond->a1].y;
	bond->x2 = bond->atoms[bond->a2].x;
	bond->y2 = bond->atoms[bond->a2].y;

	bond->z = (double)(bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / (double)2;
	bond->len = sqrt (pow (bond->x2 - bond->x1, 2) + pow (bond->y2 - bond->y1, 2));
	bond->dx = (bond->x2 - bond->x1) / bond->len;
	bond->dy = (bond->y2 - bond->y1) / bond->len;
}

// Allocates memory for the molecule based on the atom_max, bond_max values
molecule *molmalloc (unsigned short atom_max, unsigned short bond_max){
	molecule *newMol = malloc (sizeof (molecule));
	if (newMol == NULL){
		free (newMol);
		fprintf (stderr, "%s", "Error allocating memory!\n");
		return NULL;
	}

	newMol->atom_max = atom_max;
	newMol->atom_no = 0;
	newMol->atoms = malloc (sizeof (struct atom) * atom_max);
	if (newMol->atoms == NULL){
		free (newMol);
		free (newMol->atoms);
		fprintf (stderr, "%s", "Error allocating memory!\n");
		return NULL;
	}
	newMol->atom_ptrs = malloc (sizeof (struct atom*) * atom_max);
	if (newMol->atom_ptrs == NULL){
		free (newMol);
		free (newMol->atoms);
		free (newMol->atom_ptrs);
		fprintf (stderr, "%s", "Error allocating memory!\n");
		return NULL;
	}

	newMol->bond_max = bond_max;
	newMol->bond_no = 0;
	newMol->bonds = malloc (sizeof (struct bond) * bond_max);
	if (newMol->bonds == NULL){
		free (newMol);
		free (newMol->atoms);
		free (newMol->atom_ptrs);
		free (newMol->bonds);
		fprintf (stderr, "%s", "Error allocating memory!\n");
		return NULL;
	}
	newMol->bond_ptrs = malloc (sizeof (struct bond*) * bond_max);
	if (newMol->bond_ptrs == NULL){
		free (newMol);
		free (newMol->atoms);
		free (newMol->atom_ptrs);
		free (newMol->bonds);
		free (newMol->bond_ptrs);
		fprintf (stderr, "%s", "Error allocating memory!\n");
		return NULL;
	}

	return newMol;
}

// Creates a copy of a molecule that is passed to this function
molecule *molcopy (molecule *src){
	molecule * copyMol = molmalloc (src->atom_max, src->bond_max);

	if (copyMol == NULL){
		free (copyMol);
		fprintf (stderr, "%s", "Error allocating memory!\n");
		return NULL;
	}

	atom tempAtom;
	for (int i = 0; i < src->atom_no; i++){
		tempAtom = src->atoms[i];
		molappend_atom (copyMol, &tempAtom);
	}

	bond tempBond;
	for (int i = 0; i < src->bond_no; i++){
		tempBond = src->bonds[i];
		tempBond.atoms = copyMol->atoms;
		molappend_bond (copyMol, &tempBond);
	}

	return copyMol;
}

// Frees all of the allocated memory
void molfree (molecule *ptr){
	free (ptr->atom_ptrs);
	free (ptr->bond_ptrs);
	free (ptr->atoms);
	free (ptr->bonds);
	free (ptr);
}

// Appends an atom to the molecule, reallocates memory if necessary
void molappend_atom (molecule *molecule, atom *atom) {
    if (molecule->atom_no == molecule->atom_max) {

        if (molecule->atom_max == 0) {
            molecule->atom_max = 1;
        } else {
            molecule->atom_max = molecule->atom_max * 2;
        }
		molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
		if (molecule->atoms == NULL){
			fprintf (stderr, "%s", "Error reallocating memory! Exiting...\n");
			exit (1);
		}

		molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);
		if (molecule->atom_ptrs == NULL){
			fprintf (stderr, "%s", "Error reallocating memory! Exiting...\n");
			free (molecule->atoms);
			exit (1);
		}
		for (int i = 0; i < molecule->atom_no; i++) {
			molecule->atom_ptrs[i] = &molecule->atoms[i];
		}
    }

    molecule->atoms[molecule->atom_no] = *atom;
    molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];
    molecule->atom_no++;
}

// Appends the bond to the molecule passed to the function and reallocates memory if necessary
void molappend_bond(molecule *molecule, bond *bond) {
	if (bond == NULL){
		fprintf (stderr, "%s", "Error, null pointer passed! Exiting...\n");
		exit (1);
	}

    if (molecule->bond_no == molecule->bond_max) {
        if (molecule->bond_max == 0) {
            molecule->bond_max = 1;
        } else {
            molecule->bond_max = molecule->bond_max * 2;
        }
		molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
		if (molecule->bonds == NULL){
			fprintf (stderr, "%s", "Error reallocating memory! Exiting...\n");
			exit (1);
		}

		molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);
		if (molecule->bond_ptrs == NULL){
			fprintf (stderr, "%s", "Error reallocating memory! Exiting...\n");
			free (molecule->bonds);
			exit (1);
		}

		for (int i = 0; i < molecule->bond_no; i++) {
			molecule->bond_ptrs[i] = &molecule->bonds[i];
		}
    }

    molecule->bonds[molecule->bond_no] = *bond;
    molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no];
    molecule->bond_no++;
}

// Compares two atoms and returns a number based on which has the larger z value
int atomcmp (const void *a, const void *b){
	atom *atom1 = *(atom **)a;
    atom *atom2 = *(atom **)b;
    return (atom1->z > atom2->z) - (atom1->z < atom2->z);
}

// Compares two bonds value and return which one is larger
int bondcmp (const void *a, const void *b){
	bond *bond1 = *(bond **)a;
    bond *bond2 = *(bond **)b;
    float b1_z = bond1->z;
    float b2_z = bond2->z;
    return (b1_z > b2_z) - (b1_z < b2_z);
}

// Sorts the atom_ptrs and bond_ptrs using the quicksort function and atomcmp and bondcmp
void molsort (molecule *molecule){
	qsort (molecule->atom_ptrs, molecule->atom_no, sizeof (atom*), atomcmp);
	qsort (molecule->bond_ptrs, molecule->bond_no, sizeof (bond*), bondcmp);
}

// Sets the values in the xform matrix according to the deg passed to the function
void xrotation (xform_matrix xform_matrix, unsigned short deg){
	double rad = deg * M_PI / 180.0;

	xform_matrix[0][0] = 1;
	xform_matrix[0][1] = 0;
	xform_matrix[0][2] = 0;
	xform_matrix[1][0] = 0;
	xform_matrix[1][1] = cos(rad);
	xform_matrix[1][2] = -sin(rad);
	xform_matrix[2][0] = 0;
	xform_matrix[2][1] = sin(rad);
	xform_matrix[2][2] = cos(rad);
}

// Sets the values in the xform matrix according to the deg passed to the function
void yrotation (xform_matrix xform_matrix, unsigned short deg){
	double rad = deg * M_PI / 180.0;

	xform_matrix[0][0] = cos(rad);
	xform_matrix[0][1] = 0;
	xform_matrix[0][2] = sin(rad);
	xform_matrix[1][0] = 0;
	xform_matrix[1][1] = 1;
	xform_matrix[1][2] = 0;
	xform_matrix[2][0] = -sin(rad);
	xform_matrix[2][1] = 0;
	xform_matrix[2][2] = cos(rad);
}

// Sets the values in the xform matrix according to the deg passed to the function
void zrotation (xform_matrix xform_matrix, unsigned short deg){
	double rad = deg * M_PI / 180.0;

	xform_matrix[0][0] = cos(rad);
	xform_matrix[0][1] = -sin(rad);
	xform_matrix[0][2] = 0;
	xform_matrix[1][0] = sin(rad);
	xform_matrix[1][1] = cos(rad);
	xform_matrix[1][2] = 0;
	xform_matrix[2][0] = 0;
	xform_matrix[2][1] = 0;
	xform_matrix[2][2] = 1;
}

// Applies the transformation matrix to the x, y, and z values of the atoms in the molecule
void mol_xform (molecule *molecule, xform_matrix matrix){
	for (int i = 0; i < molecule->atom_no; i++){
		double x, y, z;
		x = molecule->atoms[i].x;
		y = molecule->atoms[i].y;
		z = molecule->atoms[i].z;

		molecule->atoms[i].x = x * matrix[0][0] + y * matrix[0][1] + z * matrix[0][2];
		molecule->atoms[i].y = x * matrix[1][0] + y * matrix[1][1] + z * matrix[1][2];
		molecule->atoms[i].z = x * matrix[2][0] + y * matrix[2][1] + z * matrix[2][2];
	}
	for (int i = 0; i < molecule->bond_no; i++){
		compute_coords (&molecule->bonds[i]);
	}
}

int main (){
	
}