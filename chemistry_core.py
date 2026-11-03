"""
실험용 화학 계산기 - 계산 로직 (원본 코드 그대로)

화면(input/print)과 상관없는 '계산 함수'만 모아둔 파일.
웹(Streamlit)에서도, 터미널에서도 그대로 가져다 쓸 수 있다.
"""

atomic_weights = {
    "H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999,
    "Na": 22.990, "Mg": 24.305, "Al": 26.982, "Si": 28.085,
    "P": 30.974, "S": 32.060, "Cl": 35.450, "K": 39.098,
    "Ca": 40.078, "Fe": 55.845, "Cu": 63.546, "Ba": 137.327,
    "Co": 58.933, "Ni": 58.693, "Zn": 65.380, "Mn": 54.938,
    "Ag": 107.868, "I": 126.904
}


def mass_to_g(value, unit):
    unit = unit.lower()
    if unit == "mg":
        return value / 1000
    elif unit == "g":
        return value
    elif unit == "kg":
        return value * 1000
    else:
        raise ValueError("질량 단위는 mg, g, kg 중 하나여야 합니다.")


def volume_to_l(value, unit):
    unit = unit.lower()
    if unit == "ml":
        return value / 1000
    elif unit == "l":
        return value
    else:
        raise ValueError("부피 단위는 mL 또는 L 중 하나여야 합니다.")


def volume_to_ml(value, unit):
    unit = unit.lower()
    if unit == "ml":
        return value
    elif unit == "l":
        return value * 1000
    else:
        raise ValueError("부피 단위는 mL 또는 L 중 하나여야 합니다.")


def validate_formula(formula):
    formula = formula.replace(" ", "")

    if formula == "":
        raise ValueError("화학식이 비어 있습니다.")

    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789().·"
    for ch in formula:
        if ch not in allowed:
            raise ValueError(f"허용되지 않는 문자: {ch}")

    for i in range(1, len(formula) - 1):
        if formula[i] == ".":
            if formula[i - 1].isdigit() and formula[i + 1].isdigit():
                raise ValueError(
                    "화학식 내부의 소수점 숫자는 허용하지 않습니다. "
                    "'.' 또는 '·'는 수화물 표시에만 사용하세요."
                )

    if formula.count("(") != formula.count(")"):
        raise ValueError("괄호 개수가 맞지 않습니다.")

    return formula


def parse_number(formula, i):
    num = ""
    while i < len(formula) and formula[i].isdigit():
        num += formula[i]
        i += 1
    return (int(num) if num else 1), i


def parse_formula(formula, i=0):
    total = 0
    steps = []

    while i < len(formula):
        ch = formula[i]

        if ch == "(":
            inside_mass, inside_steps, i = parse_formula(formula, i + 1)
            count, i = parse_number(formula, i)
            total += inside_mass * count
            steps.append(f"({' + '.join(inside_steps)}) × {count}")

        elif ch == ")":
            return total, steps, i + 1

        elif ch.isupper():
            element = ch
            i += 1

            if i < len(formula) and formula[i].islower():
                element += formula[i]
                i += 1

            if element not in atomic_weights:
                raise ValueError(f"{element} 원소의 원자량 정보가 없습니다.")

            count, i = parse_number(formula, i)
            mass = atomic_weights[element] * count
            total += mass
            steps.append(f"{element}({atomic_weights[element]}×{count})")

        else:
            raise ValueError(f"잘못된 화학식입니다: {ch}")

    return total, steps, i


def calculate_part(part):
    i = 0
    multiplier, i = parse_number(part, i)
    mass, steps, _ = parse_formula(part, i)

    if multiplier > 1:
        return mass * multiplier, [f"{multiplier} × ({' + '.join(steps)})"]
    return mass, steps


def calculate_formula(formula):
    formula = validate_formula(formula)
    formula = formula.replace("·", ".")
    parts = formula.split(".")

    total = 0
    all_steps = []

    for part in parts:
        part = part.strip()
        if part == "":
            continue
        part_mass, part_steps = calculate_part(part)
        total += part_mass
        all_steps.extend(part_steps)

    return total, all_steps
