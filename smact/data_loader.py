################################################################################
#  Copyright J. M. Sketon, D. W. Davies (2016)                                 #
#                                                                              #
#  This file is part of SMACT: smact.__init__ is free software: you can        #
#  redistribute it and/or modify it under the terms of the GNU General Public  #
#  License as published by the Free Software Foundation, either version 3 of   #
#  the License, or (at your option) any later version.                         #
#  This program is distributed in the hope that it will be useful, but WITHOUT #
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for   #
#  more details.                                                               #
#  You should have received a copy of the GNU General Public License along with#
#  this program.  If not, see <http://www.gnu.org/licenses/>.                  #
################################################################################

"""
This module handles the loading of external data used to initialise the core smact.Element and smact.Species classes.
It implements a transparent data-caching system to avoid a large amount of I/O when naively constructing several of these objects.
It also implements a switchable system to print verbose warning messages about possible missing data (mainly for debugging purposes).
"""


import csv;
import os;

from smact import data_directory;


# Module-level switch for printing "verbose" warning messages about missing data.

_PrintWarnings = False;

def ToggleWarnings(enable):
    """
    Toggles verbose warning messages on and off.
    ** In order to see any of the warnings, this function needs to be called _before_ the first call to the smact.Element() constructor. **
    
    Args:
        enable : print verbose warning messages.
    """
    
    global _PrintWarnings;
    
    _PrintWarnings = enable;


# Loader and cache for the element oxidation-state data.

_ElementOxidationStates = None;

def LookupElementOxidationStates(symbol, copy = True):
    """
    Retrieve a list of known oxidation states for an element.
    
    Args:
        symbol : the atomic symbol of the element to look up.
        copy : if True (default), return a copy of the oxidation-state list, rather than a reference to the cached data -- only use copy = False in performance-sensitive code and where the list will not be modified!
    
    Returns:
        A list of elements, or None if oxidation states for the element were not found in the external data.
    """
    
    global _ElementOxidationStates;
    
    if _ElementOxidationStates == None:
        _ElementOxidationStates = { };

        with open(os.path.join(data_directory, "oxidation_states.txt"), 'r') as file:
            for line in file:
                line = line.strip()

                if line[0] != '#':
                    items = line.split()

                    _ElementOxidationStates[items[0]] = [int(oxidationState) for oxidationState in items[1:]]

    if symbol in _ElementOxidationStates:
        if copy:
            # _ElementOxidationStates stores lists -> if copy is set, make an implicit deep copy.
            # The elements of the lists are integers, which are "value types" in Python.
            
            return [oxidationState for oxidationState in _ElementOxidationStates[symbol]];
        else:
            return _ElementOxidationStates[symbol];
    else:
        if _PrintWarnings:
            print("WARNING: Oxidation states for element {0} not found.".format(symbol));
        
        return None;

# Loader and cache for the element crustal abundances.

_ElementCrustalAbundances = None;

def LookupElementCrustalAbundance(symbol):
    """
    Retrieve the crustal abundance for an element.
    
    Args:
        symbol : the atomic symbol of the element to look up.
    
    Returns:
        The crustal abundance, or None if a value for the element was not found in the external data.
    """
    
    global _ElementCrustalAbundances;

    if _ElementCrustalAbundances == None:
        _ElementCrustalAbundances = { };

        with open(os.path.join(data_directory, "crustal_abundance.txt"), 'r') as file:
            for line in file:
                line = line.strip();

                if line[0] != '#':
                    items = line.split();

                    _ElementCrustalAbundances[items[0]] = float(items[1]);

    if symbol in _ElementCrustalAbundances:
        return _ElementCrustalAbundances[symbol];
    else:
        if _PrintWarnings:
            print("WARNING: Crustal-abundance data for element {0} not found.".format(symbol));
        
        return None;

# Loader and cache for the element HHI scores.

_ElementHHIs = None;

def LookupElementHHIs(symbol):
    """
    Retrieve the HHI_R and HHI_p scores for an element.
    
    Args:
        symbol : the atomic symbol of the element to look up.
    
    Returns:
        A (HHI_p, HHI_R) tuple, or None if values for the elements were not found in the external data.
    """
    
    global _ElementHHIs;
    
    if _ElementHHIs == None:
        _ElementHHIs = { };

        with open(os.path.join(data_directory, "HHIs.txt"), 'r') as file:
            for line in file:
                line = line.strip();
                
                if line[0] != '#':
                    items = line.split();

                    _ElementHHIs[items[0]] = (float(items[1]), float(items[2]));

    if symbol in _ElementHHIs:
        return _ElementHHIs[symbol];
    else:
        if _PrintWarnings:
            print("WARNING: HHI data for element {0} not found.".format(symbol));
        
        return None;

# Loader and cache for the Open Babel-derived element data.

_ElementOpenBabelDerivedData = None;

def LookupElementOpenBabelDerivedData(symbol, copy = True):
    """
    Retrieve the Open Banel-derived data for an element.
    
    Args:
        symbol : the atomic symbol of the element to look up.
        copy : if True (default), return a copy of the data dictionary, rather than a reference to the cached object -- only use copy = False in performance-sensitive code and where you are certain the dictionary will not be modified!
    
    Returns:
        A dictionary containing the data read from the Open Babel table, keyed with the column headings.
    """
    
    global _ElementOpenBabelDerivedData;
    
    if _ElementOpenBabelDerivedData == None:
        _ElementOpenBabelDerivedData = { };

        with open(os.path.join(data_directory, "element.txt"), 'r') as file:
            for line in file:
                line = line.strip();

                if line[0] != '#':
                    items = line.split();

                    key = items[1];

                    dataset = { };
                    
                    dataset['Number'] = int(items[0]);

                    areNeg = float(items[2]);
                    
                    # These values are not (presently) used by SMACT -> no need to print a warning.
                    
                    #if _PrintWarnings and areNeg == 0.0:
                    #    print("WARNING: Aldred-Rochow electronegativity for element {0} may be set to the default value of zero in the Open Babel-derived data.".format(symbol));

                    dataset['ARENeg'] = areNeg;

                    rCov = float(items[3]);

                    if _PrintWarnings and rCov == 1.6:
                        print("WARNING: Covalent radius for element {0} may be set to the default value of 1.6 in the Open Babel-derived data.".format(key));

                    dataset['RCov'] = float(items[3]);

                    dataset['RBO'] = float(items[4]);

                    rVDW = float(items[5]);

                    # These values are not (presently) used by SMACT -> no need to print a warning.

                    #if _PrintWarnings and rVDW == 2.0:
                    #    print("WARNING: Van der Waals raius for element {0} may be set to the default value of 2.0 in the Open Babel-derived data.".format(symbol));

                    dataset['RVdW'] = float(rVDW);
                    
                    maxBnd = int(items[6]);
                    
                    # These values are not (presently) used by SMACT -> no need to print a warning.

                    #if _PrintWarnings and maxBnd == 6:
                    #    print("WARNING: Maximum bond valence for element {0} may be set to the default value of 6 in the Open Babel-derived data.".format(symbol));

                    dataset['MaxBnd'] = maxBnd;

                    dataset['Mass'] = float(items[7]);
                    
                    elNeg = float(items[8]);

                    if _PrintWarnings and elNeg == 0.0:
                        print("WARNING: Pauling electronegativity for {0} may be set to the default of zero in the Open Babel-derived data.".format(key));
                    
                    dataset['ElNeg.'] = elNeg;

                    ionization = float(items[9]);

                    if _PrintWarnings and ionization == 0.0:
                        print("WARNING: Ionisation potential for {0} may be set to the default of zero in the Open Babel-derived data.".format(key));

                    dataset['Ionization'] = ionization;
                    
                    elAffinity = float(items[10]);

                    if _PrintWarnings and elAffinity == 0.0:
                        print("WARNING: Electron affinity for {0} may be set to the default of zero in the Open Babel-derived data.".format(key));
                    
                    dataset['ElAffinity'] = elAffinity;

                    dataset['RGB'] = (float(items[11]), float(items[12]), float(items[13]));
                    dataset['Name'] = items[14];

                    _ElementOpenBabelDerivedData[items[1]] = dataset;

    if symbol in _ElementOpenBabelDerivedData:
        if copy:
            # _ElementOpenBabelDerivedData stores dictionaries -> if copy is set, use the dict.copy() function to return a copy.
            # The values are all Python "value types", so explicitly cloning the elements is not necessary to make a deep copy.
            
            return _ElementOpenBabelDerivedData[symbol].copy();
        else:
            return _ElementOpenBabelDerivedData[symbol];
    else:
        if _PrintWarnings:
            print("WARNING: Open Babel-derived element data for {0} not found.".format(symbol));
        
        return None;

# Loader and cache for the element eigenvalues.

_ElementEigenvalues = None;

def LookupElementEigenvalue(symbol):
    """
    Retrieve the eigenvalue for an element.
    
    Args:
        symbol : the atomic symbol of the element to look up.
    
    Returns:
        The eigenvalue, or None if an eigenvalue was not found in the external data.
    """
    
    global _ElementEigenvalues;
    
    if _ElementEigenvalues == None:
        _ElementEigenvalues = { };
        
        with open(os.path.join(data_directory, "Eigenvalues.csv"),'r') as file:
            reader = csv.reader(file);

            # Skip the first row (headers).
            
            next(reader);

            for row in reader:
                _ElementEigenvalues[row[0]] = float(row[1]);
    
    if symbol in _ElementEigenvalues:
        return _ElementEigenvalues[symbol];
    else:
        if _PrintWarnings:
            print("WARNING: Eigenvalue data for element {0} not found.".format(symbol));
        
        return None;

# Loader and cache for the element s eigenvalues.

_ElementSEigenvalues = None;

def LookupElementSEigenvalue(symbol):
    """
    Retrieve the s eigenvalue for an element.
    
    Args:
        symbol : the atomic symbol of the element to look up.
    
    Returns:
        The s eigenvalue, or None if an s eigenvalue was not found in the external data.
    """
    
    global _ElementSEigenvalues;
    
    if _ElementSEigenvalues == None:
        _ElementSEigenvalues = { };
        
        with open(os.path.join(data_directory, "Eigenvalues_s.csv"), 'rU') as file:
            reader = csv.reader(file);

            # Skip the first row (headers).
            
            next(reader);

            for row in reader:
                _ElementEigenvalues[row[0]] = float(row[1]);

    if symbol in _ElementSEigenvalues:
        return _ElementSEigenvalues[symbol];
    else:
        if _PrintWarnings:
            print("WARNING: s-eigenvalue data for element {0} not found.".format(symbol));
        
        return None;

# Loader and cache for the element Shannon radii datasets.

_ElementShannonRadiiData = None;

def LookupElementShannonRadiusData(symbol, copy = True):
    """
    Retrieve Shannon radii for known oxidation states/coordination environments of an element.
    
    Args:
        symbol : the atomic symbol of the element to look up.
        copy : if True (default), return a copy of the data dictionary, rather than a reference to the cached object -- only use copy = False in performance-sensitive code and where you are certain the dictionary will not be modified!
    
    Returns:
        A list of Shannon radii datasets, or None if the element was not found among the external data.
    """
    
    global _ElementShannonRadiiData;
    
    if _ElementShannonRadiiData == None:
        _ElementShannonRadiiData = { };
        
        with open(os.path.join(data_directory, "shannon_radii.csv"), 'rU') as file:
            reader = csv.reader(file);
            
            # Skip the first row (headers).
            
            next(reader);
        
            for row in reader:
                # For the shannon radii, there are multiple datasets for different element/oxidation-state/coordination combinations.
                
                key = row[0];
                
                dataset = {
                    'charge' : int(row[1]),
                    'coordination' : row[2],
                    'crystal_radius' : float(row[3]),
                    'ionic_radius' : float(row[4]),
                    'comment' : row[5]
                    };
                
                if key in _ElementShannonRadiiData:
                    _ElementShannonRadiiData[key].append(dataset);
                else:
                    _ElementShannonRadiiData[key] = [dataset];
    
    if symbol in _ElementShannonRadiiData:
        if copy:
            # _ElementShannonRadiiData stores a list of dictionaries -> if copy is set, copy the list and use the dict.copy() function on each element.
            # The dictionary values are all Python "value types", so nothing further is required to make a deep copy.
            
            return [item.copy() for item in _ElementShannonRadiiData[symbol]];
        else:
            return _ElementShannonRadiiData[symbol];
    else:
        if _PrintWarnings:
            print("WARNING: Shannon-radius data for element {0} not found.".format(symbol));
        
        return None;

# Loader and cache for the element solid-state energy (SSE) datasets.

_ElementSSEData = None;

def LookupElementSSEData(symbol):
    """
    Retrieve the solid-state energy (SSE) data for an element.
    
    Taken from J. Am. Chem. Soc., 2011, 133 (42), pp 16852-16960, DOI: 10.1021/ja204670s 

    Args:
        symbol : the atomic symbol of the element to look up.
    
    Returns:
        A dictionary containing the SSE dataset for the element, or None if the element was not found among the external data.
    """
    
    global _ElementSSEData;
    
    if _ElementSSEData == None:
        _ElementSSEData = { };
        
        with open(os.path.join(data_directory, "SSE.csv"), 'rU') as file:
            reader = csv.reader(file)
            
            for row in reader:
                dataset = {
                    'AtomicNumber' : int(row[1]),
                    'SolidStateEnergy' : float(row[2]),
                    'IonisationPotential' : float(row[3]),
                    'ElectronAffinity' : float(row[4]),
                    'MullikenElectronegativity' : float(row[5]),
                    'SolidStateRenormalisationEnergy' : float(row[6])
                    };
                
                _ElementSSEData[row[0]] = dataset;

    if symbol in _ElementSSEData:
        return _ElementSSEData[symbol];
    else:
        if _PrintWarnings:
            print("WARNING: Solid-state energy data for element {0} not found.".format(symbol));
        
        return None;

# Loader and cache for the revised (2015) element solid-state energy (SSE) datasets.

_ElementSSE2015Data = None;

def LookupElementSSE2015Data(symbol, copy = True):
    """
    Retrieve the solid-state energy (SSE2015) data for an element in an oxidation state.
    
    Taken from J. Solid State Chem., 2015, 231, pp 138-144, DOI: 10.1016/j.jssc.2015.07.037

    Args:
        symbol : the atomic symbol of the element to look up.
        copy: if True (deafault), return a copy of the data dictionary, rather than a reference to a cached object -- only use copy = False in performance-sensitive code and where you are certain the dictionary will not be modified!
    
    Returns:
        A list of SSE datasets for the element, or None if the element was not found among the external data.
    """
    
    global _ElementSSE2015Data;
    
    if _ElementSSE2015Data == None:
        _ElementSSE2015Data = { };
        
        with open(os.path.join(data_directory, "SSE_2015.csv"), 'rU') as file:
            reader = csv.reader(file)
            
            for row in reader:
                # Elements can have multiple SSE values depending on their oxidation state
                
                key = row[0]
                
                dataset = {
                    'OxidationState' : int(row[1]),
                    'SolidStateEnergy2015' : float(row[2])}
                    
                if key in _ElementSSE2015Data:
                    _ElementSSE2015Data[key].append(dataset)
                else:
                    _ElementSSE2015Data[key] = [dataset]

    if symbol in _ElementSSE2015Data:
        if copy:
            return [item.copy() for item in _ElementSSE2015Data[symbol]]
        else:
            return _ElementSSE2015Data[symbol]
    else:
        if _PrintWarnings:
            print("WARNING: Solid-state energy (revised 2015) data for element {0} not found.".format(symbol));
        
        return None;

# Loader and cache for the element solid-state energy (SSE) from Pauling eletronegativity datasets.

_ElementSSEPaulingData = None;

def LookupElementSSEPaulingData(symbol):
    """
    Retrieve the solid-state energy (SSEPauling) data for an element from the regression fit when SSE2015 is plotted against Pauling electronegativity. 
    
    Taken from J. Solid State Chem., 2015, 231, pp 138-144, DOI: 10.1016/j.jssc.2015.07.037

    Args:
        symbol : the atomic symbol of the element to look up.
    
    Returns:
        A dictionary containing the SSE2015 dataset for the element, or None if the element was not found among the external data.
    """
    
    global _ElementSSEPaulingData;
    
    if _ElementSSEPaulingData == None:
        _ElementSSEPaulingData = { };
        
        with open(os.path.join(data_directory, "SSE_Pauling.csv"), 'rU') as file:
            reader = csv.reader(file)
            
            for row in reader:
                dataset = {
                    'SolidStateEnergyPauling' : float(row[1])}
                    
                _ElementSSEPaulingData[row[0]] = dataset;

    if symbol in _ElementSSEPaulingData:
        return _ElementSSEPaulingData[symbol];
    else:
        if _PrintWarnings:
            print("WARNING: Solid-state energy data from Pauling electronegativity regression fit for element {0} not found.".format(symbol));
        
        return None;

