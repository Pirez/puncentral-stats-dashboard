#!/usr/bin/env python3
"""
CS2 Demo Processor
Combined script for downloading CS2 demos and parsing/uploading stats to API.

Modes:
1. download - Download demos from Steam
2. parse - Parse and upload demos to API
3. all - Download and then parse (default)
"""

import os
import sys
import argparse
from pathlib import Path

# Import functions from existing modules
from get_data import etl as download_demos, get_download_folder
from parse_demo import parse_demo_file, get_download_folder as parse_get_download_folder


def run_download_mode():
    """Download demos from Steam"""
    print("=" * 60)
    print("MODE: Download demos")
    print("=" * 60)
    download_demos()
    print("\nDownload completed!")


def run_parse_mode(api_url=None, api_token=None, use_api=True, cleanup=False, recursive=False):
    """Parse demos and upload to API or database"""
    print("=" * 60)
    print("MODE: Parse and upload demos")
    print("=" * 60)

    # Get download folder
    download_folder = get_download_folder()
    demo_path = Path(download_folder)

    if not demo_path.exists():
        print(f"Error: Download folder {demo_path} does not exist")
        return False

    # Collect demo files
    if recursive:
        demo_files = list(demo_path.rglob('*.dem'))
    else:
        demo_files = list(demo_path.glob('*.dem'))

    if not demo_files:
        print("No demo files found")
        return False

    print(f"Found {len(demo_files)} demo file(s)")

    # Process each demo
    successful = 0
    skipped = 0
    failed = 0

    for demo_file in sorted(demo_files):
        result = parse_demo_file(
            str(demo_file),
            use_api=use_api,
            api_url=api_url,
            api_token=api_token,
            cleanup=cleanup
        )

        if result:
            successful += 1
        elif result is False:
            skipped += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print("PARSE SUMMARY")
    print(f"{'='*60}")
    print(f"Total demos processed: {len(demo_files)}")
    print(f"Successfully uploaded: {successful}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="CS2 Demo Processor - Download and parse CS2 demos",
        epilog="""
Examples:
  # Download and parse demos (default)
  %(prog)s --api-url https://api.example.com --api-token YOUR_TOKEN

  # Only download demos
  %(prog)s --mode download

  # Only parse existing demos
  %(prog)s --mode parse --api-url https://api.example.com

  # Download, parse, and clean up demos after 3 hours
  %(prog)s --api-url https://api.example.com --clean

  # Use environment variables
  export steam_token=YOUR_STEAM_TOKEN
  export download_folder=/path/to/demos
  export CS2_API_URL=https://api.example.com
  export CS2_API_TOKEN=YOUR_TOKEN
  export clean=true
  %(prog)s
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--mode', choices=['download', 'parse', 'all'], default='all',
                       help='Operation mode: download demos, parse demos, or both (default: all)')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit (for Railway cron jobs)')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Recursively search for demo files when parsing')
    parser.add_argument('--database', '--db', action='store_true',
                       help='Upload directly to database instead of API')
    parser.add_argument('--api-url', type=str,
                       help='API server URL (default: from CS2_API_URL env var)')
    parser.add_argument('--api-token', type=str,
                       help='API authentication token (default: from CS2_API_TOKEN env var)')
    parser.add_argument('--clean', action='store_true',
                       help='Clean up demo files 3 hours after processing (default: from clean env var)')

    args = parser.parse_args()

    # Get configuration
    api_url = args.api_url or os.getenv('CS2_API_URL')
    api_token = args.api_token or os.getenv('CS2_API_TOKEN')
    use_api = not args.database
    cleanup = args.clean or os.getenv('clean', '').lower() == 'true'

    # Validate API configuration if needed
    if args.mode in ['parse', 'all'] and use_api and not api_url:
        print("Error: API mode requires --api-url or CS2_API_URL environment variable")
        print("Use --database flag to upload directly to database instead")
        sys.exit(1)

    # Print configuration
    print("=" * 60)
    print("CS2 DEMO PROCESSOR")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Download folder: {get_download_folder()}")

    if args.mode in ['parse', 'all']:
        if use_api:
            print(f"Upload mode: API ({api_url})")
            print(f"API token: {'configured' if api_token else 'not set'}")
        else:
            print("Upload mode: Direct database")

        if cleanup:
            print("Cleanup: Enabled (3 hours after processing)")
        else:
            print("Cleanup: Disabled")

    print("=" * 60)
    print()

    # Execute based on mode
    try:
        if args.mode == 'download':
            run_download_mode()
        elif args.mode == 'parse':
            run_parse_mode(
                api_url=api_url,
                api_token=api_token,
                use_api=use_api,
                cleanup=cleanup,
                recursive=args.recursive
            )
        elif args.mode == 'all':
            # First download
            run_download_mode()
            print()
            # Then parse
            run_parse_mode(
                api_url=api_url,
                api_token=api_token,
                use_api=use_api,
                cleanup=cleanup,
                recursive=args.recursive
            )

        print("\n" + "=" * 60)
        print("COMPLETED SUCCESSFULLY")
        print("=" * 60)

        # Exit successfully after one run (for Railway cron)
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
