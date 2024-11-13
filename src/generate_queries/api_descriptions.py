search_query = """This system leverages advanced search techniques that combine vector embedding methods with keyword matching algorithms to retrieve the most relevant results for a user's search query. By capturing both the semantic meaning and the exact keywords, it delivers precise and contextually appropriate results. For example, when a user searches for "how to improve indoor air quality," the system not only identifies documents containing those exact keywords but also understands related concepts like "air purifiers," "ventilation," or "reduce indoor pollutants" through vector embeddings. This hybrid approach ensures a comprehensive set of results that address the user's intent.
This method differs from using an SQL WHERE clause, which is a deterministic filter used in relational databases to retrieve records that exactly match specified conditions. While SQL WHERE clauses operate on structured data and rely on exact matching of predefined criteria, the described search system handles unstructured or semi-structured data and incorporates semantic understanding. It adapts to variations in language and captures user intent more effectively, providing relevant information even if the exact keywords are not present.
"""

text_property_filter = """Only return objects that match a condition on a text-valued property."""

int_property_filter = """Only return objects that match a condition on an integer-valued property."""

boolean_property_filter = """Only return objects that match a condition on a boolean-valued property."""

text_property_aggregation = """Aggregate the values of a text-valued property."""

int_property_aggregation = """Aggregate the values of an integer-valued property."""

boolean_property_aggregation = """Aggregate the values of a boolean-valued property."""

groupby = """Group the results by a property."""