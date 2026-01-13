import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()
from src.modules.disease.workflow import app as workflow_app
from langchain_core.messages import HumanMessage

def debug_invoke():
    print("Invoking workflow with 'Use model PGS000025'...")
    inputs = {
        "messages": [HumanMessage(content="Use model PGS000025")]
    }
    try:
        result = workflow_app.invoke(inputs)
        print("Success!")
        print(f"Result Next Node: {result.get('next_node')}")
        print(f"Messages: {result.get('messages')}")
    except Exception as e:
        print("Exception occurred:")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_invoke()
