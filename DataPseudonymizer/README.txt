This program has been developed by students from the bachelor Computer Science at Utrecht University within the
Software and Game project course
©Copyright Utrecht University Department of Information and Computing Sciences.


DataPseudonymizer removes all the solisID's in a given list from the input file and replaces them with a hashed (+salt) version of those ID's.
This makes it near impossible to find out which solisID's the hash values represent.



===========================
	How it works

The program takes three files as input parameters. First it takes a file in which it will search for id's to replace,
then it takes a file with on each line one id to search for and finally it takes a filepath to which it will write the output.
The first two files should exist and should not be opened in other programs. The last file will be created by the program, and will be overwritten if it already exists.

The program will also ask for a password to use when hashing. When the program is run twice with the same password, the identical solis id's will have identical hash values.



==========================
	How to use

For processing the test data, a random password should be used, which is not shared with anyone. If the testdata consists of multiple files, each of the files should be converted using the same password.



==============================
	Possible risks

There are a few scenearios in which problems might occur.

The first risk is in things like timestamps. If the data file contains timestamps, there is a possibility that the part of the timestamp corresponds with a specific solisid.
In that case, part of the timestamp will be replaces with a hashed version of the solisid. If this happens, it might be possible that the solisid could be deduced from the context of that timestamp.

The second would be a case where the solisid is not detected by the program. The program searches for exact matches with the solisid, which means that if there is an aditional character in the solisid in the file, such as a newline/tab/another random character, the program will not find that occurence.
This could mean that this solisid would still be in the processed result. However, we expect that the chance of this happening is very small.