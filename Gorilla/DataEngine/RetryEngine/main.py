import argparse
from RetryEngine import RetryEngine

def main():
    parser = argparse.ArgumentParser(description='Run the RetryEngine with the provided API key, input path, and output path.')
    parser.add_argument('api_key', type=str, help='OpenAI API key')
    parser.add_argument('input_path', type=str, help='Path to input JSON file')
    parser.add_argument('output_path', type=str, help='Path to save the output JSON file')
    
    args = parser.parse_args()
    
    engine = RetryEngine(api_key=args.api_key, input_path=args.input_path, output_path=args.output_path)
    engine.Run()

if __name__ == '__main__':
    main()
