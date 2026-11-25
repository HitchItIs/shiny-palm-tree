import random

from core.models import InputField, Task
from generators.base import BaseGenerator


class NumeralGenerator(BaseGenerator):
    @property
    def category_id(self) -> str:
        return "numerals"

    @property
    def name(self) -> str:
        return "Zahlensysteme (Dez/Bin/Hex)"

    def generate(self) -> Task:
        source_system = random.choice(("Dezimalzahl", "Binärzahl", "Hexadezimalzahl"))
        number = random.randint(16, 4095)
        binary = format(number, "b")
        hexadecimal = format(number, "X")

        if source_system == "Dezimalzahl":
            given_value = str(number)
            targets = (("binary", "Binärzahl", binary), ("hexadecimal", "Hexadezimalzahl", hexadecimal))
        elif source_system == "Binärzahl":
            given_value = binary
            targets = (("decimal", "Dezimalzahl", str(number)), ("hexadecimal", "Hexadezimalzahl", hexadecimal))
        else:
            given_value = hexadecimal
            targets = (("decimal", "Dezimalzahl", str(number)), ("binary", "Binärzahl", binary))

        fields = [
            InputField(key, label, expected)
            for key, label, expected in targets
        ]
        padded_binary = binary.zfill(((len(binary) + 3) // 4) * 4)
        binary_groups = " ".join(
            padded_binary[index:index + 4]
            for index in range(0, len(padded_binary), 4)
        )
        solution_steps = [
            f"Ausgangszahl: {given_value} ({source_system}). Der Zahlenwert beträgt {number} im Dezimalsystem.",
            f"Binärumrechnung: wiederholte Division durch 2 mit Resten von unten nach oben ergibt {binary}.",
            f"Hexadezimalumrechnung: Binärzahl in 4-Bit-Blöcke gliedern: {binary_groups}. "
            f"Die Blöcke entsprechen den Hex-Ziffern {hexadecimal}.",
            f"Ergebnis: {', '.join(f'{label}: {value}' for _, label, value in targets)}.",
        ]

        return Task(
            category=self.category_id,
            title=f"{self.name}: {source_system}",
            description=(
                f"Gegeben ist die Zahl {given_value} im System {source_system}. "
                "Wandle sie in die beiden anderen Zahlensysteme um. "
                "Gib Binär- und Hexadezimalzahlen ohne Präfix an."
            ),
            fields=fields,
            solution_steps=solution_steps,
        )
