import random
from core.models import InputField, Task
from generators.base import BaseGenerator


class TransferGenerator(BaseGenerator):
    @property
    def category_id(self) -> str:
        return "transfer"

    @property
    def name(self) -> str:
        return "Datenübertragung"

    def generate(self) -> Task:
        is_binary = random.choice([True, False])
        unit = "GiB" if is_binary else "GB"
        base = 1024 if is_binary else 1000
        file_size = random.choice([1, 2, 4, 5, 8, 10, 16, 25, 32, 50, 64, 100])
        bandwidth_mbits = random.choice([50, 100, 250, 500, 1000])
        bytes_in_unit = base ** 3
        file_size_bytes = file_size * bytes_in_unit
        transfer_rate_mb = bandwidth_mbits / 8.0
        bytes_per_second = bandwidth_mbits * 125_000
        duration_seconds = file_size_bytes / bytes_per_second
        duration_minutes = round(duration_seconds / 60.0, 2)

        fields = [
            InputField(
                key="transfer_rate_mb",
                label="Übertragungsrate",
                expected_value=transfer_rate_mb,
                unit="MB/s",
                tolerance=0.1,
            ),
            InputField(
                key="duration_seconds",
                label="Übertragungsdauer (Sekunden)",
                expected_value=round(duration_seconds, 2),
                unit="s",
                tolerance=1.0,
            ),
            InputField(
                key="duration_minutes",
                label="Übertragungsdauer (Minuten)",
                expected_value=duration_minutes,
                unit="min",
                tolerance=0.1,
            ),
        ]

        base_desc = "Binärsystem (Basis 1024, 1 GiB = 1024³ Byte)" if is_binary else "Dezimalsystem (Basis 1000, 1 GB = 1000³ Byte)"
        solution_steps = [
            f"Verwendete Basis: {base_desc}.",
            f"Dateigröße in Byte: {file_size} {unit} = {file_size} × {base}³ Byte = {file_size_bytes:,} Byte.",
            f"Übertragungsrate in MB/s: {bandwidth_mbits} Mbit/s ÷ 8 = {transfer_rate_mb} MB/s.",
            f"Übertragungsdauer in Sekunden: {file_size_bytes:,} Byte ÷ ({bandwidth_mbits} Mbit/s ÷ 8) = {duration_seconds:.2f} Sekunden.",
            f"Übertragungsdauer in Minuten: {duration_seconds:.2f} s ÷ 60 = {duration_minutes} Minuten.",
        ]

        return Task(
            category=self.category_id,
            title=f"{self.name}: {file_size} {unit} bei {bandwidth_mbits} Mbit/s",
            description=(
                f"Berechne für eine Datei der Größe {file_size} {unit} "
                f"(unter Verwendung der Basis {base}) und einer Bandbreite von {bandwidth_mbits} Mbit/s:\n"
                f"1. Die Übertragungsrate in MB/s\n"
                f"2. Die Übertragungsdauer in Sekunden\n"
                f"3. Die Übertragungsdauer in Minuten (auf 2 Dezimalstellen gerundet)"
            ),
            fields=fields,
            solution_steps=solution_steps,
        )
