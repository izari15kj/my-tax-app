import streamlit as st
# --------------------------------------------------
# パスワード保護設定
# --------------------------------------------------
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🔒 閲覧制限")
    password = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if password == "1108":  # ← 💡 友達に教える好きなパスワードに変更してください
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    return False

if not check_password():
    st.stop()

import streamlit as st

# ==============================================================================
# 1. 所得税・住民税の計算ロジック (令和8年分税制改正対応)
# ==============================================================================

def calculate_employment_income(gross_salary):
    """給与所得控除後の所得金額"""
    if gross_salary < 741000:
        return 0
    elif gross_salary <= 2190999:
        return gross_salary - 740000
    elif gross_salary <= 2192999:
        return 1451000
    elif gross_salary <= 2195999:
        return 1453000
    elif gross_salary <= 2199999:
        return 1456000
    elif gross_salary <= 3599999:
        return int(gross_salary * 0.70 - 80000)
    elif gross_salary <= 6599999:
        return int(gross_salary * 0.80 - 440000)
    elif gross_salary <= 8499999:
        return int(gross_salary * 0.90 - 1100000)
    else:
        return gross_salary - 1950000

def calculate_life_insurance_deduction(premium):
    """生命保険料控除額（新制度基準）"""
    if premium <= 20000:
        ded_it = premium
    elif premium <= 40000:
        ded_it = int(premium * 0.5 + 10000)
    elif premium <= 80000:
        ded_it = int(premium * 0.25 + 20000)
    else:
        ded_it = 40000

    if premium <= 12000:
        ded_rt = premium
    elif premium <= 32000:
        ded_rt = int(premium * 0.5 + 6000)
    elif premium <= 56000:
        ded_rt = int(premium * 0.25 + 14000)
    else:
        ded_rt = 28000

    return ded_it, ded_rt

def calculate_medical_deduction(medical_exp, insurance_reimbursement, net_income):
    """医療費控除額の計算"""
    actual_exp = max(0, medical_exp - insurance_reimbursement)
    threshold = min(100000, int(net_income * 0.05))
    return max(0, actual_exp - threshold)

def calculate_basic_deduction_it(net_income):
    """所得税基礎控除（令和8年分基準：最大104万円）"""
    if net_income <= 4890000:
        return 1040000
    elif net_income <= 6550000:
        return 670000
    elif net_income <= 23500000:
        return 620000
    elif net_income <= 24000000:
        return 480000
    elif net_income <= 24500000:
        return 320000
    elif net_income <= 25000000:
        return 160000
    else:
        return 0

def calculate_spouse_deduction_it(net_income, spouse_net_income):
    """配偶者控除・特別控除（所得税）"""
    if net_income > 10000000:
        return 0
    col = 'A' if net_income <= 9000000 else ('B' if net_income <= 9500000 else 'C')

    if spouse_net_income <= 620000:
        return {'A': 380000, 'B': 260000, 'C': 130000}[col]
    elif spouse_net_income <= 950000:
        return {'A': 380000, 'B': 260000, 'C': 130000}[col]
    elif spouse_net_income <= 1000000:
        return {'A': 360000, 'B': 240000, 'C': 120000}[col]
    elif spouse_net_income <= 1050000:
        return {'A': 310000, 'B': 210000, 'C': 110000}[col]
    elif spouse_net_income <= 1100000:
        return {'A': 260000, 'B': 180000, 'C': 90000}[col]
    elif spouse_net_income <= 1150000:
        return {'A': 210000, 'B': 140000, 'C': 70000}[col]
    elif spouse_net_income <= 1200000:
        return {'A': 160000, 'B': 110000, 'C': 60000}[col]
    elif spouse_net_income <= 1250000:
        return {'A': 110000, 'B': 80000, 'C': 40000}[col]
    elif spouse_net_income <= 1300000:
        return {'A': 60000, 'B': 40000, 'C': 20000}[col]
    elif spouse_net_income <= 1330000:
        return {'A': 30000, 'B': 20000, 'C': 10000}[col]
    else:
        return 0

def calculate_income_tax(taxable_income):
    """所得税額（7段階累進税率 5%〜45% ＋ 復興特別所得税 102.1%）"""
    taxable = (taxable_income // 1000) * 1000
    if taxable <= 0:
        return 0

    if taxable <= 1950000:
        tax = taxable * 0.05
    elif taxable <= 3300000:
        tax = taxable * 0.10 - 97500
    elif taxable <= 6950000:
        tax = taxable * 0.20 - 427500
    elif taxable <= 9000000:
        tax = taxable * 0.23 - 636000
    elif taxable <= 18000000:
        tax = taxable * 0.33 - 1536000
    elif taxable <= 40000000:
        tax = taxable * 0.40 - 2796000
    else:
        tax = taxable * 0.45 - 4796000

    tax = max(0, tax)
    final_tax = int(tax * 1.021)
    return (final_tax // 100) * 100

def check_resident_tax_exemption(net_income, spouse_net_income, total_dep_count):
    """住民税の非課税限度額（均等割・所得割）の判定"""
    is_same_livelihood_spouse = 1 if (spouse_net_income <= 620000) else 0
    num_family_members = 1 + is_same_livelihood_spouse + total_dep_count

    if is_same_livelihood_spouse or total_dep_count > 0:
        per_capita_limit = 320000 * num_family_members + 100000 + 168000
        income_crop_limit = 350000 * num_family_members + 100000 + 320000
    else:
        per_capita_limit = 420000
        income_crop_limit = 450000

    is_per_capita_exempt = (net_income <= per_capita_limit)
    is_income_crop_exempt = (net_income <= income_crop_limit)

    return is_per_capita_exempt, is_income_crop_exempt

def calculate_person_taxes(
    income_type,
    gross_amount,
    business_expenses=0,
    blue_deduction=650000,
    spouse_net_income=0,
    social_insurance=0,
    life_insurance_premium=0,
    small_enterprise_mutual_aid=0,
    medical_exp=0,
    medical_reimbursement=0,
    housing_loan_deduction_input=0,
    num_under_16=0,
    num_dep_16_18=0,
    num_dep_19_22=0,
    municipality="仙台市"
):
    """個人単体の所得税・住民税・手取り額算出"""
    if income_type == "給与所得者":
        net_income = calculate_employment_income(gross_amount)
        gross_revenue = gross_amount
    else:
        net_income = max(0, gross_amount - business_expenses - blue_deduction)
        gross_revenue = gross_amount - business_expenses

    life_ded_it, life_ded_rt = calculate_life_insurance_deduction(life_insurance_premium)
    medical_ded = calculate_medical_deduction(medical_exp, medical_reimbursement, net_income)

    dep_ded_it = num_dep_16_18 * 380000 + num_dep_19_22 * 630000
    dep_ded_rt = num_dep_16_18 * 330000 + num_dep_19_22 * 450000

    basic_ded_it = calculate_basic_deduction_it(net_income)
    basic_ded_rt = 430000

    spouse_ded_it = calculate_spouse_deduction_it(net_income, spouse_net_income)
    spouse_ded_rt = 380000 if (spouse_net_income <= 620000 and net_income <= 9000000) else 0

    total_deductions_it = (
        basic_ded_it + spouse_ded_it + social_insurance +
        life_ded_it + small_enterprise_mutual_aid + medical_ded + dep_ded_it
    )
    taxable_income_it = max(0, net_income - total_deductions_it)
    raw_income_tax = calculate_income_tax(taxable_income_it)

    income_tax = max(0, raw_income_tax - housing_loan_deduction_input)
    unused_housing_deduction = max(0, housing_loan_deduction_input - raw_income_tax)

    total_deductions_rt = (
        basic_ded_rt + spouse_ded_rt + social_insurance +
        life_ded_rt + small_enterprise_mutual_aid + medical_ded + dep_ded_rt
    )
    taxable_income_rt = max(0, net_income - total_deductions_rt)
    taxable_income_rt = (taxable_income_rt // 1000) * 1000

    income_crop_rt = int(taxable_income_rt * 0.10)

    resident_tax_housing_cap = min(int(taxable_income_it * 0.05), 97500)
    resident_tax_housing_ded = min(unused_housing_deduction, resident_tax_housing_cap)
    income_crop_rt_final = max(0, income_crop_rt - resident_tax_housing_ded)

    per_capita_rt = 6200

    total_dep_count = num_under_16 + num_dep_16_18 + num_dep_19_22
    is_per_capita_exempt, is_income_crop_exempt = check_resident_tax_exemption(
        net_income, spouse_net_income, total_dep_count
    )

    if is_income_crop_exempt:
        income_crop_rt_final = 0
    if is_per_capita_exempt:
        per_capita_rt = 0

    resident_tax = income_crop_rt_final + per_capita_rt

    if income_type == "給与所得者":
        take_home = gross_amount - social_insurance - (income_tax + resident_tax)
    else:
        take_home = gross_revenue - social_insurance - (income_tax + resident_tax) - small_enterprise_mutual_aid - life_insurance_premium - medical_exp

    return {
        "net_income": net_income,
        "income_tax": income_tax,
        "resident_tax": resident_tax,
        "is_per_capita_exempt": is_per_capita_exempt,
        "is_income_crop_exempt": is_income_crop_exempt,
        "total_tax": income_tax + resident_tax,
        "take_home": take_home
    }

def run_couple_simulation(husband_data, wife_data, dep_h_under_16, dep_h_16_18, dep_h_19_22, dep_w_under_16, dep_w_16_18, dep_w_19_22, municipality):
    """夫婦の合計手取り額・税額を合成"""
    h_net_temp = calculate_employment_income(husband_data["gross_amount"]) if husband_data["income_type"] == "給与所得者" else max(0, husband_data["gross_amount"] - husband_data["expenses"] - husband_data["blue_ded"])
    w_net_temp = calculate_employment_income(wife_data["gross_amount"]) if wife_data["income_type"] == "給与所得者" else max(0, wife_data["gross_amount"] - wife_data["expenses"] - wife_data["blue_ded"])

    res_h = calculate_person_taxes(
        income_type=husband_data["income_type"],
        gross_amount=husband_data["gross_amount"],
        business_expenses=husband_data["expenses"],
        blue_deduction=husband_data["blue_ded"],
        spouse_net_income=w_net_temp,
        social_insurance=husband_data["social_ins"],
        life_insurance_premium=husband_data["life_ins"],
        small_enterprise_mutual_aid=husband_data["small_ent"],
        medical_exp=husband_data["medical_exp"],
        medical_reimbursement=husband_data["medical_reimb"],
        housing_loan_deduction_input=husband_data["housing_loan"],
        num_under_16=dep_h_under_16,
        num_dep_16_18=dep_h_16_18,
        num_dep_19_22=dep_h_19_22,
        municipality=municipality
    )

    res_w = calculate_person_taxes(
        income_type=wife_data["income_type"],
        gross_amount=wife_data["gross_amount"],
        business_expenses=wife_data["expenses"],
        blue_deduction=wife_data["blue_ded"],
        spouse_net_income=h_net_temp,
        social_insurance=wife_data["social_ins"],
        life_insurance_premium=wife_data["life_ins"],
        small_enterprise_mutual_aid=wife_data["small_ent"],
        medical_exp=wife_data["medical_exp"],
        medical_reimbursement=wife_data["medical_reimb"],
        housing_loan_deduction_input=wife_data["housing_loan"],
        num_under_16=dep_w_under_16,
        num_dep_16_18=dep_w_16_18,
        num_dep_19_22=dep_w_19_22,
        municipality=municipality
    )

    return {
        "husband": res_h,
        "wife": res_w,
        "total_take_home": res_h["take_home"] + res_w["take_home"],
        "total_tax": res_h["total_tax"] + res_w["total_tax"]
    }

def find_optimal_child_allocation(husband_data, wife_data, num_under_16, num_16_18, num_19_22, municipality):
    """
    お子様（各年齢区分）の人数を夫と妻で分ける全パターンを探索し、
    世帯手取り額が最大となる最適な組み合わせを自動算出する
    """
    best_take_home = -1
    best_allocation = None
    best_result = None

    for h_u16 in range(num_under_16 + 1):
        w_u16 = num_under_16 - h_u16
        for h_16_18 in range(num_16_18 + 1):
            w_16_18 = num_16_18 - h_16_18
            for h_19_22 in range(num_19_22 + 1):
                w_19_22 = num_19_22 - h_19_22

                sim = run_couple_simulation(
                    husband_data, wife_data,
                    h_u16, h_16_18, h_19_22,
                    w_u16, w_16_18, w_19_22,
                    municipality
                )

                if sim["total_take_home"] > best_take_home:
                    best_take_home = sim["total_take_home"]
                    best_allocation = {
                        "h_under_16": h_u16, "w_under_16": w_u16,
                        "h_16_18": h_16_18, "w_16_18": w_16_18,
                        "h_19_22": h_19_22, "w_19_22": w_19_22
                    }
                    best_result = sim

    return best_allocation, best_result

# ==============================================================================
# 2. Streamlit UI 画面構築
# ==============================================================================

st.set_page_config(page_title="夫婦税金＆扶養人数自動最適化シミュレーター", layout="wide")
st.title("夫婦の所得税・住民税 扶養人数自動最適化シミュレーター")
st.write("お子様が複数人（例：5人など）いる場合、**何歳のお子様を夫側に何人、妻側に何人扶養に入れると世帯手取り額が最大になるか**を全パターン比較して自動算出します。")

st.divider()

# --- 基本設定 ---
st.subheader("📍 【基本設定】お住まいの自治体 ＆ お子様の人数")
col_base1, col_base2, col_base3, col_base4 = st.columns(4)

with col_base1:
    municipality = st.selectbox(
        "居住市町村の選択",
        ("仙台市", "富谷市", "大崎市", "多賀城市", "七ヶ浜町", "利府町", "加美町", "その他自治体")
    )

with col_base2:
    num_under_16 = st.number_input("16歳未満のお子様の人数", min_value=0, max_value=10, value=3, step=1)

with col_base3:
    num_dep_16_18 = st.number_input("16歳〜18歳のお子様の人数", min_value=0, max_value=10, value=1, step=1)

with col_base4:
    num_dep_19_22 = st.number_input("19歳〜22歳のお子様の人数", min_value=0, max_value=10, value=1, step=1)

total_children = num_under_16 + num_dep_16_18 + num_dep_19_22
st.info(f"👨‍👩‍👧‍👦 現在設定されているお子様の合計人数： **{total_children}人**")

st.divider()

blue_options = (650000, 550000, 100000, 0)

# --- 夫婦の収入・控除入力 ---
col_h, col_w = st.columns(2)

with col_h:
    st.header("👨 夫の情報")
    h_type = st.radio("働き方 (夫)", ("給与所得者", "個人事業主"), key="h_type")
    
    if h_type == "給与所得者":
        h_gross = st.number_input("給与収入（額面年収・円）", value=6000000, step=100000, key="h_gross")
        h_expenses = 0
        h_blue = 0
    else:
        h_gross = st.number_input("事業売上高（円）", value=8000000, step=100000, key="h_gross_b")
        h_expenses = st.number_input("必要経費（円）", value=2000000, step=100000, key="h_exp_b")
        h_blue = st.selectbox("青色申告特別控除（円）", blue_options, index=0, key="h_blue_b")

    h_soc = st.number_input("社会保険料 (年間支払額・円)", value=900000, step=10000, key="h_soc")
    h_life = st.number_input("生命保険料 (年間支払額・円)", value=120000, step=10000, key="h_life")
    h_small = st.number_input("小規模企業共済 / iDeCo (年間掛金・円)", value=240000, step=10000, key="h_small")
    
    st.markdown("🔹 **追加控除（夫）**")
    h_housing = st.number_input("住宅ローン控除 (年間控除可能額・円)", value=200000, step=10000, key="h_housing")
    h_med_exp = st.number_input("医療費支払額 (年間合計・円)", value=150000, step=10000, key="h_med_exp")
    h_med_reimb = st.number_input("医療費の補填金額 (保険金等・円)", value=0, step=10000, key="h_med_reimb")

with col_w:
    st.header("👩 妻の情報")
    w_type = st.radio("働き方 (妻)", ("給与所得者", "個人事業主"), key="w_type")
    
    if w_type == "給与所得者":
        w_gross = st.number_input("給与収入（額面年収・円）", value=3500000, step=100000, key="w_gross")
        w_expenses = 0
        w_blue = 0
    else:
        w_gross = st.number_input("事業売上高（円）", value=4000000, step=100000, key="w_gross_b")
        w_expenses = st.number_input("必要経費（円）", value=1000000, step=100000, key="w_exp_b")
        w_blue = st.selectbox("青色申告特別控除（円）", blue_options, index=0, key="w_blue_b")

    w_soc = st.number_input("社会保険料 (年間支払額・円)", value=500000, step=10000, key="w_soc")
    w_life = st.number_input("生命保険料 (年間支払額・円)", value=60000, step=10000, key="w_life")
    w_small = st.number_input("小規模企業共済 / iDeCo (年間掛金・円)", value=120000, step=10000, key="w_small")
    
    st.markdown("🔹 **追加控除（妻）**")
    w_housing = st.number_input("住宅ローン控除 (年間控除可能額・円)", value=0, step=10000, key="w_housing")
    w_med_exp = st.number_input("医療費支払額 (年間合計・円)", value=0, step=10000, key="w_med_exp")
    w_med_reimb = st.number_input("医療費の補填金額 (保険金等・円)", value=0, step=10000, key="w_med_reimb")

husband_data = {
    "income_type": h_type,
    "gross_amount": h_gross,
    "expenses": h_expenses,
    "blue_ded": h_blue,
    "social_ins": h_soc,
    "life_ins": h_life,
    "small_ent": h_small,
    "housing_loan": h_housing,
    "medical_exp": h_med_exp,
    "medical_reimb": h_med_reimb
}

wife_data = {
    "income_type": w_type,
    "gross_amount": w_gross,
    "expenses": w_expenses,
    "blue_ded": w_blue,
    "social_ins": w_soc,
    "life_ins": w_life,
    "small_ent": w_small,
    "housing_loan": w_housing,
    "medical_exp": w_med_exp,
    "medical_reimb": w_med_reimb
}

st.divider()

# ==============================================================================
# 3. 最適な扶養分け方の全自動判定
# ==============================================================================

st.subheader("🏆 最適な扶養人数の振り分け結果（手取り最大化）")

best_alloc, best_res = find_optimal_child_allocation(
    husband_data, wife_data,
    num_under_16, num_dep_16_18, num_dep_19_22,
    municipality
)

sim_all_h = run_couple_simulation(husband_data, wife_data, num_under_16, num_dep_16_18, num_dep_19_22, 0, 0, 0, municipality)
sim_all_w = run_couple_simulation(husband_data, wife_data, 0, 0, 0, num_under_16, num_dep_16_18, num_dep_19_22, municipality)

st.success(f"🎉 **最も世帯手取り額が多くなる分け方（最大手取り額: {best_res['total_take_home']:,} 円）**")

col_opt_h, col_opt_w = st.columns(2)

with col_opt_h:
    st.markdown("### 👨 【夫の扶養に入れる人数】")
    st.write(f"- **16歳未満のお子様**: **{best_alloc['h_under_16']}人** / {num_under_16}人中")
    st.write(f"- **16歳〜18歳のお子様**: **{best_alloc['h_16_18']}人** / {num_dep_16_18}人中")
    st.write(f"- **19歳〜22歳のお子様**: **{best_alloc['h_19_22']}人** / {num_dep_19_22}人中")
    st.write(f"- **夫の年間税額合計**: {best_res['husband']['total_tax']:,} 円 (所得税: {best_res['husband']['income_tax']:,}円 / 住民税: {best_res['husband']['resident_tax']:,}円)")

with col_opt_w:
    st.markdown("### 👩 【妻の扶養に入れる人数】")
    st.write(f"- **16歳未満のお子様**: **{best_alloc['w_under_16']}人** / {num_under_16}人中")
    st.write(f"- **16歳〜18歳のお子様**: **{best_alloc['w_16_18']}人** / {num_dep_16_18}人中")
    st.write(f"- **19歳〜22歳のお子様**: **{best_alloc['w_19_22']}人** / {num_dep_19_22}人中")
    st.write(f"- **妻の年間税額合計**: {best_res['wife']['total_tax']:,} 円 (所得税: {best_res['wife']['income_tax']:,}円 / 住民税: {best_res['wife']['resident_tax']:,}円)")

st.divider()

# --- パターン比較（極端なパターンとの比較） ---
st.subheader("📈 他パターン（全員夫 vs 全員妻）との比較")

col_cmp1, col_cmp2, col_cmp3 = st.columns(3)

with col_cmp1:
    st.markdown("#### ⭐ **最適に分けた場合**")
    st.metric("世帯手取り額", f"{best_res['total_take_home']:,} 円")
    st.metric("世帯年間税額", f"{best_res['total_tax']:,} 円")

with col_cmp2:
    st.markdown("#### 👨 全員を【夫】に入れる")
    st.metric("世帯手取り額", f"{sim_all_h['total_take_home']:,} 円", delta=f"{sim_all_h['total_take_home'] - best_res['total_take_home']:,} 円")
    st.metric("世帯年間税額", f"{sim_all_h['total_tax']:,} 円")

with col_cmp3:
    st.markdown("#### 👩 全員を【妻】に入れる")
    st.metric("世帯手取り額", f"{sim_all_w['total_take_home']:,} 円", delta=f"{sim_all_w['total_take_home'] - best_res['total_take_home']:,} 円")
    st.metric("世帯年間税額", f"{sim_all_w['total_tax']:,} 円")

caption_text = (
    "※令和8年分税制改正、住宅ローン控除の繰り越し、医療費控除、16歳未満の年少扶養親族を含む"
    "住民税非課税基準（均等割・所得割）を考慮し、最も世帯手取りが多くなる組合せを全自動算出しています。"
    "※年齢23歳未満の扶養親族を有する場合の生命保険料控除の特例」は所得税（国税）のみに適用される制度であり、"
    "住民税（個人住民税）の控除計算には適用されません" \
    "※会社の家族手当（扶養手当）の条件会社の規定で子どもを健康保険や税制上の扶養に入れている人数規定がある場合"
    "夫の給与で家族手当をもらう方が節税額より大きくなるケースがあります"
)
st.caption(caption_text)
