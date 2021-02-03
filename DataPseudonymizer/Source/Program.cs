using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Security.Cryptography;

/**
 * This program has been developed by students from the bachelor Computer Science at Utrecht University within the
 * Software and Game project course
 * ©Copyright Utrecht University Department of Information and Computing Sciences.
 * 
 * DataPseudonymizer for software project 2020, Box-in-a-box ICT
 * 
 * Author: J.W. Bakker
 * Version: 1.0
 */

namespace DataPseudonymizer
{
    class Program
    {
        static void Main(string[] args)
        {
            //Ask user which files to use
            SelectFiles(out string inputFile, out string filterFile, out string outputFile, out string password);

            //Hash the password to make it harder to guess
            password = Convert(password, "");

            //Get all the id's to search for
            string[] ids = new StreamReader(new FileStream(filterFile, FileMode.Open))
                .ReadToEnd()
                .Split(new string[] { "\r\n" }, StringSplitOptions.RemoveEmptyEntries);

            //Calculate for each id the mapping to the hash value
            string[] mapped = ids.Select((id) => Convert(id, password)).ToArray();


            //Open the files required for converting.
            StreamReader inputReader = new StreamReader(new FileStream(inputFile, FileMode.Open));
            StreamWriter outputWriter = new StreamWriter(new FileStream(outputFile, FileMode.Create));


            Console.WriteLine("Converting....");

            //For each line search for all id's and replace them with the correct hash value
            string line;
            while ((line = inputReader.ReadLine()) != null)
            {
                for (int i = 0; i<ids.Length; i++)
                {
                    line = line.Replace(ids[i], mapped[i]);
                }
                outputWriter.WriteLine(line);
            }
            
            //Close the files
            outputWriter.Close();
            inputReader.Close();

            Console.WriteLine("Done, press any key to continue...");
            Console.ReadLine();
        }

        /// <summary>
        /// Ask the user which files to use
        /// </summary>
        /// <param name="inputFile">The file to convert</param>
        /// <param name="filterFile">The list of id's to remove</param>
        /// <param name="outputFile">The file to write the result to</param>
        /// <param name="password">A password to use as salt when converting the id.</param>"
        public static void SelectFiles(out string inputFile, out string filterFile, out string outputFile, out string password)
        {
            Console.WriteLine("Enter the path of the file to convert");
            inputFile = Console.ReadLine();

            Console.WriteLine("Enter the path of the file containing the solis-id's to remove");
            filterFile = Console.ReadLine();

            Console.WriteLine("Enter the path of the file to write the output to");
            outputFile = Console.ReadLine();

            if (!File.Exists(inputFile))
            {
                Console.WriteLine($"File '{inputFile}' could not be found");
                throw new Exception($"File {inputFile} could not be found.");
            }

            if (!File.Exists(filterFile))
            {
                Console.WriteLine($"File '{filterFile}' could not be found");
                throw new Exception($"File {filterFile} could not be found.");
            }

            Console.WriteLine("Enter a password to use for salt values");
            password = Console.ReadLine();

        }


        /// <summary>
        /// Converts a string to a hash representation of the string
        /// </summary>
        /// <param name="id">The id string to convert</param>
        /// <param name="password">A password to add to the ID before hashing</param>
        /// <returns>The hashed value in the form of "<id@{thehashedstring}>" </returns>
        public static string Convert(string id, string password)
        {
            using (SHA256 sha = SHA256.Create())
            {

                byte[] idBytes = Encoding.UTF8.GetBytes(id + password);
                byte[] hash = sha.ComputeHash(idBytes);

                StringBuilder result = new StringBuilder("<id@");

                for (int i = 0; i < hash.Length; i++)
                    result.Append(hash[i].ToString("x2"));

                result.Append(">");

                return result.ToString();

            }
        }
    }

}
