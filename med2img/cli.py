import argparse
from .pipeline import process_directory

def main():
    parser = argparse.ArgumentParser(description='Convert DICOM to PNG/JPG')
    parser.add_argument('input', help='Input directory or file')
    parser.add_argument('-o', '--output', default=None,
                        help='Output base directory (default: patient/study/view)')
    parser.add_argument('-f', '--format', choices=['jpg', 'png'], default='jpg')
    parser.add_argument('-w', '--workers', type=int, default=1,
                        help='Number of parallel workers')
    args = parser.parse_args()

    out_base = args.output or ''  # pipeline will handle default tree
    process_directory(args.input, out_base, args.format, args.workers)

if __name__ == '__main__':
    main()