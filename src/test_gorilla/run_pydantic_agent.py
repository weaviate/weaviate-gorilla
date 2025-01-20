import asyncio
import os

import weaviate
import weaviate.classes as wvc
from weaviate.classes.init import Auth

from src.lm.pydantic_agents.agent import WeaviateSearchAgentSimple

async def main():
    # Initialize Weaviate client
    client = weaviate.use_async_with_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
        headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
    )

    try:
        # Connect to client before any operations
        await client.connect()

        # Delete existing collections if they exist
        for collection_name in ["Courses", "Instructors", "Students"]:
            if await client.collections.exists(collection_name):
                await client.collections.delete(collection_name)

        # Create Courses collection
        courses_collection = await client.collections.create(
            name="Courses",
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
            properties=[
                wvc.config.Property(
                    name="courseTitle",
                    data_type=wvc.config.DataType.TEXT,
                ),
                wvc.config.Property(
                    name="courseDescription",
                    data_type=wvc.config.DataType.TEXT,
                ),
                wvc.config.Property(
                    name="courseDuration",
                    data_type=wvc.config.DataType.NUMBER,
                ),
                wvc.config.Property(
                    name="currentlyEnrolling",
                    data_type=wvc.config.DataType.BOOL,
                )
            ]
        )

        # Mock data for Courses
        courses_data = [
            {
                "properties": {
                    "courseTitle": "Advanced Machine Learning",
                    "courseDescription": "Deep dive into neural networks, reinforcement learning, and deep learning architectures. Students will implement cutting-edge ML models and understand their theoretical foundations.",
                    "courseDuration": 48,
                    "currentlyEnrolling": True
                }
            },
            {
                "properties": {
                    "courseTitle": "Quantum Computing Fundamentals", 
                    "courseDescription": "Introduction to quantum mechanics, quantum circuits, and quantum algorithms. Covers basic principles of superposition, entanglement, and quantum gates.",
                    "courseDuration": 36,
                    "currentlyEnrolling": False
                }
            }
        ]

        # Insert mock data
        for course in courses_data:
            await courses_collection.data.insert(properties=course["properties"])

        # Create and run agent
        agent = await WeaviateSearchAgentSimple.create(
            query="What are the most common words, or top occurrences, of the course titles?",
            collections=courses_collection,
            tenant=None,
            collection_view_properties=["courseTitle", "courseDuration", "currentlyEnrolling", "courseDescription"]
        )

        # Run query
        result = await agent.run(agent.query)

        # Print results
        print("\nOriginal Query:", result.original_query)
        print("\nFinal Answer:", result.final_answer)
        print("\nAggregation Queries sent:", result.aggregations)
        print("\nBasic Retrieval Queries sent:", result.searches)
        print("\nTotal Time:", result.total_time)
        print("\nUsage Stats:", result.usage)

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
