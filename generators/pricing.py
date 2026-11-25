import random
from decimal import Decimal, ROUND_HALF_UP

from core.models import InputField, Task
from generators.base import BaseGenerator


class PricingGenerator(BaseGenerator):
    @property
    def category_id(self) -> str:
        return "pricing"

    @property
    def name(self) -> str:
        return "Bezugskalkulation"

    @staticmethod
    def _money(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _format_euro(value: Decimal) -> str:
        return f"{value:.2f}".replace(".", ",")

    def generate(self) -> Task:
        list_price = Decimal(str(random.choice((499.99, 899.00, 1299.99, 2499.00))))
        discount_rate = random.choice((5, 10, 15, 20))
        cash_discount_rate = random.choice((2, 3))
        procurement_costs = Decimal(str(random.choice((19.99, 49.90, 89.00, 129.00))))

        discount = self._money(list_price * Decimal(discount_rate) / Decimal(100))
        target_purchase_price = list_price - discount
        cash_discount = self._money(
            target_purchase_price * Decimal(cash_discount_rate) / Decimal(100)
        )
        cash_purchase_price = target_purchase_price - cash_discount
        landed_price = cash_purchase_price + procurement_costs

        fields = [
            InputField(
                "target_purchase_price",
                "Zieleinkaufspreis",
                float(target_purchase_price),
                unit="€",
                tolerance=0.05,
            ),
            InputField(
                "cash_purchase_price",
                "Bareinkaufspreis",
                float(cash_purchase_price),
                unit="€",
                tolerance=0.05,
            ),
            InputField(
                "landed_price",
                "Bezugspreis (Einstandspreis)",
                float(landed_price),
                unit="€",
                tolerance=0.05,
            ),
        ]
        solution_steps = [
            f"Listeneinkaufspreis: {self._format_euro(list_price)} €.",
            f"Lieferrabatt: {self._format_euro(list_price)} € × {discount_rate} % "
            f"= {self._format_euro(discount)} €.",
            f"Zieleinkaufspreis: {self._format_euro(list_price)} € − "
            f"{self._format_euro(discount)} € = {self._format_euro(target_purchase_price)} €.",
            f"Lieferskonto: {self._format_euro(target_purchase_price)} € × "
            f"{cash_discount_rate} % = {self._format_euro(cash_discount)} €.",
            f"Bareinkaufspreis: {self._format_euro(target_purchase_price)} € − "
            f"{self._format_euro(cash_discount)} € = {self._format_euro(cash_purchase_price)} €.",
            f"Bezugspreis: {self._format_euro(cash_purchase_price)} € + "
            f"{self._format_euro(procurement_costs)} € Bezugskosten = "
            f"{self._format_euro(landed_price)} €.",
        ]

        return Task(
            category=self.category_id,
            title=f"{self.name}: Hardware-Bestellung",
            description=(
                f"Ein IT-Betrieb bestellt Hardware zum Listeneinkaufspreis von "
                f"{self._format_euro(list_price)} €. Der Lieferant gewährt "
                f"{discount_rate} % Lieferrabatt und {cash_discount_rate} % Lieferskonto. "
                f"Die Bezugskosten betragen {self._format_euro(procurement_costs)} €. "
                "Berechne Zieleinkaufspreis, Bareinkaufspreis und Bezugspreis."
            ),
            fields=fields,
            solution_steps=solution_steps,
        )
