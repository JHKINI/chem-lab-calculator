"""
실험용 화학 계산기 - Streamlit 웹 화면

실행:  streamlit run app.py
계산 공식은 chemistry_core.py / 아래 각 함수 안에 원본 그대로 들어있다.
"""

import streamlit as st

from chemistry_core import (
    calculate_formula,
    mass_to_g,
    volume_to_l,
    volume_to_ml,
)

st.set_page_config(page_title="실험용 화학 계산기", page_icon="🧪", layout="centered")


# ─────────────────────────────────────────────
# 입력 도우미 (원본의 get_positive_float / get_mass_in_g 등을 웹 위젯으로 바꾼 것)
# ─────────────────────────────────────────────

def check_positive(*values):
    """원본 get_positive_float의 '0보다 큰 값' 검사. 버튼 누른 뒤에 호출한다."""
    for value in values:
        if value <= 0:
            raise ValueError("0보다 큰 값을 입력하세요.")


def float_input(label, key, value=1.0):
    return st.number_input(label, value=value, format="%g", key=key)


def mass_input(name, key):
    """값 + 단위(mg/g/kg)를 받아서 (g 단위 값, 입력한 원래 값)을 돌려준다."""
    col_value, col_unit = st.columns([2, 1])
    with col_value:
        value = float_input(f"{name} 값", key=f"{key}_value")
    with col_unit:
        unit = st.selectbox("단위", ["mg", "g", "kg"], index=1, key=f"{key}_unit")
    return mass_to_g(value, unit), value


def volume_l_input(name, key):
    """값 + 단위(mL/L)를 받아서 (L 단위 값, 입력한 원래 값)을 돌려준다."""
    col_value, col_unit = st.columns([2, 1])
    with col_value:
        value = float_input(f"{name} 값", key=f"{key}_value")
    with col_unit:
        unit = st.selectbox("단위", ["mL", "L"], index=1, key=f"{key}_unit")
    return volume_to_l(value, unit), value


def volume_ml_input(name, key):
    """값 + 단위(mL/L)를 받아서 (mL 단위 값, 입력한 원래 값)을 돌려준다."""
    col_value, col_unit = st.columns([2, 1])
    with col_value:
        value = float_input(f"{name} 값", key=f"{key}_value")
    with col_unit:
        unit = st.selectbox("단위", ["mL", "L"], index=0, key=f"{key}_unit")
    return volume_to_ml(value, unit), value


# ─────────────────────────────────────────────
# 메뉴별 화면 + 계산 (계산식은 원본 그대로)
# ─────────────────────────────────────────────

def formula_mass():
    st.subheader("화학식량 / 분자량 / 몰질량")
    formula = st.text_input("화학식 입력", placeholder="예: H2O, Ca(OH)2, CuSO4·5H2O", key="fm_formula")

    if st.button("계산", key="fm_btn"):
        result, steps = calculate_formula(formula)

        st.markdown("**계산 과정**")
        st.code(" + ".join(steps), language=None)
        st.success(f"화학식량 = {result:.3f}")
        st.write(f"분자량 = {result:.3f}")
        st.write(f"몰질량 = {result:.3f} g/mol")


def molarity():
    st.subheader("몰농도 M = mol / L")
    mole = float_input("용질 몰수(mol)", key="mo_mole")
    volume_l, _ = volume_l_input("용액 부피", key="mo_vol")

    if st.button("계산", key="mo_btn"):
        check_positive(mole, volume_l)
        result = mole / volume_l
        st.success(f"몰농도 = {result:.4f} M")


def molality():
    st.subheader("몰랄농도 m = mol / kg")
    mole = float_input("용질 몰수(mol)", key="ml_mole")
    solvent_g, _ = mass_input("용매 질량", key="ml_solvent")

    if st.button("계산", key="ml_btn"):
        check_positive(mole, solvent_g)
        solvent_kg = solvent_g / 1000
        result = mole / solvent_kg
        st.success(f"몰랄농도 = {result:.4f} m")


def normality():
    st.subheader("노르말농도 N = M × n-factor")
    molarity_value = float_input("몰농도(M)", key="no_m")
    n_factor = float_input("반응가수(n-factor)", key="no_n")

    if st.button("계산", key="no_btn"):
        check_positive(molarity_value, n_factor)
        result = molarity_value * n_factor
        st.success(f"노르말농도 = {result:.4f} N")


def mass_percent_ww():
    st.subheader("질량퍼센트 w/w %")
    solute_g, _ = mass_input("용질 질량", key="ww_solute")
    solution_g, _ = mass_input("용액 전체 질량", key="ww_solution")

    if st.button("계산", key="ww_btn"):
        check_positive(solute_g, solution_g)
        if solute_g > solution_g:
            raise ValueError("용질 질량이 전체 용액 질량보다 클 수 없습니다.")

        result = (solute_g / solution_g) * 100
        st.success(f"질량퍼센트(w/w %) = {result:.2f} %")


def mass_volume_percent_wv():
    st.subheader("w/v % = 용질 g / 용액 mL × 100")
    solute_g, _ = mass_input("용질 질량", key="wv_solute")
    solution_ml, _ = volume_ml_input("용액 부피", key="wv_solution")

    if st.button("계산", key="wv_btn"):
        check_positive(solute_g, solution_ml)
        result = (solute_g / solution_ml) * 100
        st.success(f"질량-부피 퍼센트(w/v %) = {result:.2f} %")


def required_mass():
    st.subheader("필요한 시약 질량 계산")
    formula = st.text_input("화학식 입력", placeholder="예: NaCl", key="rm_formula")
    molarity_value = float_input("목표 농도(M)", key="rm_m")
    volume_l, _ = volume_l_input("최종 부피", key="rm_vol")

    if st.button("계산", key="rm_btn"):
        molar_mass, _ = calculate_formula(formula)
        check_positive(molarity_value, volume_l)

        mole = molarity_value * volume_l
        mass = mole * molar_mass

        st.write(f"몰질량 = {molar_mass:.3f} g/mol")
        st.write(f"필요 몰수 = {molarity_value} × {volume_l} = {mole:.6f} mol")
        st.success(f"필요 질량 = {mole:.6f} × {molar_mass:.3f} = {mass:.6f} g")


def dilution():
    st.subheader("희석 계산 C1V1 = C2V2")
    c1 = float_input("원액 농도 C1", key="di_c1")
    c2 = float_input("목표 농도 C2", key="di_c2")
    v2_ml, _ = volume_ml_input("최종 부피 V2", key="di_v2")

    if st.button("계산", key="di_btn"):
        check_positive(c1, c2, v2_ml)
        if c2 >= c1:
            raise ValueError("희석에서는 원액 농도 C1이 목표 농도 C2보다 커야 합니다.")

        v1_ml = (c2 * v2_ml) / c1
        st.success(f"필요한 원액 부피 V1 = ({c2} × {v2_ml}) / {c1} = {v1_ml:.4f} mL")


def mass_to_mole():
    st.subheader("질량 → 몰수")
    formula = st.text_input("화학식 입력", placeholder="예: NaCl", key="mm_formula")
    mass_g, _ = mass_input("질량", key="mm_mass")

    if st.button("계산", key="mm_btn"):
        molar_mass, _ = calculate_formula(formula)
        check_positive(mass_g)

        mole = mass_g / molar_mass
        st.write(f"몰질량 = {molar_mass:.3f} g/mol")
        st.success(f"몰수 = {mass_g:.6f} / {molar_mass:.3f} = {mole:.6f} mol")


def mole_to_mass():
    st.subheader("몰수 → 질량")
    formula = st.text_input("화학식 입력", placeholder="예: NaCl", key="om_formula")
    mole = float_input("몰수(mol)", key="om_mole")

    if st.button("계산", key="om_btn"):
        molar_mass, _ = calculate_formula(formula)
        check_positive(mole)

        mass = mole * molar_mass
        st.write(f"몰질량 = {molar_mass:.3f} g/mol")
        st.success(f"질량 = {mole:.6f} × {molar_mass:.3f} = {mass:.6f} g")


def hydrate_correction():
    st.subheader("수화물 보정 질량 계산")
    anhydrous_formula = st.text_input("기준 무수염 화학식 입력", placeholder="예: CuSO4", key="hy_anhydrous")
    hydrate_formula = st.text_input("실제로 사용할 수화물 화학식 입력", placeholder="예: CuSO4·5H2O", key="hy_hydrate")
    target_mole = float_input("필요한 무수염 기준 몰수(mol)", key="hy_mole")

    if st.button("계산", key="hy_btn"):
        anhydrous_mw, _ = calculate_formula(anhydrous_formula)
        hydrate_mw, _ = calculate_formula(hydrate_formula)
        check_positive(target_mole)

        needed_mass = target_mole * hydrate_mw

        st.write(f"무수염 몰질량 = {anhydrous_mw:.3f} g/mol")
        st.write(f"수화물 몰질량 = {hydrate_mw:.3f} g/mol")
        st.success(f"필요한 수화물 질량 = {target_mole:.6f} × {hydrate_mw:.3f} = {needed_mass:.6f} g")


def yield_percent():
    st.subheader("수율 계산")
    actual_g, _ = mass_input("실제 수득량", key="yi_actual")
    theoretical_g, _ = mass_input("이론 수득량", key="yi_theory")

    if st.button("계산", key="yi_btn"):
        check_positive(actual_g, theoretical_g)
        result = (actual_g / theoretical_g) * 100
        st.success(f"수율 = ({actual_g:.6f} / {theoretical_g:.6f}) × 100 = {result:.2f} %")


def purity_correction():
    st.subheader("순도 보정 계산")
    pure_mass, _ = mass_input("이론적으로 필요한 질량", key="pu_mass")
    purity = float_input("시약 순도 입력 (%)", key="pu_purity", value=99.0)

    if st.button("계산", key="pu_btn"):
        check_positive(pure_mass)
        if purity <= 0 or purity > 100:
            raise ValueError("순도는 0~100 사이여야 합니다.")

        real_mass = pure_mass / (purity / 100)

        st.write(f"순도 = {purity}%")
        st.success(f"실제 달아야 할 질량 = {pure_mass:.6f} / ({purity}/100) = {real_mass:.6f} g")


def ppm_calculation():
    st.subheader("ppm 계산 (mg/L)")
    solute_mg = float_input("용질 질량 (mg)", key="pp_mg")
    volume_l, _ = volume_l_input("용액 부피", key="pp_vol")

    if st.button("계산", key="pp_btn"):
        check_positive(solute_mg, volume_l)
        ppm = solute_mg / volume_l
        st.success(f"ppm = {solute_mg:.6f} / {volume_l:.6f} = {ppm:.4f} ppm")


def density_conversion():
    st.subheader("밀도 기반 변환")
    choice = st.radio("변환 방향", ["mL → g 변환", "g → mL 변환"], key="de_choice")
    density = float_input("밀도 (g/mL)", key="de_density")

    if choice == "mL → g 변환":
        volume_ml, _ = volume_ml_input("부피", key="de_vol")
    else:
        mass_g, _ = mass_input("질량", key="de_mass")

    if st.button("계산", key="de_btn"):
        check_positive(density)

        if choice == "mL → g 변환":
            check_positive(volume_ml)
            mass = volume_ml * density
            st.success(f"질량 = {volume_ml:.4f} × {density} = {mass:.6f} g")
        else:
            check_positive(mass_g)
            volume = mass_g / density
            st.success(f"부피 = {mass_g:.6f} / {density} = {volume:.6f} mL")


def not_supported(feature_name):
    st.info(f"{feature_name} 기능은 현재 지원되지 않습니다. 추후 업데이트 예정입니다.")


# ─────────────────────────────────────────────
# 메뉴 목록 (원본 while 루프의 1~18번 메뉴)
# ─────────────────────────────────────────────

MENU = {
    "1. 화학식량 / 분자량 / 몰질량": formula_mass,
    "2. 몰농도(M)": molarity,
    "3. 몰랄농도(m)": molality,
    "4. 노르말농도(N)": normality,
    "5. 질량퍼센트(w/w %)": mass_percent_ww,
    "6. 질량-부피 퍼센트(w/v %)": mass_volume_percent_wv,
    "7. 필요한 시약 질량 계산": required_mass,
    "8. 희석 계산(C1V1=C2V2)": dilution,
    "9. 질량 → 몰수": mass_to_mole,
    "10. 몰수 → 질량": mole_to_mass,
    "11. 수화물 보정 질량": hydrate_correction,
    "12. 수율 계산": yield_percent,
    "13. 순도 보정": purity_correction,
    "14. ppm 계산": ppm_calculation,
    "15. 밀도 변환": density_conversion,
    "16. pH 계산 (미지원)": lambda: not_supported("pH 계산"),
    "17. ppb 계산 (미지원)": lambda: not_supported("ppb 계산"),
    "18. 대괄호 화학식 [] 지원 (미지원)": lambda: not_supported("대괄호 화학식 []"),
}

st.title("실험용 화학 계산기")

with st.sidebar:
    st.header("메뉴")
    selected = st.radio("계산 종류 선택", list(MENU.keys()), label_visibility="collapsed")

# 원본의 try / except ValueError / except Exception 과 같은 역할
try:
    MENU[selected]()
except ValueError as e:
    st.error(f"오류: {e}")
except Exception:
    st.error("입력 형식이 잘못되었습니다.")
