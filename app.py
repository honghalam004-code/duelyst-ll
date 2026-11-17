import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DUELYST // CHRONICLES OF MYTHRON",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {
        padding: 0.25rem 0.5rem 0rem 0.5rem !important;
        max-width: 100% !important;
    }
    .stApp { background-color: #04060c; }
    iframe {
        border: none !important;
        display: block;
        margin: 0 auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

GAME_HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Press+Start+2P&family=Noto+Sans+KR:wght@400;700;900&display=swap');
  * { box-sizing: border-box; user-select: none; }
  body {
    margin: 0;
    padding: 0;
    background: #04060c;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Noto Sans KR', sans-serif;
    overflow: hidden;
  }
  canvas {
    background: #060913;
    border: 2px solid #1e293b;
    border-radius: 6px;
    box-shadow: 0 0 45px rgba(0, 0, 0, 0.95);
    max-width: 100vw;
    max-height: 99vh;
  }
</style>
</head>
<body>
<canvas id="game" width="1280" height="800"></canvas>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const W = canvas.width;
const H = canvas.height;

// =========================================================================
// 1. 24x24 고해상도 다층 도트 스프라이트 엔진 (외곽선 + 3단계 명암 + 발광 효과)
// =========================================================================
function buildSprite24(palette, rows) {
  const off = document.createElement('canvas');
  off.width = 24;
  off.height = 24;
  const octx = off.getContext('2d');
  for (let y = 0; y < 24; y++) {
    const row = (rows[y] || '').padEnd(24, '.').slice(0, 24);
    for (let x = 0; x < 24; x++) {
      const ch = row[x];
      if (ch !== '.' && palette[ch]) {
        octx.fillStyle = palette[ch];
        octx.fillRect(x, y, 1, 1);
      }
    }
  }
  return off;
}

const P = {
  O: '#080b12', // 외곽선
  W: '#ffffff', S: '#cbd5e1', D: '#475569', K: '#1e293b',
  // 금빛/태양 (라이오나르)
  Y: '#fef08a', G: '#f59e0b', B: '#b45309', U: '#2563eb', C: '#38bdf8',
  // 진홍/그림자 (송하이)
  R: '#fb7185', M: '#e11d48', N: '#881337',
  // 청록/사막 (베트루비안)
  T: '#5eead4', E: '#0d9488', A: '#d97706',
  // 자수정/심연 (어비시안)
  V: '#e879f9', P: '#9333ea', X: '#4c1d95',
  // 에메랄드/용족 (마그마르)
  L: '#6ee7b7', Z: '#059669', Q: '#064e3b', H: '#f97316',
  // 빙하/서리 (바나르)
  I: '#bae6fd', F: '#0284c7', J: '#1e3a8a'
};

const SPRITES = {
  // 1) 아르게온 하이메이 (황금 성기사 장군)
  argeon: buildSprite24(P, [
    '.......OO......OO.......',
    '......OYYO....OYYO......',
    '.....OYGGYO..OYGGYO.....',
    '.....OGGGGGGGGGGGGO.....',
    '....OOGWWWWWWWWWWGOO....',
    '....OGWCCCCCCCCCCWGO....',
    '....OGWCCCCCCCCCCWGO....',
    '.....OGGGGGGGGGGGGO.....',
    '......OOBBBBBBBBOO......',
    '...OOOBBGGGGGGGGBBOOO...',
    '..OYYBGGGGYYYYGGGGBYYO..',
    '.OYYBGGGGYYYYYYGGGGBYYO.',
    '.OOBGGGGGGYYYYGGGGGGBOO.',
    '..OUBGGGGGGGGGGGGGGBUO..',
    '..OUBBGGGGGGGGGGGGBBUO..',
    '...OUUOBBBBBBBBBBOUUO...',
    '....OO.OOGGGGGGOO.OO....',
    '.......OGGGOOGGGO.......',
    '.......OGGGOOGGGO.......',
    '......OBBBBOOBBBBO......',
    '......OOOOOO.OOOOO......',
    '........................',
    '........................',
    '........................'
  ]),
  // 2) 칼레오스 잔 (송하이 붉은 닌자 장군)
  kaleos: buildSprite24(P, [
    '......OOOO....OOOO......',
    '.....OMMMMO..OMMMMO.....',
    '......OMMMMMMMMMMO......',
    '.....OMMMMMMMMMMMMO.....',
    '....OOMKKKKKKKKKKMOO....',
    '....OMKRRRRRRRRRRKMO....',
    '....OMKKKKKKKKKKKKMO....',
    '.....OMMMMMMMMMMMMO.....',
    '......OONNNNNNNNOO......',
    '..OOOONNKKKKKKKKNNOOOO..',
    '.OMMMNKKKKKKKKKKKKNMMMO.',
    '.OMMNKKKKMMMMMMKKKKNMMO.',
    '..OONKKKMMMMMMMMKKKNOO..',
    '..OWOKKKKKKKKKKKKKKOWO..',
    '.OWWOKKKKNNNNNNKKKKOWWO.',
    '.OWO.OONNNNNNNNNNOO.OWO.',
    '......ONNNNOONNNNO......',
    '......OKKKKOOKKKKO......',
    '.....ONNNNNOONNNNNO.....',
    '.....OOOOOO..OOOOOO.....',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  // 3) 지릭스 스타스트라이더 (베트루비안 사이버 파라오)
  zirix: buildSprite24(P, [
    '.....OOO........OOO.....',
    '....OGGGO......OGGGO....',
    '....OGGGO......OGGGO....',
    '....OGGGGGGGGGGGGGGO....',
    '....OGGTTTTTTTTTTGGO....',
    '....OGGTEEEEEEEETGGO....',
    '.....OGGGGGGGGGGGGO.....',
    '......OOAAAAAAAAOO......',
    '..OOOOAAGGGGGGGGAOOOO...',
    '.OTTTAAGGGTTTTGGGAAATT0.',
    '.OTTAAGGGTTTTTTGGGAAATO.',
    '..OOAAGGGGTTTTGGGGAAOO..',
    '...OOGGGGGGGGGGGGGGOO...',
    '....OOTTTTTTTTTTTTOO....',
    '.....OOAAAAAAAAAOO......',
    '......OOGGGOOGGGO.......',
    '......OAAAOO.OAAAO......',
    '.....OGGGGO...OGGGGO....',
    '.....OOOOO.....OOOOO....',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  // 4) 리리스 블라이트체이서 (어비시안 심연 여왕)
  lilithe: buildSprite24(P, [
    '...OOO............OOO...',
    '..OVVVO..........OVVVO..',
    '..OVPPVO........OVPPVO..',
    '...OVPPVVVVVVVVVVPPVO...',
    '....OVPPPPPPPPPPPPVO....',
    '....OVPWWWWWWWWWWPVO....',
    '....OVPWVVWWWWVVWPVO....',
    '.....OVPPPPPPPPPPVO.....',
    '.OOOOOXXPPPPPPPPXXOOOOO.',
    'OXXXXXXXPPPPPPPPXXXXXXXO',
    'OXXPPXXXPPVVVVPPXXXPPXXO',
    '.OOXXOXXPPPPPPPPXXOXXOO.',
    '....OOXXPPPPPPPPXXOO....',
    '.....OXXPPPPPPPPXXO.....',
    '.....OXXXXPPPPXXXXO.....',
    '....OXXXXXXOOXXXXXXO....',
    '....OXXXXXO..OXXXXXO....',
    '...OXXXXXO....OXXXXXO...',
    '...OOOOOO......OOOOOO...',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  // 5) 바스 디 이모탈 (마그마르 고대 용군주)
  vaath: buildSprite24(P, [
    '..OOO..............OOO..',
    '.OHHHO............OHHHO.',
    '.OHLLHO..........OHLLHO.',
    '..OHLLLLLLLLLLLLLLLLHO..',
    '..OLLLLLLLLLLLLLLLLLLO..',
    '..OLLHHHHHHHHHHHHHHLLO..',
    '..OLLHRRRRRRRRRRRRHLLO..',
    '...OLLLLLLLLLLLLLLLLO...',
    '.OOQQLLLLLLLLLLLLLLQQOO.',
    'OQQQQLLLLLHHHHLLLLLQQQQO',
    'OQQLLLLLLHHHHHHLLLLLLQQO',
    'OQQLLLLLLLHHHHLLLLLLLQQO',
    '.OOQQLLLLLLLLLLLLLLQQOO.',
    '..OQQQQLLLLLLLLLLQQQQO..',
    '...OQQQQOOOOOOOOQQQQO...',
    '....OLLLLOO..OOLLLLO....',
    '...OQQQQQO....OQQQQQO...',
    '...OOOOOO......OOOOOO...',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  // 6) 페이 블러드윙 (바나르 서리 발키리)
  faie: buildSprite24(P, [
    '...OOO............OOO...',
    '..OIIIO..........OIIIO..',
    '..OIFFIO........OIFFIO..',
    '...OIFIIIIIIIIIIIIFIO...',
    '....OIIIIIIIIIIIIIIO....',
    '....OIIWWWWWWWWWWIIO....',
    '....OIIWCCWWWWCCWIIO....',
    '.....OIIIIIIIIIIIIO.....',
    '..OOOOJJFFFFFFFFJJOOOO..',
    '.OSSSSJJIIIIIIIIJJSSSSO.',
    '.OSSSJJIIIIWWIIIIJJSSSO.',
    '..OO.OJJIIIIIIIIJJO.OO..',
    '.....OJJFFFFFFFFJJO.....',
    '......OIIIIIIIIIIO......',
    '......OJJJJOOJJJJO......',
    '.....OIIIIO..OIIIIO.....',
    '.....OFFFFO..OFFFFO.....',
    '....OOOOOO....OOOOOO....',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),

  // 하수인 스프라이트들
  paladin: buildSprite24(P, [
    '.......OOOOOOOOOO.......',
    '......OYYYYYYYYYYO......',
    '......OGGGGGGGGGGO......',
    '......OGCCCCCCCCGO......',
    '.......OGGGGGGGGO.......',
    '....OOOBBGGGGGGGBOOO....',
    '...OYYYBGGGGGGGGBWWO....',
    '...OYYGBGGGGGGGGBWWO....',
    '...OYYGBGGGGGGGGBWWO....',
    '....OOOBBBBBBBBBOWWO....',
    '......OOGGGGGGGOOWO.....',
    '......OGGGOOGGGO........',
    '......OBBBOOBBBO........',
    '.....OOOOOO.OOOOO.......',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  assassin: buildSprite24(P, [
    '.......OOOOOOOOOO.......',
    '......OMMMMMMMMMMO......',
    '......OKKKKKKKKKKO......',
    '......OKRRRRRRRRKO......',
    '.......OKKKKKKKKO.......',
    '...OOOONNKKKKKKNNOOOO...',
    '..OMMMNKKKKKKKKKKNMMMO..',
    '..OONNKKKKKKKKKKKKNNOO..',
    '....OOKKKKKKKKKKKKOO....',
    '...OWWOKKKKNNKKKKOWWO...',
    '..OWWW.ONNNOONNNO.WWWO..',
    '.......OKKKOOKKKO.......',
    '......ONNNNOONNNNO......',
    '......OOOOO..OOOOO......',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  dervish: buildSprite24(P, [
    '.......OOOOOOOOOO.......',
    '......OTTTTTTTTTTO......',
    '......OTYYYYYYYYTO......',
    '......OTEEEEEEEEtO......',
    '.......OTTTTTTTTO.......',
    '....OOOAATTTTTTAAOOO....',
    '...OGGGATTTTTTTTAGGGO...',
    '....OOOAATTTTTTAAOOO....',
    '......OOTTTTTTTTOO......',
    '.......OTTTTTTTTO.......',
    '........OTTTTTTO........',
    '.........OTTTTO.........',
    '..........OTTO..........',
    '...........OO...........',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  wraith: buildSprite24(P, [
    '.......OOOOOOOOOO.......',
    '......OVVVVVVVVVVO......',
    '......OVPPPPPPPPVO......',
    '......OVWWPPPPWWVO......',
    '.......OVPPPPPPVO.......',
    '...OOOOXXPPPPPPXXOOOO...',
    '..OPPPXXXPPPPPPXXXPPPO..',
    '..OOXXXXXPPPPPPXXXXXOO..',
    '....OXXXXPPPPPPXXXXO....',
    '.....OXXXPPPPPPXXXO.....',
    '......OXXOXXXXOXXO......',
    '.......OO..OO..OO.......',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  beast: buildSprite24(P, [
    '...OOO............OOO...',
    '..OHHHO..........OHHHO..',
    '...OHLLLLLLLLLLLLLLHO...',
    '..OLLLLLLLLLLLLLLLLLLO..',
    '..OLLRRRRRRRRRRRRRRLLO..',
    '.OLLLLLLLLLLLLLLLLLLLLO.',
    'OQQLLLLLLHHHHHHLLLLLLQQO',
    'OQQLLLLLLHHHHHHLLLLLLQQO',
    '.OOQQLLLLLLLLLLLLLLQQOO.',
    '..OQQQLLLLLLLLLLLLQQQO..',
    '..OQQQOO........OOQQQO..',
    '.OLLLLLO........OLLLLLO.',
    '.OOOOOO..........OOOOOO.',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  wolf: buildSprite24(P, [
    '....OO............OO....',
    '...OIIO..........OIIO...',
    '...OIIIIIIIIIIIIIIIIO...',
    '..OIIFFFFFFFFFFFFFFIIO..',
    '..OIFCCCCCCCCCCCCCCFIO..',
    '.OIIIIIIIIIIIIIIIIIIIIO.',
    'OSSSSIIIIIIIIIIIIIISSSSO',
    '.OOSSIIIIIIIIIIIIIIISSO.',
    '..OIIIIOO......OOIIIIO..',
    '..OFFFFO........OFFFFO..',
    '.OIIIIIO........OIIIIIO.',
    '.OOOOOO..........OOOOOO.',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  archer: buildSprite24(P, [
    '.......OOOOOOOOOO.......',
    '......OLLLLLLLLLLO......',
    '......OLYYYYYYYYLO......',
    '.......OLLLLLLLLO.......',
    '....OOOZZLLLLLLZZOOO....',
    '...OZZZLLLLLLLLLLZZZOAA.',
    '....OOOZZLLLLLLZZOOO.AWA',
    '......OOLLLLLLLLOO...AWA',
    '......OZZZOOOOZZZO...AWA',
    '......OZZZO..OZZZO..AA..',
    '.....OLLLLLO.OLLLLLO....',
    '.....OOOOOO..OOOOOO.....',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ]),
  golem: buildSprite24(P, [
    '.....OOOOOOOOOOOOOO.....',
    '....ODDDDDDDDDDDDDDO....',
    '...ODSSSSSSSSSSSSSSDO...',
    '...ODSSCCCCCCCCCCSSDO...',
    '...ODSSSSSSSSSSSSSSDO...',
    '..OODDDDDDDDDDDDDDDDOO..',
    '.ODDDDDDDDDDDDDDDDDDDDO.',
    '.ODDDDCCCCCCCCCCCCDDDDO.',
    '.ODDDDDDDDDDDDDDDDDDDDO.',
    '..OODDDDDDDDDDDDDDDDOO..',
    '...ODDDDDOOOOOODDDDDO...',
    '...ODDDDDO....ODDDDDO...',
    '..OSSSSSSO....OSSSSSSO..',
    '..OOOOOOO......OOOOOOO..',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................',
    '........................'
  ])
};

// =========================================================================
// 2. 듀얼리스트 오리지널 6대 진영 + 풍부한 스펠/아티팩트/하수인 카드 데이터베이스
// =========================================================================
const FACTIONS = {
  argeon: {
    id: 'argeon', name: '아르게온 하이메이', title: '라이오나르 왕국 (LYONAR)',
    color: '#fbbf24', accent: '#38bdf8', sprite: 'argeon',
    bbsName: '왕의 포효 (Roar)', bbsCost: 1,
    bbsDesc: '아군 장군 주변 8칸 내 아군 1기에게 공격력 +2 영구 부여',
    lore: '태양의 방패와 신성 마법으로 전선을 장악하는 황금 기사단',
    cards: [
      { name: '은빛 방패기사', type: 'minion', cost: 2, atk: 1, hp: 4, sprite: 'paladin', keywords: ['provoke'], art: 'shield', desc: '도발: 인접 적의 이동 및 원거리 공격을 강제로 봉쇄합니다.' },
      { name: '태양의 돌격병', type: 'minion', cost: 3, atk: 3, hp: 3, sprite: 'paladin', keywords: ['rush'], art: 'sun', desc: '돌진: 소환 즉시 이동하고 적을 공격할 수 있습니다.' },
      { name: '신성한 결속', type: 'spell', cost: 2, spell: 'divine_bond', art: 'holy', desc: '스펠: 아군 하수인 1기에게 현재 체력만큼 공격력을 부여합니다!' },
      { name: '성스러운 제물', type: 'spell', cost: 4, spell: 'holy_immolation', art: 'nova', desc: '스펠: 아군 1기 체력 +4 회복 & 그 주변 모든 적에게 4 광역 피해!' },
      { name: '순교 (Martyrdom)', type: 'spell', cost: 2, spell: 'martyrdom', art: 'judgment', desc: '스펠: 대상 하수인 1기를 즉시 처치하고 그 주인의 장군을 체력만큼 회복.' },
      { name: '태양석 건틀릿', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_sun', desc: '아티팩트 (내구도 3): 아군 장군에게 공격력 +2를 부여합니다.' }
    ]
  },
  kaleos: {
    id: 'kaleos', name: '칼레오스 잔', title: '송하이 제국 (SONGHAI)',
    color: '#f43f5e', accent: '#fb923c', sprite: 'kaleos',
    bbsName: '점멸 (Blink)', bbsCost: 1,
    bbsDesc: '아군 하수인 1기를 최대 2칸 떨어진 빈 칸으로 순간이동',
    lore: '그림자 도약과 불사조 비술로 적 장군을 단숨에 암살하는 붉은 일족',
    cards: [
      { name: '카게 번개사수', type: 'minion', cost: 2, atk: 2, hp: 2, sprite: 'archer', keywords: ['ranged'], art: 'arrow', desc: '원거리: 보드 어디서든 반격 없이 적을 저격합니다.' },
      { name: '붉은 달 암살자', type: 'minion', cost: 3, atk: 4, hp: 2, sprite: 'assassin', keywords: ['rush'], art: 'blade', desc: '돌진: 소환 즉시 적의 측면을 파고드는 암살자입니다.' },
      { name: '불사조의 불꽃', type: 'spell', cost: 2, spell: 'phoenix_fire', art: 'fire', desc: '스펠: 대상 적(장군 포함)에게 3 피해를 입히고 카드 1장을 뽑습니다.' },
      { name: '내면의 집중', type: 'spell', cost: 1, spell: 'inner_focus', art: 'lightning', desc: '스펠: 공격력 3 이하 아군 하수인 1기를 즉시 재행동시킵니다!' },
      { name: '안개 용의 인장', type: 'spell', cost: 2, spell: 'mist_seal', art: 'teleport', desc: '스펠: 아군 하수인 1기에게 +1/+1을 주고 원하는 빈 칸으로 순간이동!' },
      { name: '그림자 가면', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_mask', desc: '아티팩트 (내구도 3): 장군 공격력 +2 및 원거리(Ranged) 부여!' }
    ]
  },
  zirix: {
    id: 'zirix', name: '지릭스 스타스트라이더', title: '베트루비안 제국 (VETRUVIAN)',
    color: '#14b8a6', accent: '#fbbf24', sprite: 'zirix',
    bbsName: '바람의 소환', bbsCost: 1,
    bbsDesc: '장군 주변 빈 칸에 2/2 돌진 바람의 데르비시 소환',
    lore: '모래폭풍의 정령과 고대 기계 유물로 전장을 지배하는 사막 제국',
    cards: [
      { name: '사막의 수호석상', type: 'minion', cost: 3, atk: 2, hp: 5, sprite: 'golem', keywords: ['provoke'], art: 'obelisk', desc: '도발: 높은 체력으로 중앙 마나 샘을 틀어막습니다.' },
      { name: '모래폭풍 정령', type: 'minion', cost: 3, atk: 3, hp: 2, sprite: 'dervish', keywords: ['rush'], art: 'sand', desc: '돌진: 황금 모래바람과 함께 돌격하는 정령입니다.' },
      { name: '자손의 축복', type: 'spell', cost: 2, spell: 'scions_wish', art: 'relic', desc: '스펠: 아군 하수인에게 +2/+2를 부여하고 카드 1장을 뽑습니다.' },
      { name: '엔트로피 붕괴', type: 'spell', cost: 3, spell: 'entropic_decay', art: 'void', desc: '스펠: 아군 장군 주변 8칸 내 적 하수인 1기를 즉시 소멸시킵니다!' },
      { name: '별의 분노', type: 'spell', cost: 4, spell: 'stars_fury', art: 'starstorm', desc: '스펠: 모든 적 유닛 바로 앞 칸에 2/2 돌진 데르비시를 소환합니다!' },
      { name: '이키르의 지팡이', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_staff', desc: '아티팩트 (내구도 3): 아군 장군에게 공격력 +2를 부여합니다.' }
    ]
  },
  lilithe: {
    id: 'lilithe', name: '리리스 블라이트체이서', title: '어비시안 군단 (ABYSSIAN)',
    color: '#c084fc', accent: '#f472b6', sprite: 'lilithe',
    bbsName: '망령의 부름', bbsCost: 1,
    bbsDesc: '장군 주변 빈 칸에 1/1 돌진 심연의 망령 2기 소환',
    lore: '끝없는 망령 물량과 암흑 의식으로 적의 생명을 흡수하는 심연 군단',
    cards: [
      { name: '심연의 사신', type: 'minion', cost: 4, atk: 5, hp: 4, sprite: 'wraith', keywords: ['rush'], art: 'reaper', desc: '돌진: 공포스러운 파괴력의 심연 사신입니다.' },
      { name: '어둠의 파수꾼', type: 'minion', cost: 3, atk: 2, hp: 4, sprite: 'golem', keywords: ['provoke'], art: 'shadow', desc: '도발: 망령 군단을 보호하는 어둠의 방벽입니다.' },
      { name: '영혼 착취', type: 'spell', cost: 2, spell: 'void_pulse', art: 'drain', desc: '스펠: 대상 적에게 2 피해를 입히고 아군 장군 체력을 3 회복합니다.' },
      { name: '악마의 유혹', type: 'spell', cost: 2, spell: 'daemonic_lure', art: 'lure', desc: '스펠: 적 하수인에게 1 피해를 주고 보드의 원하는 빈 칸으로 강제 이동!' },
      { name: '영혼 파쇄 서약', type: 'spell', cost: 2, spell: 'soulshatter', art: 'swarm', desc: '스펠: 이번 턴 동안 모든 아군 하수인에게 공격력 +2를 부여합니다!' },
      { name: '유령의 칼날', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_void', desc: '아티팩트 (내구도 3): 장군 공격력 +2 및 처치 시 체력 +2 회복!' }
    ]
  },
  vaath: {
    id: 'vaath', name: '바스 디 이모탈', title: '마그마르 위상 (MAGMAR)',
    color: '#10b981', accent: '#f97316', sprite: 'vaath',
    bbsName: '과부하 (Overload)', bbsCost: 1,
    bbsDesc: '아군 장군의 공격력이 영구적으로 +1 증가',
    lore: '장군 스스로 괴물로 진화하며 광란의 야수들과 전장을 부수는 용족',
    cards: [
      { name: '마칸토르 전투야수', type: 'minion', cost: 5, atk: 4, hp: 4, sprite: 'beast', keywords: ['rush', 'frenzy'], art: 'beast_rage', desc: '돌진 · 광란: 소환 즉시 돌격하여 인접 모든 적을 동시 타격!' },
      { name: '태고의 수호룡', type: 'minion', cost: 3, atk: 3, hp: 4, sprite: 'beast', keywords: ['frenzy'], art: 'claw', desc: '광란: 공격 시 주변 8칸의 모든 적을 동시에 베어버립니다.' },
      { name: '자연의 선택', type: 'spell', cost: 2, spell: 'natural_select', art: 'acid', desc: '스펠: 전장에서 공격력이 가장 낮은 하수인 1기를 즉시 처치합니다.' },
      { name: '플라즈마 폭풍', type: 'spell', cost: 4, spell: 'plasma_storm', art: 'plasma', desc: '스펠: 공격력 3 이하인 모든 하수인을 전장에서 일소합니다!' },
      { name: '대지의 구체', type: 'spell', cost: 3, spell: 'earth_sphere', art: 'nature', desc: '스펠: 아군 장군의 체력을 7 회복합니다.' },
      { name: '아다만타이트 발톱', type: 'artifact', cost: 3, atkBonus: 3, art: 'artifact_claw', desc: '아티팩트 (내구도 3): 아군 장군에게 공격력 +3을 부여합니다!' }
    ]
  },
  faie: {
    id: 'faie', name: '페이 블러드윙', title: '바나르 혈족 (VANAR)',
    color: '#38bdf8', accent: '#e0f2fe', sprite: 'faie',
    bbsName: '전쟁의 새 (Warbird)', bbsCost: 1,
    bbsDesc: '적 장군과 같은 세로줄(열)의 모든 적에게 2 피해',
    lore: '혹한의 빙결 마법과 침묵 주문으로 적의 전략을 얼려버리는 북방 결사대',
    cards: [
      { name: '서리 송곳니 늑대', type: 'minion', cost: 2, atk: 3, hp: 2, sprite: 'wolf', keywords: ['rush'], art: 'wolf_ice', desc: '돌진: 빙원을 가르는 민첩한 사냥꾼입니다.' },
      { name: '빙하의 파수꾼', type: 'minion', cost: 4, atk: 3, hp: 6, sprite: 'golem', keywords: ['provoke'], art: 'ice_wall', desc: '도발: 뚫기 힘든 거대한 만년설 방벽입니다.' },
      { name: '냉혹한 한기', type: 'spell', cost: 2, spell: 'chromatic_cold', art: 'frost', desc: '스펠: 대상 하수인의 모든 능력을 침묵(해제)시키고 2 피해를 입힙니다!' },
      { name: '우박 감옥', type: 'spell', cost: 2, spell: 'hailstone', art: 'prison', desc: '스펠: 대상 적 하수인을 원래 주인의 손패로 되돌려 보냅니다!' },
      { name: '눈사태 (Avalanche)', type: 'spell', cost: 4, spell: 'avalanche', art: 'blizzard', desc: '스펠: 전장 왼쪽 절반(1~4열)의 모든 적에게 4 피해 및 기절(Stun)!' },
      { name: '콜드바이터', type: 'artifact', cost: 2, atkBonus: 1, art: 'artifact_ice', desc: '아티팩트 (내구도 3): 장군 공격력 +1 및 턴 종료 시 주변 적 2 피해!' }
    ]
  }
};

const NEUTRAL_CARDS = [
  { name: '전장의 척후병', type: 'minion', cost: 1, atk: 2, hp: 1, sprite: 'paladin', keywords: ['rush'], art: 'sun', desc: '돌진: 1턴부터 중앙 마나 샘을 선점할 수 있는 기동 병력.' },
  { name: '치유의 신비술사', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'archer', keywords: [], art: 'holy', desc: '균형 잡힌 공방 능력치를 지닌 2코스트 전사입니다.' },
  { name: '에메랄드 심판관', type: 'minion', cost: 3, atk: 2, hp: 3, sprite: 'archer', keywords: ['ranged'], art: 'arrow', desc: '원거리: 먼 거리에서 반격 없이 안전하게 지원 사격합니다.' },
  { name: '석화 토템 수호자', type: 'minion', cost: 3, atk: 2, hp: 5, sprite: 'golem', keywords: ['provoke'], art: 'obelisk', desc: '도발: 인접한 적들의 발을 묶는 단단한 수호자입니다.' }
];

// =========================================================================
// 3. 게임 상태 및 전장 레이아웃 상수
// =========================================================================
const ROWS = 5, COLS = 9;
const BOARD_X = 62, BOARD_Y = 128, TILE_W = 92, TILE_H = 76, GAP = 4;

let state = {
  screen: 'title', // 'title' | 'select' | 'battle'
  selectedFaction: 'argeon',
  enemyChoice: 'random',
  playerFaction: null,
  enemyFaction: null,
  board: [],
  manaOrbs: [],
  turn: 1,
  pMana: 2, pMaxMana: 2,
  eMana: 3, eMaxMana: 3,
  pDeck: [], pHand: [],
  eDeck: [], eHand: [],
  pBbsCd: 0, eBbsCd: 0,
  pArtifacts: [], // {name, atkBonus, dur, id}
  eArtifacts: [],
  replacedThisTurn: false,
  replaceMode: false,
  targetMode: null, // null | { kind: 'bbs_argeon' | 'bbs_kaleos_1' | 'bbs_kaleos_2' | 'spell_step2', cardIdx, firstPos }
  selectedPos: null,
  selectedCardIdx: null,
  hoverTile: null,
  hoverCardIdx: null,
  aiBusy: false,
  winner: null,
  logs: [],
  effects: [],
  tick: 0
};

function addLog(msg) {
  state.logs.unshift(msg);
  if (state.logs.length > 16) state.logs.pop();
}

function tileCenter(r, c) {
  return {
    x: BOARD_X + c * (TILE_W + GAP) + TILE_W / 2,
    y: BOARD_Y + r * (TILE_H + GAP) + TILE_H / 2
  };
}

function spawnFloatText(r, c, text, color) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'text', x: pt.x, y: pt.y - 20, text, color, t: 0, maxT: 60 });
}

function spawnBeam(r1, c1, r2, c2, color) {
  const p1 = tileCenter(r1, c1);
  const p2 = tileCenter(r2, c2);
  state.effects.push({ type: 'beam', x: p1.x, y: p1.y, x2: p2.x, y2: p2.y, color, t: 0, maxT: 24 });
}

function spawnRing(r, c, color) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'ring', x: pt.x, y: pt.y, color, t: 0, maxT: 28 });
}

function spawnBurst(r, c, color, count = 16) {
  const pt = tileCenter(r, c);
  for (let i = 0; i < count; i++) {
    const ang = (Math.PI * 2 * i) / count;
    const spd = 1.6 + Math.random() * 2.8;
    state.effects.push({
      type: 'particle', x: pt.x, y: pt.y,
      vx: Math.cos(ang) * spd, vy: Math.sin(ang) * spd,
      color, t: 0, maxT: 32
    });
  }
}

function buildDeck(factionId) {
  const fCards = FACTIONS[factionId].cards;
  const pool = [...fCards, ...NEUTRAL_CARDS];
  const deck = [];
  for (const c of pool) {
    deck.push({ ...c, keywords: [...(c.keywords || [])] });
    deck.push({ ...c, keywords: [...(c.keywords || [])] });
  }
  for (let i = deck.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [deck[i], deck[j]] = [deck[j], deck[i]];
  }
  return deck;
}

function startBattle(pFid, eChoice) {
  let eFid = eChoice;
  if (eFid === 'random') {
    const keys = Object.keys(FACTIONS).filter(k => k !== pFid);
    eFid = keys[Math.floor(Math.random() * keys.length)];
  }
  const pf = FACTIONS[pFid];
  const ef = FACTIONS[eFid];

  const board = Array.from({ length: ROWS }, () => Array(COLS).fill(null));
  board[2][0] = {
    name: pf.name, owner: 'player', isGeneral: true, sprite: pf.sprite,
    baseAtk: 2, atk: 2, hp: 25, maxHp: 25, keywords: [], stunned: false, canMove: true, canAttack: true
  };
  board[2][8] = {
    name: ef.name, owner: 'enemy', isGeneral: true, sprite: ef.sprite,
    baseAtk: 2, atk: 2, hp: 25, maxHp: 25, keywords: [], stunned: false, canMove: true, canAttack: true
  };

  const pDeck = buildDeck(pFid);
  const eDeck = buildDeck(eFid);

  state.screen = 'battle';
  state.playerFaction = pf;
  state.enemyFaction = ef;
  state.board = board;
  state.manaOrbs = [{ r: 0, c: 4 }, { r: 2, c: 4 }, { r: 4, c: 4 }];
  state.turn = 1;
  state.pMana = 2; state.pMaxMana = 2;
  state.eMana = 3; state.eMaxMana = 3;
  state.pDeck = pDeck;
  state.pHand = [pDeck.pop(), pDeck.pop(), pDeck.pop(), pDeck.pop(), pDeck.pop()];
  state.eDeck = eDeck;
  state.eHand = [eDeck.pop(), eDeck.pop(), eDeck.pop(), eDeck.pop(), eDeck.pop()];
  state.pBbsCd = 0;
  state.eBbsCd = 0;
  state.pArtifacts = [];
  state.eArtifacts = [];
  state.replacedThisTurn = false;
  state.replaceMode = false;
  state.targetMode = null;
  state.selectedPos = null;
  state.selectedCardIdx = null;
  state.aiBusy = false;
  state.winner = null;
  state.effects = [];
  state.logs = [`⚔️ ${pf.name} vs ${ef.name} 결투 시작!`];
}

// =========================================================================
// 4. 전술 판정 (이동, 도발, 원거리, 광란, 침묵, 기절, 아티팩트)
// =========================================================================
function neighbors8(r, c) {
  const res = [];
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (dr === 0 && dc === 0) continue;
      const nr = r + dr, nc = c + dc;
      if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS) res.push({ r: nr, c: nc });
    }
  }
  return res;
}

function findGeneral(owner) {
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && u.owner === owner && u.isGeneral) return { r, c, unit: u };
    }
  }
  return null;
}

function recalcGeneralStats(owner) {
  const g = findGeneral(owner);
  if (!g) return;
  const arts = owner === 'player' ? state.pArtifacts : state.eArtifacts;
  const bonus = arts.reduce((acc, a) => acc + a.atkBonus, 0);
  g.unit.atk = g.unit.baseAtk + bonus;
  const hasMask = arts.some(a => a.art === 'artifact_mask');
  g.unit.keywords = hasMask ? ['ranged'] : [];
}

function damageArtifacts(owner) {
  const arts = owner === 'player' ? state.pArtifacts : state.eArtifacts;
  if (!arts.length) return;
  for (let i = arts.length - 1; i >= 0; i--) {
    arts[i].dur--;
    if (arts[i].dur <= 0) {
      addLog(`💔 [${arts[i].name}] 내구도가 다해 파괴됨!`);
      arts.splice(i, 1);
    }
  }
  recalcGeneralStats(owner);
}

function getAdjacentProvokers(r, c, owner) {
  const list = [];
  for (const n of neighbors8(r, c)) {
    const u = state.board[n.r][n.c];
    if (u && u.owner !== owner && u.keywords.includes('provoke')) list.push(n);
  }
  return list;
}

function getValidMoves(r, c) {
  const u = state.board[r][c];
  if (!u || !u.canMove || u.stunned) return [];
  if (getAdjacentProvokers(r, c, u.owner).length > 0) return [];

  const visited = new Set([`${r},${c}`]);
  const q = [{ r, c, dist: 0 }];
  const valid = [];
  while (q.length) {
    const cur = q.shift();
    if (cur.dist === 2) continue;
    for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
      const nr = cur.r + dr, nc = cur.c + dc;
      const key = `${nr},${nc}`;
      if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS && !state.board[nr][nc] && !visited.has(key)) {
        visited.add(key);
        valid.push({ r: nr, c: nc });
        q.push({ r: nr, c: nc, dist: cur.dist + 1 });
      }
    }
  }
  return valid;
}

function getValidAttacks(r, c) {
  const u = state.board[r][c];
  if (!u || !u.canAttack || u.stunned) return [];
  const prov = getAdjacentProvokers(r, c, u.owner);
  if (prov.length > 0) return prov;

  const targets = [];
  if (u.keywords.includes('ranged')) {
    for (let tr = 0; tr < ROWS; tr++) {
      for (let tc = 0; tc < COLS; tc++) {
        const t = state.board[tr][tc];
        if (t && t.owner !== u.owner) targets.push({ r: tr, c: tc });
      }
    }
  } else {
    for (const n of neighbors8(r, c)) {
      const t = state.board[n.r][n.c];
      if (t && t.owner !== u.owner) targets.push(n);
    }
  }
  return targets;
}

function getValidSummonTiles(owner) {
  const map = new Map();
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && u.owner === owner) {
        for (const n of neighbors8(r, c)) {
          if (!state.board[n.r][n.c]) map.set(`${n.r},${n.c}`, n);
        }
      }
    }
  }
  return Array.from(map.values());
}

function getValidSpellTargets(card, owner) {
  const targets = [];
  const sp = card.spell;
  if (['holy_immolation', 'divine_bond', 'inner_focus', 'mist_seal', 'scions_wish'].includes(sp)) {
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (!u || u.owner !== owner) continue;
      if (sp === 'holy_immolation') targets.push({ r, c });
      else if (!u.isGeneral) {
        if (sp === 'inner_focus' && u.atk > 3) continue;
        targets.push({ r, c });
      }
    }
  } else if (['martyrdom', 'natural_select'].includes(sp)) {
    let minAtk = 999;
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && !u.isGeneral && u.atk < minAtk) minAtk = u.atk;
    }
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && !u.isGeneral) {
        if (sp === 'natural_select' && u.atk !== minAtk) continue;
        targets.push({ r, c });
      }
    }
  } else if (['phoenix_fire', 'void_pulse'].includes(sp)) {
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && u.owner !== owner) targets.push({ r, c });
    }
  } else if (['entropic_decay', 'daemonic_lure', 'chromatic_cold', 'hailstone'].includes(sp)) {
    const g = findGeneral(owner);
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (!u || u.owner === owner || u.isGeneral) continue;
      if (sp === 'entropic_decay' && g && (Math.abs(r - g.r) > 1 || Math.abs(c - g.c) > 1)) continue;
      targets.push({ r, c });
    }
  } else if (['stars_fury', 'soulshatter', 'plasma_storm', 'earth_sphere', 'avalanche'].includes(sp)) {
    // 광역/장군 대상 스펠은 보드 아무 칸이나 클릭해도 발동
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) targets.push({ r, c });
  }
  return targets;
}

function checkGameOver() {
  const p = findGeneral('player');
  const e = findGeneral('enemy');
  if (!e) state.winner = 'PLAYER';
  else if (!p) state.winner = 'ENEMY';
}

function checkOrbPickup(r, c, owner) {
  const idx = state.manaOrbs.findIndex(o => o.r === r && o.c === c);
  if (idx !== -1) {
    state.manaOrbs.splice(idx, 1);
    spawnRing(r, c, '#38bdf8');
    spawnBurst(r, c, '#38bdf8', 18);
    spawnFloatText(r, c, '+1 MANA', '#38bdf8');
    if (owner === 'player') {
      state.pMana++;
      addLog('💎 플레이어가 마나 샘(+1 마나) 흡수!');
    } else {
      state.eMana++;
      addLog('💎 적 AI가 마나 샘(+1 마나) 흡수!');
    }
  }
}

function dealDamageToUnit(r, c, dmg, color = '#ef4444') {
  const u = state.board[r][c];
  if (!u) return false;
  u.hp -= dmg;
  spawnFloatText(r, c, `-${dmg}`, color);
  spawnBurst(r, c, color, 14);
  if (u.isGeneral && dmg > 0) damageArtifacts(u.owner);
  if (u.hp <= 0) {
    addLog(`💥 [${u.name}] 처치됨!`);
    state.board[r][c] = null;
    return true; // killed
  }
  return false;
}

function moveUnit(r1, c1, r2, c2) {
  const u = state.board[r1][c1];
  state.board[r2][c2] = u;
  state.board[r1][c1] = null;
  u.canMove = false;
  spawnBurst(r2, c2, '#94a3b8', 10);
  checkOrbPickup(r2, c2, u.owner);
}

function attackUnit(r1, c1, r2, c2) {
  const atkU = state.board[r1][c1];
  const defU = state.board[r2][c2];
  if (!atkU || !defU) return;

  atkU.canAttack = false;
  atkU.canMove = false;
  const isRanged = atkU.keywords.includes('ranged');
  const isFrenzy = atkU.keywords.includes('frenzy');

  spawnBeam(r1, c1, r2, c2, isRanged ? '#38bdf8' : '#fbbf24');

  const victims = [{ r: r2, c: c2 }];
  if (isFrenzy && !isRanged) {
    for (const n of neighbors8(r1, c1)) {
      const adj = state.board[n.r][n.c];
      if (adj && adj.owner !== atkU.owner && !(n.r === r2 && n.c === c2)) victims.push(n);
    }
  }

  let anyKilled = false;
  for (const v of victims) {
    if (dealDamageToUnit(v.r, v.c, atkU.atk, '#ef4444')) anyKilled = true;
  }

  // 유령의 칼날 아티팩트 효과 (장군이 적 처치 시 체력 +2)
  if (anyKilled && atkU.isGeneral) {
    const arts = atkU.owner === 'player' ? state.pArtifacts : state.eArtifacts;
    if (arts.some(a => a.art === 'artifact_void')) {
      atkU.hp = Math.min(atkU.maxHp, atkU.hp + 2);
      spawnFloatText(r1, c1, '+2 HP', '#e879f9');
    }
  }

  // 원거리 공격이 아니면 방어자 동시 반격
  if (!isRanged && defU.hp > 0) {
    dealDamageToUnit(r1, c1, defU.atk, '#f97316');
  }
  addLog(`⚔️ ${atkU.name} → ${defU.name} 공격 (${atkU.atk} 피해)`);
  checkGameOver();
}

function summonMinion(card, r, c, owner) {
  const rush = card.keywords.includes('rush');
  state.board[r][c] = {
    name: card.name, owner, isGeneral: false, sprite: card.sprite,
    atk: card.atk, hp: card.hp, maxHp: card.hp,
    keywords: [...card.keywords], stunned: false, canMove: rush, canAttack: rush
  };
  spawnRing(r, c, '#10b981');
  spawnBurst(r, c, '#10b981', 14);
  spawnFloatText(r, c, card.name, '#34d399');
  addLog(`✨ ${owner === 'player' ? '아군' : '적'} [${card.name}] 소환!`);
  checkOrbPickup(r, c, owner);
}

function equipArtifact(card, owner) {
  const g = findGeneral(owner);
  if (!g) return;
  const list = owner === 'player' ? state.pArtifacts : state.eArtifacts;
  if (list.length >= 3) list.shift();
  list.push({ name: card.name, atkBonus: card.atkBonus, dur: 3, art: card.art });
  recalcGeneralStats(owner);
  spawnRing(g.r, g.c, '#fbbf24');
  spawnFloatText(g.r, g.c, `+${card.atkBonus} ATK`, '#fbbf24');
  addLog(`🛡️ ${owner === 'player' ? '아군' : '적'} 장군 [${card.name}] 장착!`);
}

function drawCards(owner, count) {
  const deck = owner === 'player' ? state.pDeck : state.eDeck;
  const hand = owner === 'player' ? state.pHand : state.eHand;
  for (let i = 0; i < count; i++) {
    if (deck.length && hand.length < 6) hand.push(deck.pop());
  }
}

function castSpell(card, r, c, owner, step2Pos = null) {
  const sp = card.spell;
  const t = state.board[r][c];
  const g = findGeneral(owner);
  const opp = owner === 'player' ? 'enemy' : 'player';
  const oppG = findGeneral(opp);
  if (g) spawnBeam(g.r, g.c, r, c, '#c084fc');

  if (sp === 'divine_bond' && t) {
    t.atk += t.hp;
    spawnRing(r, c, '#fbbf24');
    spawnFloatText(r, c, `+${t.hp} ATK!`, '#fbbf24');
  } else if (sp === 'holy_immolation' && t) {
    t.hp = Math.min(t.maxHp, t.hp + 4);
    spawnRing(r, c, '#fef08a');
    spawnFloatText(r, c, '+4 HP', '#34d399');
    for (const n of neighbors8(r, c)) {
      const adj = state.board[n.r][n.c];
      if (adj && adj.owner !== owner) dealDamageToUnit(n.r, n.c, 4, '#fbbf24');
    }
  } else if (sp === 'martyrdom' && t) {
    const heal = t.hp;
    const targetOwnerG = findGeneral(t.owner);
    state.board[r][c] = null;
    spawnBurst(r, c, '#fef08a', 20);
    if (targetOwnerG) {
      targetOwnerG.unit.hp = Math.min(targetOwnerG.unit.maxHp, targetOwnerG.unit.hp + heal);
      spawnFloatText(targetOwnerG.r, targetOwnerG.c, `+${heal} HP`, '#34d399');
    }
  } else if (sp === 'phoenix_fire' && t) {
    dealDamageToUnit(r, c, 3, '#f97316');
    drawCards(owner, 1);
  } else if (sp === 'inner_focus' && t) {
    t.canMove = true; t.canAttack = true; t.stunned = false;
    spawnRing(r, c, '#38bdf8');
    spawnFloatText(r, c, 'REACTIVATE!', '#38bdf8');
  } else if (sp === 'mist_seal' && t && step2Pos) {
    t.atk += 1; t.hp += 1; t.maxHp += 1;
    state.board[step2Pos.r][step2Pos.c] = t;
    state.board[r][c] = null;
    spawnRing(step2Pos.r, step2Pos.c, '#f43f5e');
    checkOrbPickup(step2Pos.r, step2Pos.c, owner);
  } else if (sp === 'scions_wish' && t) {
    t.atk += 2; t.hp += 2; t.maxHp += 2;
    spawnRing(r, c, '#14b8a6');
    spawnFloatText(r, c, '+2/+2', '#14b8a6');
    drawCards(owner, 1);
  } else if (sp === 'entropic_decay' && t) {
    spawnBurst(r, c, '#14b8a6', 22);
    spawnFloatText(r, c, 'DECAY', '#14b8a6');
    state.board[r][c] = null;
  } else if (sp === 'stars_fury') {
    const dir = owner === 'player' ? -1 : 1;
    for (let er = 0; er < ROWS; er++) for (let ec = 0; ec < COLS; ec++) {
      const eu = state.board[er][ec];
      if (eu && eu.owner !== owner) {
        const sc = ec + dir;
        if (sc >= 0 && sc < COLS && !state.board[er][sc]) {
          summonMinion({ name: '바람의 데르비시', atk: 2, hp: 2, sprite: 'dervish', keywords: ['rush'] }, er, sc, owner);
        }
      }
    }
  } else if (sp === 'void_pulse' && t) {
    dealDamageToUnit(r, c, 2, '#c084fc');
    if (g) {
      g.unit.hp = Math.min(g.unit.maxHp, g.unit.hp + 3);
      spawnFloatText(g.r, g.c, '+3 HP', '#34d399');
    }
  } else if (sp === 'daemonic_lure' && t && step2Pos) {
    const dead = dealDamageToUnit(r, c, 1, '#c084fc');
    if (!dead && state.board[r][c]) {
      state.board[step2Pos.r][step2Pos.c] = state.board[r][c];
      state.board[r][c] = null;
      spawnRing(step2Pos.r, step2Pos.c, '#c084fc');
    }
  } else if (sp === 'soulshatter') {
    for (let ar = 0; ar < ROWS; ar++) for (let ac = 0; ac < COLS; ac++) {
      const au = state.board[ar][ac];
      if (au && au.owner === owner && !au.isGeneral) {
        au.atk += 2;
        spawnFloatText(ar, ac, '+2 ATK', '#e879f9');
      }
    }
  } else if (sp === 'natural_select' && t) {
    spawnBurst(r, c, '#10b981', 20);
    spawnFloatText(r, c, 'CONSUMED', '#10b981');
    state.board[r][c] = null;
  } else if (sp === 'plasma_storm') {
    for (let mr = 0; mr < ROWS; mr++) for (let mc = 0; mc < COLS; mc++) {
      const mu = state.board[mr][mc];
      if (mu && !mu.isGeneral && mu.atk <= 3) {
        spawnBurst(mr, mc, '#10b981', 16);
        state.board[mr][mc] = null;
      }
    }
  } else if (sp === 'earth_sphere' && g) {
    g.unit.hp = Math.min(g.unit.maxHp, g.unit.hp + 7);
    spawnRing(g.r, g.c, '#10b981');
    spawnFloatText(g.r, g.c, '+7 HP', '#10b981');
  } else if (sp === 'chromatic_cold' && t) {
    t.keywords = []; // 침묵(Dispel)
    spawnFloatText(r, c, 'DISPELLED!', '#bae6fd');
    dealDamageToUnit(r, c, 2, '#38bdf8');
  } else if (sp === 'hailstone' && t) {
    const tHand = t.owner === 'player' ? state.pHand : state.eHand;
    if (tHand.length < 6) {
      tHand.push({
        name: t.name, type: 'minion', cost: Math.max(1, Math.min(6, Math.round((t.atk + t.maxHp) / 2))),
        atk: t.atk, hp: t.maxHp, sprite: t.sprite, keywords: [...t.keywords], art: 'ice_wall',
        desc: '우박 감옥에서 귀환한 하수인입니다.'
      });
    }
    spawnBurst(r, c, '#38bdf8', 18);
    state.board[r][c] = null;
  } else if (sp === 'avalanche') {
    for (let ar = 0; ar < ROWS; ar++) for (let ac = 0; ac <= 3; ac++) {
      const au = state.board[ar][ac];
      if (au && au.owner !== owner) {
        au.stunned = true;
        dealDamageToUnit(ar, ac, 4, '#38bdf8');
      }
    }
  }
  addLog(`🔮 [${card.name}] 시전!`);
  checkGameOver();
}

// =========================================================================
// 5. 장군 고유 스킬 (BBS)
// =========================================================================
function triggerBBS(owner) {
  const fac = owner === 'player' ? state.playerFaction : state.enemyFaction;
  const mana = owner === 'player' ? state.pMana : state.eMana;
  const cd = owner === 'player' ? state.pBbsCd : state.eBbsCd;
  if (cd > 0 || mana < fac.bbsCost) return false;
  const g = findGeneral(owner);
  if (!g) return false;

  if (fac.id === 'vaath') {
    g.unit.baseAtk += 1;
    recalcGeneralStats(owner);
    spawnRing(g.r, g.c, '#10b981');
    spawnFloatText(g.r, g.c, '+1 ATK', '#10b981');
    addLog(`🦖 [${fac.bbsName}] 장군 공격력 영구 +1!`);
  } else if (fac.id === 'zirix') {
    const empty = neighbors8(g.r, g.c).filter(n => !state.board[n.r][n.c]);
    if (!empty.length) return false;
    const pos = empty[Math.floor(Math.random() * empty.length)];
    summonMinion({ name: '바람의 데르비시', atk: 2, hp: 2, sprite: 'dervish', keywords: ['rush'] }, pos.r, pos.c, owner);
  } else if (fac.id === 'lilithe') {
    const empty = neighbors8(g.r, g.c).filter(n => !state.board[n.r][n.c]);
    if (!empty.length) return false;
    for (const pos of empty.slice(0, 2)) {
      summonMinion({ name: '심연의 망령', atk: 1, hp: 1, sprite: 'wraith', keywords: ['rush'] }, pos.r, pos.c, owner);
    }
  } else if (fac.id === 'faie') {
    const oppG = findGeneral(owner === 'player' ? 'enemy' : 'player');
    if (!oppG) return false;
    for (let r = 0; r < ROWS; r++) {
      const u = state.board[r][oppG.c];
      if (u && u.owner !== owner) dealDamageToUnit(r, oppG.c, 2, '#38bdf8');
    }
    addLog(`❄️ [${fac.bbsName}] ${oppG.c + 1}열 전체 냉기 폭격!`);
    checkGameOver();
  } else if (fac.id === 'argeon') {
    if (owner === 'player') {
      state.targetMode = { kind: 'bbs_argeon' };
      state.selectedCardIdx = null; state.selectedPos = null;
      addLog('👑 장군 주변 아군을 클릭해 공격력 +2 부여!');
      return true;
    } else {
      const allies = neighbors8(g.r, g.c).map(n => ({ ...n, u: state.board[n.r][n.c] })).filter(x => x.u && x.u.owner === 'enemy');
      if (!allies.length) return false;
      allies[0].u.atk += 2;
      spawnFloatText(allies[0].r, allies[0].c, '+2 ATK', '#fbbf24');
    }
  } else if (fac.id === 'kaleos') {
    if (owner === 'player') {
      state.targetMode = { kind: 'bbs_kaleos_1' };
      state.selectedCardIdx = null; state.selectedPos = null;
      addLog('🦊 순간이동할 아군 하수인을 선택하세요!');
      return true;
    }
    return false;
  }

  if (owner === 'player') { state.pMana -= fac.bbsCost; state.pBbsCd = 2; }
  else { state.eMana -= fac.bbsCost; state.eBbsCd = 2; }
  return true;
}

// =========================================================================
// 6. 턴 종료 & AI 전술 사고 엔진
// =========================================================================
function endPlayerTurn() {
  if (state.winner || state.aiBusy) return;
  // 콜드바이터 아티팩트 턴 종료 광역 피해
  if (state.pArtifacts.some(a => a.art === 'artifact_ice')) {
    const pg = findGeneral('player');
    if (pg) {
      for (const n of neighbors8(pg.r, pg.c)) {
        const eu = state.board[n.r][n.c];
        if (eu && eu.owner === 'enemy') dealDamageToUnit(n.r, n.c, 2, '#38bdf8');
      }
      checkGameOver();
    }
  }
  if (state.winner) return;

  state.aiBusy = true;
  state.selectedPos = null; state.selectedCardIdx = null; state.targetMode = null; state.replaceMode = false;

  state.eMaxMana = Math.min(9, state.eMaxMana + 1);
  state.eMana = state.eMaxMana;
  if (state.eBbsCd > 0) state.eBbsCd--;
  drawCards('enemy', 2);

  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const u = state.board[r][c];
    if (u && u.owner === 'enemy') { u.canMove = true; u.canAttack = true; u.stunned = false; }
  }

  const steps = [];
  // 1) AI 카드 사용 (하수인 + 아티팩트 + 스펠)
  steps.push(() => {
    for (let idx = state.eHand.length - 1; idx >= 0; idx--) {
      const card = state.eHand[idx];
      if (card.cost > state.eMana) continue;
      if (card.type === 'minion') {
        const tiles = getValidSummonTiles('enemy').sort((a, b) => a.c - b.c);
        if (tiles.length) {
          state.eMana -= card.cost; state.eHand.splice(idx, 1);
          summonMinion(card, tiles[0].r, tiles[0].c, 'enemy');
        }
      } else if (card.type === 'artifact') {
        state.eMana -= card.cost; state.eHand.splice(idx, 1);
        equipArtifact(card, 'enemy');
      } else if (card.type === 'spell') {
        const targets = getValidSpellTargets(card, 'enemy');
        if (targets.length) {
          const t = targets[0];
          let step2 = null;
          if (['mist_seal', 'daemonic_lure'].includes(card.spell)) {
            const empties = [];
            for (let er = 0; er < ROWS; er++) for (let ec = 0; ec < COLS; ec++) if (!state.board[er][ec]) empties.push({ r: er, c: ec });
            if (!empties.length) continue;
            empties.sort((a, b) => card.spell === 'mist_seal' ? a.c - b.c : b.c - a.c);
            step2 = empties[0];
          }
          state.eMana -= card.cost; state.eHand.splice(idx, 1);
          castSpell(card, t.r, t.c, 'enemy', step2);
        }
      }
    }
  });

  // 2) AI 고유 스킬
  steps.push(() => { if (!state.winner) triggerBBS('enemy'); });

  // 3) AI 이동 및 공격
  steps.push(() => {
    if (state.winner) return;
    const units = [];
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && u.owner === 'enemy') units.push({ r, c });
    }
    for (const pos of units) {
      if (state.winner) break;
      const u = state.board[pos.r][pos.c];
      if (!u || u.owner !== 'enemy' || u.stunned) continue;

      let atks = getValidAttacks(pos.r, pos.c);
      if (atks.length) {
        atks.sort((a, b) => state.board[a.r][a.c].hp - state.board[b.r][b.c].hp);
        attackUnit(pos.r, pos.c, atks[0].r, atks[0].c);
        continue;
      }
      const moves = getValidMoves(pos.r, pos.c);
      if (moves.length) {
        const pg = findGeneral('player') || { r: 2, c: 0 };
        if (u.isGeneral && u.hp <= 9) moves.sort((a, b) => b.c - a.c);
        else moves.sort((a, b) => (Math.abs(a.r - pg.r) + Math.abs(a.c - pg.c)) - (Math.abs(b.r - pg.r) + Math.abs(b.c - pg.c)));
        const dest = moves[0];
        moveUnit(pos.r, pos.c, dest.r, dest.c);
        atks = getValidAttacks(dest.r, dest.c);
        if (atks.length) {
          atks.sort((a, b) => state.board[a.r][a.c].hp - state.board[b.r][b.c].hp);
          attackUnit(dest.r, dest.c, atks[0].r, atks[0].c);
        }
      }
    }
  });

  // 4) 플레이어 턴 시작
  steps.push(() => {
    if (!state.winner) {
      if (state.eArtifacts.some(a => a.art === 'artifact_ice')) {
        const eg = findGeneral('enemy');
        if (eg) {
          for (const n of neighbors8(eg.r, eg.c)) {
            const pu = state.board[n.r][n.c];
            if (pu && pu.owner === 'player') dealDamageToUnit(n.r, n.c, 2, '#38bdf8');
          }
          checkGameOver();
        }
      }
      state.turn++;
      state.pMaxMana = Math.min(9, state.pMaxMana + 1);
      state.pMana = state.pMaxMana;
      if (state.pBbsCd > 0) state.pBbsCd--;
      state.replacedThisTurn = false;
      drawCards('player', 2);
      for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
        const u = state.board[r][c];
        if (u && u.owner === 'player') { u.canMove = true; u.canAttack = true; u.stunned = false; }
      }
      addLog(`🔵 TURN ${state.turn} — 당신의 차례`);
    }
    state.aiBusy = false;
  });

  steps.forEach((fn, i) => setTimeout(fn, (i + 1) * 430));
}

// =========================================================================
// 7. 입력(클릭 / 호버) 처리
// =========================================================================
function getMousePos(evt) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (evt.clientX - rect.left) * (W / rect.width),
    y: (evt.clientY - rect.top) * (H / rect.height)
  };
}
function inside(mx, my, x, y, w, h) { return mx >= x && mx <= x + w && my >= y && my <= y + h; }

canvas.addEventListener('mousemove', (e) => {
  const { x, y } = getMousePos(e);
  state.hoverTile = null;
  state.hoverCardIdx = null;
  if (state.screen !== 'battle') return;

  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const tx = BOARD_X + c * (TILE_W + GAP);
    const ty = BOARD_Y + r * (TILE_H + GAP);
    if (inside(x, y, tx, ty, TILE_W, TILE_H)) state.hoverTile = { r, c };
  }
  for (let i = 0; i < state.pHand.length; i++) {
    const cx = 195 + i * 155;
    if (inside(x, y, cx, 550, 146, 225)) state.hoverCardIdx = i;
  }
});

canvas.addEventListener('click', (e) => {
  const { x, y } = getMousePos(e);

  // [0] 타이틀 화면
  if (state.screen === 'title') {
    if (inside(x, y, W / 2 - 170, 520, 340, 68)) state.screen = 'select';
    return;
  }

  // [1] 진영 선택 화면
  if (state.screen === 'select') {
    const keys = Object.keys(FACTIONS);
    keys.forEach((fid, idx) => {
      const cx = 55 + idx * 196;
      if (inside(x, y, cx, 115, 184, 150)) state.selectedFaction = fid;
    });
    if (inside(x, y, 790, 685, 220, 54)) {
      const opts = ['random', ...keys];
      state.enemyChoice = opts[(opts.indexOf(state.enemyChoice) + 1) % opts.length];
    }
    if (inside(x, y, 1025, 685, 200, 54)) {
      startBattle(state.selectedFaction, state.enemyChoice);
    }
    return;
  }

  // [2] 전투 화면
  if (state.winner) {
    if (inside(x, y, W / 2 - 150, H / 2 + 40, 300, 58)) state.screen = 'select';
    return;
  }
  if (state.aiBusy) return;

  // 좌측 상단 BBS 아이콘 클릭
  if (inside(x, y, 225, 24, 72, 72)) {
    if (state.targetMode) state.targetMode = null;
    else triggerBBS('player');
    return;
  }

  // 좌측 하단 Replace 슬롯 클릭
  if (inside(x, y, 55, 575, 118, 175)) {
    if (!state.replacedThisTurn && state.pDeck.length > 0) {
      state.replaceMode = !state.replaceMode;
      state.selectedCardIdx = null; state.selectedPos = null; state.targetMode = null;
    }
    return;
  }

  // 우측 하단 END TURN & 진영 변경 버튼
  if (inside(x, y, 1135, 575, 115, 110)) {
    endPlayerTurn();
    return;
  }
  if (inside(x, y, 1135, 695, 115, 55)) {
    state.screen = 'select';
    return;
  }

  // 손패 카드 클릭
  for (let i = 0; i < state.pHand.length; i++) {
    const cx = 195 + i * 155;
    if (inside(x, y, cx, 550, 146, 225)) {
      if (state.replaceMode) {
        const oldC = state.pHand[i];
        const newC = state.pDeck.pop();
        state.pDeck.unshift(oldC);
        state.pHand[i] = newC;
        state.replacedThisTurn = true;
        state.replaceMode = false;
        addLog(`🔄 [${oldC.name}] → [${newC.name}] 교체!`);
        return;
      }
      const card = state.pHand[i];
      // 아티팩트 카드는 선택 후 재클릭 또는 바로 장착 지원
      if (card.type === 'artifact' && state.selectedCardIdx === i && card.cost <= state.pMana) {
        state.pMana -= card.cost;
        state.pHand.splice(i, 1);
        equipArtifact(card, 'player');
        state.selectedCardIdx = null;
        return;
      }
      state.selectedCardIdx = state.selectedCardIdx === i ? null : i;
      state.selectedPos = null;
      state.targetMode = null;
      return;
    }
  }

  // 보드 타일 클릭
  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const tx = BOARD_X + c * (TILE_W + GAP);
    const ty = BOARD_Y + r * (TILE_H + GAP);
    if (!inside(x, y, tx, ty, TILE_W, TILE_H)) continue;

    const u = state.board[r][c];

    // 다단계 타겟팅 모드 처리
    if (state.targetMode) {
      const tm = state.targetMode;
      if (tm.kind === 'bbs_argeon') {
        const pg = findGeneral('player');
        if (u && u.owner === 'player' && !u.isGeneral && pg && Math.abs(r - pg.r) <= 1 && Math.abs(c - pg.c) <= 1) {
          u.atk += 2;
          state.pMana -= state.playerFaction.bbsCost;
          state.pBbsCd = 2;
          spawnFloatText(r, c, '+2 ATK', '#fbbf24');
          spawnRing(r, c, '#fbbf24');
          addLog(`👑 [왕의 포효] ${u.name} 공격력 +2!`);
        }
        state.targetMode = null;
        return;
      }
      if (tm.kind === 'bbs_kaleos_1') {
        if (u && u.owner === 'player' && !u.isGeneral) {
          state.targetMode = { kind: 'bbs_kaleos_2', firstPos: { r, c } };
          addLog('🦊 순간이동할 빈 칸(2칸 이내)을 클릭하세요!');
        } else state.targetMode = null;
        return;
      }
      if (tm.kind === 'bbs_kaleos_2') {
        const fp = tm.firstPos;
        if (!u && Math.abs(r - fp.r) + Math.abs(c - fp.c) <= 2) {
          state.board[r][c] = state.board[fp.r][fp.c];
          state.board[fp.r][fp.c] = null;
          state.pMana -= state.playerFaction.bbsCost;
          state.pBbsCd = 2;
          spawnRing(r, c, '#f43f5e');
          checkOrbPickup(r, c, 'player');
        }
        state.targetMode = null;
        return;
      }
      if (tm.kind === 'spell_step2') {
        if (!u) {
          const card = state.pHand[tm.cardIdx];
          state.pMana -= card.cost;
          state.pHand.splice(tm.cardIdx, 1);
          castSpell(card, tm.firstPos.r, tm.firstPos.c, 'player', { r, c });
        }
        state.targetMode = null;
        state.selectedCardIdx = null;
        return;
      }
    }

    // 카드 사용 모드
    if (state.selectedCardIdx !== null) {
      const card = state.pHand[state.selectedCardIdx];
      if (card.cost <= state.pMana) {
        if (card.type === 'minion' && getValidSummonTiles('player').some(t => t.r === r && t.c === c)) {
          state.pMana -= card.cost;
          state.pHand.splice(state.selectedCardIdx, 1);
          summonMinion(card, r, c, 'player');
          state.selectedCardIdx = null;
          return;
        }
        if (card.type === 'artifact') {
          state.pMana -= card.cost;
          state.pHand.splice(state.selectedCardIdx, 1);
          equipArtifact(card, 'player');
          state.selectedCardIdx = null;
          return;
        }
        if (card.type === 'spell' && getValidSpellTargets(card, 'player').some(t => t.r === r && t.c === c)) {
          if (['mist_seal', 'daemonic_lure'].includes(card.spell)) {
            state.targetMode = { kind: 'spell_step2', cardIdx: state.selectedCardIdx, firstPos: { r, c } };
            addLog('✨ 이동시킬 목적지 빈 칸을 클릭하세요!');
            return;
          }
          state.pMana -= card.cost;
          state.pHand.splice(state.selectedCardIdx, 1);
          castSpell(card, r, c, 'player');
          state.selectedCardIdx = null;
          return;
        }
      }
      state.selectedCardIdx = null;
    }

    // 유닛 이동 / 공격
    if (state.selectedPos) {
      const sp = state.selectedPos;
      if (sp.r === r && sp.c === c) { state.selectedPos = null; return; }
      if (getValidMoves(sp.r, sp.c).some(m => m.r === r && m.c === c)) {
        moveUnit(sp.r, sp.c, r, c);
        state.selectedPos = { r, c };
        return;
      }
      if (getValidAttacks(sp.r, sp.c).some(a => a.r === r && a.c === c)) {
        attackUnit(sp.r, sp.c, r, c);
        state.selectedPos = null;
        return;
      }
    }

    if (u && u.owner === 'player') {
      state.selectedPos = { r, c };
      state.selectedCardIdx = null;
    } else {
      state.selectedPos = null;
    }
  }
});

// =========================================================================
// 8. 고퀄리티 렌더링 헬퍼 (입체 카드 아트, 배경 모노리스, 타이틀 & 전투 화면)
// =========================================================================
function roundRect(x, y, w, h, r, fill, stroke, lw = 2) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.stroke(); }
}

function drawSprite24(key, cx, cy, size, flipX = false, bob = 0) {
  const img = SPRITES[key] || SPRITES.paladin;
  ctx.save();
  ctx.imageSmoothingEnabled = false;
  ctx.translate(cx, cy + bob);
  if (flipX) ctx.scale(-1, 1);
  ctx.drawImage(img, -size / 2, -size / 2, size, size);
  ctx.restore();
}

// 카드 내부 전용 일러스트 아트워크 렌더링
function drawCardArt(card, x, y, w, h, bob = 0) {
  ctx.save();
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, 4);
  ctx.clip();

  const grad = ctx.createLinearGradient(x, y, x, y + h);
  if (card.type === 'spell') {
    grad.addColorStop(0, '#2e1065');
    grad.addColorStop(1, '#090d16');
  } else if (card.type === 'artifact') {
    grad.addColorStop(0, '#451a03');
    grad.addColorStop(1, '#090d16');
  } else {
    grad.addColorStop(0, '#0f172a');
    grad.addColorStop(1, '#1e293b');
  }
  ctx.fillStyle = grad;
  ctx.fillRect(x, y, w, h);

  const cx = x + w / 2;
  const cy = y + h / 2;

  if (card.type === 'spell') {
    // 마법진 & 원소 광채
    ctx.strokeStyle = 'rgba(216, 180, 254, 0.45)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(cx, cy, 26, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = '#38bdf8';
    ctx.beginPath();
    ctx.moveTo(cx, cy - 22); ctx.lineTo(cx + 20, cy + 12); ctx.lineTo(cx - 20, cy + 12); ctx.closePath();
    ctx.stroke();

    // 스펠 중앙 빛구슬
    const rg = ctx.createRadialGradient(cx, cy, 2, cx, cy, 22);
    rg.addColorStop(0, '#ffffff');
    rg.addColorStop(0.4, '#c084fc');
    rg.addColorStop(1, 'rgba(192,132,252,0)');
    ctx.fillStyle = rg;
    ctx.beginPath();
    ctx.arc(cx, cy, 22, 0, Math.PI * 2);
    ctx.fill();
  } else if (card.type === 'artifact') {
    // 황금 아티팩트 광배
    const rg = ctx.createRadialGradient(cx, cy, 4, cx, cy, 28);
    rg.addColorStop(0, '#fef08a');
    rg.addColorStop(0.5, '#f59e0b');
    rg.addColorStop(1, 'rgba(245,158,11,0)');
    ctx.fillStyle = rg;
    ctx.beginPath();
    ctx.arc(cx, cy, 28, 0, Math.PI * 2);
    ctx.fill();
    drawSprite24(card.sprite, cx, cy + 4, 48, false, bob);
  } else {
    // 하수인 바닥 그림자 + 스프라이트
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.beginPath();
    ctx.ellipse(cx, y + h - 8, 22, 6, 0, 0, Math.PI * 2);
    ctx.fill();
    drawSprite24(card.sprite, cx, cy + 4, 56, false, bob);
  }
  ctx.restore();
}

// 대기적인 듀얼리스트 스타일 배경 (부유하는 석조 모노리스 & 룬 광선)
function drawAtmosphereBg() {
  const bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#040711');
  bg.addColorStop(0.55, '#091124');
  bg.addColorStop(1, '#04060c');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  // 은은한 중앙 광원
  const sun = ctx.createRadialGradient(W / 2, 260, 20, W / 2, 260, 460);
  sun.addColorStop(0, 'rgba(56, 189, 248, 0.14)');
  sun.addColorStop(1, 'rgba(4, 7, 17, 0)');
  ctx.fillStyle = sun;
  ctx.fillRect(0, 0, W, H);

  // 부유하는 고대 석조 기둥(모노리스) 실루엣
  const pillars = [
    { x: 110, y: 180, w: 46, h: 170, spd: 0.02 },
    { x: 230, y: 120, w: 30, h: 120, spd: 0.03 },
    { x: 1020, y: 130, w: 34, h: 135, spd: 0.025 },
    { x: 1130, y: 190, w: 50, h: 185, spd: 0.018 }
  ];
  pillars.forEach((p, idx) => {
    const py = p.y + Math.sin(state.tick * p.spd + idx) * 8;
    ctx.fillStyle = '#0c152b';
    ctx.fillRect(p.x, py, p.w, p.h);
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.25)';
    ctx.lineWidth = 1;
    ctx.strokeRect(p.x, py, p.w, p.h);
    // 기둥 중앙 빛나는 룬 라인
    ctx.fillStyle = 'rgba(56, 189, 248, 0.45)';
    ctx.fillRect(p.x + p.w / 2 - 1, py + 18, 2, p.h - 36);
  });

  // 떠다니는 마나 입자
  for (let i = 0; i < 45; i++) {
    const px = (i * 173 + state.tick * 0.2) % W;
    const py = (H - ((i * 97 + state.tick * 0.45) % H));
    ctx.fillStyle = i % 2 === 0 ? 'rgba(56,189,248,0.45)' : 'rgba(251,191,36,0.35)';
    ctx.fillRect(px, py, 2, 2);
  }
}

// [0] 타이틀 화면
function drawTitleScreen() {
  drawAtmosphereBg();
  const bob = Math.sin(state.tick * 0.05) * 6;

  // 중앙 거대 육각 룬 엠블럼
  ctx.save();
  ctx.translate(W / 2, 260);
  ctx.rotate(state.tick * 0.004);
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
  ctx.lineWidth = 2;
  ctx.strokeRect(-95, -95, 190, 190);
  ctx.rotate(Math.PI / 4);
  ctx.strokeStyle = 'rgba(251, 191, 36, 0.35)';
  ctx.strokeRect(-95, -95, 190, 190);
  ctx.restore();

  // 좌우 대치하는 대표 장군 도트 일러스트
  drawSprite24('argeon', W / 2 - 210, 270, 128, false, bob);
  drawSprite24('kaleos', W / 2 + 210, 270, 128, true, -bob);

  ctx.textAlign = 'center';
  ctx.font = '900 54px "Cinzel", serif';
  ctx.fillStyle = '#f8fafc';
  ctx.fillText('DUELYST II', W / 2, 255);

  ctx.font = '700 16px "Press Start 2P", monospace';
  ctx.fillStyle = '#38bdf8';
  ctx.fillText('CHRONICLES OF MYTHRON', W / 2, 295);

  ctx.font = '15px "Noto Sans KR"';
  ctx.fillStyle = '#94a3b8';
  ctx.fillText('6대 진영 · 고유 장군 스킬(BBS) · 전술 그리드 · 스펠 & 아티팩트 카드 배틀', W / 2, 465);

  // 시작 버튼
  const pulse = 0.6 + Math.sin(state.tick * 0.08) * 0.4;
  roundRect(W / 2 - 170, 520, 340, 68, 8, '#0284c7', `rgba(56, 189, 248, ${pulse})`, 3);
  ctx.font = '900 22px "Noto Sans KR"';
  ctx.fillStyle = '#ffffff';
  ctx.fillText('⚔️ PLAY NOW', W / 2, 562);
}

// [1] 진영 & 덱 프리뷰 선택 화면
function drawSelectScreen() {
  drawAtmosphereBg();
  const keys = Object.keys(FACTIONS);
  const bob = Math.sin(state.tick * 0.07) * 4;

  ctx.textAlign = 'center';
  ctx.font = '900 26px "Cinzel", serif';
  ctx.fillStyle = '#f8fafc';
  ctx.fillText('SELECT YOUR FACTION & GENERAL', W / 2, 52);

  // 상단 6개 진영 초상 탭
  keys.forEach((fid, idx) => {
    const f = FACTIONS[fid];
    const cx = 55 + idx * 196;
    const isSel = state.selectedFaction === fid;
    roundRect(cx, 115, 184, 150, 8, isSel ? '#111d38' : '#090e1c', isSel ? f.color : '#1e293b', isSel ? 3 : 1.5);
    drawSprite24(f.sprite, cx + 92, 174, 72, false, isSel ? bob : 0);
    ctx.textAlign = 'center';
    ctx.font = '900 13px "Noto Sans KR"';
    ctx.fillStyle = isSel ? f.color : '#cbd5e1';
    ctx.fillText(f.name, cx + 92, 232);
    ctx.font = '11px "Noto Sans KR"';
    ctx.fillStyle = '#64748b';
    ctx.fillText(f.title.split(' ')[0], cx + 92, 250);
  });

  // 하단 선택된 진영 상세 프리뷰 + 전용 카드(스펠/아티팩트/하수인) 6장 전시
  const sel = FACTIONS[state.selectedFaction];
  roundRect(55, 285, 1170, 380, 10, 'rgba(9, 14, 28, 0.92)', sel.color, 2);

  // 좌측 장군 대형 전시대
  ctx.fillStyle = 'rgba(0,0,0,0.5)';
  ctx.beginPath();
  ctx.ellipse(175, 455, 52, 14, 0, 0, Math.PI * 2);
  ctx.fill();
  drawSprite24(sel.sprite, 175, 390, 124, false, bob);

  ctx.textAlign = 'center';
  ctx.font = 'bold 12px "Noto Sans KR"';
  ctx.fillStyle = sel.color;
  ctx.fillText(sel.title, 175, 488);
  ctx.font = '900 20px "Noto Sans KR"';
  ctx.fillStyle = '#ffffff';
  ctx.fillText(sel.name, 175, 514);

  roundRect(75, 532, 200, 112, 6, '#050811', '#1e293b', 1.5);
  ctx.textAlign = 'left';
  ctx.font = 'bold 12px "Noto Sans KR"';
  ctx.fillStyle = '#38bdf8';
  ctx.fillText(`⭐ 고유 스킬: ${sel.bbsName}`, 86, 554);
  ctx.font = '11.5px "Noto Sans KR"';
  ctx.fillStyle = '#e2e8f0';
  ctx.fillText(sel.bbsDesc.slice(0, 17), 86, 576);
  ctx.fillText(sel.bbsDesc.slice(17, 34), 86, 594);
  ctx.fillStyle = '#94a3b8';
  ctx.fillText(sel.lore.slice(0, 17), 86, 618);
  ctx.fillText(sel.lore.slice(17), 86, 634);

  // 우측 진영 전용 카드 6장 미리보기 (하수인 + 스펠 + 아티팩트)
  ctx.textAlign = 'left';
  ctx.font = '900 15px "Noto Sans KR"';
  ctx.fillStyle = '#fbbf24';
  ctx.fillText(`🃏 [${sel.title}] 전용 덱 핵심 카드 (스펠 · 아티팩트 · 하수인)`, 305, 318);

  sel.cards.forEach((c, idx) => {
    const kx = 305 + idx * 150;
    const ky = 335;
    roundRect(kx, ky, 140, 310, 7, '#0c1324', c.type === 'spell' ? '#a855f7' : (c.type === 'artifact' ? '#f59e0b' : '#38bdf8'), 1.5);
    drawCardArt(c, kx + 8, ky + 34, 124, 96, bob);

    // 코스트
    ctx.fillStyle = '#0284c7';
    ctx.beginPath();
    ctx.arc(kx + 20, ky + 18, 12, 0, Math.PI * 2);
    ctx.fill();
    ctx.textAlign = 'center';
    ctx.font = '900 13px "Noto Sans KR"';
    ctx.fillStyle = '#ffffff';
    ctx.fillText(c.cost, kx + 20, ky + 23);

    // 타입 배지
    ctx.font = 'bold 11px "Noto Sans KR"';
    ctx.fillStyle = c.type === 'spell' ? '#e879f9' : (c.type === 'artifact' ? '#fbbf24' : '#38bdf8');
    ctx.fillText(c.type === 'spell' ? 'SPELL' : (c.type === 'artifact' ? 'ARTIFACT' : 'MINION'), kx + 82, ky + 22);

    ctx.font = '900 13px "Noto Sans KR"';
    ctx.fillStyle = '#f8fafc';
    ctx.fillText(c.name, kx + 70, ky + 150);

    if (c.type === 'minion') {
      ctx.fillStyle = '#fbbf24';
      ctx.fillText(`⚔️ ${c.atk}   ❤️ ${c.hp}`, kx + 70, ky + 172);
    } else if (c.type === 'artifact') {
      ctx.fillStyle = '#fbbf24';
      ctx.fillText(`장군 공격력 +${c.atkBonus}`, kx + 70, ky + 172);
    } else {
      ctx.fillStyle = '#c084fc';
      ctx.fillText('즉시 발동 주문', kx + 70, ky + 172);
    }

    ctx.font = '11px "Noto Sans KR"';
    ctx.fillStyle = '#cbd5e1';
    for (let line = 0; line < 5; line++) {
      ctx.fillText(c.desc.slice(line * 12, (line + 1) * 12), kx + 70, ky + 198 + line * 18);
    }
  });

  // 하단 상대 AI 선택 & 출격 버튼
  const eLabel = state.enemyChoice === 'random' ? '🎲 상대 AI: 랜덤' : `🤖 AI: ${FACTIONS[state.enemyChoice].name.split(' ')[0]}`;
  roundRect(790, 685, 220, 54, 8, '#0f172a', '#475569', 2);
  ctx.textAlign = 'center';
  ctx.font = 'bold 15px "Noto Sans KR"';
  ctx.fillStyle = '#e2e8f0';
  ctx.fillText(eLabel, 900, 718);

  roundRect(1025, 685, 200, 54, 8, '#0284c7', '#38bdf8', 2);
  ctx.font = '900 18px "Noto Sans KR"';
  ctx.fillStyle = '#ffffff';
  ctx.fillText('⚔️ 전투 시작', 1125, 718);
}

// [2] 전투 화면
function drawBattleScreen() {
  drawAtmosphereBg();

  const pf = state.playerFaction;
  const ef = state.enemyFaction;
  const pg = findGeneral('player');
  const eg = findGeneral('enemy');
  const pHp = pg ? pg.unit.hp : 0;
  const eHp = eg ? eg.unit.hp : 0;
  const bob = Math.sin(state.tick * 0.08) * 2.5;

  // --- 상단 좌측: 플레이어 장군 초상 + 체력 + 마나 + 아티팩트 + BBS ---
  roundRect(55, 16, 158, 96, 8, '#0b1224', pf.color, 2);
  drawSprite24(pf.sprite, 102, 62, 66, false, 0);
  ctx.textAlign = 'center';
  ctx.font = '900 12px "Noto Sans KR"';
  ctx.fillStyle = pf.color;
  ctx.fillText(pf.name.split(' ')[0], 102, 104);
  // 체력 구슬
  ctx.fillStyle = '#be123c';
  ctx.beginPath(); ctx.arc(176, 48, 22, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = '#fda4af'; ctx.lineWidth = 2; ctx.stroke();
  ctx.font = '900 16px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText(pHp, 176, 54);
  // 장군 공격력 배지
  roundRect(156, 78, 40, 22, 4, '#ca8a04', '#fef08a', 1.5);
  ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText(`⚔️${pg ? pg.unit.atk : 0}`, 176, 94);

  // BBS 스킬 원형 슬롯 (장군 바로 옆)
  const bbsReady = state.pBbsCd === 0 && state.pMana >= pf.bbsCost;
  ctx.fillStyle = bbsReady ? '#172554' : '#0f172a';
  ctx.beginPath(); ctx.arc(261, 60, 34, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = state.targetMode ? '#fbbf24' : (bbsReady ? '#38bdf8' : '#334155');
  ctx.lineWidth = 3; ctx.stroke();
  ctx.font = '900 11px "Noto Sans KR"';
  ctx.fillStyle = bbsReady ? '#38bdf8' : '#64748b';
  ctx.fillText('BBS 스킬', 261, 56);
  ctx.fillText(state.pBbsCd === 0 ? `${pf.bbsCost}마나` : `${state.pBbsCd}턴대기`, 261, 73);

  // 마나 크리스탈 9칸 & 장착 아티팩트 표시
  for (let m = 0; m < 9; m++) {
    ctx.fillStyle = m < state.pMana ? '#38bdf8' : (m < state.pMaxMana ? '#1e3a5f' : '#0f172a');
    ctx.beginPath();
    ctx.moveTo(318 + m * 22, 26); ctx.lineTo(326 + m * 22, 36);
    ctx.lineTo(318 + m * 22, 46); ctx.lineTo(310 + m * 22, 36);
    ctx.closePath(); ctx.fill();
  }
  ctx.textAlign = 'left';
  ctx.font = 'bold 13px "Noto Sans KR"'; ctx.fillStyle = '#93c5fd';
  ctx.fillText(`MANA ${state.pMana}/${state.pMaxMana}`, 516, 41);

  // 장착된 아티팩트 표시
  state.pArtifacts.forEach((a, idx) => {
    roundRect(310 + idx * 118, 56, 112, 38, 5, '#451a03', '#f59e0b', 1.5);
    ctx.font = 'bold 10.5px "Noto Sans KR"'; ctx.fillStyle = '#fef08a';
    ctx.fillText(a.name.slice(0, 7), 316 + idx * 118, 72);
    ctx.fillStyle = '#fbbf24';
    ctx.fillText(`내구도: ${'◆'.repeat(a.dur)}`, 316 + idx * 118, 87);
  });

  // --- 상단 중앙: 턴 & 상태 안내 ---
  ctx.textAlign = 'center';
  ctx.font = '900 16px "Cinzel", serif';
  ctx.fillStyle = '#f8fafc';
  ctx.fillText(`TURN ${state.turn}`, W / 2 + 40, 42);
  ctx.font = '12px "Noto Sans KR"';
  ctx.fillStyle = state.aiBusy ? '#f43f5e' : '#38bdf8';
  ctx.fillText(state.aiBusy ? '적 AI 작전 수행 중...' : '카드 클릭 또는 유닛 선택', W / 2 + 40, 64);

  // --- 상단 우측: 적 장군 HUD ---
  roundRect(1067, 16, 158, 96, 8, '#0b1224', ef.color, 2);
  drawSprite24(ef.sprite, 1178, 62, 66, true, 0);
  ctx.textAlign = 'center';
  ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = ef.color;
  ctx.fillText(ef.name.split(' ')[0], 1178, 104);
  ctx.fillStyle = '#be123c';
  ctx.beginPath(); ctx.arc(1104, 48, 22, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = '#fda4af'; ctx.lineWidth = 2; ctx.stroke();
  ctx.font = '900 16px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText(eHp, 1104, 54);
  roundRect(1084, 78, 40, 22, 4, '#ca8a04', '#fef08a', 1.5);
  ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText(`⚔️${eg ? eg.unit.atk : 0}`, 1104, 94);

  ctx.textAlign = 'right';
  ctx.font = '12px "Noto Sans KR"'; ctx.fillStyle = '#94a3b8';
  ctx.fillText(`적 마나 ${state.eMana}/${state.eMaxMana} | 덱 ${state.eDeck.length}장`, 1052, 42);
  state.eArtifacts.forEach((a, idx) => {
    ctx.fillStyle = '#fbbf24';
    ctx.fillText(`🛡️ ${a.name} (${a.dur})`, 1052, 64 + idx * 16);
  });

  // --- 중앙 5x9 전술 입체 보드 렌더링 ---
  let moves = [], attacks = [], summons = [], spells = [];
  if (state.selectedPos) {
    moves = getValidMoves(state.selectedPos.r, state.selectedPos.c);
    attacks = getValidAttacks(state.selectedPos.r, state.selectedPos.c);
  }
  if (state.selectedCardIdx !== null) {
    const c = state.pHand[state.selectedCardIdx];
    if (c.type === 'minion') summons = getValidSummonTiles('player');
    else if (c.type === 'spell') spells = getValidSpellTargets(c, 'player');
  }

  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const tx = BOARD_X + c * (TILE_W + GAP);
      const ty = BOARD_Y + r * (TILE_H + GAP);
      const isMove = moves.some(m => m.r === r && m.c === c);
      const isAtk = attacks.some(a => a.r === r && a.c === c);
      const isSum = summons.some(s => s.r === r && s.c === c);
      const isSpl = spells.some(s => s.r === r && s.c === c);
      const isSel = state.selectedPos && state.selectedPos.r === r && state.selectedPos.c === c;
      const isHov = state.hoverTile && state.hoverTile.r === r && state.hoverTile.c === c;

      // 3D 석조 타일 두께(그림자)
      ctx.fillStyle = '#040711';
      ctx.fillRect(tx, ty + 4, TILE_W, TILE_H);

      let fill = (r + c) % 2 === 0 ? 'rgba(15, 23, 42, 0.88)' : 'rgba(20, 30, 54, 0.88)';
      let stroke = '#1e293b';
      let lw = 1.5;

      if (isMove) { fill = 'rgba(14, 116, 144, 0.55)'; stroke = '#38bdf8'; lw = 2.5; }
      if (isSum) { fill = 'rgba(6, 95, 70, 0.6)'; stroke = '#10b981'; lw = 2.5; }
      if (isAtk || isSpl) { fill = 'rgba(159, 18, 57, 0.65)'; stroke = '#f43f5e'; lw = 2.5; }
      if (isSel) { fill = 'rgba(30, 58, 138, 0.75)'; stroke = '#fbbf24'; lw = 3; }
      if (isHov) { stroke = '#f8fafc'; lw = 2.5; }

      roundRect(tx, ty, TILE_W, TILE_H, 5, fill, stroke, lw);

      // 타일 내부 은은한 룬 문양
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.08)';
      ctx.strokeRect(tx + 8, ty + 8, TILE_W - 16, TILE_H - 16);

      // 마나 샘(Mana Spring)
      if (state.manaOrbs.some(o => o.r === r && o.c === c)) {
        const pulse = Math.sin(state.tick * 0.1) * 3;
        const mg = ctx.createRadialGradient(tx + TILE_W / 2, ty + TILE_H / 2, 2, tx + TILE_W / 2, ty + TILE_H / 2, 22 + pulse);
        mg.addColorStop(0, '#ffffff');
        mg.addColorStop(0.4, '#38bdf8');
        mg.addColorStop(1, 'rgba(56,189,248,0)');
        ctx.fillStyle = mg;
        ctx.beginPath();
        ctx.arc(tx + TILE_W / 2, ty + TILE_H / 2, 22 + pulse, 0, Math.PI * 2);
        ctx.fill();
      }

      // 유닛 렌더링
      const u = state.board[r][c];
      if (u) {
        const cx = tx + TILE_W / 2;
        const cy = ty + TILE_H / 2 - 8;

        // 발밑 그림자 & 진영 오라
        ctx.fillStyle = 'rgba(0,0,0,0.55)';
        ctx.beginPath(); ctx.ellipse(cx, ty + TILE_H - 14, 24, 7, 0, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = u.owner === 'player' ? '#38bdf8' : '#f43f5e';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.ellipse(cx, ty + TILE_H - 14, 24, 7, 0, 0, Math.PI * 2); ctx.stroke();

        // 키워드 / 기절 표기
        ctx.textAlign = 'center';
        ctx.font = 'bold 10px "Noto Sans KR"';
        if (u.stunned) { ctx.fillStyle = '#38bdf8'; ctx.fillText('❄️기절', cx, ty + 13); }
        else if (u.keywords.includes('provoke')) { ctx.fillStyle = '#fbbf24'; ctx.fillText('🛡️도발', cx, ty + 13); }
        else if (u.keywords.includes('ranged')) { ctx.fillStyle = '#38bdf8'; ctx.fillText('🏹원거리', cx, ty + 13); }
        else if (u.keywords.includes('frenzy')) { ctx.fillStyle = '#10b981'; ctx.fillText('💥광란', cx, ty + 13); }

        drawSprite24(u.sprite, cx, cy, u.isGeneral ? 62 : 52, u.owner === 'enemy', bob);

        // 공격력(노랑) & 체력(빨강) 배지
        roundRect(tx + 6, ty + TILE_H - 22, 25, 18, 4, '#ca8a04', '#fef08a', 1);
        ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
        ctx.fillText(u.atk, tx + 18, ty + TILE_H - 9);

        roundRect(tx + TILE_W - 31, ty + TILE_H - 22, 25, 18, 4, '#be123c', '#fda4af', 1);
        ctx.fillText(u.hp, tx + TILE_W - 18, ty + TILE_H - 9);
      }
    }
  }

  // --- 우측 전술 기록 & 호버 유닛 상세 정보창 ---
  roundRect(940, 128, 285, 396, 8, 'rgba(9, 14, 28, 0.9)', '#1e293b', 2);
  ctx.textAlign = 'left';
  ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = '#38bdf8';
  ctx.fillText(`📜 전투 로그 (남은 덱: ${state.pDeck.length}장)`, 954, 152);
  ctx.font = '11.5px "Noto Sans KR"';
  state.logs.slice(0, 10).forEach((l, i) => {
    ctx.fillStyle = i === 0 ? '#f8fafc' : '#94a3b8';
    ctx.fillText(l.slice(0, 26), 954, 174 + i * 19);
  });

  // 호버된 타일 유닛 정보
  if (state.hoverTile) {
    const hu = state.board[state.hoverTile.r][state.hoverTile.c];
    if (hu) {
      roundRect(952, 376, 261, 134, 6, '#050811', hu.owner === 'player' ? '#38bdf8' : '#f43f5e', 1.5);
      drawSprite24(hu.sprite, 992, 430, 56, hu.owner === 'enemy', 0);
      ctx.font = '900 14px "Noto Sans KR"'; ctx.fillStyle = '#f8fafc';
      ctx.fillText(hu.name, 1030, 404);
      ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = '#fbbf24';
      ctx.fillText(`공격력 ${hu.atk}  |  체력 ${hu.hp}/${hu.maxHp}`, 1030, 426);
      ctx.font = '11px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
      ctx.fillText(`특성: ${hu.keywords.length ? hu.keywords.join(', ').toUpperCase() : '기본'}`, 1030, 448);
      ctx.fillStyle = '#38bdf8';
      ctx.fillText(hu.stunned ? '상태: 기절 (이번 턴 행동 불가)' : (hu.canAttack ? '상태: 행동 가능' : '상태: 행동 완료'), 1030, 468);
    }
  }

  // --- 하단 액션 바 (Replace 슬롯 + 손패 6장 + End Turn) ---
  // 1. 좌측 Replace 오브
  const canRep = !state.replacedThisTurn && state.pDeck.length > 0;
  roundRect(55, 575, 118, 175, 10, state.replaceMode ? '#78350f' : '#0b1224', state.replaceMode ? '#fbbf24' : (canRep ? '#38bdf8' : '#1e293b'), 2);
  ctx.textAlign = 'center';
  ctx.font = '900 13px "Noto Sans KR"';
  ctx.fillStyle = canRep ? '#38bdf8' : '#475569';
  ctx.fillText('REPLACE', 114, 645);
  ctx.font = '11px "Noto Sans KR"';
  ctx.fillStyle = '#cbd5e1';
  ctx.fillText(state.replaceMode ? '교체할 카드 클릭' : (canRep ? '카드 교체 (1회)' : '교체 완료'), 114, 670);

  // 2. 손패 카드 6장
  for (let i = 0; i < state.pHand.length; i++) {
    const c = state.pHand[i];
    const isSel = state.selectedCardIdx === i;
    const isHov = state.hoverCardIdx === i;
    const cx = 195 + i * 155;
    const cy = 550 - (isSel || isHov ? 22 : 0);
    const ok = c.cost <= state.pMana;
    const borderCol = isSel ? '#fbbf24' : (ok ? (c.type === 'spell' ? '#c084fc' : (c.type === 'artifact' ? '#f59e0b' : '#38bdf8')) : '#334155');

    roundRect(cx, cy, 146, 225, 8, isSel ? '#172554' : '#0b1224', borderCol, isSel ? 3 : 2);
    drawCardArt(c, cx + 8, cy + 32, 130, 82, isHov ? bob : 0);

    // 코스트 보석
    ctx.fillStyle = '#0284c7';
    ctx.beginPath(); ctx.arc(cx + 18, cy + 16, 11, 0, Math.PI * 2); ctx.fill();
    ctx.textAlign = 'center';
    ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
    ctx.fillText(c.cost, cx + 18, cy + 21);

    ctx.font = 'bold 10px "Noto Sans KR"';
    ctx.fillStyle = c.type === 'spell' ? '#e879f9' : (c.type === 'artifact' ? '#fbbf24' : '#38bdf8');
    ctx.fillText(c.type.toUpperCase(), cx + 84, cy + 20);

    ctx.font = '900 12.5px "Noto Sans KR"'; ctx.fillStyle = '#f8fafc';
    ctx.fillText(c.name, cx + 73, cy + 130);

    if (c.type === 'minion') {
      ctx.font = 'bold 11.5px "Noto Sans KR"'; ctx.fillStyle = '#fbbf24';
      ctx.fillText(`⚔️ ${c.atk}   ❤️ ${c.hp}`, cx + 73, cy + 148);
    } else if (c.type === 'artifact') {
      ctx.font = 'bold 11px "Noto Sans KR"'; ctx.fillStyle = '#fbbf24';
      ctx.fillText(`장군 +${c.atkBonus} ATK`, cx + 73, cy + 148);
    } else {
      ctx.font = 'bold 11px "Noto Sans KR"'; ctx.fillStyle = '#e879f9';
      ctx.fillText('주문 카드', cx + 73, cy + 148);
    }

    ctx.font = '10.5px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
    for (let line = 0; line < 3; line++) {
      ctx.fillText(c.desc.slice(line * 13, (line + 1) * 13), cx + 73, cy + 168 + line * 16);
    }
  }

  // 3. 우측 END TURN & 진영 변경 버튼
  roundRect(1135, 575, 115, 110, 10, state.aiBusy ? '#1e293b' : '#0284c7', '#38bdf8', 2.5);
  ctx.textAlign = 'center';
  ctx.font = '900 16px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText('END', 1192, 624);
  ctx.fillText('TURN', 1192, 646);

  roundRect(1135, 695, 115, 55, 8, '#0f172a', '#475569', 1.5);
  ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
  ctx.fillText('🔙 진영 변경', 1192, 727);

  // --- 이펙트 레이어 ---
  for (let i = state.effects.length - 1; i >= 0; i--) {
    const efObj = state.effects[i];
    efObj.t++;
    if (efObj.t >= efObj.maxT) { state.effects.splice(i, 1); continue; }
    const alpha = 1 - efObj.t / efObj.maxT;
    ctx.save();
    ctx.globalAlpha = alpha;
    if (efObj.type === 'text') {
      efObj.y -= 0.7;
      ctx.textAlign = 'center';
      ctx.font = '900 18px "Noto Sans KR"';
      ctx.fillStyle = efObj.color;
      ctx.fillText(efObj.text, efObj.x, efObj.y);
    } else if (efObj.type === 'beam') {
      ctx.strokeStyle = efObj.color;
      ctx.lineWidth = 5 * alpha;
      ctx.beginPath(); ctx.moveTo(efObj.x, efObj.y); ctx.lineTo(efObj.x2, efObj.y2); ctx.stroke();
    } else if (efObj.type === 'ring') {
      ctx.strokeStyle = efObj.color;
      ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(efObj.x, efObj.y, 12 + efObj.t * 1.4, 0, Math.PI * 2); ctx.stroke();
    } else if (efObj.type === 'particle') {
      efObj.x += efObj.vx; efObj.y += efObj.vy;
      ctx.fillStyle = efObj.color;
      ctx.fillRect(efObj.x - 2, efObj.y - 2, 4, 4);
    }
    ctx.restore();
  }

  // --- 승패 오버레이 ---
  if (state.winner) {
    ctx.fillStyle = 'rgba(4, 6, 12, 0.85)';
    ctx.fillRect(0, 0, W, H);
    ctx.textAlign = 'center';
    ctx.font = '900 44px "Cinzel", serif';
    ctx.fillStyle = state.winner === 'PLAYER' ? '#38bdf8' : '#f43f5e';
    ctx.fillText(state.winner === 'PLAYER' ? 'VICTORY' : 'DEFEAT', W / 2, H / 2 - 20);

    roundRect(W / 2 - 150, H / 2 + 40, 300, 58, 8, '#0284c7', '#38bdf8', 2);
    ctx.font = '900 18px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
    ctx.fillText('🔄 진영 선택으로 돌아가기', W / 2, H / 2 + 75);
  }
}

function loop() {
  state.tick++;
  if (state.screen === 'title') drawTitleScreen();
  else if (state.screen === 'select') drawSelectScreen();
  else drawBattleScreen();
  requestAnimationFrame(loop);
}
loop();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=810, scrolling=False)
