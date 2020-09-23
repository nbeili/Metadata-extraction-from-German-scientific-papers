from pubmex.pubmexinference import *
import argparse
from PIL import Image
import json
import os

def get_parser():
    parser = argparse.ArgumentParser(description="Demo of our model for automatic Metadata Extraction from Scientific Publications.")
    parser.add_argument("input", metavar="FILE", nargs=1, help="The input PDF the model should be called with.")
    parser.add_argument("output", metavar="PATH", nargs=1, help="The path to which the model's output should be saved. The model will generate a JPEG and a JSON file.")
    parser.add_argument("--use_cuda", default=False, metavar="BOOLEAN", help="Whether or not to use CUDA (Boolean). Defaults to False. If set to False, the model will be called using the CPU. Setting this option to True requires the device to support CUDA.")
    parser.add_argument("--config-file", default="configs/train_config.yaml", metavar="FILE", help="path to config file")
    parser.add_argument("--model-dump", default="models/model_final.pth", metavar="FILE", help="path to the model (.pth)")

    return parser

if __name__ == "__main__":
    args = get_parser().parse_args()

    print("Loading model...")
    pubmex = PubMexInference(
        model_dump=args.model_dump,
        config_file=args.config_file,
        use_cuda=args.use_cuda
    )

    filename = args.input[0].split("/")[-1]
    print("Calling model with {}".format(filename))
    v, metadata = pubmex.predict(args.input[0])
    img = Image.fromarray(v.get_image()[:, :, ::-1])
    
    img.save(args.output[0] + filename[:-4] + ".jpg")
    
    with open(args.output[0] + filename[:-4] + ".json", "w") as f:
        json.dump(metadata, f)

    print("Successfully saved output to {}".format(os.path.abspath(args.output[0])))