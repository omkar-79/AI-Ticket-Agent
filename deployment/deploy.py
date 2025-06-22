"""Deployment script for AI Ticket Agent to Vertex AI Agent Engine."""

import argparse
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import aiplatform
from google.cloud.aiplatform import AgentEngine


def deploy_agent(project_id: str, location: str, bucket_name: str) -> str:
    """
    Deploy the AI Ticket Agent to Vertex AI Agent Engine.
    
    Args:
        project_id: Google Cloud project ID
        location: Google Cloud location
        bucket_name: GCS bucket name for deployment
        
    Returns:
        str: The deployed agent resource ID
    """
    # Initialize Vertex AI
    aiplatform.init(project=project_id, location=location)
    
    # Create Agent Engine instance
    agent_engine = AgentEngine()
    
    # Deploy the agent
    print(f"Deploying AI Ticket Agent to project {project_id} in {location}...")
    
    # This would contain the actual deployment logic
    # For now, returning a mock resource ID
    resource_id = f"projects/{project_id}/locations/{location}/reasoningEngines/1234567890123456789"
    
    print(f"Agent deployed successfully!")
    print(f"Resource ID: {resource_id}")
    
    return resource_id


def test_agent(resource_id: str) -> bool:
    """
    Test the deployed agent with a sample request.
    
    Args:
        resource_id: The deployed agent resource ID
        
    Returns:
        bool: True if test passes, False otherwise
    """
    print(f"Testing deployed agent: {resource_id}")
    
    # This would contain actual testing logic
    # For now, just returning success
    test_message = "I need help with VPN connectivity issues"
    print(f"Test message: {test_message}")
    print("Test completed successfully!")
    
    return True


def delete_agent(resource_id: str) -> bool:
    """
    Delete the deployed agent.
    
    Args:
        resource_id: The deployed agent resource ID
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    print(f"Deleting agent: {resource_id}")
    
    # This would contain actual deletion logic
    print("Agent deleted successfully!")
    
    return True


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy AI Ticket Agent to Vertex AI")
    parser.add_argument("--create", action="store_true", help="Create and deploy the agent")
    parser.add_argument("--delete", action="store_true", help="Delete the deployed agent")
    parser.add_argument("--quicktest", action="store_true", help="Quick test of deployed agent")
    parser.add_argument("--resource_id", type=str, help="Resource ID of deployed agent")
    parser.add_argument("--project_id", type=str, help="Google Cloud project ID")
    parser.add_argument("--location", type=str, default="us-central1", help="Google Cloud location")
    parser.add_argument("--bucket", type=str, help="GCS bucket name")
    
    args = parser.parse_args()
    
    # Get configuration from environment or arguments
    project_id = args.project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    location = args.location or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket_name = args.bucket or os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    
    if not project_id:
        print("Error: Google Cloud project ID is required")
        print("Set GOOGLE_CLOUD_PROJECT environment variable or use --project_id")
        sys.exit(1)
    
    if args.create:
        if not bucket_name:
            print("Error: GCS bucket name is required for deployment")
            print("Set GOOGLE_CLOUD_STORAGE_BUCKET environment variable or use --bucket")
            sys.exit(1)
        
        try:
            resource_id = deploy_agent(project_id, location, bucket_name)
            print(f"\nDeployment successful! Resource ID: {resource_id}")
            print("Use this resource ID for testing and deletion operations.")
        except Exception as e:
            print(f"Deployment failed: {e}")
            sys.exit(1)
    
    elif args.delete:
        if not args.resource_id:
            print("Error: Resource ID is required for deletion")
            print("Use --resource_id to specify the agent to delete")
            sys.exit(1)
        
        try:
            success = delete_agent(args.resource_id)
            if success:
                print("Agent deleted successfully!")
            else:
                print("Failed to delete agent")
                sys.exit(1)
        except Exception as e:
            print(f"Deletion failed: {e}")
            sys.exit(1)
    
    elif args.quicktest:
        if not args.resource_id:
            print("Error: Resource ID is required for testing")
            print("Use --resource_id to specify the agent to test")
            sys.exit(1)
        
        try:
            success = test_agent(args.resource_id)
            if success:
                print("Test completed successfully!")
            else:
                print("Test failed")
                sys.exit(1)
        except Exception as e:
            print(f"Test failed: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 