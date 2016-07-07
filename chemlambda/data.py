
# modified to run on VS Code IDE 
# modifier: Yuvaraj Athur
# email   : yuvaraj.a.r@gmail.com
# date    : Tue 24 May 2016 
# touch   : Thu 07 Jul 2016
# ver    :


import topology
import settings
from collections import Counter
from string import Template
import random
import string
import json

class ChemCounter:
    """
    Various (unnecessary) Counters
    """
    def __init__(self):
        self._reset()

    def update(self, ds):
        # per atom counter
        # per port counter
        self.total_move_count = ds.dict_moves.__len_()

    def _reset(self):
        self.cycle_count = 0  # intial visualisation = cycle 0
        self.total_move_count = 0
        self.atom_count = 0
        self.port_count = 0
        self.move_count = 0

        # move counts
        self.total_moves_count = Counter({})


class ChemlambdaDicts:
    """"""
    def __init__(self):
        self._reset()

    def _take_snapshot(self, curr_cycle):
        """
        Combines, compress and saves the dicitonary of atoms and ports as a
        snapshot of the current cycle.
        Returns None
        """
        d = self.mega_atoms_list[curr_cycle] = {}
        d.update(self.dict_atoms)
        d.update(self.dict_ports)
        for k, atom in d.items():
            d[k] = atom._deflate()

    def _get_snapshot(self, cycle):
        """
        Retrives combined dict snapshot for cycle
        and inflate it.
        Returns Atom_dict
        """
        d = self.mega_atoms_list[cycle]
        d_new = {}
        for k, atom in d.items():
            d_new[k] = atom._inflate(d)
        return d_new

    def _reset(self):
        """Empties every variables"""
        self.mega_atoms_list = {}  # snapshot of atoms and ports for cycles
        self.moves_list = {}
        self.dict_atoms = {}
        self.dict_ports = {}
        self.atoms_taken = []

    def _write_to_mol_file(self, cycle, file_name):
        """Fetches a cycle snapshot from mega_atoms_list and writes it"""
        used_port_name = set(['abc'])
        def create_pn(used_port_name):
            port_name = 'abc'
            pn_len = 3
            i = 0
            if port_name in used_port_name:
                while port_name not in used_port_name:
                    if i > 10:
                        pn_len += 1
                    port_name = ''.join([random.choice(string.ascii_lowercase)
                                         for i in range(pn_len)])
                    i += 1
            used_port_name.add(port_name)
            return port_name

        pn_dict = {}

        def write_pn(p):
            """write port_name for port p and it's target"""
            return p

# priority low
        lines = []
        d_c = self._get_snapshot(cycle)
        d_p = {k:v for k, v in d_c.item()
                if v.atom in ['mo', 'mi', 'ro', 'ri', 'lo', 'li', 'fo', 'fi'] }
        #for k, v in d_p.items():

        used_port_name.add(port_name)


class GenerateMoves:    
    """
    Wrapper to generate d3 fragments 
    and manage file io
    """
    def __init__(self):
        self._reset()

    def _reset(self):
        self.generate = False
        self.out_file = None


    def start(self,out_file):
        self.generate = True
        self.out_file = out_file
        self._clear_temp_files()

    def _clear_temp_files(self):
        """
        temp files have fragments of generated code
        for each generation cycle 
        """
        #delete temp files of previous runs if any
        open(settings.graph_temp,'w').close()
        open(settings.force_temp,'w').close()
        open(settings.button_temp,'w').close()

    def add(self,d_a, cycle_count):
        """ sets up the nodes in the graph
        {
        "nodes": [{'atom': uid, 'size': size, 'color': color}, ......],
        "links": [{'source': s#, 'target': t#}, ...]
        }
        """
        if(not self.generate):
            return

        node_list = [{'atom': v.uid,
                    'size': v._get_size()*settings.atom_scale_factor,
                    'color': v._get_color()} for k, v in d_a.items()]
        node_list_search = [d['atom'] for d in node_list]


        link_list = []
        for i, nl_d in enumerate(node_list):
            [link_list.append({'source': i,
                            'target': node_list_search.index(t)})
            for t in d_a[nl_d['atom']].targets]

        # graph nodes & links fragment     
        jsh = '<script type="application/json" id="mis'+ str(cycle_count)+'"> \n'     
        js = jsh + json.dumps({"nodes": node_list, "links": link_list}, indent=4)
        js += "\n</script> \n"

        with open(settings.graph_temp,'a') as fp:
            fp.write(js)
            fp.close()

        #button to show  generation step fragment    
        b_data = '\n<button onclick="turnForceOn('+'graph'+str(cycle_count)+')">Move '+str(cycle_count)+'</button>'
        with open(settings.button_temp,'a') as fp:
            fp.write(b_data)
            fp.close

        #reset d3, force, svg fragment    
        js_data = "var mis"+str(cycle_count)+" = document.getElementById('mis"+str(cycle_count)+"').innerHTML; \n"
        js_data += "graph"+str(cycle_count)+" = JSON.parse(mis"+str(cycle_count)+"); \n"

        with open(settings.force_temp,'a') as fp:
            fp.write (js_data)
            fp.close()

    def finalize(self):
        """
        format the output file based on Template
        use previous dumps to write the final output
        """
        if(not self.generate):
            return

        # read template files
        with open(settings.html_temp, 'r') as fp:
            html_data = fp.read()

        # read previous generation runs
        with open(settings.graph_temp,'r') as fp:
            js = fp.read()

        with open(settings.button_temp,'r') as fp:
            b_data = fp.read()
                
        with open(settings.force_temp,'r') as fp:
            js_data = fp.read()


        output = Template(html_data)
        outdata = output.substitute(json_dump=js,button_dump=b_data ,javascript_dump=js_data)

        with open(self.out_file, 'w') as fp:
                    fp.write(outdata)
                    fp.close()
