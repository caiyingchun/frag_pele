import prody
import Bio.PDB as bio
import logging
import numpy as np
import sys

# Getting the name of the module for the log system
logger = logging.getLogger(__name__)


def get_ligand_from_PDB(pdb_file):
    """
    :param pdb_file: PDB file with only the ligand
    :return: Bio.PDB object of the input PDB
    """
    parser = bio.PDBParser()
    structure = parser.get_structure("structure", pdb_file)
    return structure


def get_atoms_from_structure(structure):
    """
    :param structure: Bio.PDB object of the input PDB
    :return: list with the atoms that form the input structure
    """
    atom_list = []
    for atom in structure.get_atoms():
        atom_list.append(atom)
    return atom_list


def select_atoms_from_list(PDB_atom_name, atoms_list):
    for atom in atoms_list:
        if atom.name == PDB_atom_name:
            return atom


def get_H_bonded_to_grow(PDB_atom_name, prody_complex):
    # Select the hydrogens bonded to the heavy atom 'PDB_atom_name'
    selected_h = prody_complex.select("chain L and hydrogen within 1.5 of name {}".format(PDB_atom_name))
    # In case that we found more than one we have to select one of them
    if len(selected_h) > 1:
        for idx, hydrogen in enumerate(selected_h):
            # We will select atoms of the protein in interaction distance
            select_h_bonds = prody_complex.select("protein and within 2.5 of (name {} and chain L)"
                                                  .format(selected_h.getNames()[idx]))
            if select_h_bonds is not None:
                logger.warning("WARNING: {} is forming a close interaction with the protein! We will try to grow"
                               "in another direction.".format(selected_h.getNames()[idx]))
            # We put this elif to select one of H randomly if all of them have contacts
            elif (select_h_bonds is not None) and (idx == len(selected_h) -1):
                hydrogen_pdbatomname = selected_h.getNames()[0]
                return hydrogen_pdbatomname[0]
            else:
                hydrogen_pdbatomname = selected_h.getNames()[idx]
                return hydrogen_pdbatomname[0]

    else:
        hydrogen_pdbatomname = selected_h.getNames()
        return hydrogen_pdbatomname[0]


def superimpose(fixed_vector, moving_vector, moving_atom_list):
    """
    Rotates and translates a list of moving atoms from a moving vector to a fixed vector
    :param fixed_vector: vector used as reference
    :param moving_vector: vector that will rotate and translate
    :param moving_atom_list: list of atoms that we want to do the rotation and translation of the moving vector
    :return: the input list of atoms is rotated an translated
    """
    sup = bio.Superimposer()
    sup.set_atoms(fixed_vector, moving_vector)
    return sup.apply(moving_atom_list)


def transform_coords(atoms_with_coords):
    """
    Transform the coords of a molecule (prody selection) into the coords from a list of atoms of Bio.PDB.
    :param atoms_with_coords: list of atoms (from a Bio.PDB) with the coordinates that we want to set.
    :param molecule_to_transform: prody selection with the molecule that we want to replace their coords.
    :return: perform the transformation of the coords.
    """
    coords = []
    for atom in atoms_with_coords:
        coords.append(list(atom.get_coord()))
    return np.asarray(coords)