import prody
import pybel
import logging
import sys
import re

# Getting the name of the module for the log system
logger = logging.getLogger(__name__)

# Creation of a list of atoms
atoms = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
         "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br",
         "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I",
         "Xe", "Cs", "Ba", "La", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po",
         "At", "Rn", "Fr", "Ra", "Ac", "Rf", "Ha", "Sg"]

def read_smi(smi):
    """
    :param smi: smile format string.
    :return: pybel molecule with the information given by the smile.
    """
    smi_object = pybel.readstring("smi", smi)
    return smi_object


def list_of_atomicnum(molecule):
    """
    :param molecule: pybel molecule
    :return: list of tuples: (index, atomic number)
    """
    list_of_atoms = []
    for atom in molecule:
        list_of_atoms.append((atom.idx, atom.atomicnum))
    return list_of_atoms


def get_atomicnum(atom):
    """
    :param atom: string with the atomic name that we want to get their atomic number.
    Only compatible with smile format.
    :return: atomic number for the atom inserted.
    """
    atom_pybel = read_smi(atom)
    for atom in atom_pybel:
        return atom.atomicnum


def find_atomic_index(molecule_list, atomicnum, index):
    """
    :param molecule_list: list of tuples: (index, atomic number)
    :param atomicnum: atomic number that you want to select
    :param index: number of atom for a certain atomic number that we want to select of the molecule_list
    :return: index that correspond to this atomic number and the selected index
    """
    list_of_specific_atomicnum = []
    for atom in molecule_list:
        if atom[1] == atomicnum:
            list_of_specific_atomicnum.append(atom)
    return list_of_specific_atomicnum[index-1][0]


def smile_to_list(smile):
    """
    In this function we will transform a smile string to a list of atoms that will be ready to be joint again as a
    single string. We want this in order to find where to add the smile correspondent to the fragment.
    :param smile: string with the input smile that we want to transform into a list.
    :return: list with the different atoms of the smile.
    """
    smile_as_list = re.findall("\(*\=*\%*[A-z][1-9]*\)*", smile)
    counter = 1
    while counter < len(smile_as_list):
        if smile_as_list[counter-1]+smile_as_list[counter] in atoms:
            smile_as_list[counter - 1] = smile_as_list[counter-1]+smile_as_list[counter]
            del smile_as_list[counter]
            counter += 1
        else:
            counter += 1
    return smile_as_list


def check_smile_len(list_of_atomicnum, smile_list):
    """
    :param list_of_atomicnum: list of tuples: (index, atomic number) of a molecule
    :param smile_list: list with the different atoms of the smile
    :return: if the lengths are not equal, a critical error will raise.
    """
    if len(list_of_atomicnum) != len(smile_list):
        logger.critical("Something went wrong in the transformation from smile to list! The length does not match!")


def add_fragment(fragment_smile, core_smile_list, where):
    """
    :param fragment_smile:
    :param core_smile_list:
    :param where:
    :return:
    """
    core_smile_list[where-1] = core_smile_list[where-1] + "({})".format(fragment_smile)
    return "".join(core_smile_list)
