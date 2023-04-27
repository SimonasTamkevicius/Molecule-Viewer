from http.server import HTTPServer, BaseHTTPRequestHandler;

import sys;     # to get command line argument for port
import urllib;  # code to parse for data

import molsql;
import MolDisplay
import io
import json

# list of files that we allow the web-server to serve to clients
# (we don't want to serve any file that the client requests)
public_files = ['/home.html', '/elements.html', '/molname.html', '/upload_sdf.html', '/selectmol.html', '/A4CSS.css', '/A4JAVASCRIPT.js'];
x = 0
y = 0
z = 0

db = molsql.Database(reset=False)

class MyHandler( BaseHTTPRequestHandler ):
    def do_GET(self):
        global db
        if self.path == '/selectmol.html':
            result = db.conn.execute ("SELECT NAME FROM Molecules")
            names = result.fetchall()
            form_html = '<form id="select-form" method="post">'
            form_html += '<select id="molecule-select" name="molecule-select">'
            form_html += '<option>Select Option</option>'
            for molecule in names:
                mol = db.load_mol(molecule[0]);
                atom_num = mol.atom_no
                bond_num = mol.bond_no
                option_text = '{} ({} Atoms, {} Bonds)'.format(molecule[0], atom_num, bond_num)
                form_html += '<option value="{}" name="{}">{}</option>'.format(molecule[0], molecule[0], option_text)

            form_html += '</select>'
            form_html += '</form>'


            fp = open ('selectmol.html')
            page = fp.read()
            fp.close()         

            page = page.replace('{{form}}', form_html)

            # Send the HTML response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(page.encode('utf-8'))

        elif self.path == '/elements.html':
            self.send_response( 200 );  # OK
            self.send_header( "Content-type", "text/html" );
            result = db.conn.execute ("SELECT ELEMENT_CODE FROM Elements")
            names = result.fetchall()

            form_html = '<menu>'
            for element in names:
                mol = db.load_mol(element[0]);
                option_text = '{}'.format(element[0])
                form_html += '<li value="{}" name="{}">{},</li>'.format(element[0], element[0], option_text)

            form_html += '</menu>'


            fp = open ('elements.html')
            page = fp.read()
            fp.close()         

            page = page.replace('{{form}}', form_html)

            # Send the HTML response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(page.encode('utf-8'))

        elif self.path in public_files:   # make sure it's a valid file
            self.send_response( 200 );  # OK
            self.send_header( "Content-type", "text/html" );

            fp = open( self.path[1:] ); 
            # [1:] to remove leading / so that file is found in current dir

            # load the specified file
            page = fp.read();
            fp.close();

            # create and send headers
            self.send_header( "Content-length", len(page) );
            self.end_headers();

            # send the contents
            self.wfile.write( bytes( page, "utf-8" ) );

        else:
            # if the requested URL is not one of the public_files
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );

    def do_POST(self):
        global db
        if self.path == "/upload-sdf":
            length = int(self.headers.get('Content-Length', 0))
            file_obj = io.TextIOWrapper(io.BytesIO(self.rfile.read(length)))
            file_obj.readline()
            file_obj.readline()
            file_obj.readline()
            file_obj.readline()

            db.add_molecule('Temp', file_obj)

            self.send_response(302)
            self.send_header('Location', 'molname.html')
            self.end_headers()

        
        elif self.path == "/element-add":
            content_length = int(self.headers.get('Content-Length', 0));
            post_data = self.rfile.read(content_length)

            # Parse form data from the request body
            parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            element_number = parsed_data.get('element_number', [''])[0]
            element_code = parsed_data.get('element_code', [''])[0]
            element_name = parsed_data.get('element_name', [''])[0]
            color1 = parsed_data.get('color1', [''])[0].upper()
            color2 = parsed_data.get('color2', [''])[0].upper()
            color3 = parsed_data.get('color3', [''])[0].upper()
            radius = parsed_data.get('radius', [''])[0]

            db['Elements'] = (element_number, element_code, element_name, color1[1:], color2[1:], color3[1:], radius)
            db.conn.execute("DELETE FROM Elements WHERE ELEMENT_CODE=''")
            db.conn.commit()

            self.send_response(302)
            self.send_header('Location', 'elements.html')
            self.end_headers()
        
        elif self.path == "/element-remove":
            content_length = int(self.headers.get('Content-Length', 0));
            post_data = self.rfile.read(content_length)

            parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            element_code1 = parsed_data.get('element_code',[''])[0]

            db.conn.execute("DELETE FROM Elements WHERE ELEMENT_CODE=?", (element_code1,))
            db.conn.commit()

            self.send_response(302)
            self.send_header('Location', 'elements.html')
            self.end_headers()

        elif self.path == "/molecule-name-form":
            content_length = int(self.headers.get('Content-Length', 0));
            body = self.rfile.read(content_length);
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );
            print (content_length)
            
            molecule_name = postvars.get('molecule_name', [''])[0]
            print (molecule_name)

            db.conn.execute("UPDATE Molecules SET NAME=? WHERE NAME='Temp'", (molecule_name,))
            db.conn.commit()

            self.send_response(302)
            self.send_header('Location', 'upload_sdf.html')
            self.end_headers()

        elif self.path == "/molecule-select":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))
            molecule = postvars.get('molecule_selected', [''])[0]

            if molecule == "Select Option":
                response = {'svg': ""}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                MolDisplay.radius = db.radius()
                MolDisplay.element_name = db.element_name()
                MolDisplay.header += db.radial_gradients()

                mol = db.load_mol(molecule)
                mol.sort()
                svg_str = mol.svg()
                response = {'svg': svg_str}

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
        elif self.path == "/rotate-right":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))
            name = postvars.get('mol_name', [''])[0]

            import molecule
            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();
            MolDisplay.header += db.radial_gradients();
        
            mol = db.load_mol(name)

            global x, y, z

            x = 0
            y += 30

            if y != 0:
                mx = molecule.mx_wrapper(x, y, z)
                mol.xform( mx.xform_matrix )
            elif y == 360:
                y = 0

            mol.sort()
            svg_str = mol.svg()

            response = {'svg': svg_str}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == "/rotate-left":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))
            name = postvars.get('mol_name', [''])[0]

            import molecule
            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();
            MolDisplay.header += db.radial_gradients();
        
            mol = db.load_mol(name)

            x = 0
            y -= 30

            if y != 0:
                mx = molecule.mx_wrapper(x, y, z)
                mol.xform( mx.xform_matrix )
            elif y == 360:
                y = 0

            mol.sort()
            svg_str = mol.svg()

            response = {'svg': svg_str}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == "/rotate-up":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))
            name = postvars.get('mol_name', [''])[0]

            import molecule
            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();
            MolDisplay.header += db.radial_gradients();
        
            mol = db.load_mol(name)

            y = 0
            x += 30

            if x != 0:
                mx = molecule.mx_wrapper(x, y, z)
                mol.xform( mx.xform_matrix )
            elif x == 360:
                x = 0

            mol.sort()
            svg_str = mol.svg()

            response = {'svg': svg_str}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == "/rotate-down":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))
            name = postvars.get('mol_name', [''])[0]

            import molecule
            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();
            MolDisplay.header += db.radial_gradients();
        
            mol = db.load_mol(name)

            y = 0
            x -= 30

            if x != 0:
                mx = molecule.mx_wrapper(x, y, z)
                mol.xform( mx.xform_matrix )
            elif x == 360:
                x = 0

            mol.sort()
            svg_str = mol.svg()

            response = {'svg': svg_str}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );





httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );
httpd.serve_forever();
