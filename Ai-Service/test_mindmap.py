import asyncio
from unittest.mock import patch
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.mind_map_service import generate_mind_map

mock_chunks = [
    "Machine learning (ML) is a field of inquiry devoted to understanding and building methods that 'learn', that is, methods that leverage data to improve performance on some set of tasks.",
    "It is seen as a part of artificial intelligence. Machine learning algorithms build a model based on sample data, known as training data, in order to make predictions or decisions without being explicitly programmed to do so.",
    "Supervised learning algorithms build a mathematical model of a set of data that contains both the inputs and the desired outputs.",
    "Unsupervised learning algorithms take a set of data that contains only inputs, and find structure in the data, like grouping or clustering of data points."
]

@patch("app.services.mind_map_service.get_document_chunks")
def run_test(mock_get_chunks):
    mock_get_chunks.return_value = mock_chunks
    print("Generating mind map based on mock chunks...")
    result = generate_mind_map("mock_user_id", "mock_doc_id")
    print("\n--- Result ---\n")
    print(result)

if __name__ == "__main__":
    run_test()
