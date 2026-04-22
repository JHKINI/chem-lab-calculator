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


def get_positive_float(msg):
    value = float(input(msg))
    if value <= 0:
        raise ValueError("0보다 큰 값을 입력하세요.")
    return value


def get_mass_in_g(name):
    value = get_positive_float(f"{name} 값 입력: ")
    unit = input(f"{name} 단위 입력 (mg/g/kg): ")
    return mass_to_g(value, unit)


def get_volume_in_l(name):
    value = get_positive_float(f"{name} 값 입력: ")
    unit = input(f"{name} 단위 입력 (mL/L): ")
    return volume_to_l(value, unit)


def get_volume_in_ml(name):
    value = get_positive_float(f"{name} 값 입력: ")
    unit = input(f"{name} 단위 입력 (mL/L): ")
    return volume_to_ml(value, unit)


def not_supported(feature_name):
    print("\n[안내]")
    print(f"{feature_name} 기능은 현재 지원되지 않습니다.")
    print("추후 업데이트 예정입니다.\n")


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


def formula_mass():
    print("\n[화학식량 / 분자량 / 몰질량]")
    formula = input("화학식 입력: ")
    result, steps = calculate_formula(formula)

    print("\n계산 과정:")
    print(" + ".join(steps))
    print(f"\n화학식량 = {result:.3f}")
    print(f"분자량 = {result:.3f}")
    print(f"몰질량 = {result:.3f} g/mol\n")


def molarity():
    print("\n[몰농도 M = mol / L]")
    mole = get_positive_float("용질 몰수(mol): ")
    volume_l = get_volume_in_l("용액 부피")
    result = mole / volume_l
    print(f"몰농도 = {result:.4f} M\n")


def molality():
    print("\n[몰랄농도 m = mol / kg]")
    mole = get_positive_float("용질 몰수(mol): ")
    solvent_g = get_mass_in_g("용매 질량")
    solvent_kg = solvent_g / 1000
    result = mole / solvent_kg
    print(f"몰랄농도 = {result:.4f} m\n")


def normality():
    print("\n[노르말농도 N = M × n-factor]")
    molarity_value = get_positive_float("몰농도(M): ")
    n_factor = get_positive_float("반응가수(n-factor): ")
    result = molarity_value * n_factor
    print(f"노르말농도 = {result:.4f} N\n")


def mass_percent_ww():
    print("\n[질량퍼센트 w/w %]")
    solute_g = get_mass_in_g("용질 질량")
    solution_g = get_mass_in_g("용액 전체 질량")

    if solute_g > solution_g:
        raise ValueError("용질 질량이 전체 용액 질량보다 클 수 없습니다.")

    result = (solute_g / solution_g) * 100
    print(f"질량퍼센트(w/w %) = {result:.2f} %\n")


def mass_volume_percent_wv():
    print("\n[w/v % = 용질 g / 용액 mL × 100]")
    solute_g = get_mass_in_g("용질 질량")
    solution_ml = get_volume_in_ml("용액 부피")

    result = (solute_g / solution_ml) * 100
    print(f"질량-부피 퍼센트(w/v %) = {result:.2f} %\n")


def required_mass():
    print("\n[필요한 시약 질량 계산]")
    formula = input("화학식 입력: ")
    molar_mass, _ = calculate_formula(formula)

    molarity_value = get_positive_float("목표 농도(M): ")
    volume_l = get_volume_in_l("최종 부피")

    mole = molarity_value * volume_l
    mass = mole * molar_mass

    print(f"\n몰질량 = {molar_mass:.3f} g/mol")
    print(f"필요 몰수 = {molarity_value} × {volume_l} = {mole:.6f} mol")
    print(f"필요 질량 = {mole:.6f} × {molar_mass:.3f} = {mass:.6f} g\n")


def dilution():
    print("\n[희석 계산 C1V1 = C2V2]")
    c1 = get_positive_float("원액 농도 C1: ")
    c2 = get_positive_float("목표 농도 C2: ")
    v2_ml = get_volume_in_ml("최종 부피 V2")

    if c2 >= c1:
        raise ValueError("희석에서는 원액 농도 C1이 목표 농도 C2보다 커야 합니다.")

    v1_ml = (c2 * v2_ml) / c1
    print(f"필요한 원액 부피 V1 = ({c2} × {v2_ml}) / {c1} = {v1_ml:.4f} mL\n")


def mass_to_mole():
    print("\n[질량 → 몰수]")
    formula = input("화학식 입력: ")
    molar_mass, _ = calculate_formula(formula)
    mass_g = get_mass_in_g("질량")

    mole = mass_g / molar_mass
    print(f"몰질량 = {molar_mass:.3f} g/mol")
    print(f"몰수 = {mass_g:.6f} / {molar_mass:.3f} = {mole:.6f} mol\n")


def mole_to_mass():
    print("\n[몰수 → 질량]")
    formula = input("화학식 입력: ")
    molar_mass, _ = calculate_formula(formula)
    mole = get_positive_float("몰수(mol): ")

    mass = mole * molar_mass
    print(f"몰질량 = {molar_mass:.3f} g/mol")
    print(f"질량 = {mole:.6f} × {molar_mass:.3f} = {mass:.6f} g\n")


def hydrate_correction():
    print("\n[수화물 보정 질량 계산]")
    anhydrous_formula = input("기준 무수염 화학식 입력: ")
    hydrate_formula = input("실제로 사용할 수화물 화학식 입력: ")
    target_mole = get_positive_float("필요한 무수염 기준 몰수(mol): ")

    anhydrous_mw, _ = calculate_formula(anhydrous_formula)
    hydrate_mw, _ = calculate_formula(hydrate_formula)

    needed_mass = target_mole * hydrate_mw

    print(f"\n무수염 몰질량 = {anhydrous_mw:.3f} g/mol")
    print(f"수화물 몰질량 = {hydrate_mw:.3f} g/mol")
    print(f"필요한 수화물 질량 = {target_mole:.6f} × {hydrate_mw:.3f} = {needed_mass:.6f} g\n")


def yield_percent():
    print("\n[수율 계산]")
    actual_g = get_mass_in_g("실제 수득량")
    theoretical_g = get_mass_in_g("이론 수득량")

    result = (actual_g / theoretical_g) * 100
    print(f"수율 = ({actual_g:.6f} / {theoretical_g:.6f}) × 100 = {result:.2f} %\n")


def purity_correction():
    print("\n[순도 보정 계산]")
    pure_mass = get_mass_in_g("이론적으로 필요한 질량")

    purity = float(input("시약 순도 입력 (%): "))
    if purity <= 0 or purity > 100:
        raise ValueError("순도는 0~100 사이여야 합니다.")

    real_mass = pure_mass / (purity / 100)

    print(f"\n순도 = {purity}%")
    print(f"실제 달아야 할 질량 = {pure_mass:.6f} / ({purity}/100) = {real_mass:.6f} g\n")


def ppm_calculation():
    print("\n[ppm 계산 (mg/L)]")
    solute_mg = get_positive_float("용질 질량 (mg): ")
    volume_l = get_volume_in_l("용액 부피")

    ppm = solute_mg / volume_l
    print(f"ppm = {solute_mg:.6f} / {volume_l:.6f} = {ppm:.4f} ppm\n")


def density_conversion():
    print("\n[밀도 기반 변환]")
    print("1. mL → g 변환")
    print("2. g → mL 변환")

    choice = input("선택: ")
    density = get_positive_float("밀도 (g/mL): ")

    if choice == "1":
        volume_ml = get_volume_in_ml("부피")
        mass = volume_ml * density
        print(f"\n질량 = {volume_ml:.4f} × {density} = {mass:.6f} g\n")

    elif choice == "2":
        mass_g = get_mass_in_g("질량")
        volume = mass_g / density
        print(f"\n부피 = {mass_g:.6f} / {density} = {volume:.6f} mL\n")

    else:
        print("잘못된 선택입니다.\n")


while True:
    print("======== 실험용 화학 계산기 ========")
    print("1. 화학식량 / 분자량 / 몰질량")
    print("2. 몰농도(M)")
    print("3. 몰랄농도(m)")
    print("4. 노르말농도(N)")
    print("5. 질량퍼센트(w/w %)")
    print("6. 질량-부피 퍼센트(w/v %)")
    print("7. 필요한 시약 질량 계산")
    print("8. 희석 계산(C1V1=C2V2)")
    print("9. 질량 → 몰수")
    print("10. 몰수 → 질량")
    print("11. 수화물 보정 질량")
    print("12. 수율 계산")
    print("13. 순도 보정")
    print("14. ppm 계산")
    print("15. 밀도 변환")
    print("16. pH 계산 (미지원)")
    print("17. ppb 계산 (미지원)")
    print("18. 대괄호 화학식 [] 지원 (미지원)")
    print("0. 종료")

    menu = input("메뉴 선택: ")

    try:
        if menu == "1":
            formula_mass()
        elif menu == "2":
            molarity()
        elif menu == "3":
            molality()
        elif menu == "4":
            normality()
        elif menu == "5":
            mass_percent_ww()
        elif menu == "6":
            mass_volume_percent_wv()
        elif menu == "7":
            required_mass()
        elif menu == "8":
            dilution()
        elif menu == "9":
            mass_to_mole()
        elif menu == "10":
            mole_to_mass()
        elif menu == "11":
            hydrate_correction()
        elif menu == "12":
            yield_percent()
        elif menu == "13":
            purity_correction()
        elif menu == "14":
            ppm_calculation()
        elif menu == "15":
            density_conversion()
        elif menu == "16":
            not_supported("pH 계산")
        elif menu == "17":
            not_supported("ppb 계산")
        elif menu == "18":
            not_supported("대괄호 화학식 []")
        elif menu == "0":
            print("프로그램 종료")
            break
        else:
            print("올바른 번호를 입력하세요.\n")

    except ValueError as e:
        print("오류:", e, "\n")
    except Exception:
        print("입력 형식이 잘못되었습니다.\n")