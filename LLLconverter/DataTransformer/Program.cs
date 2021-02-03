// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace DataTransformer
{
    /**
     * This is a simple tool that can convert LLL data to xAPI statements.
     * Note that not all events are supported and unsupported events will be ignored.
     */

    class Program
    {
        /// <summary>
        /// The url of the moodle instance it should work with
        /// </summary>
        public static string MoodleBaseURL = "https://testla.lifelong.learning.uu.nl";

        /// <summary>
        /// The homepage that actors should use
        /// </summary>
        public static string ActorHomePage = "https://testla.lifelong.learning.uu.nl";

        /// <summary>
        /// The moodle id of the course
        /// </summary>
        public static string CourseID = "8";

        /// <summary>
        /// The amount of statements to put in a single file
        /// </summary>
        public static int batchSize = 10000;

        public static Dictionary<string, Statement> templates;

        public static Dictionary<string, (string name, string type)> idData;
        public static Dictionary<string, string> idMapping;


        public static void AddID(string[] parts)
        {
            string id = GetModuleID(parts[6]);
            if (idData.ContainsKey(id))
                return;
            string actname = string.Join(": ", parts[3].Split(new string[] { ": " }, StringSplitOptions.None).Skip(1));
            string acttype = parts[4];
            idData.Add(id, (actname, acttype));
        }

        public static void ExportIDs()
        {
            StreamWriter idList = new StreamWriter(new FileStream("../../../../ids.csv", FileMode.Create));

            idList.WriteLine("Module ID,Module type,Module name");

            foreach (KeyValuePair<string, (string name, string type)> kvp in idData)
            {
                idList.WriteLine($"{kvp.Key},{kvp.Value.type},{kvp.Value.name}");
            }

            idList.Close();
        }

        public static void ImportIDMapping()
        {
            StreamReader idmap = new StreamReader(new FileStream("../../../../idmapping.csv", FileMode.Open));
            idmap.ReadLine();

            string line;
            while((line = idmap.ReadLine()) != null)
            {
                string[] parts = line.Split(';');
                idMapping.Add(parts[0], parts[3]);
                Console.WriteLine($"Mapping {parts[0]} to {parts[3]}");
            }

        }

        static void Main()
        {
            idData = new Dictionary<string, (string, string)>();
            idMapping = new Dictionary<string, string>();
            LoadTemplates();
            ImportIDMapping();
            StreamReader sr = new StreamReader(new FileStream("../../../../data.csv", FileMode.Open));

            StreamWriter sw = null;

            Console.WriteLine("Starting conversion...");

            string line;
            string[] parts;
           

            int counter = 0;
            int totalcounter = 0;
            int batchcounter = 0;
            int current_batch = 0;
            bool isFirst = true;
            while ((line = sr.ReadLine()) != null) {
                totalcounter++;
                parts = line.Split(',');
                if (parts.Length != 9)
                    continue;

                if (isFirst)
                {
                    sw = new StreamWriter(new FileStream($"../../../../statements_{current_batch}.txt", FileMode.Create));
                    sw.AutoFlush = true;
                    sw.WriteLine("[");
                    isFirst = false;
                }

                switch (parts[4])
                {
                    case "Forum":
                        {
                            Statement stm = templates["page_viewed"];

                            if (parts[5] == "Cursusmodule bekeken")
                                stm = templates["forum_viewed"];
                            else 
                                continue;

                            stm.activity.id = $"{MoodleBaseURL}/mod/forum/view.php?id={GetModuleID(parts[6])}";

                            AddID(parts);
                            sw.WriteLine(JsonSerializer.Serialize(FinalizeSTM(stm, parts)) + ",");
                            break;
                        }
                    case "Pagina":
                        {
                            Statement stm = templates["page_viewed"];

                            stm.activity.id = $"{MoodleBaseURL}/mod/page/view.php?id={GetModuleID(parts[6])}";

                            AddID(parts);
                            sw.WriteLine(JsonSerializer.Serialize(FinalizeSTM(stm, parts)) + ",");
                            break;
                        }
                    case "H5P":
                        {
                            Statement stm = templates["hvp_viewed"];

                            stm.activity.id = $"{MoodleBaseURL}/mod/hvp/view.php?id={GetModuleID(parts[6])}";

                            AddID(parts);
                            sw.WriteLine(JsonSerializer.Serialize(FinalizeSTM(stm, parts)) + ",");
                            break;
                        }
                    case "Systeem":
                        {
                            if (parts[5] != "Cursus bekeken")
                                continue;
                            Statement stm = templates["course_viewed"];

                            sw.WriteLine(JsonSerializer.Serialize(FinalizeSTM(stm, parts)) + ",");
                            break;
                        }
                    case "SCORM-pakket":
                        {
                            Statement stm;
                            if (parts[5] == "Sco-gestart")
                                stm = templates["scorm_launched"];
                            else if (parts[5] == "Cursusmodule bekeken")
                                stm = templates["scorm_viewed"];
                            else if (parts[5] == "Ingestuurde SCORM-status")
                            {
                                stm = templates["scorm_status"];
                                string verb = getScormStatus(parts[6]);
                                stm.verb.id = "http://adlnet.gov/expapi/verbs/" + verb;
                                stm.verb.display.nl = verb;
                            }
                            else
                                continue;

                            // TODO handle 'Ingestuurde ruwe SCORM-score'

                            AddID(parts);
                            stm.activity.id = $"{MoodleBaseURL}/mod/scorm/view.php?id={GetModuleID(parts[6])}";

                            sw.WriteLine(JsonSerializer.Serialize(FinalizeSTM(stm, parts)) + ",");
                            break;
                        }
                    case "Externe tool":
                        {
                            Statement stm = templates["lti_viewed"];

                            AddID(parts);
                            stm.activity.id = $"{MoodleBaseURL}/mod/lti/view.php?id={GetModuleID(parts[6])}";

                            sw.WriteLine(JsonSerializer.Serialize(FinalizeSTM(stm, parts)) + ",");
                            break;
                        }
                    default:
                        {
                            continue;
                        }
                }

                counter++;
                batchcounter++;
                if (batchcounter >= batchSize)
                {
                    sw.WriteLine("]");
                    sw.Close();
                    batchcounter = 0;
                    current_batch++;
                    isFirst = true;
                }
                
            }

            sw.WriteLine("]");

            sr.Close();
            sw.Close();

            ExportIDs();
            Console.WriteLine($"Done, {counter} statements generated in {current_batch + 1} batches (skipped {totalcounter - counter}, {(counter * 100f / totalcounter).ToString("0.00")}% coverage)");
            Console.WriteLine("\nPress enter to exit");
            Console.ReadLine();
        }

        /// <summary>
        /// Add some parameters that need to be changed in all types of statements
        /// </summary>
        /// <param name="stm">The statement to finalize</param>
        /// <param name="parts">A line of data split on the ,</param>
        /// <returns>The finalized statement</returns>
        public static Statement FinalizeSTM(Statement stm, string[] parts)
        {
            stm.timestamp = ConvertTimeStamp(parts[0]);

            stm.actor.SetName(parts[1]);
            
            string actname = string.Join(": ", parts[3].Split(new string[] { ": " }, StringSplitOptions.None).Skip(1));
            stm.activity.definition.name.nl = actname;

            return stm;
        }

        /// <summary>
        /// Extract the module id from the summary column
        /// </summary>
        /// <param name="summary"></param>
        /// <returns>the id of the module</returns>
        public static string GetModuleID(string summary)
        {
            string id = summary.Substring(summary.IndexOf("course module id '") + " course module id '".Length - 1, 8);
            if (idMapping.ContainsKey(id))
                return idMapping[id];
            return id;
        }

        /// <summary>
        /// Extract the scorm status from the summary column
        /// </summary>
        /// <param name="summary"></param>
        /// <returns>the correct status (failed|passed|completed)</returns>
        public static string getScormStatus(string summary)
        {
            if (summary.IndexOf("element 'cmi.success_status' with the value of 'failed'") != -1)
                return "failed";
            if (summary.IndexOf("element 'cmi.success_status' with the value of 'passed'") != -1)
                return "passed";
            if (summary.IndexOf("element 'cmi.completion_status' with the value of 'completed'") != -1)
                return "completed";
            throw new Exception("Invalid status: " + summary);
        }

        /// <summary>
        /// Convert the timestamp into the correct format
        /// </summary>
        /// <param name="timestamp"></param>
        /// <returns></returns>
        public static string ConvertTimeStamp(string timestamp)
        {
            string[] timeparts = timestamp.Split(' ');
            return string.Join("-", timeparts[0].Split('/').Reverse().Select(str => str.Length == 4 || str.Length == 2 ? str : "0" + str).ToArray()) + "T" + timeparts[1] + ":00.000Z";
        }

        /// <summary>
        /// Load all templates of all supported statements
        /// </summary>
        public static void LoadTemplates()
        {
            templates = new Dictionary<string, Statement>();
            int templatecounter = 0;

            Console.WriteLine("Loading templates...");

            LoadTemplate("page_viewed", LoadPageViewed);
            LoadTemplate("hvp_viewed", LoadHvpViewed);
            LoadTemplate("course_viewed", LoadCourseViewed);
            LoadTemplate("scorm_viewed", LoadScormViewed);
            LoadTemplate("scorm_launched", LoadScormLaunched);
            LoadTemplate("scorm_status", LoadScormStatus);
            LoadTemplate("lti_viewed", LoadLtiViewed);
            LoadTemplate("forum_viewed", LoadForumViewed);


            Console.WriteLine($"Loaded {templatecounter} templates.\n");

            void LoadTemplate(string name, Func<Statement> loader)
            {
                Statement stm = loader();
                stm.actor.account.homePage = ActorHomePage;
                stm.context.contextActivities.grouping[0].id = MoodleBaseURL;
                templates.Add(name, stm);
                Console.WriteLine($"Loaded {name} template");
                templatecounter++;
            }

            ///Template for the page_viewed event
            Statement LoadPageViewed()
            {
                Statement stm = JsonSerializer.Deserialize<Statement>(File.ReadAllText("../../../templates/page_viewed.json"));
                stm.context.contextActivities.grouping[1].id = $"{MoodleBaseURL}/course/view.php?id={CourseID}";
                return stm;
            }

            ///Template for the lti_viewed event
            Statement LoadLtiViewed()
            {
                Statement stm = JsonSerializer.Deserialize<Statement>(File.ReadAllText("../../../templates/lti_viewed.json"));
                stm.context.contextActivities.grouping[1].id = $"{MoodleBaseURL}/course/view.php?id={CourseID}";
                return stm;
            }

            ///Template for the h5p_viewed events
            Statement LoadHvpViewed()
            {
                Statement stm = JsonSerializer.Deserialize<Statement>(File.ReadAllText("../../../templates/hvp_viewed.json"));
                stm.context.contextActivities.grouping[1].id = $"{MoodleBaseURL}/course/view.php?id={CourseID}";
                return stm;
            }

            ///Template for the course_viewed event
            Statement LoadCourseViewed()
            {
                Statement stm = JsonSerializer.Deserialize<Statement>(File.ReadAllText("../../../templates/course_viewed.json"));
                stm.activity.id = $"{MoodleBaseURL}/course/view.php?id={CourseID}";
                return stm;
            }

            ///Template for the scorm_viewed event
            Statement LoadScormViewed()
            {
                Statement stm = JsonSerializer.Deserialize<Statement>(File.ReadAllText("../../../templates/scorm_viewed.json"));
                stm.context.contextActivities.grouping[1].id = $"{MoodleBaseURL}/course/view.php?id={CourseID}";
                return stm;
            }

            ///Template for the scorm_launched event
            Statement LoadScormLaunched()
            {
                Statement stm = JsonSerializer.Deserialize<Statement>(File.ReadAllText("../../../templates/scorm_launched.json"));
                stm.context.contextActivities.grouping[1].id = $"{MoodleBaseURL}/course/view.php?id={CourseID}";
                return stm;
            }

            ///Template for the scorm_status event
            Statement LoadScormStatus()
            {
                Statement stm = JsonSerializer.Deserialize<Statement>(File.ReadAllText("../../../templates/scorm_status.json"));
                stm.context.contextActivities.grouping[1].id = $"{MoodleBaseURL}/course/view.php?id={CourseID}";
                return stm;
            }

            ///Template for the forum_viewed event
            Statement LoadForumViewed()
            {
                Statement stm = JsonSerializer.Deserialize<Statement>(File.ReadAllText("../../../templates/forum_viewed.json"));
                stm.context.contextActivities.grouping[1].id = $"{MoodleBaseURL}/course/view.php?id={CourseID}";
                return stm;
            }
        }

    }
}
