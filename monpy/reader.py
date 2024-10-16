import psutil
import subprocess
import time
import csv
import os


class Reader:
    SUPPORTED_CPU_TEMP_DRIVERS = ["k10temp", "coretemp"]
    MAX_BUFFER_SIZE = 50

    def __init__(self, farenheit=False, output_file=None) -> None:
        self.farenheit = farenheit
        self.output_file = output_file
        self._detect_hardware()

        # The temperature buffer which holds the values.
        # Values are written in to .csv file when buffer sizes exceed
        # MAX_BUFFER_SIZE
        self.temp_buffer_size = 0
        self.temp_buffer = {} if output_file else None

    def __str__(self) -> str:
        return f"GPU: {self._gpu_vendor}, CPU_temp_driver: {self._cpu_temp_driver}"

    @property
    def temp_buffer(self):
        """The temp_buffer property."""
        return self._temp_buffer

    @temp_buffer.setter
    def temp_buffer(self, value):
        self._temp_buffer = value

        # If buffer size is over MAX_BUFFER_SIZE flush the contents in to a file
        if (
            self.output_file
            and type(self.temp_buffer) == dict
            and self.temp_buffer_size >= Reader.MAX_BUFFER_SIZE
        ):
            self._flush_buffers_to_file()

    def write_to_temp_buffer(self, key, value):

        # Make sure we write only to the buffer if output file
        # is present, else self.temp_buffer would be None
        # thereby causing errors
        if self.output_file:
            if key not in self.temp_buffer:
                self.temp_buffer[key] = [value]
            else:
                self.temp_buffer[key] = [*self.temp_buffer[key], value]

            self.temp_buffer = self.temp_buffer
            self.temp_buffer_size += 1

    def _flush_buffers_to_file(self):
        if self.output_file != None:
            try:
                file_exists = os.path.isfile(self.output_file)
                with open(self.output_file, "a") as file:
                    keys = sorted(self.temp_buffer.keys())
                    writer = csv.DictWriter(file, keys)

                    if not file_exists:
                        writer.writeheader()

                    list_sizes = int(self.temp_buffer_size / len(keys))

                    for i in range(list_sizes):
                        row = {}
                        for key in keys:
                            row[key] = self.temp_buffer[key][i]

                        writer.writerow(row)
                self._temp_buffer = {}
                self.temp_buffer_size = 0
            except Exception as error:
                print("Could not write buffer contents to a file.", error)

    def _detect_hardware(self):
        """
        Detects hardware and their respective drivers in use.
        """
        self._detect_cpu_temp_driver()
        self._detect_gpu_vendor()

    def _detect_cpu_temp_driver(self):
        """
        Detect the CPU temperature driver in use with
        psutils.sensors_temperatures()

        Currently supported drivers: k10temp
        """
        for sensor in psutil.sensors_temperatures().keys():
            if sensor in Reader.SUPPORTED_CPU_TEMP_DRIVERS:
                self._cpu_temp_driver = sensor
                return

        self._cpu_temp_driver = None

    def _detect_gpu_vendor(self):
        """
        Detect the graphic card's vendor.

        Currently supported: nvidia
        """

        # Excepting that the user uses nvidia's proprietary drivers
        try:
            if self._get_cmd_return_code("nvidia-smi") == 0:
                self._gpu_vendor = "nvidia"
        except FileNotFoundError:
            self._gpu_vendor = None

    def _get_cmd_return_code(self, cmd: str) -> int:
        return subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode

    def get_gpu_temp(self, buf_write=True):
        temp = 0.0

        match self._gpu_vendor:
            case "nvidia":
                output = str(
                    subprocess.check_output(
                        [
                            "nvidia-smi",
                            "--query-gpu=temperature.gpu",
                            "--format=csv,noheader",
                        ],
                    ).decode(encoding="utf-8")
                )

                try:
                    temp = float(output)
                except ValueError:
                    raise ValueError("Could not convert output to int")
            case "amd":
                pass
            case _:
                raise Exception("Unsupported GPU vendor")

        temp = temp if not self.farenheit else (temp * 9 / 5) + 32

        # Write value to the temperature buffer.
        if buf_write:
            self.write_to_temp_buffer("gpu_temp", temp)

        return temp

    def get_cpu_temp(self, buf_write=True):
        temp = 0.0

        match self._cpu_temp_driver:
            case "k10temp":
                try:
                    sensors = psutil.sensors_temperatures(fahrenheit=self.farenheit)
                    temp = round(sensors["k10temp"][0].current, ndigits=1)
                except KeyError as error:
                    raise error
            case "coretemp":
                sensors = psutil.sensors_temperatures(fahrenheit=self.farenheit)
                temp = round(sensors["coretemp"][0].current, ndigits=1)
            case _:
                raise Exception("Unsupported CPU temp driver")

        # Write value to the temperature buffer.
        if buf_write:
            self.write_to_temp_buffer("cpu_temp", temp)

        return temp

    def read_loop(self, interval=1):
        self._read_loop_running = True
        while self._read_loop_running:
            yield (self.get_cpu_temp(), self.get_gpu_temp())
            time.sleep(interval)

    def terminate_loop(self):
        self._read_loop_running = False


if __name__ == "__main__":
    reader = Reader(farenheit=False, output_file="statistics.csv")

    while True:
        reader.get_cpu_temp()
        reader.get_gpu_temp()
        time.sleep(1)
