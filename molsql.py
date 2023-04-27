import sqlite3
import os
import MolDisplay

# Database class for interacting with the database
class Database:
    # Removes the database file if reset is true
    def __init__(self, reset=False):
        if reset == True:
            os.remove('molecules.db')

        self.conn = sqlite3.connect('molecules.db')
        self.curr = self.conn.cursor()

    def create_tables(self):
        # Creates Elements table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements
                              (ELEMENT_NO   INTEGER NOT NULL,
                               ELEMENT_CODE VARCHAR(3) NOT NULL,
                               ELEMENT_NAME VARCHAR(32) NOT NULL,
                               COLOUR1      CHAR(6) NOT NULL,
                               COLOUR2      CHAR(6) NOT NULL,
                               COLOUR3      CHAR(6) NOT NULL,
                               RADIUS       DECIMAL(3) NOT NULL,
                               PRIMARY KEY  (ELEMENT_CODE));""")
        self.conn.commit ()
        # Creates Atoms table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms
                              (ATOM_ID       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                               ELEMENT_CODE  VARCHAR(3) NOT NULL,
                               X             DECIMAL(7,4) NOT NULL,
                               Y             DECIMAL(7,4) NOT NULL,
                               Z             DECIMAL(7,4) NOT NULL,
                               FOREIGN KEY   (ELEMENT_CODE) REFERENCES Elements (ELEMENT_CODE));""")
        self.conn.commit ()
        # Creates Bonds table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Bonds
                              (BOND_ID       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                               A1            INTEGER NOT NULL,
                               A2            INTEGER NOT NULL,
                               EPAIRS        INTEGER NOT NULL);""")
        self.conn.commit ()
        # Creates Molecules table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Molecules
                              (MOLECULE_ID   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                               NAME          TEXT NOT NULL UNIQUE);""")
        self.conn.commit ()
        # Creates MoleculeAtom table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom
                              (MOLECULE_ID   INTEGER NOT NULL,
                               ATOM_ID       INTEGER NOT NULL,
                               PRIMARY KEY   (MOLECULE_ID, ATOM_ID),
                               FOREIGN KEY   (MOLECULE_ID) REFERENCES Molecules (MOLECULE_ID),
                               FOREIGN KEY   (ATOM_ID) REFERENCES Atoms (ATOM_ID));""")
        self.conn.commit ()
        # Creates MoleculeBond table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond
                              (MOLECULE_ID   INTEGER NOT NULL,
                               BOND_ID       INTEGER NOT NULL,
                               PRIMARY KEY   (MOLECULE_ID, BOND_ID),
                               FOREIGN KEY   (MOLECULE_ID) REFERENCES Molecules (MOLECULE_ID),
                               FOREIGN KEY   (BOND_ID) REFERENCES Bonds (BOND_ID));""")
        self.conn.commit()

# Sets the values in values into the table
    def __setitem__ (self, table, values):
        num_values = len(values)
        placeholders = ["?"] * num_values
        comma_separated_placeholders = ",".join(placeholders)

        temp = "(" + comma_separated_placeholders + ")"
        search = f"INSERT OR IGNORE INTO {table} VALUES {temp}"
        self.conn.execute(search, values)
        self.conn.commit()

# Adds an atom to the Atoms table and also adds the mol id and atom id to the MoleculeAtom table
    def add_atom(self, molname, atom):
        atom_data = (atom.c_atom.element, atom.c_atom.x, atom.c_atom.y, atom.c_atom.z)
        self.conn.execute("INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)", atom_data)
        self.conn.commit()
        result = self.conn.execute ("SELECT * FROM Atoms WHERE ATOM_ID = LAST_INSERT_ROWID()")
        atom_id = result.fetchone()[0]

        result = self.conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=?", (molname,))
        mol_id = result.fetchone()[0]

        self.conn.execute("INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID) VALUES (?, ?)",(mol_id, atom_id))
        self.conn.commit()

# Adds a bond to the Bonds table and also adds the mol id and bond id to the MoleculeBond table
    def add_bond(self, molname, bond):
        bond_data = (bond.c_bond.a1, bond.c_bond.a2, bond.c_bond.epairs)
        self.conn.execute("INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (?, ?, ?)", bond_data)
        self.conn.commit ()

        result = self.conn.execute ("SELECT * FROM Bonds WHERE BOND_ID = LAST_INSERT_ROWID()")
        bond_id = result.fetchone()[0]

        result = self.conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=?", (molname,))
        mol_id = result.fetchone()[0]

        self.conn.execute("INSERT INTO Moleculebond (MOLECULE_ID, BOND_ID) VALUES (?, ?)",(mol_id, bond_id))
        self.conn.commit()

# Adds the molecule from the file pointer into the Molecules table
    def add_molecule (self, name, fp):
        molecule = MolDisplay.Molecule ()
        molecule.parse(fp)

        self.curr.execute ("INSERT OR IGNORE INTO Molecules (NAME) VALUES (?)", (name,))

        if self.curr.rowcount != 0:
            for i in range (molecule.atom_no):
                atom_c = molecule.get_atom (i)
                atom = MolDisplay.Atom (atom_c)
                self.add_atom(name, atom)

            for i in range (molecule.bond_no):
                bond_c = molecule.get_bond (i)
                bond = MolDisplay.Bond (bond_c)
                self.add_bond (name, bond)
                
            self.conn.commit ()

# Appends the atoms and bonds associated with the given molecule name
    def load_mol(self, name):
        molecule = MolDisplay.Molecule()
        
        atom_query = """SELECT Atoms.ELEMENT_CODE, Atoms.X, Atoms.Y, Atoms.Z
                        FROM MoleculeAtom
                        JOIN Atoms ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID
                        JOIN Molecules ON MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID
                        WHERE Molecules.NAME = ?
                        ORDER BY Atoms.ATOM_ID ASC"""
        atoms = self.conn.execute(atom_query, (name,))
        for atom in atoms:
            molecule.append_atom(atom[0], atom[1], atom[2], atom[3])
        
        bond_query = """SELECT Bonds.A1, Bonds.A2, Bonds.EPAIRS
                        FROM BONDS 
                        JOIN MoleculeBond ON Bonds.BOND_ID = MoleculeBond.BOND_ID
                        JOIN Molecules ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                        WHERE Molecules.NAME = ? 
                        ORDER BY Bonds.BOND_ID ASC"""
        bonds = self.conn.execute(bond_query, (name,))
        for bond in bonds:
            a1, a2, epairs = bond[0], bond[1], bond[2]
            molecule.append_bond(a1, a2, epairs)
        
        return molecule

# Creates a radius dictionary that maps element codes to the radius
    def radius (self):
        radius_dict = {}
        elements = self.conn.execute ("SELECT ELEMENT_CODE FROM Elements ORDER BY ELEMENT_CODE")
        radius = self.conn.execute ("SELECT RADIUS FROM Elements ORDER BY ELEMENT_CODE")
        for element_code, radi in zip(elements, radius):
            radius_dict[element_code[0]] = radi[0]
        
        return radius_dict

# Creates an element name dictionary that maps the element codes to their element names
    def element_name (self):
        name_dict = {}
        element_codes = self.conn.execute ("SELECT ELEMENT_CODE FROM Elements ORDER BY ELEMENT_CODE")
        element_names = self.conn.execute ("SELECT ELEMENT_NAME FROM Elements ORDER BY ELEMENT_CODE")
        for element_code, element_name in zip(element_codes, element_names):
            name_dict[element_code[0]] = element_name[0]
        return name_dict

# Creates an svg string for the radial gradient
    def radial_gradients (self):
        elements = self.conn.execute ("SELECT * FROM Elements")
        string = ""
        for element in elements:
            string += """
<radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
  <stop offset="0%%" stop-color="#%s"/>
  <stop offset="50%%" stop-color="#%s"/>
  <stop offset="100%%" stop-color="#%s"/>
</radialGradient>""" %(element[2], element[3], element[4], element[5])
        return string


if __name__ == "__main__":
    db = Database(reset=True)
    db.create_tables()
    db['Elements'] = (1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25)
    db['Elements'] = (6, 'C', 'Carbon', '808080', '010101', '000000', 40)
    db['Elements'] = (7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40)
    db['Elements'] = (8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40)
    db['Elements'] = (16, 'S', 'Sulfur', '669C35', '96D35F', 'E0EDD4', 32)

    #db.conn.execute ("DELETE FROM Elements WHERE ELEMENT_CODE=?", ('H',))

    fp = open( 'water.sdf' );
    db.add_molecule( 'Water', fp );
    '''fp = open( 'caffeine.sdf' );
    db.add_molecule( 'Caffeine', fp );
    fp = open( 'CID_31260.sdf' );
    db.add_molecule( 'Isopentanol', fp );
    fp = open( 'benzene.sdf' )
    db.add_molecule( 'Benzene', fp )'''
    # display tables
    print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() );
    print ("\n");
    print( db.conn.execute( "SELECT * FROM Molecules;" ).fetchall() );
    print ("\n");
    print( db.conn.execute( "SELECT * FROM Atoms;" ).fetchall() );
    print ("\n");
    print( db.conn.execute( "SELECT * FROM Bonds;" ).fetchall() );
    print ("\n");
    print( db.conn.execute( "SELECT * FROM MoleculeAtom;" ).fetchall() );
    print ("\n");
    print( db.conn.execute( "SELECT * FROM MoleculeBond;" ).fetchall() );

    db = Database(reset=False); # or use default
    MolDisplay.radius = db.radius();
    MolDisplay.element_name = db.element_name();
    MolDisplay.header += db.radial_gradients();
    for molecule in [ 'Water', 'Caffeine', 'Isopentanol' 'Benzene']:
        mol = db.load_mol( molecule );
        mol.sort();
        fp = open( molecule + ".svg", "w" );
        fp.write( mol.svg() );
        fp.close();
