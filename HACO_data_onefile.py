#!/usr/bin/python

import sys, os, os.path

usage = '''HACO_data_onefile.py PDBid          Will go look for the PDB with that id (for 1UBQ) /home/smlewis/whole_PDB_as_PDB/ub/pdb1ubq.ent.gz, and ????'''

muscle_path = "/home/smlewis/whole_PDB_as_PDB/"

if __name__ == '__main__':

    if (len(sys.argv) != 2) :
        print usage
        exit(1)

    pdb = sys.argv[1].lower() #NOTE the lower is an assumption for case-sensitive file systems
    cwd = os.getcwd() + "/"

    #path to this PDB
    interstice = pdb[1:3]
    in_path = muscle_path + interstice + "/pdb" + pdb + ".ent.gz"
    unzipped_path = cwd + pdb + ".pdb"

    #generate local copy of file
    gunzip_command = "gunzip --to-stdout " + in_path + " > " + unzipped_path
    print gunzip_command
    os.system(gunzip_command)

    #run Reduce to strip old H
    reduce_stripped_path = cwd + pdb + ".stripped.pdb"
    reduce_strip_command = "phenix.reduce -quiet -trim -allalt " + unzipped_path + " | grep -v '^USER  MOD' > " + reduce_stripped_path
    print reduce_strip_command
    os.system(reduce_strip_command)

    #run Reduce
    reduced_path = cwd + pdb + "H.pdb"
    reduce_command = "phenix.reduce -quiet -nobuild9999 " + reduce_stripped_path + " > " + reduced_path
    print reduce_command
    os.system(reduce_command)

    #remove stripped pdb
    rm_strip_command = "rm " + reduce_stripped_path
    print rm_strip_command
    os.system(rm_strip_command)

    #run CaBLAM
    CaBLAM_results_path = cwd + pdb + "_3CA_angle.txt"
    CaBLAM_command = "phenix.cablam_training cablam=True " + reduced_path + " > " +  CaBLAM_results_path
    print CaBLAM_command
    os.system(CaBLAM_command)

    #get DSSP
    #this is dumb to use FTP, but when I tried rsyncing the whole database I realized they have literally every PDB's dssp in one directory, which causes performance issues
    #curl ftp://ftp.cmbi.ru.nl/pub/molbio/data/dssp/1ubq.dssp
    dssp_path = cwd + pdb + ".dssp"
    dssp_command = "curl ftp://ftp.cmbi.ru.nl/pub/molbio/data/dssp/" + pdb + ".dssp > " + dssp_path
    print dssp_command
    os.system(dssp_command)

    #cryptic remark
    # Run DSSP on xxxx.pdb
    #     - to generate dssp.txt file (I have trimmed mine, but script could be revised to include                 'line.startswith')

    #run Probe
    #**Note:  the two underscores following the O are correct.
    probe_path = cwd + pdb + "H_onedot_HACO.txt"
    probe_command = 'phenix.probe -once -mc -Radius1.0 -u -onedot "atom_HA_,atom_HA2 protein" "atom_O__ protein" ' + reduced_path + " > " + probe_path
    print probe_command
    os.system(probe_command)

    # Run Angle_add_HACO.py to combine pertinent data from all three previous runs into one text file and then transfer to an excel sheet for graphing, sorting.
    #Total commandline is "python Angle_add_HACO_02292016.py 3XXXH_cablam3CA_angle.txt 3XXX__dssp_1lineHeader.txt 3XXXH_onedot_1.0rad_All_02292016.txt"
    HACO_path = cwd + pdb + ".HACOresult.csv"
    HACO_Liz_command = "python Angle_add_HACO.py " + CaBLAM_results_path + " " + dssp_path + " " + probe_path + " > " + HACO_path
    print HACO_Liz_command
    os.system(HACO_Liz_command)