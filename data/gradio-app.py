import gradio as gr
import json
import pandas as pd
import os
import plotly.express as px
from collections import Counter

# Configuration
DATA_FILE = "./weaviate-gorilla.json"  # Ensure this path is correct
SCHEMA_FILE = "./3-collection-schemas-with-search-property.json"  # Path to schema file

def load_data():
    """Load the transformed dataset."""
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    # If the JSON is a single record (a dict), wrap it in a list.
    if isinstance(data, dict):
        data = [data]
    return data

def load_schemas():
    """Load the collection schemas."""
    if not os.path.exists(SCHEMA_FILE):
        return None
    try:
        with open(SCHEMA_FILE, "r") as f:
            schemas = json.load(f)
        # Parse each schema string into a JSON object
        parsed_schemas = []
        for schema_str in schemas:
            schema_data = json.loads(schema_str)
            if "weaviate_collections" in schema_data:
                parsed_schemas.extend(schema_data["weaviate_collections"])
        return parsed_schemas
    except Exception as e:
        print(f"Error loading schemas: {str(e)}")
        return None

def get_dataset_stats(data):
    """Generate basic statistics about the dataset."""
    if not data:
        return "No data loaded"
    total_records = len(data)
    valid_records = sum(1 for item in data if item.get("is_valid_lm_verifier", False))
    collections = []
    for item in data:
        if "ground_truth_query" in item and "target_collection" in item["ground_truth_query"]:
            collections.append(item["ground_truth_query"]["target_collection"])
    collection_counts = Counter(collections)
    operators = []
    for item in data:
        operators.extend(item.get("ground_truth_operators", []))
    operator_counts = Counter(operators)
    
    stats = "## Dataset Overview\n\n"
    stats += f"**Total Records:** {total_records}\n\n"
    stats += f"**Valid Queries:** {valid_records} ({(valid_records/total_records*100):.1f}%)\n\n"
    stats += "### Target Collections\n\n"
    for collection, count in collection_counts.most_common():
        stats += f"- {collection}: {count} ({(count/total_records*100):.1f}%)\n"
    stats += "\n### Operator Usage\n\n"
    for operator, count in operator_counts.most_common():
        stats += f"- {operator}: {count} ({(count/total_records*100):.1f}%)\n"
    return stats

def generate_charts(data):
    """Generate visualization charts for the dataset."""
    if not data:
        return None, None
    # Collection distribution chart.
    collections = []
    for item in data:
        if "ground_truth_query" in item and "target_collection" in item["ground_truth_query"]:
            collections.append(item["ground_truth_query"]["target_collection"])
    collection_counts = Counter(collections)
    if collection_counts:
        collection_df = pd.DataFrame({
            "Collection": list(collection_counts.keys()),
            "Count": list(collection_counts.values())
        })
        collection_fig = px.bar(
            collection_df,
            x="Collection",
            y="Count",
            title="Distribution of Target Collections",
            color="Collection"
        )
    else:
        collection_fig = px.bar(title="Distribution of Target Collections (No Data)")
    
    # Operator usage chart.
    operators = []
    for item in data:
        operators.extend(item.get("ground_truth_operators", []))
    operator_counts = Counter(operators)
    if operator_counts:
        operator_df = pd.DataFrame({
            "Operator": list(operator_counts.keys()),
            "Count": list(operator_counts.values())
        })
        operator_fig = px.bar(
            operator_df,
            x="Operator",
            y="Count",
            title="Usage of Query Operators",
            color="Operator"
        )
    else:
        operator_fig = px.bar(title="Usage of Query Operators (No Data)")
    
    return collection_fig, operator_fig

def view_record(data, index):
    """Display details of a specific record."""
    if not data or index >= len(data) or index < 0:
        return "Invalid index or no data loaded"
    try:
        record = data[index]
        content = "# Record Details\n\n"
        if "natural_language_command" in record:
            content += f"## Natural Language Command\n{record['natural_language_command']}\n\n"
        if "ground_truth_query" in record:
            content += "## Ground Truth Query Details\n"
            query = record["ground_truth_query"]
            content += f"- **Target Collection:** {query.get('target_collection', 'N/A')}\n"
            content += f"- **Search Query:** {query.get('search_query', 'N/A')}\n"
            for filter_type in ["integer_property_filter", "text_property_filter", "boolean_property_filter"]:
                filter_data = query.get(filter_type)
                if filter_data:
                    content += f"- **{filter_type.replace('_', ' ').title()}:** "
                    if isinstance(filter_data, dict):
                        prop = filter_data.get("property_name", "unknown")
                        op = filter_data.get("operator", "unknown")
                        val = filter_data.get("value", "unknown")
                        content += f"{prop} {op} {val}\n"
                    else:
                        content += f"{filter_data}\n"
            for agg_type in ["integer_property_aggregation", "text_property_aggregation", "boolean_property_aggregation"]:
                agg_data = query.get(agg_type)
                if agg_data:
                    content += f"- **{agg_type.replace('_', ' ').title()}:** "
                    if isinstance(agg_data, dict):
                        content += f"{agg_data.get('property_name', 'unknown')}\n"
                    else:
                        content += f"{agg_data}\n"
            if "groupby_property" in query:
                content += f"- **Group By:** {query['groupby_property']}\n"
            if query.get("total_count", False):
                content += f"- **Total Count:** Yes\n"
        content += "\n## Verification\n"
        content += f"- **Is Valid:** {record.get('is_valid_lm_verifier', 'N/A')}\n"
        if "lm_verifier_rationale" in record:
            content += "\n## Verification Rationale\n" + record["lm_verifier_rationale"] + "\n"
        if "weaviate_schemas" in record:
            content += "\n## Schema Description\n<details><summary>Click to expand schema details</summary>\n\n"
            content += json.dumps(record["weaviate_schemas"], indent=2)
            content += "\n</details>\n"
        return content
    except Exception as e:
        return f"Error processing record: {str(e)}"

def explore_schema(schemas, index):
    """Explore the schema at the given index."""
    if not schemas or index >= len(schemas) or index < 0:
        return "Invalid index or no schemas loaded"
    try:
        collection = schemas[index]
        collection_name = collection.get("name", "Unknown Collection")
        content = f"# Collection: {collection_name}\n\n"
        content += "## Properties\n\n"
        content += "| Property | Data Type | Description |\n"
        content += "|----------|-----------|-------------|\n"
        for prop in collection.get("properties", []):
            name = prop.get("name", "Unknown")
            data_type = ", ".join(prop.get("data_type", ["Unknown"]))
            description = prop.get("description", "No description")
            content += f"| {name} | {data_type} | {description} |\n"
        content += "\n"
        use_case = collection.get("envisioned_use_case_overview", "No use case description")
        content += f"## Use Case\n{use_case}\n\n"
        return content
    except Exception as e:
        return f"Error exploring schema: {str(e)}"

def get_leaderboard_data():
    """Generate synthetic leaderboard data."""
    models = [
        "GPT-4 Turbo",
        "Claude 3 Opus",
        "Llama 3 70B",
        "Gemini Pro",
        "Claude 3 Sonnet",
        "GPT-3.5 Turbo",
        "Mistral Large",
        "Llama 3 8B",
        "Gemini Flash",
        "Claude 3 Haiku"
    ]
    
    # Generate synthetic exact match scores (higher for more capable models)
    scores = [
        0.87,
        0.85,
        0.79,
        0.77,
        0.75,
        0.68,
        0.65,
        0.58,
        0.55,
        0.52
    ]
    
    # Create a DataFrame
    df = pd.DataFrame({
        "Model Name": models,
        "Exact Match Score": scores
    })
    
    return df

# --- Create the App and Define Navigation Helpers Within ---
def create_app():
    data = load_data()
    schemas = load_schemas()
    
    if data is None:
        with gr.Blocks(title="Weaviate Queries Dataset Visualizer") as app:
            gr.Markdown(f"⚠️ Error: Could not load data file from {DATA_FILE}")
        return app

    max_index = len(data) - 1
    max_schema_index = len(schemas) - 1 if schemas else -1

    with gr.Blocks(title="Weaviate Queries Dataset Visualizer") as app:
        gr.Markdown("# Weaviate Gorilla Visualizer")
        
        # Leaderboard Tab
        with gr.Tab("Leaderboard"):
            leaderboard_df = get_leaderboard_data()
            gr.Markdown("# Model Performance Leaderboard")
            gr.Markdown("This leaderboard shows the exact match score for different models on the Weaviate query generation task.")
            
            # Display the leaderboard as a DataFrame
            gr.Dataframe(
                value=leaderboard_df,
                headers=["Model Name", "Exact Match Score"],
                datatype=["str", "number"],
                row_count=(len(leaderboard_df), "fixed"),
                col_count=(2, "fixed")
            )
            
            # Add a bar chart visualization
            leaderboard_fig = px.bar(
                leaderboard_df,
                x="Model Name",
                y="Exact Match Score",
                title="Model Performance Comparison",
                color="Model Name"
            )
            gr.Plot(leaderboard_fig)
        
        # Record Explorer Tab
        with gr.Tab("Record Explorer"):
            with gr.Row():
                record_index = gr.Number(value=0, label="Record Index", precision=0)
                prev_btn = gr.Button("← Previous")
                next_btn = gr.Button("Next →")
                record_counter = gr.Markdown(f"Record 1 of {max_index + 1}")
            record_md = gr.Markdown(value=view_record(data, 0))
            
            def update_record(index):
                index = int(index)
                if index < 0:
                    index = 0
                if index > max_index:
                    index = max_index
                return index, view_record(data, index), f"Record {index + 1} of {max_index + 1}"
            
            def prev_record(index):
                return update_record(int(index) - 1)
            
            def next_record(index):
                return update_record(int(index) + 1)
            
            prev_btn.click(fn=prev_record, inputs=record_index, outputs=[record_index, record_md, record_counter])
            next_btn.click(fn=next_record, inputs=record_index, outputs=[record_index, record_md, record_counter])
            record_index.change(fn=update_record, inputs=record_index, outputs=[record_index, record_md, record_counter])
        
        # Schema Explorer Tab
        with gr.Tab("Schema Explorer"):
            if schemas:
                with gr.Row():
                    schema_index = gr.Number(value=0, label="Schema Index", precision=0)
                    schema_prev_btn = gr.Button("← Previous")
                    schema_next_btn = gr.Button("Next →")
                    schema_counter = gr.Markdown(f"Schema 1 of {max_schema_index + 1}")
                schema_md = gr.Markdown(value=explore_schema(schemas, 0))
                
                def update_schema(index):
                    index = int(index)
                    if index < 0:
                        index = 0
                    if index > max_schema_index:
                        index = max_schema_index
                    return index, explore_schema(schemas, index), f"Schema {index + 1} of {max_schema_index + 1}"
                
                def prev_schema(index):
                    return update_schema(int(index) - 1)
                
                def next_schema(index):
                    return update_schema(int(index) + 1)
                
                schema_prev_btn.click(fn=prev_schema, inputs=schema_index, outputs=[schema_index, schema_md, schema_counter])
                schema_next_btn.click(fn=next_schema, inputs=schema_index, outputs=[schema_index, schema_md, schema_counter])
                schema_index.change(fn=update_schema, inputs=schema_index, outputs=[schema_index, schema_md, schema_counter])
            else:
                gr.Markdown("⚠️ Error: Could not load schema file or no schemas found.")
        
        # Dataset Overview Tab
        with gr.Tab("Project Overview"):
            gr.Markdown(get_dataset_stats(data))
            collection_chart, operator_chart = generate_charts(data)
            with gr.Row():
                gr.Plot(collection_chart)
                gr.Plot(operator_chart)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.launch()
