# Weaviate Schema Zoo!

These are the toy schemas used to create synthetic queries from the Weaviate APIs, as well as synthetic instructions to simulate the natural language commands to invoke the APIs.

Some notes:
- All of these schemas have at least 2 `text` properties to enable synthetic queries for the BM25F API.
- All schemas contain at least 1 `int` or `number` property, at least 1 `boolean` property, and at least 1 cross-reference. The simulated cross-reference class is defined as well and contains at least 1 `text` property and at least 1 `int` property.

The schemas are generated with the following prompt:

Could you please help me come up with examples of Weaviate database schemas? Weaviate's schema defines its data structure in a formal language. In other words, it is a blueprint of how the data is to be organized and stored. The schema defines data classes (i.e. collections of objects), the properties within each class (name, type, description, settings), possible graph links between data objects (called cross-references), and the vectorizer module to be used for the class, as well as settings such as the vectorizer module, and index configurations.

A collection of data in Weaviate is called a "class".  Every class has properties. Properties define what kind of data values you will add to an object in Weaviate. In the schema, you define at least the name of the property and its dataType. When creating a property, Weaviate needs to know what type of data you will give it. Weaviate accepts the following types: `text`, `text[]`, `int`, `int[]`, `boolean`, `boolean[]`, `number`, `number[]`, `date`, `date[]`, `uuid`, `uuid[]`, `cross reference`. The cross-reference type is the graph element of Weaviate: you can create a link from one object to another. In the schema you can define multiple classes to which a property can point, in a list of strings. The strings in the dataType list are names of classes defined elsewhere in the schema.

Here is an example of a Weaviate schema for code repositories. It contains two classes, `Repository` and `Developer`. 

```json
 {
      "classes": [
        {
          "class": "PodClip",
          "description": "A podcast clip.",
          "vectorIndexType": "hnsw",
          "vectorizer": "text2vec-transformers",
          "properties": [
            {
              "name": "summary",
              "dataType": ["text"],
              "description": "An LLM-generated summary of the podcast clip.",
            },
            {
              "name": "content",
              "dataType": ["text"],
              "description": "The text content of the podcast clip",
            },
            {
              "name": "speaker",
              "dataType": ["text"],
              "description": "The speaker in the podcast",
            },
            {
              "name": "podNum",
              "dataType": ["int"],
              "description": "The podcast number.",
            },
            {
              "name": "clipNumber",
              "dataType": ["int"],
              "description": "The clip number within the podcast.",
            },
            {
              "name": "Featured",
              "dataType": ["boolean"],
              "description": "Whether this clip was featured individually on social media.",
            },
            {
              "name": "inPodcast",
              "dataType": ["Podcast"],
              "description": "The podcast this clip was sourced from.",
            },
            {
              "name": "inChapter",
              "dataType": ["Chapter"],
              "description": "The chapter this clip is associated with.",
            }
          ]
        },
        {
          "class": "Podcast",
          "description": "A Weaviate Podcast!",
          "vectorIndexType": "hnsw",
          "vectorizer": "text2vec-transformers",
          "properties": [
            {
              "name": "summary",
              "dataType": ["text"],
              "description": "The text content of the podcast clip",
            },
            {
              "name": "podNum",
              "dataType": ["int"],
              "description": "The speaker in the podcast",
            },
            {
              "name": "hasClip",
              "dataType": ["PodClip"],
              "description": "A clip contained in the podcast",
            },
            {
              "name": "hasChapter",
              "dataType": ["Chapter"],
              "description": "A chapter contained in the podcast",
            }
          ]
        },
        {
          "class": "Chapter",
          "description": "A Podcast Chapter",
          "vectorIndexType": "hnsw",
          "vectorizer": "text2vec-transformers",
          "properties": [
            {
              "name": "description",
              "dataType": ["text"],
              "description": "A description of the chapter",
            },
            {
              "name": "title",
              "dataType": ["text"],
              "description": "The title of the chapter",
            },
            {
              "name": "timeStart",
              "dataType": ["int"],
              "description": "The timestamp where this chapter begins",
            },
            {
              "name": "timeEnd",
              "dataType": ["int"],
              "description": "The title of the chapter",
            },
            {
              "name": "duration",
              "dataType": ["int"],
              "description": "The title of the chapter",
            },
            {
              "name": "fromPodcast",
              "dataType": ["Podcast"],
              "description": "The podcast this chapter was sourced from.",
            },
            {
              "name": "hasClip",
              "dataType": ["PodClip"],
              "description": "A clip associated with this chapter",
            }
          ]
        }
      ]
 }
```

Could you please design 5 more fictional schemas? For each could you please include at least 2 text properties, at least 1 int or number property, at least 1 boolean property, and at least 1 cross-reference? For the cross-referenced class, could you please create that class as well with at least 1 text property and at least 1 int property?

---------------------------------
The Schemas include:
1. Podcasts
2. Clothing
3. Books
4. CRM
5. Event Planning
6. Movies
7. Music
8. Social Media
9. Supplements
10. Travel Destinations
11. Workout Tracker
12. Code Repository