from monpy.reader import Reader
from monpy.ui import UI
import argparse
import time
import sys


def get_args():
    parser = argparse.ArgumentParser(
        prog="MonPy",
        description="Simple to use terminal based system temperature monitor.",
    )

    parser.add_argument(
        "-i",
        "--interval",
        help="Poll for new temperature data in x second intervals",
        default=1,
        type=int,
    )

    parser.add_argument(
        "-o", "--output", help="Output file name to write recorded data to.", type=str
    )

    parser.add_argument(
        "-f",
        "--farenheit",
        help="Display temperatures in farenheit",
        action="store_true",
    )

    parser.add_argument(
        "-t",
        "--theme",
        help="Specify TUI theme",
        default="pro",
        type=str,
    )

    parser.add_argument(
        "--list-themes", help="List all the available TUI themes", action="store_true"
    )

    parser.add_argument(
        "-c", "--current", help="Display the current temperature", action="store_true"
    )

    parser.add_argument(
        "-p",
        "--peak",
        help="Display the peak temperature",
        action="store_true",
    )

    parser.add_argument(
        "-m",
        "--modules",
        help="""Specify explicitly which hardware components to monitor.
        This sould be a comma separated list of values,
        see all available modules with --list-modules""",
        default="gpu,cpu",
    )

    parser.add_argument(
        "--list-modules", help="List all available modules", action="store_true"
    )

    return parser.parse_args()


def main():
    args = get_args()

    reader = Reader(farenheit=args.farenheit, output_file=args.output)
    ui = UI(theme=args.theme)

    if args.output and not args.output.endswith(".csv"):
        raise ValueError("Output file needs to be a csv file")

    if args.list_themes:
        valid_themes = UI().VALID_THEMES
        print(", ".join(valid_themes))
        sys.exit(0)

    if args.list_modules:
        print("Available modules for your system:", ", ".join(reader.modules))
        sys.exit(0)

    modules = []

    for module in args.modules.split(","):
        if module.strip() in reader.modules:
            modules.append(module)

    for module in modules:
        ui.add_source(module, peak=args.peak, current=args.current)

    while True:
        try:
            for module in modules:
                match module:
                    case "cpu":
                        cpu_temp = reader.get_cpu_temp()
                        ui.append_data("cpu_temp", cpu_temp)
                    case "gpu":
                        gpu_temp = reader.get_gpu_temp()
                        ui.append_data("gpu_temp", gpu_temp)

            ui.draw()
            time.sleep(abs(args.interval))
        except KeyboardInterrupt:
            match input("\nDo you want to stop monitoring [y/n]: "):
                case "y":
                    reader.cleanup()
                    break
                case _:
                    continue


if __name__ == "__main__":
    main()
