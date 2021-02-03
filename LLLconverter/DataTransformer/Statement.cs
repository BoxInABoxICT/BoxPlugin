// This program has been developed by students from the bachelor Computer Science at Utrecht University within the
// Software and Game project course
// ©Copyright Utrecht University Department of Information and Computing Sciences.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace DataTransformer
{
    /**
     * This file contains the class representation of the json structure in an LRS statement.
     * It is used for the deserializing of the templates and the serializing of the statements
     */
    public class Statement
    {
        public Actor actor { get; set; }
        public Verb verb { get; set; }
        [JsonPropertyName("object")]
        public Activity activity { get; set; }
        public string timestamp { get; set; }
        public Context context { get; set; }
    }

    //=====================ACTOR=====================//
    public class Actor
    {
        public string name { get; set; }
        public Account account { get; set; }

        public void SetName(string name)
        {
            this.name = name;
            account.name = name;
        }
    }

    public class Account
    {
        public string homePage { get; set; }
        public string name { get; set; }

    }
    //=====================VERB=====================//
    public class Verb
    {
        public string id { get; set; }
        public DisplayNL display { get; set; }
    }

    public class DisplayNL
    {
        public string nl { get; set; }
    }
    public class DisplayEN
    {
        public string en { get; set; }
    }


    //=====================OBJECT=====================//
    public class Activity
    {
        public string id { get; set; }
        public DefinitionNL definition {get; set; }
    }

    public class DefinitionNL
    {
        public string type { get; set; }
        public DisplayNL name { get; set; }
    }
    public class DefinitionEN
    {
        public string type { get; set; }
        public DisplayEN name { get; set; }
    }

    //=====================CONTEXT=====================//

    public class Context
    {
        public string platform { get; set; }
        public string language { get; set; }
        public Extensions extensions { get; set; }
        public ContextActivities contextActivities { get; set; }
    }

    public class Extensions
    {
        [JsonPropertyName("http://lrs.learninglocker.net/define/extensions/info")]
        public Info info { get; set; }
    }

    public class Info
    {
        [JsonPropertyName("http://moodle.org")]
        public string moodle { get; set; }
        [JsonPropertyName("https://github.com/xAPI-vle/moodle-logstore_xapi")]
        public string xapi { get; set; }
        public string event_name { get; set; }
        public string event_function { get; set; }
    }

    public class ContextActivities
    {
        public Grouping[] grouping { get; set; }
        public Category[] category { get; set; }
    }

    public class Grouping
    {
        public string id { get; set; }
        public DefinitionNL definition { get; set; }
    }

    public class Category
    {
        public string id { get; set; }
        public DefinitionEN definition { get; set; }
    }

}
