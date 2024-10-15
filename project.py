from monpy.reader import Reader
from monpy.ui import UI
import argparse
import time


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

    return parser.parse_args()


def main():
    args = get_args()

    if args.output and not args.output.endswith(".csv"):
        raise ValueError("Output file needs to be a csv file")

    reader = Reader(farenheit=args.farenheit, output_file=args.output)
    ui = UI(theme=args.theme)
    ui.add_source("cpu_temp", "CPU temperature")
    ui.add_source("gpu_temp", "GPU temperature")

    while True:
        cpu_temp = reader.get_cpu_temp()
        gpu_temp = reader.get_gpu_temp()
        ui.append_data("cpu_temp", cpu_temp)
        ui.append_data("gpu_temp", gpu_temp)

        ui.draw()
        time.sleep(abs(args.interval))


if __name__ == "__main__":
    main()
