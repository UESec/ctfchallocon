from flask import Flask, render_template, request
import html
import random
import time

app = Flask(__name__)


def fake_reactor_reading():
    return round(random.uniform(1.00, 7.92), 2)


def fake_batch_code():
    return f"OCB-{random.randint(1000, 9999)}-{random.choice(['A', 'B', 'C', 'R'])}"


def run_formula_engine(formula: str):
    """
    Intentionally vulnerable CTF logic.

    The calculator is supposed to normalize formula notes to uppercase.
    The implementation evaluates a Python expression that wraps user input.
    This keeps the reverse-shell challenge behavior intact.
    """

    expression = f"'{formula}'.upper()"
    return eval(expression)


@app.route("/")
def challenge():
    return render_template("challenge.html")


@app.route("/calculator", methods=["GET"])
def calculator():
    return render_template(
        "index.html",
        formula="5L orangejuice + 5gr orangium",
        result=None,
        status=None,
        enrichment=None,
        batch=None,
    )


@app.route("/calculate", methods=["POST"])
def calculate():
    formula = request.form.get("formula", "")

    status = {
        "core": random.choice(["STABLE", "WARM", "WATCH"]),
        "coolant": random.choice(["OK", "OK", "LOW FLOW"]),
        "redis": random.choice(["SYNC", "SYNC", "QUEUE"]),
        "valve": random.choice(["LOCKED", "LOCKED", "CHECK"]),
    }

    try:
        result = run_formula_engine(formula)

        if isinstance(result, tuple):
            safe_result = (
                "Batch queued for internal validation.\n"
                "No printable formula returned by enrichment worker."
            )
        else:
            safe_result = str(result)

        return render_template(
            "index.html",
            formula=formula,
            result=safe_result,
            status=status,
            enrichment=8.00,
            batch=fake_batch_code(),
        )

    except Exception:
        enrichment = fake_reactor_reading()

        fake_messages = [
            "Batch rejected by Citrus Critical Control. Enrichment drift detected.",
            "Formula accepted by parser, but reactor balance stayed below target.",
            "Orange cake mix is unstable. Adjust juice ratio and retry.",
            "Validation worker returned incomplete enrichment telemetry.",
            "Redis formula queue delayed the batch. Current mix is below 8 percent.",
        ]

        fake_output = (
            f"{random.choice(fake_messages)}\n\n"
            f"Measured enrichment: {enrichment}%\n"
            f"Target enrichment: 8.00%\n"
            f"Batch reference: {fake_batch_code()}\n"
            "Operator note: formula normalization completed, but validation did not approve the mix."
        )

        time.sleep(0.2)

        return render_template(
            "index.html",
            formula=formula,
            result=fake_output,
            status=status,
            enrichment=enrichment,
            batch=fake_batch_code(),
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
