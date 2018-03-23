import os
import sys
import json
import urllib.request
from rdkit import Chem

from pdbeccdutils.core import structure_reader


class PubChemDownloader:
    """Toolkit to retrieve pubchem 2D depictions from the
    """

    def __init__(self, components, pubchem_templates):
        self.components = components
        self.pubchem_templates = pubchem_templates
        self.blacklist = list()

    def run(self):
        """Update 2d images of pdbechem components which are available in the pubchem database
        """

        print('Querying pubchem database...')
        downloaded = self._download()
        print('Downloaded {} new structures.'.format(downloaded))

    def _download(self):
        """
        Downloads 2D structures of the components and returns a number of new structures
        """
        counter = 0
        i = 0
        for file in os.listdir(self.components):
            id = os.path.basename(file).split('.')[0]
            destination = os.path.join(self.pubchem_templates, id + '.sdf')
            counter += 1
            print('{} | new {}'.format(counter, i), end='\r')

            if os.path.isfile(destination):
                continue
            inchikey = structure_reader.read_pdb_cif_file(os.path.join(self.components, file)).component.inchikey

            try:
                inchi_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/{}/cids/json'.format(inchikey)
                response = urllib.request.urlopen(inchi_url).read().decode('utf-8')
                jsonFile = json.loads(response)
                cid = jsonFile['IdentifierList']['CID'][0]

                structure_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/record/SDF/?record_type=2d&response_type=save&response_basename={}'.format(cid, id + '.sdf')
                urllib.request.urlretrieve(structure_url, destination)
                i += 1
            except urllib.request.HTTPError:
                pass
            except urllib.error.URLError:
                pass
        return i


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='PDBe downloader of pubchem depictions')
    parser.add_argument('-components', type=str, help='Path to the component library', required=True)
    parser.add_argument('-pubchem_templates', type=str, help='Path to the pubchem templates.', required=True)

    config = parser.parse_args()
    PubChemDownloader(config.components, config.pubchem_templates).run()
