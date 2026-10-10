# -*- coding: utf-8 -*-
import streamlit as st

from src import config as C
from src import data as D
from src import tables as T
from src.ui import header, table

header("🎯 기회 탐색", "표 13–16 — 조건으로 행정동을 거르고, 순위를 보고, CSV 로 내려받기")
st.warning(
    "현재 기회 유형·점수·순위는 OA-22166 지출 자료를 사용한 기존 모델 기준입니다. "
    "결제 집계 위치 등에 따른 왜곡 가능성이 있어 창업 유망도, 소비 유출액, 임대료 상승이나 성공 확률로 해석할 수 없습니다. "
    "상권별 추정매출과 업종별 점포·개폐업 자료로 재검증해야 합니다.",
    icon="⚠️",
)

COLS = ("행정동_코드", "자치구", "행정동_코드_명", "상권_원형", "금융MBTI", "상권_유형", "기회_유형", "기회점수",
        "기회순위", "배율", "격차금액_억", "잔차_추세_pct", "업종_공백", "업종_강점", "타깃_업종",
        "키워드_접근성인프라", "키워드_소비배후수요", "키워드_환경리스크", "해석주의", "기회_인사이트")
df = D.dong(COLS)

a, b = st.columns(2)
with a:
    table(
        13, "① 선점형 (기존 모델) Top 10", T.ranking(df, C.OPP_ORDER[0]),
        fmt={"기회순위": "{:.0f}", "배율": "×{:.2f}", "격차금액_억": "{:+,.0f}", "기회점수": "{:.1f}"},
        summary="기존 지출 모형에서 기대치보다 낮고 격차가 개선된 행정동 10곳입니다. 점포 매출 증가나 임대료 상승 전 선점 기회를 입증하지는 않습니다.",
        details="""
##### 1. 선정 기준
* 기존 모형의 관측 지출÷예측 지출 배율과 잔차 추세·배후인구를 기준으로 산출된 분류입니다.

##### 2. 해석 및 추가 확인
* 실제 창업 후보지로 검토하려면 상권 추정매출 추세, 입지별 임대료, 동일 업종 점포 수 및 개폐업을 추가 확인해야 합니다.
"""
    )
with b:
    table(
        14, "② 유출보완형 (기존 모델) Top 10", T.ranking(df, C.OPP_ORDER[1]),
        fmt={"기회순위": "{:.0f}", "배율": "×{:.2f}", "격차금액_억": "{:+,.0f}", "기회점수": "{:.1f}"},
        summary="기존 지출 모형에서 기대 대비 지출이 낮고 격차가 비교적 안정적인 행정동 10곳입니다. 주민 소비 유출이나 상가 공급 부족이 확인된 것은 아닙니다.",
        details="""
##### 1. 선정 기준
* 배후인구와 기존 모형의 지출 배율·추세를 이용한 분류입니다. 배율은 점포 매출이나 주민 소비 유출률과 같지 않습니다.

##### 2. 해석 및 추가 확인
* '격차금액'은 관측 지출과 예측 지출의 모형상 차이이지 외부 소비 유출액이 아닙니다. '업종 공백'도 유사 상권 대비 상대적 저지출 비중으로, 점포 부족을 확인한 값은 아닙니다.
"""
    )
st.caption("기존 모델의 ①·② 통합 순위입니다. 해석주의 동은 제외했으나, 이 순위는 창업 추천 순위가 아닙니다.")

st.divider()
st.subheader("조건 필터")
with st.form("filter"):
    f1, f2, f3 = st.columns(3)
    gus = f1.multiselect("자치구", D.gu_list())
    opps = f2.multiselect("기존 기회 유형 (검증 전)", C.OPP_ORDER, default=C.OPP_ORDER[:2])
    archs = f3.multiselect("상권 원형", C.ARCH_ORDER)
    f4, f5, f6 = st.columns(3)
    mbtis = f4.multiselect("금융MBTI", C.MBTI_ORDER)
    tags = f5.multiselect("태그 포함 (모두 만족)", sorted(D.tags()["태그"].unique()))
    lo, hi = f6.select_slider("기존 지출 배율 범위", options=[0.1, 0.25, 0.5, 0.67, 0.9, 1.1, 1.5, 2, 5, 100], value=(0.1, 100))
    excl = st.checkbox("해석주의 동 제외", value=True)
    st.form_submit_button("적용", type="primary")

q = df.copy()
if gus:
    q = q[q["자치구"].isin(gus)]
if opps:
    q = q[q["기회_유형"].isin(opps)]
if archs:
    q = q[q["상권_원형"].isin(archs)]
if mbtis:
    q = q[q["금융MBTI"].isin(mbtis)]
q = q[q["배율"].between(lo, hi)]
if excl:
    q = q[q["해석주의"].isna()]
if tags:
    alltags = q[["키워드_접근성인프라", "키워드_소비배후수요", "키워드_환경리스크"]].fillna("").agg(" ".join, axis=1)
    for t in tags:
        q = q[alltags.loc[q.index].str.split().map(lambda s, t=t: t in s)]

q = q.sort_values(["기회순위", "배율"], na_position="last")
st.markdown(f"**{len(q)}개 동**")
table(
    15, "필터 결과", q.drop(columns=["행정동_코드", "기회_인사이트"]),
    fmt={"기회점수": "{:.1f}", "기회순위": "{:.0f}", "배율": "×{:.2f}", "격차금액_억": "{:+,.0f}",
         "잔차_추세_pct": "{:+.1f}"}, height=420,
    summary="사용자가 설정한 자치구, 기회 유형, 상권 원형, 금융MBTI, 태그 등의 조건에 맞는 행정동 맞춤 목록입니다.",
    details="""
##### 1. 맞춤형 상권 탐색
* 자치구, 기존 기회 유형, 상권 원형, 주민 금융MBTI 등을 조합해 행정동을 탐색합니다. 주민 금융MBTI는 창업자 위험 선호와 다른 지표입니다.

##### 2. CSV 다운로드
* 아래 버튼을 눌러 필터링된 행정동 전체 데이터를 엑셀(CSV)로 내려받아 세부 분석에 활용할 수 있습니다.
"""
)
st.download_button("필터 결과 CSV 내려받기", q.to_csv(index=False).encode("utf-8-sig"),
                   "상권기회_필터결과.csv", "text/csv")

st.divider()
table(
    16, "해석주의 동 (배율 극단)", T.caution(df), fmt={"배율": "×{:.2f}", "격차금액_억": "{:+,.0f}"},
    summary="기존 모형에서 배율이 극단적인(×5 이상 또는 ×0.25 이하) 22개 동입니다. 그 외 지역도 집계·모델 한계를 검토해야 합니다.",
    details="""
##### 1. 왜 주의해서 해석해야 하나요?
* **배율 ×5 이상 (극단적 초과)**: 대기업 본사 카드 결제가 본사 주소지로 일괄 잡히거나, 대형 백화점 등이 입점해 있어 실제 동네 상권보다 통계가 부풀려졌을 수 있습니다.
* **배율 ×0.25 이하 (극단적 저평가)**: 동 전체가 대규모 재건축 공사 중이거나, 바로 옆 초대형 상권에 완전히 흡수되어 통계상 왜곡이 생겼을 수 있습니다.

##### 2. 분석 원칙
* 이 22개 동은 기존 순위표에서 제외됐지만, 나머지 순위 역시 사업성 검증을 거친 것은 아닙니다.
"""
)
