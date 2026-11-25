import html
import time
from pathlib import Path

import streamlit as st

st.set_page_config(layout="wide", page_title="KORAIL Field-AI 코파일럿")

BLUE = "#0054A6"
COMM_PARTS = [
    "주회선 광모듈 #1",
    "예비회선 광모듈 #2",
    "이중화 수동 절체 스위치",
    "메인 전원 차단기",
    "UPS 배터리 모듈",
    "LTE-R 연결 광점퍼 포트",
]
COMM_TASKS = {
    COMM_PARTS[0]: ["이 광모듈 뽑았다가 다시 꽂을게요", "이 광모듈 교체할게요"],
    COMM_PARTS[1]: ["예비 광모듈 분리해서 점검할게요"],
    COMM_PARTS[2]: ["먼저 예비 회선으로 전환할게요", "작업 끝났으니 주회선으로 복귀할게요"],
    COMM_PARTS[3]: ["이 메인 전원 차단기 내릴게요"],
    COMM_PARTS[4]: ["UPS 배터리 모듈 교체할게요"],
    COMM_PARTS[5]: ["LTE-R 광점퍼 뽑아서 청소할게요"],
}
COMM_CHIPS = [
    "이 광모듈 뽑았다가 다시 꽂을게요",
    "먼저 예비 회선으로 전환할게요",
    "이 메인 전원 차단기 내릴게요",
]
COMM_GENERAL = {
    "주회선 광모듈 #1": "광커넥터 단면 오염 여부 확인, 레이저 출력 중 직접 육안 확인 금지, 작업 전 절체 상태를 확인하세요.",
    "예비회선 광모듈 #2": "예비 모듈은 우회 시 주 경로가 됩니다. 수신 광레벨과 링크 LED 정상 여부를 점검하세요.",
    "이중화 수동 절체 스위치": "절체 전 예비회선 링크 정상 여부를 확인하고, 절체 후 하위 설비 3종의 통신 복구를 확인하세요.",
    "UPS 배터리 모듈": "배터리 모듈 교체는 상용전원 정상 상태에서 1개씩만 진행하고, 교체 후 충전 상태와 경보 해제를 확인하세요.",
    "LTE-R 연결 광점퍼 포트": "광점퍼 접속부는 청소 전 반드시 해당 회선 사용 여부를 관제에 확인하고, 단면에 직접 시선을 두지 마세요.",
    "메인 전원 차단기": "차단기 조작은 전체 장비 정지로 이어집니다. 반드시 작업 승인 및 상급자 확인 후 진행하세요.",
}

SIG_PARTS = [
    "운용계(A계) CPU 보드",
    "대기계(B계) CPU 보드",
    "계 절체 스위치",
    "선로전환기 제어전원 모듈",
    "궤도회로 송수신 모듈",
    "서지보호기(SPD) 모듈",
]
SIG_TASKS = {
    SIG_PARTS[0]: ["A계 CPU 보드 교체할게요", "A계 CPU 보드 뽑았다가 다시 꽂을게요"],
    SIG_PARTS[1]: ["B계 CPU 보드 분리해서 점검할게요"],
    SIG_PARTS[2]: ["먼저 B계로 절체할게요", "작업 끝났으니 A계로 복귀할게요"],
    SIG_PARTS[3]: ["제어전원 모듈 끄고 교체할게요"],
    SIG_PARTS[4]: ["궤도회로 모듈 교체할게요"],
    SIG_PARTS[5]: ["서지보호기 모듈 교체할게요"],
}
SIG_CHIPS = [
    "A계 CPU 보드 교체할게요",
    "먼저 B계로 절체할게요",
    "제어전원 모듈 끄고 교체할게요",
]
SIG_GENERAL = {
    SIG_PARTS[0]: "운용계 보드 작업 전 반드시 B계 절체 상태와 동기화 상태를 확인하세요.",
    SIG_PARTS[1]: "대기계는 절체 시 운용계가 됩니다. 진단 LED와 A/B계 데이터 일치 여부를 확인하세요.",
    SIG_PARTS[2]: "절체 전 B계 정상 및 동기화 완료를 확인하고, 절체 후 선로전환기·궤도·신호기 표시를 확인하세요.",
    SIG_PARTS[3]: "제어전원은 선로전환기 전환과 직결됩니다. 열차 운행 중에는 관제 승인 없이 조작 금지입니다.",
    SIG_PARTS[4]: "궤도회로 모듈은 해당 구간 점유 검지와 직결됩니다. 작업 구간 폐쇄 후 진행하세요.",
    SIG_PARTS[5]: "SPD 교체는 접지선 체결 상태를 확인하고, 교체 후 접지저항 및 표시등을 점검하세요.",
}

# ---------------------------------------------------------------- images
ASSETS = Path(__file__).parent / "assets"


def find_photo(idx):
    prefix = "sig_" if ss.site == "signal" else ""
    for ext in ("png", "jpg", "jpeg", "webp"):
        f = ASSETS / f"{prefix}part{idx + 1}.{ext}"
        if f.exists():
            return str(f)
    return None


def sig_svg(idx):
    wrap = ('<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg" '
            'style="width:100%;max-height:220px;background:#0e1628;border:1px solid #1f2d4a;border-radius:8px">')
    if idx in (0, 1):  # CPU 보드
        tag = "#22c55e" if idx == 0 else "#3b82f6"
        name = "A계 (운용)" if idx == 0 else "B계 (대기)"
        chips = "".join(f'<rect x="{110 + c * 60}" y="70" width="44" height="44" fill="#111827" stroke="#9ca3af"/>'
                        for c in range(3))
        pins = "".join(f'<rect x="{66 + k * 14}" y="150" width="8" height="18" fill="#facc15"/>' for k in range(20))
        body = (f'<rect x="60" y="40" width="280" height="110" rx="4" fill="#14532d" stroke="#86efac" stroke-width="2"/>'
                f'{chips}<circle cx="320" cy="55" r="6" fill="{tag}"/>'
                f'<text x="200" y="136" fill="#d1fae5" font-size="12" text-anchor="middle">EIS CPU BOARD · {name}</text>{pins}')
        return wrap + body + "</svg>"
    if idx == 2:  # 계 절체 스위치
        bk = ss.is_backup_active
        ang = 40 if bk else -40
        body = f"""
<rect x="110" y="20" width="180" height="160" rx="10" fill="#1e293b" stroke="#64748b" stroke-width="3"/>
<circle cx="200" cy="100" r="52" fill="#0b1220" stroke="#94a3b8" stroke-width="4"/>
<g transform="rotate({ang} 200 100)"><rect x="190" y="52" width="20" height="56" rx="6" fill="#facc15"/></g>
<text x="128" y="62" fill="#4ade80" font-size="14" font-weight="bold">A계</text>
<text x="246" y="62" fill="#60a5fa" font-size="14" font-weight="bold">B계</text>
<text x="200" y="172" fill="#d7e0ee" font-size="12" text-anchor="middle">계 절체 스위치 [{"B계" if bk else "A계"}]</text>"""
        return wrap + body + "</svg>"
    labels = {3: ("제어전원 모듈 (DC 110V)", "#ef4444", "POWER"), 4: ("궤도회로 송수신 모듈", "#38bdf8", "TC"),
              5: ("SPD 서지보호기", "#f59e0b", "SPD")}
    txt, col, tag = labels[idx]
    body = f"""
<rect x="120" y="25" width="160" height="140" rx="8" fill="#1f2937" stroke="#6b7280" stroke-width="3"/>
<rect x="140" y="45" width="120" height="30" rx="4" fill="#0b1220"/>
<text x="200" y="65" fill="{col}" font-size="12" text-anchor="middle" font-weight="bold">{tag}</text>
<circle cx="150" cy="105" r="7" fill="{col}"/><circle cx="180" cy="105" r="7" fill="#374151"/>
<rect x="140" y="125" width="120" height="8" fill="#4b5563"/>
<text x="200" y="155" fill="#d7e0ee" font-size="11" text-anchor="middle">{txt}</text>"""
    return wrap + body + "</svg>"


def part_svg(idx):
    if ss.site == "signal":
        return sig_svg(idx)
    wrap = ('<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg" '
            'style="width:100%;max-height:220px;background:#0e1628;border:1px solid #1f2d4a;border-radius:8px">')
    if idx in (0, 1):  # SFP 광모듈
        latch = "#22c55e" if idx == 0 else "#3b82f6"
        tag = "MAIN · 1310nm" if idx == 0 else "BACKUP · 1310nm"
        body = f"""
<rect x="70" y="60" width="230" height="80" rx="6" fill="#9aa5b5" stroke="#e2e8f0" stroke-width="2"/>
<rect x="70" y="60" width="230" height="22" rx="6" fill="#c3ccd8"/>
<rect x="300" y="68" width="34" height="64" rx="4" fill="#475569"/>
<circle cx="316" cy="86" r="8" fill="#0b1220" stroke="#facc15" stroke-width="2"/>
<circle cx="316" cy="114" r="8" fill="#0b1220" stroke="#facc15" stroke-width="2"/>
<text x="326" y="90" fill="#facc15" font-size="8">TX</text><text x="326" y="118" fill="#facc15" font-size="8">RX</text>
<rect x="34" y="78" width="40" height="44" rx="8" fill="{latch}" stroke="#0b1220" stroke-width="2"/>
<rect x="95" y="95" width="170" height="30" rx="3" fill="#e2e8f0"/>
<text x="180" y="108" fill="#0b1220" font-size="10" text-anchor="middle" font-weight="bold">SFP LC DUPLEX</text>
<text x="180" y="120" fill="#334155" font-size="9" text-anchor="middle">{tag}</text>
<rect x="100" y="140" width="160" height="6" fill="#64748b"/>"""
        return wrap + body + "</svg>"
    if idx == 2:  # 절체 스위치
        pos = "예비" if ss.is_backup_active else "주"
        ang = 40 if ss.is_backup_active else -40
        body = f"""
<rect x="110" y="20" width="180" height="160" rx="10" fill="#1e293b" stroke="#64748b" stroke-width="3"/>
<circle cx="200" cy="100" r="52" fill="#0b1220" stroke="#94a3b8" stroke-width="4"/>
<g transform="rotate({ang} 200 100)"><rect x="190" y="52" width="20" height="56" rx="6" fill="#facc15"/>
<circle cx="200" cy="58" r="5" fill="#0b1220"/></g>
<text x="128" y="62" fill="#4ade80" font-size="14" font-weight="bold">주</text>
<text x="256" y="62" fill="#60a5fa" font-size="14" font-weight="bold">예비</text>
<text x="200" y="172" fill="#d7e0ee" font-size="12" text-anchor="middle">수동 절체 스위치 [{pos}]</text>"""
        return wrap + body + "</svg>"
    if idx == 4:  # UPS 배터리
        cells = "".join(
            f'<rect x="{80 + k * 62}" y="60" width="52" height="80" rx="5" fill="#1e293b" stroke="#64748b" stroke-width="2"/>'
            f'<rect x="{96 + k * 62}" y="52" width="20" height="8" fill="#94a3b8"/>'
            f'<rect x="{88 + k * 62}" y="{150 - 20 * (k % 2 + 3)}" width="36" height="{20 * (k % 2 + 3) - 18}" fill="#22c55e"/>'
            for k in range(4))
        return wrap + cells + '<text x="200" y="170" fill="#d7e0ee" font-size="12" text-anchor="middle">UPS 배터리 모듈 (12V × 4)</text></svg>'
    if idx == 5:  # 광점퍼
        body = """
<rect x="60" y="40" width="280" height="90" rx="6" fill="#1e293b" stroke="#64748b" stroke-width="3"/>
<g fill="#0b1220" stroke="#facc15" stroke-width="2"><circle cx="110" cy="85" r="12"/><circle cx="160" cy="85" r="12"/>
<circle cx="210" cy="85" r="12"/><circle cx="260" cy="85" r="12"/></g>
<path d="M110 97 C 110 150, 70 150, 50 170" stroke="#facc15" stroke-width="5" fill="none"/>
<rect x="100" y="55" width="20" height="14" fill="#facc15"/>
<text x="110" y="30" fill="#d7e0ee" font-size="10" text-anchor="middle">→ LTE-R</text>
<text x="200" y="180" fill="#d7e0ee" font-size="12" text-anchor="middle">광 점퍼(LC) 패치 패널</text>"""
        return wrap + body + "</svg>"
    body = """
<rect x="130" y="15" width="140" height="170" rx="8" fill="#1f2937" stroke="#6b7280" stroke-width="3"/>
<rect x="150" y="30" width="100" height="36" rx="4" fill="#0b1220"/>
<text x="200" y="54" fill="#e2e8f0" font-size="14" text-anchor="middle" font-weight="bold">MCCB 63A</text>
<rect x="170" y="78" width="60" height="64" rx="6" fill="#111827" stroke="#9ca3af" stroke-width="2"/>
<rect x="184" y="84" width="32" height="30" rx="4" fill="#ef4444"/>
<text x="200" y="102" fill="#fff" font-size="11" text-anchor="middle" font-weight="bold">ON</text>
<text x="200" y="134" fill="#9ca3af" font-size="10" text-anchor="middle">OFF</text>
<rect x="140" y="154" width="120" height="6" fill="#4b5563"/>
<text x="200" y="176" fill="#d7e0ee" font-size="11" text-anchor="middle">메인 전원 차단기</text>"""
    return wrap + body + "</svg>"


# ---------------------------------------------------------------- state
ss = st.session_state
ss.setdefault("site", "comm")
ss.setdefault("is_backup_active", False)
ss.setdefault("selected", None)
ss.setdefault("messages", [])
ss.setdefault("alert", None)  # None | "danger" | "fatal"
ss.setdefault("alert_nodes", None)  # None = 전체, 아니면 영향받는 하위설비 인덱스 목록
ss.setdefault("alert_msg", "")
ss.setdefault("pending", None)
ss.setdefault("pending_fix", None)
ss.setdefault("last_text", "")
ss.setdefault("cleared", set())


def reset():
    ss.is_backup_active = False
    ss.selected = None
    ss.messages = []
    ss.alert = None
    ss.alert_nodes = None
    ss.alert_msg = ""
    ss.pending = None
    ss.pending_fix = None
    ss.last_text = ""
    ss.cleared = set()


def select(p):
    ss.selected = p


def queue(t):
    ss.pending = t


# ---------------------------------------------------------------- logic
def has(text, words):
    return any(w in text for w in words)


def judge_comm(text):
    p = ss.selected
    if not p:
        return dict(kind="info", intent="부품 미선택", verdict="대기",
                    risk=None, change="-",
                    action="좌측 도면에서 작업할 부품을 먼저 선택해 주세요.")
    ss.alert_nodes = None
    ss.alert_msg = ""
    if p == "메인 전원 차단기" and has(text, ["내리", "차단", "끄", "전원"]) and p in ss.cleared:
        ss.alert = None
        return dict(kind="warn", intent="메인 전원 차단기 OFF (계획정전, 승인 완료)", verdict="조건부 진행 가능", risk=40,
                    change="계획정전으로 MSPP #1 및 하위 설비 3종이 일시 중단됨 (사전 통보 완료)",
                    action="승인된 시간대에 차단기를 조작하고, 복구 후 전원 투입과 통신 복구를 확인하세요.")
    if p == "메인 전원 차단기" and has(text, ["내리", "차단", "끄", "전원"]):
        ss.alert = "fatal"
        return dict(kind="fatal", intent="메인 전원 차단기 OFF 조작",
                    verdict="작업 불가", risk=100,
                    change="MSPP #1 전체 전원 차단 → 주/예비 회선 및 하위 설비 3종(LTE-R, 행선안내기, CCTV) 전면 중단",
                    action="⚠ 전체 전원 차단 위험! 조작을 즉시 중지하고 관제센터 및 상급자 승인을 받으세요.")
    if p == "이중화 수동 절체 스위치" and has(text, ["복귀", "원복"]) and ss.is_backup_active:
        ss.alert = None
        ss.is_backup_active = False
        return dict(kind="safe", intent="주회선 복귀 절체 수행", verdict="작업 가능 · 복귀 절체 완료",
                    risk=8, change="트래픽이 주회선(광모듈 #1)으로 복귀. 하위 설비 통신 유지",
                    action="복귀 후 주회선 링크 LED, 광레벨, 하위 설비 3종 통신 상태를 확인하세요.")
    if p == "이중화 수동 절체 스위치" and has(text, ["전환", "절체", "예비", "우회"]):
        ss.alert = None
        ss.is_backup_active = True
        return dict(kind="backup", intent="예비회선 수동 절체 수행",
                    verdict="작업 가능 · 무중단 절체 완료", risk=5,
                    change="트래픽이 예비회선(광모듈 #2)으로 우회됨. 하위 설비 통신 유지",
                    action="이제 주회선 광모듈 #1 작업이 가능합니다. 작업 후 복귀 절체를 잊지 마세요.")
    if p == "주회선 광모듈 #1" and has(text, ["뽑", "분리", "교체", "빼"]):
        if not ss.is_backup_active:
            ss.alert = "danger"
            return dict(kind="danger", intent="주회선 광모듈 분리 시도 (미절체 상태)",
                        verdict="작업 불가", risk=95,
                        change="주회선 단독 운용 중 → 통신 두절 발생, LTE-R / 행선안내기 / CCTV 전부 끊김",
                        action="먼저 '이중화 수동 절체 스위치'로 예비회선 절체 후 재시도하세요.")
        ss.alert = None
        return dict(kind="safe", intent="주회선 광모듈 분리/교체 (절체 완료 상태)",
                    verdict="작업 가능 · 안전", risk=10,
                    change="예비회선이 트래픽을 담당 중이므로 하위 설비 통신 영향 없음",
                    action="정전기 방지 장갑 착용 후 작업, 재장착 후 링크 LED 및 광레벨 확인하세요.")
    if p == "예비회선 광모듈 #2" and has(text, ["뽑", "분리", "교체", "빼"]):
        if ss.is_backup_active:
            ss.alert = "danger"
            ss.alert_msg = "예비회선이 현재 트래픽을 담당 중! 분리 시 통신 두절"
            return dict(kind="danger", intent="예비회선 광모듈 분리 시도 (우회 운용 중)", verdict="작업 불가",
                        risk=90, change="우회 중인 예비회선 차단 → LTE-R / 행선안내기 / CCTV 전부 끊김",
                        action="먼저 절체 스위치로 주회선 복귀 후 재시도하세요.")
        ss.alert = None
        return dict(kind="safe", intent="예비회선 광모듈 분리/점검 (주회선 운용 중)", verdict="작업 가능 · 안전",
                    risk=15, change="예비회선은 대기 상태라 통신 영향 없음 (이중화 일시 해제)",
                    action="작업 후 재장착하여 예비회선 링크 정상 여부를 반드시 확인하세요.")
    if p == "UPS 배터리 모듈" and has(text, ["뽑", "분리", "교체", "빼"]):
        ss.alert = None
        return dict(kind="warn", intent="UPS 배터리 모듈 교체", verdict="조건부 가능 · 주의", risk=35,
                    change="모듈 1개 탈거 시 백업 시간 단축. 상용전원 정상이면 통신 영향 없음",
                    action="상용전원 정상 확인 후 1개씩 교체하고, 교체 후 충전 및 경보 해제를 확인하세요.")
    if p == "LTE-R 연결 광점퍼 포트" and has(text, ["뽑", "분리", "교체", "빼", "청소"]) and p in ss.cleared:
        ss.alert = None
        return dict(kind="warn", intent="LTE-R 광점퍼 분리/청소 (사전 통보 완료)", verdict="조건부 진행 가능", risk=25,
                    change="작업 중 3번 승강장 LTE-R만 일시 중단 (관제 통보 완료)",
                    action="비운행 시간대에 작업하고, 재접속 후 LTE-R 통신 복구를 확인하세요.")
    if p == "LTE-R 연결 광점퍼 포트" and has(text, ["뽑", "분리", "교체", "빼", "청소"]):
        ss.alert = "danger"
        ss.alert_nodes = [0]
        ss.alert_msg = "해당 광점퍼 분리 시 3번 승강장 LTE-R 통신 두절"
        return dict(kind="danger", intent="LTE-R 연결 광점퍼 분리/청소", verdict="작업 불가 (사전 조치 필요)", risk=70,
                    change="3번 승강장 LTE-R 회선만 두절 (다른 하위 설비는 정상). 열차무선 영향 가능",
                    action="관제센터에 사전 통보하고 비운행 시간대에 작업하세요.")
    ss.alert = None
    return dict(kind="info", intent=f"'{p}' 일반 점검 문의", verdict="참고",
                risk=None, change="상태 변화 없음", action=S["general"][p])


def judge_signal(text):
    p = ss.selected
    P = SIG_PARTS
    bk = ss.is_backup_active
    change_kw = ["뽑", "분리", "교체", "빼"]
    if p == P[3] and has(text, change_kw + ["끄", "차단", "내리", "전원"]) and p in ss.cleared:
        ss.alert = None
        return dict(kind="warn", intent="제어전원 모듈 차단/교체 (관제 승인 완료)", verdict="조건부 진행 가능", risk=40,
                    change="작업 구간 폐쇄 상태에서 선로전환기 제어전원이 일시 차단됨",
                    action="승인된 구간·시간에만 작업하고, 복구 후 선로전환기 전환 시험을 실시하세요.")
    if p == P[3] and has(text, change_kw + ["끄", "차단", "내리", "전원"]):
        ss.alert = "fatal"
        return dict(kind="fatal", intent="선로전환기 제어전원 모듈 차단/교체", verdict="작업 불가", risk=100,
                    change="제어전원 상실 → 모든 선로전환기 전환 불능, 진로 설정 중단, 열차 운행 전면 정지",
                    action="⚠ 즉시 중지! 열차 운행 중에는 관제 승인 및 작업 구간 폐쇄 후에만 진행하세요.")
    if p == P[2] and has(text, ["복귀", "원복"]) and bk:
        ss.alert = None
        ss.is_backup_active = False
        return dict(kind="safe", intent="A계 복귀 절체 수행", verdict="작업 가능 · 복귀 절체 완료", risk=8,
                    change="연동 기능이 A계로 복귀. 선로전환기·궤도·신호기 표시 유지",
                    action="복귀 후 A/B계 동기화 상태와 진단 LED를 확인하세요.")
    if p == P[2] and has(text, ["전환", "절체", "B계", "대기", "예비"]):
        ss.alert = None
        ss.is_backup_active = True
        return dict(kind="backup", intent="B계로 계 절체 수행", verdict="작업 가능 · 무중단 절체 완료", risk=5,
                    change="연동 기능이 B계(대기계)로 넘어감. 열차 운행 영향 없음",
                    action="이제 A계 CPU 보드 작업이 가능합니다. 작업 후 A계 복귀를 잊지 마세요.")
    if p == P[0] and has(text, change_kw):
        if not bk:
            ss.alert = "danger"
            ss.alert_msg = "A계가 운용 중! 분리 시 연동장치 기능 상실"
            return dict(kind="danger", intent="운용계(A계) CPU 보드 분리 시도 (미절체)", verdict="작업 불가", risk=95,
                        change="연동 기능 정지 → 선로전환기·궤도회로·신호기 제어 불능, 열차 운행 중단",
                        action="먼저 '계 절체 스위치'로 B계 절체 후 재시도하세요.")
        ss.alert = None
        return dict(kind="safe", intent="A계 CPU 보드 분리/교체 (B계 절체 완료)", verdict="작업 가능 · 안전", risk=10,
                    change="B계가 연동 기능을 담당 중이므로 운행 영향 없음",
                    action="정전기 방지 조치 후 작업하고, 재장착 후 A/B계 동기화를 확인하세요.")
    if p == P[1] and has(text, change_kw):
        if bk:
            ss.alert = "danger"
            ss.alert_msg = "B계가 현재 운용 중! 분리 시 연동장치 기능 상실"
            return dict(kind="danger", intent="B계 CPU 보드 분리 시도 (B계 운용 중)", verdict="작업 불가", risk=90,
                        change="운용 중인 B계 정지 → 전 설비 제어 불능",
                        action="먼저 A계로 복귀 절체 후 재시도하세요.")
        ss.alert = None
        return dict(kind="safe", intent="B계 CPU 보드 분리/점검 (A계 운용 중)", verdict="작업 가능 · 안전", risk=15,
                    change="대기계 분리라 운행 영향 없음 (이중계 일시 해제)",
                    action="재장착 후 A/B계 동기화 완료를 반드시 확인하세요.")
    if p == P[4] and has(text, change_kw) and p in ss.cleared:
        ss.alert = None
        return dict(kind="warn", intent="궤도회로 모듈 교체 (구간 폐쇄 완료)", verdict="조건부 진행 가능", risk=25,
                    change="폐쇄된 T1 구간 점유 표시가 일시 변동될 수 있음 (관제 통보 완료)",
                    action="교체 후 궤도 표시 정상 복귀와 구간 개방 전 점검을 실시하세요.")
    if p == P[4] and has(text, change_kw):
        ss.alert = "danger"
        ss.alert_nodes = [1]
        ss.alert_msg = "T1 궤도회로 모듈 분리 시 해당 구간 점유 오표시"
        return dict(kind="danger", intent="궤도회로 송수신 모듈 교체", verdict="작업 불가 (사전 조치 필요)", risk=75,
                    change="T1 구간이 점유로 표시(안전측) → 진로 설정 불가, 열차 지연. 다른 설비는 정상",
                    action="해당 구간을 폐쇄하고 관제에 통보한 후 작업하세요.")
    if p == P[5] and has(text, change_kw):
        ss.alert = None
        return dict(kind="warn", intent="서지보호기(SPD) 모듈 교체", verdict="조건부 가능 · 주의", risk=30,
                    change="교체 중 낙뢰 방호 일시 해제. 맑은 날 교체 시 운행 영향 없음",
                    action="기상 확인 후 교체하고, 접지선 체결과 접지저항을 점검하세요.")
    ss.alert = None
    return dict(kind="info", intent=f"'{p}' 일반 점검 문의", verdict="참고",
                risk=None, change="상태 변화 없음", action=S["general"][p])


def judge(text):
    if not ss.selected:
        return dict(kind="info", intent="부품 미선택", verdict="대기", risk=None, change="-",
                    action="좌측 도면에서 작업할 부품을 먼저 선택해 주세요.")
    ss.alert_nodes = None
    ss.alert_msg = ""
    res = judge_signal(text) if ss.site == "signal" else judge_comm(text)
    meta = META.get((ss.selected, res["kind"]))
    if meta:
        res["steps"] = meta["steps"]
        res["fix"] = meta.get("fix")
    return res


def handle(text):
    ss.last_text = text
    ss.messages.append(dict(role="user", text=text))
    with st.spinner("AI가 작업 의도를 분석하고 결과를 예측하는 중..."):
        time.sleep(0.5)
        res = judge(text)
    ss.messages.append(dict(role="assistant", card=res))


def comm_rows():
    bk = ss.is_backup_active
    mm = "#3b0d0d" if (ss.alert and not bk) else "#14233f"
    return [(f"주회선 광모듈 #1 {'(대기)' if bk else '(운용)'}", mm),
            (f"예비회선 광모듈 #2 {'(운용)' if bk else '(대기)'}", "#14233f"),
            (f"절체 스위치 [{'예비' if bk else '주'}]", "#14233f"),
            ("메인 전원 차단기 [ON]", "#14233f"),
            ("UPS 배터리 모듈 [정상]", "#14233f"),
            ("LTE-R 연결 광점퍼 포트", "#14233f")]


def sig_rows():
    bk = ss.is_backup_active
    a = "#3b0d0d" if (ss.alert and not bk) else "#14233f"
    return [(f"A계 CPU 보드 {'(대기)' if bk else '(운용)'}", a),
            (f"B계 CPU 보드 {'(운용)' if bk else '(대기)'}", "#14233f"),
            (f"계 절체 스위치 [{'B계' if bk else 'A계'}]", "#14233f"),
            ("선로전환기 제어전원 [ON]", "#14233f"),
            ("궤도회로 송수신 모듈", "#14233f"),
            ("서지보호기(SPD) 모듈 [정상]", "#14233f")]


SITES = {
    "comm": dict(
        label="통신설비 (광전송장비 MSPP)", site_name="대전역 주통신실 - 광전송장비 MSPP #1",
        rack_title="광전송장비 MSPP #1 통신 랙", diagram="통신 설비 계통도",
        badge=("주회선 단독 운용", "예비회선 우회 중"), parts=COMM_PARTS, tasks=COMM_TASKS,
        chips=COMM_CHIPS, general=COMM_GENERAL, rows=comm_rows,
        nodes=[("3번 승강장 LTE-R", 70, "📡"), ("승강장 행선안내기", 190, "🪧"), ("역무실 CCTV", 310, "📹")],
        fatal_msg="메인 전원 차단 시 장비 전체 정지 및 모든 하위 설비 통신 두절!",
        default_msg="현재 작업 시 주회선 통신 두절 발생! 절체 스위치를 먼저 조작하세요.",
        placeholder="작업 계획을 입력하세요 (예: 이 광모듈 교체할게요)"),
    "signal": dict(
        label="신호설비 (전자연동장치 EIS)", site_name="대전조차장 신호기계실 - 전자연동장치 EIS #1",
        rack_title="전자연동장치 EIS #1 랙", diagram="신호 설비 계통도",
        badge=("A계 단독 운용", "B계 절체 운용 중"), parts=SIG_PARTS, tasks=SIG_TASKS,
        chips=SIG_CHIPS, general=SIG_GENERAL, rows=sig_rows,
        nodes=[("1번 선로전환기 (P101)", 70, "🔀"), ("T1 궤도회로 구간", 190, "🛤"), ("출발신호기 (S1)", 310, "🚦")],
        fatal_msg="제어전원 차단 시 모든 선로전환기 전환 불능 및 열차 운행 전면 정지!",
        default_msg="현재 작업 시 연동 기능이 정지됩니다. 계 절체를 먼저 수행하세요.",
        placeholder="작업 계획을 입력하세요 (예: A계 CPU 보드 교체할게요)"),
}
S = SITES[ss.site]
PARTS = S["parts"]

def fx(kind, label, bubble, intent="", change=""):
    return dict(kind=kind, label=label, bubble=bubble, intent=intent, change=change)


META = {
    # ---- 통신설비
    ("주회선 광모듈 #1", "danger"): dict(
        steps=["이중화 수동 절체 스위치로 예비회선 절체", "절체 후 하위 설비 3종 통신 정상 확인", "주회선 광모듈 분리/교체 진행"],
        fix=fx("switch", "① 예비회선 절체 수행 후 작업 재개", "✅ 선행 조치: 이중화 수동 절체 스위치로 예비회선 절체",
               "예비회선 수동 절체 수행 (선행 조치)", "트래픽이 예비회선(광모듈 #2)으로 우회됨. 하위 설비 통신 유지")),
    ("주회선 광모듈 #1", "safe"): dict(
        steps=["정전기 방지 장갑 착용", "광모듈 분리 후 커넥터 단면 점검/청소", "재장착 후 링크 LED·광레벨 확인", "이중화 스위치로 주회선 복귀 절체"]),
    ("예비회선 광모듈 #2", "danger"): dict(
        steps=["이중화 스위치로 주회선 복귀", "주회선 링크·광레벨 정상 확인", "예비 광모듈 분리/점검 진행"],
        fix=fx("restore", "① 주회선 복귀 절체 후 작업 재개", "✅ 선행 조치: 주회선으로 복귀 절체",
               "주회선 복귀 절체 수행 (선행 조치)", "트래픽이 주회선으로 복귀. 예비회선은 대기 상태")),
    ("예비회선 광모듈 #2", "safe"): dict(steps=["예비회선 대기 상태 확인", "모듈 분리·점검", "재장착 후 예비회선 링크 정상 확인"]),
    ("이중화 수동 절체 스위치", "backup"): dict(
        steps=["하위 설비 3종 통신 정상 확인", "주회선 광모듈 #1 작업 진행", "작업 완료 후 복귀 절체"]),
    ("이중화 수동 절체 스위치", "safe"): dict(steps=["주회선 링크 LED·광레벨 확인", "하위 설비 3종 통신 정상 확인"]),
    ("메인 전원 차단기", "fatal"): dict(
        steps=["관제센터·상급자에 작업 승인 요청", "하위 설비(LTE-R/행선안내기/CCTV) 중단 통보", "계획정전 시간대 확정", "승인 후 차단기 조작"],
        fix=fx("clear", "① 승인·통보 완료 후 작업 재개", "✅ 선행 조치: 관제·상급자 승인 및 하위 설비 중단 통보 완료")),
    ("메인 전원 차단기", "warn"): dict(steps=["승인 시간대 확인", "차단기 OFF 조작", "작업 수행", "전원 투입 후 통신 복구 확인"]),
    ("UPS 배터리 모듈", "warn"): dict(steps=["상용전원 정상 확인", "모듈 1개 탈거·교체", "충전 상태·경보 해제 확인"]),
    ("LTE-R 연결 광점퍼 포트", "danger"): dict(
        steps=["관제센터에 LTE-R 일시 중단 통보", "비운행 시간대 확인", "해당 포트 광점퍼 분리·청소", "재접속 후 LTE-R 통신 복구 확인"],
        fix=fx("clear", "① 관제 통보 완료 후 작업 재개", "✅ 선행 조치: 관제 통보 및 비운행 시간대 확인 완료")),
    ("LTE-R 연결 광점퍼 포트", "warn"): dict(steps=["비운행 시간대 작업", "광점퍼 분리·단면 청소", "재접속 후 LTE-R 통신 복구 확인"]),
    # ---- 신호설비
    ("운용계(A계) CPU 보드", "danger"): dict(
        steps=["계 절체 스위치로 B계 절체", "A/B계 동기화 및 표시 정상 확인", "A계 CPU 보드 분리/교체 진행"],
        fix=fx("switch", "① B계 절체 수행 후 작업 재개", "✅ 선행 조치: 계 절체 스위치로 B계 절체",
               "B계로 계 절체 수행 (선행 조치)", "연동 기능이 B계(대기계)로 넘어감. 열차 운행 영향 없음")),
    ("운용계(A계) CPU 보드", "safe"): dict(steps=["정전기 방지 조치", "A계 보드 분리·교체", "재장착 후 A/B계 동기화 확인", "A계 복귀 절체"]),
    ("대기계(B계) CPU 보드", "danger"): dict(
        steps=["계 절체 스위치로 A계 복귀", "A/B계 동기화 정상 확인", "B계 CPU 보드 분리/점검 진행"],
        fix=fx("restore", "① A계 복귀 절체 후 작업 재개", "✅ 선행 조치: A계로 복귀 절체",
               "A계 복귀 절체 수행 (선행 조치)", "연동 기능이 A계로 복귀. B계는 대기 상태")),
    ("대기계(B계) CPU 보드", "safe"): dict(steps=["대기계 상태 확인", "B계 보드 분리·점검", "재장착 후 A/B계 동기화 완료 확인"]),
    ("계 절체 스위치", "backup"): dict(steps=["선로전환기·궤도·신호기 표시 확인", "A계 CPU 보드 작업 진행", "작업 완료 후 A계 복귀"]),
    ("계 절체 스위치", "safe"): dict(steps=["A/B계 동기화 상태 확인", "진단 LED 확인"]),
    ("선로전환기 제어전원 모듈", "fatal"): dict(
        steps=["관제 승인 요청", "작업 구간 폐쇄 및 열차 운행 통제 확인", "승인된 시간대 확정", "제어전원 차단·교체 진행"],
        fix=fx("clear", "① 관제 승인·구간 폐쇄 후 작업 재개", "✅ 선행 조치: 관제 승인 및 작업 구간 폐쇄 완료")),
    ("선로전환기 제어전원 모듈", "warn"): dict(steps=["승인 구간·시간 확인", "제어전원 차단·교체", "복구 후 선로전환기 전환 시험"]),
    ("궤도회로 송수신 모듈", "danger"): dict(
        steps=["T1 구간 폐쇄", "관제에 통보", "궤도회로 모듈 교체", "점유 표시 정상 복귀 확인 후 구간 개방"],
        fix=fx("clear", "① 구간 폐쇄·관제 통보 후 작업 재개", "✅ 선행 조치: T1 구간 폐쇄 및 관제 통보 완료")),
    ("궤도회로 송수신 모듈", "warn"): dict(steps=["폐쇄 구간 확인", "모듈 교체", "점유 표시 복귀 확인 후 구간 개방"]),
    ("서지보호기(SPD) 모듈", "warn"): dict(steps=["기상 확인", "SPD 모듈 교체", "접지선 체결·접지저항 점검"]),
}


def steps_html(r):
    if not r.get("steps"):
        return ""
    items = "".join(f"<li>{html.escape(x)}</li>" for x in r["steps"])
    return f'<br><b class="k">작업 절차</b><ol>{items}</ol>'


def run_fix(fix):
    ss.messages.append(dict(role="user", text=fix["bubble"]))
    with st.spinner("선행 조치를 반영하고 작업을 다시 평가하는 중..."):
        time.sleep(0.5)
        if fix["kind"] == "switch":
            ss.is_backup_active = True
            ss.alert = None
            done = dict(kind="backup", intent=fix["intent"], verdict="선행 조치 완료", risk=5,
                        change=fix["change"], action="이제 원래 작업을 다시 평가합니다.")
        elif fix["kind"] == "restore":
            ss.is_backup_active = False
            ss.alert = None
            done = dict(kind="safe", intent=fix["intent"], verdict="선행 조치 완료", risk=8,
                        change=fix["change"], action="이제 원래 작업을 다시 평가합니다.")
        else:
            ss.cleared.add(ss.selected)
            ss.alert = None
            done = dict(kind="safe", intent="사전 승인·통보 절차 완료", verdict="선행 조치 완료", risk=None,
                        change="작업에 필요한 사전 절차가 확인됨", action="이제 원래 작업을 다시 평가합니다.")
        ss.messages.append(dict(role="assistant", card=done))
        time.sleep(0.5)
        ss.messages.append(dict(role="assistant", card=judge(ss.last_text)))


def queue_fix(fix):
    ss.pending_fix = fix


# input handling first so left panel reflects new state
if ss.pending:
    t, ss.pending = ss.pending, None
    handle(t)
if ss.pending_fix:
    f, ss.pending_fix = ss.pending_fix, None
    run_fix(f)

# ---------------------------------------------------------------- CSS
st.markdown(f"""
<style>
.stApp {{ background:#0b1220; color:#d7e0ee; }}
header[data-testid="stHeader"] {{ background:transparent; }}
.block-container {{ padding-top:2.2rem; max-width:1500px; }}
.hdr {{ display:flex; align-items:center; gap:14px; padding:12px 18px; background:#111a2e;
  border:1px solid #1f2d4a; border-left:5px solid {BLUE}; border-radius:8px; }}
.hdr .t {{ font-size:1.35rem; font-weight:700; color:#fff; }}
.hdr .s {{ color:#8fa3c4; font-size:.9rem; }}
.badge {{ padding:4px 12px; border-radius:14px; font-size:.82rem; font-weight:700; }}
.b-main {{ background:#0f3d24; color:#4ade80; border:1px solid #22c55e; }}
.b-bk {{ background:#0b2a52; color:#60a5fa; border:1px solid {BLUE}; }}
.panel-t {{ color:#8fa3c4; font-size:.85rem; margin:6px 0; letter-spacing:.5px; }}
.warn {{ background:#3b0d0d; border:1px solid #ef4444; color:#fecaca; padding:10px 14px;
  border-radius:8px; margin-bottom:8px; font-weight:600; animation:blink 1s infinite; }}
@keyframes blink {{ 50% {{ opacity:.45; }} }}
.sel {{ display:inline-block; background:#0b2a52; border:1px solid {BLUE}; color:#9cc4f5;
  padding:4px 12px; border-radius:6px; font-size:.88rem; margin-bottom:8px; }}
.card {{ background:#111a2e; border:1px solid #1f2d4a; border-left:4px solid #64748b;
  border-radius:8px; padding:10px 14px; margin:4px 0; font-size:.88rem; line-height:1.55; }}
.card.danger, .card.fatal {{ border-left-color:#ef4444; background:#1f1015; }}
.card.warn {{ border-left-color:#f59e0b; background:#1f1a0e; }}
.card.safe {{ border-left-color:#22c55e; background:#0e1f18; }}
.card.backup {{ border-left-color:#3b82f6; background:#0d1a30; }}
.card ol {{ margin:4px 0 0 18px; padding:0; }}
.card b.k {{ color:#8fa3c4; font-weight:600; }}
.umsg {{ text-align:right; margin:6px 0; }}
.umsg span {{ background:{BLUE}; color:#fff; padding:6px 12px; border-radius:12px 12px 0 12px;
  display:inline-block; font-size:.9rem; }}
.stButton>button {{ background:#111a2e; color:#d7e0ee; border:1px solid #2a3b5f; border-radius:8px; }}
.stButton>button:hover {{ border-color:{BLUE}; color:#fff; }}
.stButton>button[kind="primary"] {{ background:{BLUE}; border-color:{BLUE}; color:#fff; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{ background:#0e1628; }}
div[data-testid="stRadio"] label, div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label div {{ color:#fff !important; opacity:1 !important; }}
[data-testid="stChatInput"], [data-testid="stChatInput"] > div, [data-testid="stChatInput"] textarea {{
  background:#f1f5f9 !important; }}
[data-testid="stChatInput"] textarea {{ color:#000 !important; -webkit-text-fill-color:#000 !important;
  font-weight:500; caret-color:#000; }}
[data-testid="stChatInput"] textarea::placeholder {{ color:#333 !important; -webkit-text-fill-color:#333 !important; opacity:1; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- header
h1, h2 = st.columns([6, 1], vertical_alignment="center")
with h1:
    bcls, btxt = (("b-bk", S["badge"][1]) if ss.is_backup_active
                  else ("b-main", S["badge"][0]))
    st.markdown(f"""<div class="hdr"><div><div class="t">🚆 KORAIL Field-AI 코파일럿</div>
<div class="s">작업 의도 판단 &amp; 결과 예측 · 현장: {S["site_name"]}</div></div>
<div style="margin-left:auto"><span class="badge {bcls}">● {btxt}</span></div></div>""",
                unsafe_allow_html=True)
with h2:
    st.button("🔄 초기화", on_click=reset, use_container_width=True)

st.radio("분야 선택", list(SITES), format_func=lambda k: SITES[k]["label"], horizontal=True,
         key="site", on_change=reset)
left, right = st.columns([55, 45], gap="large")

# ---------------------------------------------------------------- left
with left:
    if ss.alert == "fatal":
        st.markdown(f'<div class="warn">🚨 경고: {html.escape(S["fatal_msg"])}</div>',
                    unsafe_allow_html=True)
    elif ss.alert == "danger":
        msg = ss.alert_msg or S["default_msg"]
        st.markdown(f'<div class="warn">🚨 경고: {html.escape(msg)}</div>', unsafe_allow_html=True)

    if ss.alert:
        lc, cls = "#ef4444", "blink"
    elif ss.is_backup_active:
        lc, cls = "#3b82f6", "flow"
    else:
        lc, cls = "#22c55e", ""

    sel = ss.selected

    def hl(name):
        return "#f5c542" if sel == name else "#2a3b5f"

    nodes = S["nodes"]
    paths, boxes = "", ""
    base_c, base_cls = ("#3b82f6", "flow") if ss.is_backup_active else ("#22c55e", "")
    for i, (label, y, ic) in enumerate(nodes):
        hit = ss.alert and (ss.alert_nodes is None or i in ss.alert_nodes)
        nc, ncls = ("#ef4444", "blink") if hit else (base_c, base_cls)
        paths += (f'<path class="ln {ncls}" d="M 300 200 C 400 200, 420 {y+25}, 520 {y+25}" '
                  f'stroke="{nc}" fill="none" stroke-width="4"/>')
        boxes += (f'<rect x="520" y="{y}" width="190" height="50" rx="8" fill="#111a2e" stroke="{nc}" stroke-width="2"/>'
                  f'<text x="615" y="{y+30}" fill="#d7e0ee" font-size="14" text-anchor="middle">{ic} {label}</text>')
    rack = "".join(
        f'<rect x="50" y="{85 + 50 * i}" width="230" height="40" rx="6" fill="{fill}" stroke="{hl(PARTS[i])}" stroke-width="2"/>'
        f'<text x="165" y="{110 + 50 * i}" fill="#d7e0ee" font-size="13" text-anchor="middle">{label}</text>'
        for i, (label, fill) in enumerate(S["rows"]()))
    svg = f"""
<svg viewBox="0 0 740 440" xmlns="http://www.w3.org/2000/svg" style="width:100%;background:#0e1628;border:1px solid #1f2d4a;border-radius:8px">
<style>
.ln.blink {{ animation: bl 0.8s infinite; }}
.ln.flow {{ stroke-dasharray: 10 6; animation: fl 1s linear infinite; }}
@keyframes bl {{ 50% {{ opacity:.2; }} }}
@keyframes fl {{ to {{ stroke-dashoffset:-32; }} }}
</style>
{paths}
<rect x="30" y="40" width="270" height="380" rx="10" fill="#0b1220" stroke="{BLUE}" stroke-width="3"/>
<text x="165" y="68" fill="#9cc4f5" font-size="15" font-weight="bold" text-anchor="middle">{S["rack_title"]}</text>
{rack}
<circle cx="300" cy="200" r="7" fill="{lc}"/>
{boxes}
</svg>"""
    st.markdown(f'<div class="panel-t">▌ {S["diagram"]}</div>{svg}', unsafe_allow_html=True)
    st.markdown('<div class="panel-t">▌ 작업 대상 부품 선택</div>', unsafe_allow_html=True)
    for i in (0, 2, 4):
        c1, c2 = st.columns(2)
        for c, p in zip((c1, c2), PARTS[i:i + 2]):
            c.button(p, key=f"p_{p}", on_click=select, args=(p,), use_container_width=True,
                     type="primary" if sel == p else "secondary")

    if sel:
        st.markdown(f'<div class="panel-t">▌ 부품 상세 이미지 · {html.escape(sel)}</div>',
                    unsafe_allow_html=True)
        photo = find_photo(PARTS.index(sel))
        if photo:
            st.image(photo, use_container_width=True)
        else:
            st.markdown(part_svg(PARTS.index(sel)), unsafe_allow_html=True)
            st.caption(f"가상 일러스트입니다. 실제 사진은 assets 폴더에 {'sig_' if ss.site == 'signal' else ''}part1~6.png(jpg)로 넣으면 자동 표시됩니다.")

# ---------------------------------------------------------------- right
with right:
    st.markdown('<div class="panel-t">▌ AI 코파일럿</div>', unsafe_allow_html=True)
    if sel:
        st.markdown(f'<span class="sel">선택된 부품: {html.escape(sel)}</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="sel">선택된 부품 없음</span>', unsafe_allow_html=True)
    for t in S["tasks"].get(sel, S["chips"]):
        st.button(t, key=f"chip_{sel}_{t}", on_click=queue, args=(t,), use_container_width=True)

    box = st.container(height=360)
    with box:
        if not ss.messages:
            st.caption("부품을 선택하고 작업 계획을 입력하면 AI가 의도를 해석하고 결과를 예측합니다.")
        for m in ss.messages:
            if m["role"] == "user":
                st.markdown(f'<div class="umsg"><span>{html.escape(m["text"])}</span></div>',
                            unsafe_allow_html=True)
            else:
                r = m["card"]
                if r["risk"] is None:
                    risk = "-"
                else:
                    ic = "🔴" if r["risk"] >= 50 else "🟢"
                    risk = f"{ic} {r['risk']}%"
                st.markdown(f"""<div class="card {r['kind']}">
<b class="k">AI 해석 의도</b> {html.escape(r['intent'])}<br>
<b class="k">판정</b> <b>{html.escape(r['verdict'])}</b><br>
<b class="k">위험도</b> {risk}<br>
<b class="k">예상 변화</b> {html.escape(r['change'])}<br>
<b class="k">권장 조치</b> {html.escape(r['action'])}{steps_html(r)}</div>""", unsafe_allow_html=True)

    last = ss.messages[-1]["card"] if ss.messages and ss.messages[-1]["role"] == "assistant" else None
    if last and last.get("fix"):
        st.button("▶ " + last["fix"]["label"], key=f"fix_{len(ss.messages)}", on_click=queue_fix,
                  args=(last["fix"],), type="primary", use_container_width=True)

    if prompt := st.chat_input(S["placeholder"]):
        queue(prompt)
        st.rerun()
