#!/usr/bin/env python3
"""
Mistral Fine-Tuning & Pixtral Multimodal Demo
==============================================

Demonstrate the advanced capabilities of Mistral AI integration including:
• Fine-tuning pipelines for custom model adaptation
• Pixtral vision-language model for multimodal interactions
• Custom dataset creation and management
• Model performance tracking and deployment
"""

import asyncio
import requests
import json
import time
from pathlib import Path
import sys

# Add the Arcade directory to the path
sys.path.insert(0, str(Path(__file__).parent))

async def demo_mistral_fine_tuning():
    """Demonstrate Mistral fine-tuning capabilities."""

    print("🧠 Mistral Fine-Tuning Integration Demo")
    print("=" * 45)

    base_url = "http://localhost:7681"

    # Check if server is running
    try:
        response = requests.get(f"{base_url}/arcade/status", timeout=5)
        if response.status_code != 200:
            print("❌ Enhanced Arcade Terminal not running!")
            print("Please start the server with: python -m arcade launch")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server!")
        print("Please start the server with: python -m arcade launch")
        return

    print("✅ Enhanced Arcade Terminal is running!")

    # Demo 1: System Capabilities
    print("\n1️⃣ Mistral System Capabilities")
    print("-" * 32)
    try:
        response = requests.get(f"{base_url}/mistral/capabilities")
        if response.status_code == 200:
            capabilities = response.json()
            print("   🤖 Fine-tuning Capabilities:"            print(f"   • Supported: {capabilities['fine_tuning']['supported']}")
            print(f"   • Task Types: {', '.join(capabilities['fine_tuning']['task_types'])}")
            print(f"   • Base Models: {', '.join(capabilities['fine_tuning']['base_models'])}")
            print(f"   • Max Dataset Size: {capabilities['fine_tuning']['max_dataset_size']}")
            print()

            print("   🖼️ Pixtral Capabilities:"            print(f"   • Supported: {capabilities['pixtral']['supported']}")
            print(f"   • Task Types: {', '.join(capabilities['pixtral']['task_types'])}")
            print(f"   • Supported Formats: {', '.join(capabilities['pixtral']['supported_formats'])}")
            print(f"   • Max Image Size: {capabilities['pixtral']['max_image_size']}")
            print()

            print("   📊 Current Status:"            print(f"   • Custom Models: {capabilities['custom_models']['total_models']}")
            print(f"   • Active Models: {capabilities['custom_models']['active_models']}")
            print(f"   • Total Datasets: {capabilities['datasets']['total_datasets']}")
            print(f"   • API Status: {capabilities['api_status']}")
        else:
            print(f"   ❌ Failed to get capabilities: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Capabilities check error: {e}")

    # Demo 2: Available Datasets
    print("\n2️⃣ Available Fine-Tuning Datasets")
    print("-" * 35)
    try:
        response = requests.get(f"{base_url}/mistral/datasets")
        if response.status_code == 200:
            datasets_data = response.json()
            print(f"   📚 Total Datasets: {datasets_data['total']}")

            for dataset in datasets_data['datasets'][:3]:
                print(f"   🗂️ {dataset['name']}")
                print(f"      Entries: {dataset['entry_count']}")
                print(f"      Categories: {', '.join(dataset['categories'])}")
        else:
            print(f"   ❌ Failed to get datasets: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Datasets check error: {e}")

    # Demo 3: Start Fine-Tuning Job
    print("\n3️⃣ Starting Fine-Tuning Job")
    print("-" * 27)
    try:
        job_data = {
            "model_name": "demo_code_model",
            "task_type": "code_generation",
            "dataset_id": "code_generation",
            "base_model": "mistral-7b-instruct",
            "hyperparameters": {
                "learning_rate": 2e-5,
                "batch_size": 8,
                "num_epochs": 3,
                "max_seq_length": 2048
            }
        }

        response = requests.post(f"{base_url}/mistral/finetune/job", json=job_data)

        if response.status_code == 200:
            job_result = response.json()
            job_id = job_result['job_id']
            print("   🎯 Fine-tuning job created successfully!"            print(f"   📋 Job ID: {job_id}")
            print(f"   🤖 Model Name: {job_result['model_name']}")
            print(f"   🎯 Task Type: {job_result['task_type']}")
            print(f"   📊 Status: {job_result['status']}")
            print(f"   ⚙️ Learning Rate: {job_result['hyperparameters']['learning_rate']}")
            print(f"   📅 Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(job_result['created_at']))}")
        else:
            print(f"   ❌ Failed to create fine-tuning job: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Fine-tuning job creation error: {e}")
        return

    # Demo 4: Check Fine-Tuning Status
    print("\n4️⃣ Monitoring Fine-Tuning Progress")
    print("-" * 35)
    try:
        response = requests.get(f"{base_url}/mistral/finetune/status/{job_id}")

        if response.status_code == 200:
            status = response.json()
            print("   📊 Fine-tuning Status:"            print(f"   📋 Job ID: {status['job_id']}")
            print(f"   🤖 Model Name: {status['model_name']}")
            print(f"   📈 Progress: {status['progress']}%")
            print(f"   📊 Status: {status['status']}")

            if status.get('completed_at'):
                duration = status['completed_at'] - status['created_at']
                print(f"   ⏱️ Duration: {duration:.2f} seconds")

            if status.get('metrics'):
                print(f"   📈 Metrics: {status['metrics']}")
        else:
            print(f"   ❌ Failed to get status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")

    # Demo 5: List Custom Models
    print("\n5️⃣ Custom Fine-Tuned Models")
    print("-" * 29)
    try:
        response = requests.get(f"{base_url}/mistral/models")
        if response.status_code == 200:
            models_data = response.json()
            print(f"   🤖 Total Custom Models: {models_data['total']}")

            if models_data['models']:
                for model in models_data['models']:
                    print(f"   🆔 {model['model_id'][:8]}...")
                    print(f"   📛 Name: {model['name']}")
                    print(f"   🎯 Task: {model['task_type']}")
                    print(f"   📊 Status: {model['status']}")
                    print(f"   🔢 Usage: {model['usage_count']} times")
                    print(f"   📈 Performance: {model['performance']}")
            else:
                print("   No custom models available yet. Complete a fine-tuning job first.")
        else:
            print(f"   ❌ Failed to get models: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Models check error: {e}")

    # Demo 6: Pixtral Image Analysis
    print("\n6️⃣ Pixtral Multimodal Analysis")
    print("-" * 30)
    try:
        # Use a sample image URL for demonstration
        pixtral_data = {
            "task_type": "image_description",
            "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&h=600&fit=crop",
            "text_prompt": "Describe this technology workspace in detail"
        }

        response = requests.post(f"{base_url}/pixtral/analyze", data=pixtral_data)

        if response.status_code == 200:
            analysis = response.json()
            print("   🖼️ Pixtral Image Analysis Complete!"            print(f"   🎯 Task Type: {analysis['task_type']}")
            print(f"   🖼️ Has Image: {analysis['has_image']}")
            print(f"   🎯 Confidence: {analysis['confidence_score']:.1%}")
            print(f"   ⏱️ Processing Time: {analysis['processing_time']:.2f}s")
            print(f"   📝 Analysis Preview: {analysis['response'][:150]}...")
        else:
            print(f"   ❌ Pixtral analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Pixtral analysis error: {e}")

    # Demo 7: Visual Question Answering
    print("\n7️⃣ Visual Question Answering with Pixtral")
    print("-" * 40)
    try:
        vqa_data = {
            "task_type": "visual_question_answering",
            "image_url": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop",
            "text_prompt": "What type of electronic device is shown in this image and what are its main features?"
        }

        response = requests.post(f"{base_url}/pixtral/analyze", data=vqa_data)

        if response.status_code == 200:
            vqa_result = response.json()
            print("   ❓ Visual Question Answering:"            print(f"   📝 Question: What type of electronic device...")
            print(f"   🎯 Confidence: {vqa_result['confidence_score']:.1%}")
            print(f"   💬 Answer: {vqa_result['response'][:200]}...")
        else:
            print(f"   ❌ VQA failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ VQA error: {e}")

    # Demo 8: Generate with Custom Model (if available)
    print("\n8️⃣ Custom Model Text Generation")
    print("-" * 33)
    try:
        # First check if we have any custom models
        models_response = requests.get(f"{base_url}/mistral/models")
        if models_response.status_code == 200:
            models_data = models_response.json()
            if models_data['models']:
                # Use the first available model
                model = models_data['models'][0]
                model_id = model['model_id']

                generation_data = {
                    "model_id": model_id,
                    "prompt": "Write a Python function to reverse a string",
                    "max_tokens": 200,
                    "temperature": 0.7
                }

                response = requests.post(f"{base_url}/mistral/generate", data=generation_data)

                if response.status_code == 200:
                    generation = response.json()
                    print("   🤖 Custom Model Generation:"                    print(f"   📝 Prompt: {generation['prompt']}")
                    print(f"   💻 Generated Code Preview: {generation['response'][:150]}...")
                else:
                    print(f"   ❌ Generation failed: {response.status_code}")
                    print("   This may be because the model is still training or not deployed.")
            else:
                print("   🤖 No custom models available for generation.")
                print("   Complete a fine-tuning job first, then the model will be available for generation.")
        else:
            print(f"   ❌ Could not check for custom models: {models_response.status_code}")
    except Exception as e:
        print(f"   ❌ Custom model generation error: {e}")

    print("\n🎉 Mistral Fine-Tuning & Pixtral Multimodal Demo Complete!")
    print("\n🧠 MISTRAL AI FEATURES:")
    print("   • Advanced fine-tuning pipelines for custom model adaptation")
    print("   • Pixtral vision-language model for multimodal interactions")
    print("   • Custom dataset creation and management")
    print("   • Real-time model performance tracking")
    print("   • Image analysis and visual question answering")
    print("   • Code generation and specialized task models")
    print("   • RESTful API for programmatic access")
    print("   • Terminal command integration")
    print("\n🚀 Mistral and Pixtral are now fully integrated for advanced AI capabilities!")

def show_terminal_commands():
    """Show terminal commands for Mistral fine-tuning and Pixtral."""

    print("💻 Mistral Fine-Tuning & Pixtral Terminal Commands")
    print("=" * 55)
    print()

    print("Fine-Tuning Management:")
    print("  mistral finetune <name> <task_type> [dataset]  # Start fine-tuning job")
    print("  mistral status <job_id>                        # Check job progress")
    print("  mistral models                                 # List custom models")
    print("  mistral datasets                               # List datasets")
    print()

    print("Fine-Tuning Task Types:")
    print("  • text_generation     - General text generation")
    print("  • instruction_tuning  - Follow instructions better")
    print("  • code_generation     - Programming code generation")
    print("  • domain_adaptation   - Specialize in specific domains")
    print()

    print("Pixtral Multimodal Analysis:")
    print("  pixtral analyze description <image_url>        # Describe image")
    print("  pixtral analyze vqa <image_url>               # Visual Q&A")
    print("  pixtral analyze ocr <image_url>               # Extract text")
    print("  pixtral ask <question> <image_url>            # Ask about image")
    print()

    print("Examples:")
    print("  # Start fine-tuning for code generation")
    print("  mistral finetune my_code_model code_generation")
    print()
    print("  # Check fine-tuning progress")
    print("  mistral status abc123-def456")
    print()
    print("  # Analyze an image")
    print("  pixtral analyze description https://example.com/image.jpg")
    print()
    print("  # Ask questions about an image")
    print("  pixtral ask 'What color is the car?' https://example.com/car.jpg")
    print()
    print("  # List available custom models")
    print("  mistral models")
    print()

    print("Note: Fine-tuning jobs may take time to complete.")
    print("Use 'mistral status <job_id>' to monitor progress.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "commands":
        show_terminal_commands()
    else:
        asyncio.run(demo_mistral_fine_tuning())
