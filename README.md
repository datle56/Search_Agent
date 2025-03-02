# Search Agent using Directed Acyclic Graph (DAG)

## Demo Video

A demonstration of the system's functionality can be viewed below:

https://github.com/user-attachments/assets/c304da8b-093e-48c6-b4da-8d3bb0f392f1

## Overview

This project implements a Search Agent that utilizes a Directed Acyclic Graph (DAG) to structure and explore search results. The agent leverages Google Search to gather initial information and then builds a DAG where:

- Nodes represent concepts or key topics.
- Edges define relationships between these concepts.

LLM (Large Language Model) is used to expand and enrich the content, providing a deeper understanding of each component.

## Features

- **Automated Web Search**: Uses Google Search to retrieve relevant information.
- **DAG-based Knowledge Representation**: Constructs a directed acyclic graph to represent relationships between concepts.
- **LLM-powered Expansion**: Enhances node content using a large language model to provide deeper insights.
- **Hierarchical Exploration**: Allows structured traversal of search results for better comprehension.
- **Demo Video Available**: A demonstration of the system's functionality can be found in [video/demo.mp4](video/demo.mp4).


## How It Works

1. **Google Search**: The agent retrieves top search results for the query.
2. **Node Creation**: Extracts key concepts and creates nodes in the DAG.
3. **Edge Definition**: Establishes relationships between nodes based on context.
4. **LLM Expansion**: Uses an LLM to enhance each node with deeper insights.
5. **Graph Output**: The final DAG structure is visualized and stored.

## Example Output

If the search query is "Machine Learning", the DAG may look like:

```
Machine Learning
├── Supervised Learning
│   ├── Regression
│   ├── Classification
├── Unsupervised Learning
│   ├── Clustering
│   ├── Dimensionality Reduction
```

Each node will have additional insights provided by the LLM.

## Future Enhancements

- Implement a web-based interface for interactive exploration.
- Integrate additional search engines for broader knowledge retrieval.
- Improve LLM prompt engineering for richer content expansion.
