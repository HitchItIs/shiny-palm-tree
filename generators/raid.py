import random
from core.models import InputField, Task
from generators.base import BaseGenerator


class RaidGenerator(BaseGenerator):
    @property
    def category_id(self) -> str:
        return "raid"

    @property
    def name(self) -> str:
        return "RAID-Kalkulator"

    def generate(self) -> Task:
        raid_level = random.choice([0, 1, 5, 6, 10])
        disk_size = random.choice([1, 2, 4, 8, 12])

        if raid_level == 0:
            num_disks = self._gauss_int(2, 6)
            gross = num_disks * disk_size
            net = num_disks * disk_size
            max_failed = 0
            efficiency = 100.0
            formula_net = f"{num_disks} × {disk_size} TB (keine Redundanz)"
        elif raid_level == 1:
            num_disks = 2
            gross = num_disks * disk_size
            net = disk_size
            max_failed = num_disks - 1
            efficiency = round((net / gross) * 100, 1)
            formula_net = f"1 × {disk_size} TB (Spiegelung)"
        elif raid_level == 5:
            num_disks = self._gauss_int(3, 8)
            gross = num_disks * disk_size
            net = (num_disks - 1) * disk_size
            max_failed = 1
            efficiency = round((net / gross) * 100, 1)
            formula_net = f"({num_disks} - 1) × {disk_size} TB (1 Paritätsplatte)"
        elif raid_level == 6:
            num_disks = self._gauss_int(4, 8)
            gross = num_disks * disk_size
            net = (num_disks - 2) * disk_size
            max_failed = 2
            efficiency = round((net / gross) * 100, 1)
            formula_net = f"({num_disks} - 2) × {disk_size} TB (2 Paritätsplatten)"
        elif raid_level == 10:
            num_disks = random.choice([4, 6, 8])
            gross = num_disks * disk_size
            net = (num_disks // 2) * disk_size
            max_failed = 1  # Worst-case as specified
            efficiency = round((net / gross) * 100, 1)
            formula_net = f"({num_disks} ÷ 2) × {disk_size} TB (Kombination aus RAID 1 und 0)"
        else:
            num_disks = 2
            gross = 2 * disk_size
            net = disk_size
            max_failed = 1
            efficiency = 50.0
            formula_net = ""

        fields = [
            InputField(
                key="gross_capacity",
                label="Bruttokapazität",
                expected_value=gross,
                unit="TB",
                tolerance=0.0,
            ),
            InputField(
                key="net_capacity",
                label="Nettokapazität",
                expected_value=net,
                unit="TB",
                tolerance=0.0,
            ),
            InputField(
                key="max_failed_disks",
                label="Maximal ausfallende Festplatten",
                expected_value=max_failed,
                unit="",
                tolerance=0.0,
            ),
            InputField(
                key="efficiency",
                label="Nutzbare Kapazität (Effizienz)",
                expected_value=efficiency,
                unit="%",
                tolerance=0.2,
            ),
        ]

        solution_steps = [
            f"Gewähltes RAID-Level: RAID {raid_level} mit {num_disks} Festplatten à {disk_size} TB.",
            f"Bruttokapazität: {num_disks} × {disk_size} TB = {gross} TB.",
            f"Nettokapazität (Nutzbare Kapazität): {formula_net} = {net} TB.",
            f"Maximal sicher ausfallende Festplatten (im Worst-Case): {max_failed}.",
            f"Effizienz / Nutzbare Kapazität: ({net} TB ÷ {gross} TB) × 100% = {efficiency}%.",
        ]

        return Task(
            category=self.category_id,
            title=f"{self.name}: RAID {raid_level} ({num_disks} × {disk_size} TB)",
            description=(
                f"Gegeben ist ein RAID-{raid_level}-Verbund bestehend aus {num_disks} Festplatten "
                f"mit jeweils {disk_size} TB Kapazität.\n"
                f"Bestimme:\n"
                f"1. Die Bruttokapazität in TB\n"
                f"2. Die Nettokapazität in TB\n"
                f"3. Die maximal sicher ausfallenden Festplatten (im Worst-Case)\n"
                f"4. Die nutzbare Kapazität in Prozent (Effizienz, auf 1 Nachkommastelle gerundet)"
            ),
            fields=fields,
            solution_steps=solution_steps,
        )
