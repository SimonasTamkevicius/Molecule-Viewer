import molecule

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">\n"""

footer = """</svg>"""

offsetx = 500
offsety = 500

# atom class that creates an atom object and returns a string in svg format for the atom
class Atom:
    def __init__(self, c_atom):
        self.c_atom = c_atom
        self.z = c_atom.z

    def __str__(self):
        return '''%f'%f'%f''' % (self.c_atom.x, self.c_atom.y, self.z)
    
    def svg (self):
        x_circle = self.c_atom.x * 100 + offsetx
        y_circle = self.c_atom.y * 100 + offsety
        circle_radius = 0.0
        circle_colour = ""

        circle_radius = radius.get(self.c_atom.element, 0)
        circle_colour = element_name.get(self.c_atom.element, "")

        return ' <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (x_circle, y_circle, circle_radius, circle_colour)

# bond class which creates a bond object and return a string in svg format for the bond
class Bond:
    def __init__(self, c_bond):
        self.c_bond = c_bond
        self.z = c_bond.z
    
    def __str__(self):
        return '''%d'%d'%c'%f'%f'%f'%f'%f'%f'%f'%f''' % (self.c_bond.a1, self.c_bond.a2, self.c_bond.epairs, self.c_bond.x1, self.c_bond.x2, self.c_bond.y1, self.c_bond.y2, self.z, self.c_bond.len, self.c_bond.dx, self.c_bond.dy)

    def svg(self):
        p1 = (100 * self.c_bond.x1 + offsetx) - (self.c_bond.dy * 10)
        p2 = (100 * self.c_bond.y1 + offsety) + (self.c_bond.dx * 10)
        p3 = (100 * self.c_bond.x1 + offsetx) + (self.c_bond.dy * 10)
        p4 = (100 * self.c_bond.y1 + offsety) - (self.c_bond.dx * 10)
        p5 = (100 * self.c_bond.x2 + offsetx) + (self.c_bond.dy * 10)
        p6 = (100 * self.c_bond.y2 + offsety) - (self.c_bond.dx * 10)
        p7 = (100 * self.c_bond.x2 + offsetx) - (self.c_bond.dy * 10)
        p8 = (100 * self.c_bond.y2 + offsety) + (self.c_bond.dx * 10)
        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (p1, p2, p3, p4, p5, p6, p7, p8)

# molecule subclass which returns a string in svg format of the molecule
class Molecule (molecule.molecule):
    def __init__(self):
        super().__init__()

    def __str__(self):
        a1 = Atom (self.get_atom(1))
        return '''%f''' %(a1.z)
    
    def svg(self):

        result = []
        i = j = 0
        while i < self.atom_no and j < self.bond_no:
            a1 = Atom (self.get_atom(i))
            b1 = Bond (self.get_bond(j))
            if a1.z < b1.z:
                result.append(a1.svg())
                i += 1
            else:
                result.append(b1.svg())
                j += 1
        while i < self.atom_no:
            a1 = Atom (self.get_atom(i))
            result.append(a1.svg())
            i += 1
        while j < self.bond_no:
            b1 = Bond (self.get_bond(j))
            result.append(b1.svg())
            j += 1

        string = ''.join (result)

        
        return header + string + footer

    def parse(self, file_obj):
        file_obj.readline()
        file_obj.readline()
        file_obj.readline()

        num_data = file_obj.readline().split()
        num_atoms = int(num_data[0])
        num_bonds = int(num_data[1])

        for i in range(num_atoms):
            atom_data = file_obj.readline().split()
            x = float (atom_data[0])
            y = float (atom_data[1])
            z = float (atom_data[2])
            element = str (atom_data[3])
            self.append_atom (element, x, y, z)

        for i in range(num_bonds):
            bond_data = file_obj.readline().split()
            atom1_idx = int (bond_data[0]) - 1
            atom2_idx = int (bond_data[1]) - 1
            bond_type = int (bond_data[2])

            self.append_bond(atom1_idx, atom2_idx, bond_type)

if __name__ == "__main__":
    with open('water.sdf') as file:
        mol = Molecule()
        mol.parse(file)
        mol.sort()
        print(mol.svg())
