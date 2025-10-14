#!/usr/bin/env python3
"""
CLI tool for running automation operations.

Usage:
    python automation/run_automation.py cleanup --analyze
    python automation/run_automation.py cleanup --auto
    python automation/run_automation.py ops test
    python automation/run_automation.py ops health_check
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automation.cleanup.project_cleaner import ProjectCleaner
from automation.standard_ops.ops_manager import OpsManager
from automation.utils.logger import AutomationLogger


def main():
    parser = argparse.ArgumentParser(
        description='UE5 AI Assistant Automation Suite')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    cleanup_parser = subparsers.add_parser('cleanup',
                                           help='Run cleanup operations')
    cleanup_parser.add_argument('--analyze',
                                action='store_true',
                                help='Analyze project for cleanup')
    cleanup_parser.add_argument('--auto',
                                action='store_true',
                                help='Run automatic cleanup')
    cleanup_parser.add_argument('--dry-run',
                                action='store_true',
                                default=True,
                                help='Dry run mode (default: True)')
    cleanup_parser.add_argument('--force',
                                action='store_true',
                                help='Force cleanup (disables dry-run)')
    cleanup_parser.add_argument('--attached-assets',
                                action='store_true',
                                help='Clean attached_assets directory')

    ops_parser = subparsers.add_parser('ops', help='Run standard operations')
    ops_parser.add_argument('operation',
                            choices=[
                                'test', 'test_backend', 'test_unit',
                                'test_integration', 'deploy_prepare',
                                'deploy_validate', 'health_check',
                                'update_dependencies', 'validate_structure'
                            ],
                            help='Operation to run')
    ops_parser.add_argument('--verbose',
                            action='store_true',
                            help='Verbose output')

    list_parser = subparsers.add_parser('list',
                                        help='List available operations')

    args = parser.parse_args()

    logger = AutomationLogger()

    if args.command == 'cleanup':
        run_cleanup(args, logger)
    elif args.command == 'ops':
        run_ops(args, logger)
    elif args.command == 'list':
        list_operations()
    else:
        parser.print_help()


def run_cleanup(args, logger):
    """Run cleanup operations."""
    logger.info("Starting cleanup operations")

    dry_run = args.dry_run and not args.force
    cleaner = ProjectCleaner(dry_run=dry_run)

    if args.analyze:
        print("=" * 80)
        print("📊 PROJECT CLEANUP ANALYSIS")
        print("=" * 80)

        report = cleaner.analyze_project()

        print(f"\n📍 Root Path: {report['root_path']}")
        print(f"⏰ Timestamp: {report['timestamp']}")
        print(f"💾 Total Size to Clean: {report['total_size_to_clean_mb']} MB")

        print("\n📂 Files by Category:")
        for category, info in report['categories'].items():
            safe_marker = "✅" if info['safe_auto_delete'] else "⚠️"
            print(f"  {safe_marker} {category}: {info['count']} files")

        if report['duplicates']:
            print(
                f"\n🔄 Duplicate Files: {len(report['duplicates'])} sets found")

        if report['large_files']:
            print("\n📦 Large Files (>5MB):")
            for file in report['large_files'][:5]:
                print(f"  - {file['path']} ({file['size_mb']} MB)")

        if report['empty_directories']:
            print(
                f"\n📁 Empty Directories: {len(report['empty_directories'])} found"
            )

        print("\n" + "=" * 80)

    elif args.auto:
        print("=" * 80)
        print(f"🧹 AUTOMATIC CLEANUP (dry_run={dry_run})")
        print("=" * 80)

        result = cleaner.auto_cleanup(force=args.force)

        print(f"\n✅ Deleted Files: {len(result['deleted_files'])}")
        print(f"✅ Deleted Directories: {len(result['deleted_dirs'])}")
        print(f"💾 Space Freed: {result['total_space_freed_mb']} MB")

        if result['errors']:
            print(f"\n❌ Errors: {len(result['errors'])}")
            for error in result['errors'][:5]:
                print(f"  - {error['path']}: {error['error']}")

        cleaner.save_cleanup_log()
        print("\n" + "=" * 80)

    elif args.attached_assets:
        print("=" * 80)
        print(f"🧹 CLEANING ATTACHED ASSETS (dry_run={dry_run})")
        print("=" * 80)

        result = cleaner.cleanup_attached_assets()

        print(f"\n✅ Deleted Files: {len(result['deleted_files'])}")
        for file in result['deleted_files']:
            print(f"  - {file}")
        print(f"💾 Space Freed: {result['total_space_freed_mb']} MB")

        print("\n" + "=" * 80)

    else:
        print(
            "Please specify an action: --analyze, --auto, or --attached-assets"
        )


def run_ops(args, logger):
    """Run standard operations."""
    logger.info(f"Running operation: {args.operation}")

    manager = OpsManager()

    print("=" * 80)
    print(f"🚀 RUNNING OPERATION: {args.operation}")
    print("=" * 80)

    try:
        result = manager.run_operation(args.operation, verbose=args.verbose)

        print(f"\n✅ Success: {result.get('success', False)}")

        if 'stdout' in result:
            print("\nOutput:")
            print(result['stdout'][:500] if len(result['stdout']) >
                  500 else result['stdout'])

        if 'checks' in result:
            print("\nChecks:")
            for check_name, check_result in result['checks'].items():
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")

        manager.save_ops_log()

    except Exception as e:
        logger.error(f"Operation failed: {e}")
        print(f"\n❌ Error: {e}")

    print("\n" + "=" * 80)


def list_operations():
    """List all available operations."""
    manager = OpsManager()
    ops = manager.get_available_operations()

    print("=" * 80)
    print("📋 AVAILABLE OPERATIONS")
    print("=" * 80)

    categories = {}
    for op in ops:
        category = op['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(op)

    for category, ops_list in categories.items():
        print(f"\n{category.upper()}:")
        for op in ops_list:
            print(f"  • {op['name']:<25} - {op['description']}")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
