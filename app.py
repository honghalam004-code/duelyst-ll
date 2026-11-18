import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DUELYST II // CHRONICLES OF MYTHRON",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {
        padding: 0.2rem 0.4rem 0rem 0.4rem !important;
        max-width: 100% !important;
    }
    .stApp { background-color: #03050a; }
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
    background: #03050a;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Noto Sans KR', sans-serif;
    overflow: hidden;
  }
  canvas {
    background: #050812;
    border: 2px solid #1e293b;
    border-radius: 6px;
    box-shadow: 0 0 50px rgba(0, 0, 0, 0.95);
    max-width: 100vw;
    max-height: 99vh;
  }
</style>
</head>
<body>
<canvas id="game" width="1280" height="820"></canvas>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const W = canvas.width;
const H = canvas.height;

// =========================================================================
// 1. 32x32 고해상도 다층 픽셀 스프라이트 빌더 (외곽선 + 4단계 명암 + 하이라이트)
// =========================================================================
function buildSprite32(palette, rows) {
  const off = document.createElement('canvas');
  off.width = 32;
  off.height = 32;
  const octx = off.getContext('2d');
  for (let y = 0; y < 32; y++) {
    const row = (rows[y] || '').padEnd(32, '.').slice(0, 32);
    for (let x = 0; x < 32; x++) {
      const ch = row[x];
      if (ch !== '.' && palette[ch]) {
        octx.fillStyle = palette[ch];
        octx.fillRect(x, y, 1, 1);
      }
    }
  }
  return off;
}

const PAL = {
  O: '#07090f', // 진한 외곽선
  W: '#ffffff', S: '#e2e8f0', M: '#94a3b8', D: '#475569', K: '#1e293b',
  // 금빛/태양 (라이오나르)
  Y: '#fef08a', G: '#f59e0b', B: '#b45309', U: '#1d4ed8', C: '#38bdf8',
  // 진홍/그림자 (송하이)
  R: '#fda4af', E: '#e11d48', N: '#881337',
  // 청록/사막 (베트루비안)
  T: '#5eead4', V: '#0d9488', A: '#d97706',
  // 자수정/심연 (어비시안)
  P: '#f0abfc', X: '#9333ea', Z: '#4c1d95',
  // 에메랄드/용족 (마그마르)
  L: '#6ee7b7', Q: '#059669', J: '#064e3b', H: '#f97316',
  // 빙하/서리 (바나르)
  I: '#bae6fd', F: '#0284c7', F2: '#1e3a8a'
};

const SPRITES = {
  // 1) 아르게온 하이메이 (라이오나르 황금 성기사)
  argeon: buildSprite32(PAL, [
    '..........OO........OO..........',
    '.........OYYO......OYYO.........',
    '........OYGGYO....OYGGYO........',
    '.......OYGGGGYYYYYYGGGGYO.......',
    '.......OGGGGGGGGGGGGGGGGO.......',
    '......OOGWWWWWWWWWWWWWWGOO......',
    '......OGWCCCCCCCCCCCCCCWGO......',
    '......OGWCCCCCCCCCCCCCCWGO......',
    '......OGGGGGGGGGGGGGGGGGGO......',
    '.......OOBBBBBBBBBBBBBBOO.......',
    '....OOOBBGGGGGGGGGGGGGBBOOO.....',
    '...OYYYBGGGGGGYYYYGGGGGGBYYYO...',
    '..OYYYBGGGGGGYYYYYYGGGGGGBYYYO..',
    '..OOBBGGGGGGGYYYYYYGGGGGGGBBOO..',
    '...OUBGGGGGGGGYYYYGGGGGGGGBUO...',
    '...OUBBGGGGGGGGGGGGGGGGGGGBBUO..',
    '....OUUOBBBBBBBBBBBBBBBBOUUO....',
    '.....OO.OOGGGGGGGGGGGGOO.OO.....',
    '........OGGGGGOOOOGGGGGO........',
    '........OGGGGGO..OGGGGGO........',
    '.......OBBBBBBO..OBBBBBBO.......',
    '.......OOOOOOO....OOOOOOO.......'
  ]),
  // 2) 칼레오스 잔 (송하이 붉은 암살 군주)
  kaleos: buildSprite32(PAL, [
    '.........OOOO......OOOO.........',
    '........OEEEEO....OEEEEO........',
    '.........OEEEEEEEEEEEEO.........',
    '........OEEEEEEEEEEEEEEO........',
    '.......OOEKKKKKKKKKKKKEOO.......',
    '.......OEKRRRRRRRRRRRRKEO.......',
    '.......OEKKKKKKKKKKKKKKEO.......',
    '........OEEEEEEEEEEEEEEO........',
    '.........OONNNNNNNNNNOO.........',
    '....OOOONNNKKKKKKKKKKNNNOOOO....',
    '...OEEEENNKKKKKKKKKKKKNNEEEEO...',
    '..OEEEENNKKKKKEEEEKKKKKNNEEEEO..',
    '...OOONNKKKKKEEEEEEKKKKKNNOOO...',
    '...OWWOKKKKKKEEEEEEKKKKKKOWWO...',
    '..OWWWOKKKKKKNNNNNNKKKKKKOWWWO..',
    '..OWWO.OONNNNNNNNNNNNNNOO.OWWO..',
    '...OO...ONNNNNNOONNNNNNO...OO...',
    '........OKKKKKKOOKKKKKKO........',
    '.......ONNNNNNNOONNNNNNNO.......',
    '.......OOOOOOOO..OOOOOOOO.......'
  ]),
  // 3) 지릭스 스타스트라이더 (베트루비안 사이버 파라오)
  zirix: buildSprite32(PAL, [
    '.......OOO............OOO.......',
    '......OGGGO..........OGGGO......',
    '......OGGGO..........OGGGO......',
    '......OGGGGGGGGGGGGGGGGGGO......',
    '......OGGGTTTTTTTTTTTTGGGO......',
    '......OGGGTVVVVVVVVVVTGGGO......',
    '.......OGGGGGGGGGGGGGGGGO.......',
    '........OOAAAAAAAAAAAAOO........',
    '....OOOOAAGGGGGGGGGGGGAAOOOO....',
    '...OTTTTAAGGGGTTTTGGGGAAAATTTO..',
    '..OTTTTAAGGGGTTTTTTGGGGAAAATTTO.',
    '...OOOAAAGGGGGTTTTGGGGGAAAOOO...',
    '....OOGGGGGGGGGGGGGGGGGGGGOO....',
    '.....OOTTTTTTTTTTTTTTTTTTOO.....',
    '......OOAAAAAAAAAAAAAAAOO.......',
    '.......OOGGGGGOOOOGGGGGO........',
    '.......OAAAAAO....OAAAAAO.......',
    '......OGGGGGGO....OGGGGGGO......',
    '......OOOOOOO......OOOOOOO......'
  ]),
  // 4) 리리스 블라이트체이서 (어비시안 심연 여왕)
  lilithe: buildSprite32(PAL, [
    '.....OOO................OOO.....',
    '....OPPPO..............OPPPO....',
    '...OPPXXPO............OPXXPPO...',
    '....OPPXXPPPPPPPPPPPPPPXXPPO....',
    '.....OPXXXXXXXXXXXXXXXXXXPO.....',
    '.....OPXWWWWWWWWWWWWWWWWXPO.....',
    '.....OPXWPPWWWWWWWWWWPPWXPO.....',
    '......OPXXXXXXXXXXXXXXXXPO......',
    '..OOOOOZZXXXXXXXXXXXXXXZZOOOOO..',
    '.OZZZZZZZXXXXXXXXXXXXXXZZZZZZZO.',
    'OZZZPPZZZZXXXXPPPPXXXXZZZZPPZZZO',
    '.OOOZZOZZZXXXXXXXXXXXXZZZOZZOOO.',
    '.....OOZZZXXXXXXXXXXXXZZZOO.....',
    '......OZZZXXXXXXXXXXXXZZZO......',
    '......OZZZZZXXXXXXXXZZZZZO......',
    '.....OZZZZZZZOOOOOOZZZZZZZO.....',
    '.....OZZZZZZO......OZZZZZZO.....',
    '....OZZZZZZO........OZZZZZZO....',
    '....OOOOOOO..........OOOOOOO....'
  ]),
  // 5) 바스 디 이모탈 (마그마르 용족 군주)
  vaath: buildSprite32(PAL, [
    '...OOO....................OOO...',
    '..OHHHO..................OHHHO..',
    '..OHLLHO................OHLLHO..',
    '...OHLLLLLLLLLLLLLLLLLLLLLLHO...',
    '...OLLLLLLLLLLLLLLLLLLLLLLLLO...',
    '...OLLHHHHHHHHHHHHHHHHHHHHLLO...',
    '...OLLHRRRRRRRRRRRRRRRRRRHLLO...',
    '....OLLLLLLLLLLLLLLLLLLLLLLO....',
    '..OOJJLLLLLLLLLLLLLLLLLLLLJJOO..',
    '.OJJJJLLLLLLHHHHHHHHLLLLLLJJJJO.',
    'OJJJJJLLLLLHHHHHHHHHHLLLLLJJJJJO',
    'OJJJJJLLLLLLHHHHHHHHLLLLLLJJJJJO',
    '.OOJJJLLLLLLLLLLLLLLLLLLLLJJJOO.',
    '..OJJJJJLLLLLLLLLLLLLLLLJJJJJO..',
    '...OJJJJJJOOOOOOOOOOOOJJJJJJO...',
    '.....OLLLLLLOO....OOLLLLLLO.....',
    '....OJJJJJJJO......OJJJJJJJO....',
    '....OOOOOOOO........OOOOOOOO....'
  ]),
  // 6) 페이 블러드윙 (바나르 서리 발키리)
  faie: buildSprite32(PAL, [
    '.....OOO................OOO.....',
    '....OIIIO..............OIIIO....',
    '...OIFFIO..............OIFFIO...',
    '....OIFIIIIIIIIIIIIIIIIIIFIO....',
    '.....OIIIIIIIIIIIIIIIIIIIIO.....',
    '.....OIIWWWWWWWWWWWWWWWWIIO.....',
    '.....OIIWCCWWWWWWWWWWCCWIIO.....',
    '......OIIIIIIIIIIIIIIIIIIO......',
    '...OOOOFF2FFFFFFFFFFFFFF2FFOOOO.',
    '..OSSSSFF2IIIIIIIIIIIIII2FFSSSSO',
    '.OSSSSSFF2IIIIIWWWWIIIII2FFSSSSS',
    '..OOO.OFF2IIIIIIIIIIIIII2FFO.OOO',
    '......OFF2FFFFFFFFFFFFFF2FFO....',
    '.......OIIIIIIIIIIIIIIIIIIO.....',
    '.......OFF2FF2OOOOOOFF2FF2O.....',
    '......OIIIIIIO......OIIIIIIO....',
    '......OFFFFFFO......OFFFFFFO....',
    '.....OOOOOOOO........OOOOOOOO...'
  ]),

  // 다양한 하수인 스프라이트 (32x32)
  paladin: buildSprite32(PAL, [
    '.........OOOOOOOOOOOO...........',
    '........OYYYYYYYYYYYYO..........',
    '........OGGGGGGGGGGGGO..........',
    '........OGCCCCCCCCCCGO..........',
    '.........OGGGGGGGGGGO...........',
    '.....OOOBBGGGGGGGGGGGBOOO.......',
    '....OYYYBGGGGGGGGGGGGGBWWWO.....',
    '...OYYYGBGGGGGGGGGGGGGBWWWO.....',
    '...OYYYGBGGGGGGGGGGGGGBWWWO.....',
    '....OOOBBBBBBBBBBBBBBBOWWWO.....',
    '.......OOGGGGGGGGGGGGOOWWO......',
    '.......OGGGGGOOOOGGGGGO.........',
    '.......OBBBBBO..OBBBBBO.........',
    '......OOOOOOO....OOOOOOO........'
  ]),
  assassin: buildSprite32(PAL, [
    '.........OOOOOOOOOOOO...........',
    '........OEEEEEEEEEEEEO..........',
    '........OKKKKKKKKKKKKO..........',
    '........OKRRRRRRRRRRKO..........',
    '.........OKKKKKKKKKKO...........',
    '....OOOONNKKKKKKKKKKNNOOOO......',
    '...OEEEENKKKKKKKKKKKKNEEEEO.....',
    '...OOONNKKKKKKKKKKKKKKNNOOO.....',
    '.....OOKKKKKKKKKKKKKKKKOO.......',
    '....OWWOKKKKKKNNNNKKKKKOWWO.....',
    '...OWWWW.ONNNNOOOONNNNO.WWWWO...',
    '........OKKKKO....OKKKKO........',
    '.......ONNNNNO....ONNNNNO.......',
    '.......OOOOOO......OOOOOO.......'
  ]),
  fox: buildSprite32(PAL, [
    '......OOO............OOO........',
    '.....OEEEO..........OEEEO.......',
    '.....OEEEEEEEEEEEEEEEEEEO.......',
    '....OEEHHHHHHHHHHHHHHHHEEO......',
    '....OEHWWWWWWWWWWWWWWWWHEO......',
    '...OEEEEEEEEEEEEEEEEEEEEEEO.....',
    '..OWWWEEEEEEEEEEEEEEEEEEWWWO....',
    '...OOOWWWEEEEEEEEEEEEWWWOOO.....',
    '.....OEEEEEOO......OOEEEEEO.....',
    '.....OHHHHHO........OHHHHHO.....',
    '....OEEEEEEO........OEEEEEEO....',
    '....OOOOOOO..........OOOOOOO....'
  ]),
  dervish: buildSprite32(PAL, [
    '.........OOOOOOOOOOOO...........',
    '........OTTTTTTTTTTTTO..........',
    '........OTYYYYYYYYYYTO..........',
    '........OTVVVVVVVVVVTO..........',
    '.........OTTTTTTTTTTO...........',
    '.....OOOAAATTTTTTTTAAAOOO.......',
    '....OGGGATTTTTTTTTTTTAGGGO......',
    '.....OOOAAATTTTTTTTAAAOOO.......',
    '.......OOTTTTTTTTTTTTOO.........',
    '........OTTTTTTTTTTTTO..........',
    '.........OTTTTTTTTTTO...........',
    '..........OTTTTTTTTO............',
    '...........OTTTTTTO.............',
    '............OOOOOO..............'
  ]),
  wraith: buildSprite32(PAL, [
    '.........OOOOOOOOOOOO...........',
    '........OPPPPPPPPPPPPO..........',
    '........OPXXXXXXXXXXPO..........',
    '........OPWWXXXXXXWWPO..........',
    '.........OPXXXXXXXXPO...........',
    '....OOOOZZXXXXXXXXXXZZOOOO......',
    '...OXXXZZZXXXXXXXXXXZZZXXXO.....',
    '...OOZZZZZXXXXXXXXXXZZZZZOO.....',
    '.....OZZZZXXXXXXXXXXZZZZO.......',
    '......OZZZXXXXXXXXXXZZZO........',
    '.......OZZOOXXXXXXOOZZO.........',
    '........OO..OOOOOO..OO..........'
  ]),
  revenant: buildSprite32(PAL, [
    '....OOO................OOO......',
    '...OPPPO..............OPPPO.....',
    '....OPXXXXXXXXXXXXXXXXXXPO......',
    '...OPXWWWWWWWWWWWWWWWWWWXPO.....',
    '...OPXWPPWWWWWWWWWWWWPPWXPO.....',
    '..OOZZXXXXXXXXXXXXXXXXXXZZOO....',
    '.OZZZZXXXXXXXXXXXXXXXXXXZZZZO...',
    'OZZZZZXXXXPPPPPPPPPPXXXXZZZZZO..',
    '.OOZZZXXXXXXXXXXXXXXXXXXZZZOO...',
    '...OZZZZXXXXXXXXXXXXXXXXZZZZO...',
    '....OZZZZZOO........OOZZZZZO....',
    '.....OOOOOO..........OOOOOO.....'
  ]),
  beast: buildSprite32(PAL, [
    '....OOO................OOO......',
    '...OHHHO..............OHHHO.....',
    '....OHLLLLLLLLLLLLLLLLLLHO......',
    '...OLLLLLLLLLLLLLLLLLLLLLLO.....',
    '...OLLRRRRRRRRRRRRRRRRRRLLO.....',
    '..OLLLLLLLLLLLLLLLLLLLLLLLLO....',
    '.OJJLLLLLLLHHHHHHHHLLLLLLLJJOO..',
    'OJJJLLLLLLLHHHHHHHHLLLLLLLJJJJO.',
    '.OOJJLLLLLLLLLLLLLLLLLLLLJJJOO..',
    '...OJJJJLLLLLLLLLLLLLLJJJJJO....',
    '...OJJJJOO..........OOJJJJJO....',
    '..OLLLLLO............OLLLLLO....',
    '..OOOOOO..............OOOOOO....'
  ]),
  wolf: buildSprite32(PAL, [
    '.....OO................OO.......',
    '....OIIO..............OIIO......',
    '....OIIIIIIIIIIIIIIIIIIIIO......',
    '...OIIFFFFFFFFFFFFFFFFFFIIO.....',
    '...OIFCCCCCCCCCCCCCCCCCCFIO.....',
    '..OIIIIIIIIIIIIIIIIIIIIIIIIO....',
    '.OSSSSIIIIIIIIIIIIIIIIIISSSSO...',
    '..OOSSIIIIIIIIIIIIIIIIIISSOO....',
    '...OIIIIIIOO........OOIIIIIIO...',
    '...OFFFFFFO..........OFFFFFFO...',
    '..OIIIIIIO............OIIIIIIO..',
    '..OOOOOOO..............OOOOOOO..'
  ]),
  archer: buildSprite32(PAL, [
    '.........OOOOOOOOOOOO...........',
    '........OLLLLLLLLLLLLO..........',
    '........OLYYYYYYYYYYLO..........',
    '.........OLLLLLLLLLLO...........',
    '.....OOOQQLLLLLLLLLLQQOOO.......',
    '....OQQQLLLLLLLLLLLLLLQQQOAA....',
    '.....OOOQQLLLLLLLLLLQQOOO.AWA...',
    '.......OOLLLLLLLLLLLLOO...AWA...',
    '.......OQQQQOOOOOOQQQQO...AWA...',
    '.......OQQQQO....OQQQQO..AA.....',
    '......OLLLLLO....OLLLLLO........',
    '......OOOOOO......OOOOOO........'
  ]),
  golem: buildSprite32(PAL, [
    '......OOOOOOOOOOOOOOOOOO........',
    '.....ODDDDDDDDDDDDDDDDDDO.......',
    '....ODSSSSSSSSSSSSSSSSSSDO......',
    '....ODSSCCCCCCCCCCCCCCSSDO......',
    '....ODSSSSSSSSSSSSSSSSSSDO......',
    '...OODDDDDDDDDDDDDDDDDDDDOO.....',
    '..ODDDDDDDDDDDDDDDDDDDDDDDDO....',
    '..ODDDDDCCCCCCCCCCCCCCDDDDDO....',
    '..ODDDDDDDDDDDDDDDDDDDDDDDDO....',
    '...OODDDDDDDDDDDDDDDDDDDDOO.....',
    '....ODDDDDDOOOOOOOODDDDDDO......',
    '....ODDDDDDO......ODDDDDDO......',
    '...OSSSSSSSO......OSSSSSSSO.....',
    '...OOOOOOOO........OOOOOOOO.....'
  ])
};

// =========================================================================
// 2. 난이도 설정 & 듀얼리스트 6대 진영 + 64종 확장 카드 풀
// =========================================================================
const DIFFICULTIES = [
  { id: 'easy', name: '입문 (EASY)', color: '#34d399', eHp: 20, bonusCard: 0, desc: 'AI가 느슨하게 플레이하며 마나 샘을 크게 의식하지 않습니다.' },
  { id: 'normal', name: '보통 (NORMAL)', color: '#38bdf8', eHp: 25, bonusCard: 0, desc: '표준 전술 AI. 체력이 낮은 적을 노리고 하수인을 전개합니다.' },
  { id: 'hard', name: '숙련 (HARD)', color: '#fbbf24', eHp: 25, bonusCard: 1, desc: '킬각(Lethal)을 계산하고 마나 샘과 원거리 견제를 적극 활용합니다.' },
  { id: 'master', name: '마스터 (MASTER)', color: '#f43f5e', eHp: 30, bonusCard: 1, desc: '최상위 전술 AI. 광역 스펠, 기습, 아티팩트 콤보를 치밀하게 구사합니다.' }
];

const FACTIONS = {
  argeon: {
    id: 'argeon', name: '아르게온 하이메이', title: '라이오나르 왕국 (LYONAR)',
    color: '#fbbf24', sprite: 'argeon',
    bbsName: '왕의 포효 (Roar)', bbsCost: 1,
    bbsDesc: '아군 장군 주변 아군 1기에게 공격력 +2 영구 부여',
    cards: [
      { name: '칼날바람 기사', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'paladin', keywords: ['rush'], desc: '돌진: 소환 즉시 전선을 압박하는 기동 기사.' },
      { name: '은빛 방패기사', type: 'minion', cost: 3, atk: 1, hp: 5, sprite: 'golem', keywords: ['provoke'], desc: '도발: 높은 체력으로 인접 적을 완전히 봉쇄.' },
      { name: '태양의 성기사', type: 'minion', cost: 4, atk: 4, hp: 4, sprite: 'paladin', keywords: ['gambit_heal_all'], desc: '전투의 함성: 아군 장군의 체력을 4 회복합니다.' },
      { name: '신성한 결속', type: 'spell', cost: 2, spell: 'divine_bond', desc: '스펠: 아군 하수인 1기에게 현재 체력만큼 공격력 부여!' },
      { name: '성스러운 제물', type: 'spell', cost: 4, spell: 'holy_immolation', desc: '스펠: 아군 1기 체력 +4 & 주변 모든 적에게 4 광역 피해!' },
      { name: '순교 (Martyrdom)', type: 'spell', cost: 2, spell: 'martyrdom', desc: '스펠: 대상 하수인 즉시 처치 & 그 주인의 장군을 체력만큼 회복.' },
      { name: '폭풍의 심판', type: 'spell', cost: 2, spell: 'tempest', desc: '스펠: 전장의 모든 하수인과 장군에게 2 광역 피해!' },
      { name: '전쟁의 함성', type: 'spell', cost: 2, spell: 'war_surge', desc: '스펠: 모든 아군 하수인에게 +1/+1을 영구 부여합니다.' },
      { name: '아클라이트 성갑', type: 'artifact', cost: 3, atkBonus: 2, art: 'artifact_regalia', desc: '아티팩트 (내구도 3): 장군 공격력 +2 & 받는 첫 피해 2 경감!' }
    ]
  },
  kaleos: {
    id: 'kaleos', name: '칼레오스 잔', title: '송하이 제국 (SONGHAI)',
    color: '#f43f5e', sprite: 'kaleos',
    bbsName: '점멸 (Blink)', bbsCost: 1,
    bbsDesc: '아군 하수인 1기를 2칸 이내 빈 칸으로 순간이동',
    cards: [
      { name: '카이도 암살자', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'assassin', keywords: ['backstab'], desc: '기습(+2): 적 등 뒤(오른쪽) 공격 시 4 피해 & 반격 무시!' },
      { name: '카게 번개사수', type: 'minion', cost: 2, atk: 2, hp: 2, sprite: 'archer', keywords: ['ranged'], desc: '원거리: 보드 어디서든 반격 없이 적을 저격합니다.' },
      { name: '등불 여우', type: 'minion', cost: 3, atk: 2, hp: 4, sprite: 'fox', keywords: ['rush'], desc: '돌진: 기동력이 뛰어난 송하이의 영물입니다.' },
      { name: '고어 혼', type: 'minion', cost: 3, atk: 3, hp: 3, sprite: 'assassin', keywords: ['backstab'], desc: '기습(+2): 적의 배후를 찌르면 5 피해 & 반격 무시!' },
      { name: '불사조의 불꽃', type: 'spell', cost: 2, spell: 'phoenix_fire', desc: '스펠: 대상 적에게 3 피해를 입히고 카드 1장을 뽑습니다.' },
      { name: '내면의 집중', type: 'spell', cost: 1, spell: 'inner_focus', desc: '스펠: 공격력 3 이하 아군 하수인 1기를 즉시 재행동!' },
      { name: '안개 용의 인장', type: 'spell', cost: 2, spell: 'mist_seal', desc: '스펠: 아군 하수인에게 +1/+1을 주고 원하는 빈 칸으로 순간이동!' },
      { name: '유령 번개', type: 'spell', cost: 1, spell: 'ghost_lightning', desc: '스펠: 모든 적 하수인에게 1 피해를 입힙니다.' },
      { name: '그림자 가면', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_mask', desc: '아티팩트 (내구도 3): 장군 공격력 +2 및 원거리(Ranged) 부여!' }
    ]
  },
  zirix: {
    id: 'zirix', name: '지릭스 스타스트라이더', title: '베트루비안 제국 (VETRUVIAN)',
    color: '#14b8a6', sprite: 'zirix',
    bbsName: '바람의 소환', bbsCost: 1,
    bbsDesc: '장군 주변 빈 칸에 2/2 돌진 바람의 데르비시 소환',
    cards: [
      { name: '화염술사', type: 'minion', cost: 2, atk: 2, hp: 1, sprite: 'archer', keywords: ['ranged'], desc: '원거리: 초반부터 안전하게 원거리 견제를 가합니다.' },
      { name: '사막의 수호석상', type: 'minion', cost: 3, atk: 2, hp: 5, sprite: 'golem', keywords: ['provoke'], desc: '도발: 높은 체력으로 중앙 마나 샘을 틀어막습니다.' },
      { name: '모래폭풍 정령', type: 'minion', cost: 3, atk: 3, hp: 2, sprite: 'dervish', keywords: ['rush'], desc: '돌진: 황금 모래바람과 함께 돌격하는 정령입니다.' },
      { name: '아이마르 치유사', type: 'minion', cost: 5, atk: 5, hp: 5, sprite: 'golem', keywords: ['provoke', 'gambit_heal_all'], desc: '도발 · 함성: 아군 장군의 체력을 5 회복합니다.' },
      { name: '자손의 축복', type: 'spell', cost: 2, spell: 'scions_wish', desc: '스펠: 아군 하수인에게 +2/+2를 부여하고 카드 1장 드로우.' },
      { name: '엔트로피 붕괴', type: 'spell', cost: 3, spell: 'entropic_decay', desc: '스펠: 아군 장군 주변 8칸 내 적 하수인 1기 즉시 소멸!' },
      { name: '별의 분노', type: 'spell', cost: 4, spell: 'stars_fury', desc: '스펠: 모든 적 유닛 바로 앞 칸에 2/2 돌진 데르비시 소환!' },
      { name: '모래의 뼈무리', type: 'spell', cost: 2, spell: 'bone_swarm', desc: '스펠: 적 장군과 그 주변 모든 적에게 2 광역 피해!' },
      { name: '이키르의 지팡이', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_staff', desc: '아티팩트 (내구도 3): 아군 장군에게 공격력 +2를 부여합니다.' }
    ]
  },
  lilithe: {
    id: 'lilithe', name: '리리스 블라이트체이서', title: '어비시안 군단 (ABYSSIAN)',
    color: '#c084fc', sprite: 'lilithe',
    bbsName: '망령의 부름', bbsCost: 1,
    bbsDesc: '장군 주변 빈 칸에 1/1 돌진 심연의 망령 2기 소환',
    cards: [
      { name: '피눈물 연금술사', type: 'minion', cost: 1, atk: 2, hp: 1, sprite: 'wraith', keywords: ['gambit_ping'], desc: '전투의 함성: 체력이 가장 낮은 적에게 1 피해를 입힙니다.' },
      { name: '어둠의 파수꾼', type: 'minion', cost: 3, atk: 2, hp: 4, sprite: 'golem', keywords: ['provoke'], desc: '도발: 망령 군단을 보호하는 어둠의 방벽입니다.' },
      { name: '심연의 사신', type: 'minion', cost: 4, atk: 5, hp: 4, sprite: 'wraith', keywords: ['rush'], desc: '돌진: 어둠 속에서 튀어나오는 고화력 사신입니다.' },
      { name: '망령의 군주', type: 'minion', cost: 6, atk: 6, hp: 6, sprite: 'revenant', keywords: ['rush'], desc: '돌진: 전장을 공포로 물들이는 최상위 심연 군주.' },
      { name: '영혼 착취', type: 'spell', cost: 2, spell: 'void_pulse', desc: '스펠: 대상 적에게 2 피해를 입히고 아군 장군 체력 +3 회복.' },
      { name: '악마의 유혹', type: 'spell', cost: 2, spell: 'daemonic_lure', desc: '스펠: 적 하수인에게 1 피해 후 원하는 빈 칸으로 강제 이동!' },
      { name: '영혼 파쇄 서약', type: 'spell', cost: 2, spell: 'soulshatter', desc: '스펠: 모든 아군 하수인에게 공격력 +2를 부여합니다!' },
      { name: '어둠의 의식', type: 'spell', cost: 3, spell: 'dark_ritual', desc: '스펠: 적 하수인 1기에게 4 피해 & 아군 장군 체력 +2 회복.' },
      { name: '유령의 칼날', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_void', desc: '아티팩트 (내구도 3): 장군 공격력 +2 & 적 처치 시 체력 +2!' }
    ]
  },
  vaath: {
    id: 'vaath', name: '바스 디 이모탈', title: '마그마르 위상 (MAGMAR)',
    color: '#10b981', sprite: 'vaath',
    bbsName: '과부하 (Overload)', bbsCost: 1,
    bbsDesc: '아군 장군의 공격력이 영구적으로 +1 증가',
    cards: [
      { name: '어린 실리타르', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'beast', keywords: [], desc: '단단한 체력을 지닌 마그마르의 기본 전사.' },
      { name: '태고의 수호룡', type: 'minion', cost: 3, atk: 3, hp: 4, sprite: 'beast', keywords: ['frenzy'], desc: '광란: 공격 시 주변 8칸의 모든 적을 동시에 베어버립니다.' },
      { name: '마칸토르 전투야수', type: 'minion', cost: 5, atk: 4, hp: 4, sprite: 'beast', keywords: ['rush', 'frenzy'], desc: '돌진 · 광란: 소환 즉시 돌격해 인접 모든 적을 동시 타격!' },
      { name: '장로 실리타르', type: 'minion', cost: 6, atk: 7, hp: 7, sprite: 'beast', keywords: ['provoke'], desc: '도발: 압도적인 거구로 전장을 지배하는 고대 용족.' },
      { name: '자연의 선택', type: 'spell', cost: 2, spell: 'natural_select', desc: '스펠: 전장에서 공격력이 가장 낮은 하수인 1기 즉시 처치.' },
      { name: '플라즈마 폭풍', type: 'spell', cost: 4, spell: 'plasma_storm', desc: '스펠: 공격력 3 이하인 모든 하수인을 전장에서 일소!' },
      { name: '대지의 구체', type: 'spell', cost: 3, spell: 'earth_sphere', desc: '스펠: 아군 장군의 체력을 7 회복합니다.' },
      { name: '태고의 강인함', type: 'spell', cost: 1, spell: 'greater_fortitude', desc: '스펠: 아군 하수인 1기에게 +2/+2를 영구 부여합니다.' },
      { name: '아다만타이트 발톱', type: 'artifact', cost: 3, atkBonus: 3, art: 'artifact_claw', desc: '아티팩트 (내구도 3): 아군 장군에게 공격력 +3 부여!' }
    ]
  },
  faie: {
    id: 'faie', name: '페이 블러드윙', title: '바나르 혈족 (VANAR)',
    color: '#38bdf8', sprite: 'faie',
    bbsName: '전쟁의 새 (Warbird)', bbsCost: 1,
    bbsDesc: '적 장군과 같은 세로줄(열)의 모든 적에게 2 피해',
    cards: [
      { name: '서리 송곳니 늑대', type: 'minion', cost: 2, atk: 3, hp: 2, sprite: 'wolf', keywords: ['rush'], desc: '돌진: 빙원을 가르는 민첩한 사냥꾼입니다.' },
      { name: '서리뼈 나가', type: 'minion', cost: 3, atk: 3, hp: 3, sprite: 'wolf', keywords: ['gambit_nova2'], desc: '전투의 함성: 소환된 칸 주변 8칸의 모든 유닛에게 2 피해!' },
      { name: '빙하의 파수꾼', type: 'minion', cost: 4, atk: 3, hp: 6, sprite: 'golem', keywords: ['provoke'], desc: '도발: 뚫기 힘든 거대한 만년설 방벽입니다.' },
      { name: '드라우가르 군주', type: 'minion', cost: 6, atk: 5, hp: 7, sprite: 'golem', keywords: ['provoke', 'frenzy'], desc: '도발 · 광란: 전선을 얼려버리는 북방의 거신.' },
      { name: '냉혹한 한기', type: 'spell', cost: 2, spell: 'chromatic_cold', desc: '스펠: 대상 하수인의 능력을 침묵(해제)시키고 2 피해!' },
      { name: '우박 감옥', type: 'spell', cost: 2, spell: 'hailstone', desc: '스펠: 대상 적 하수인을 원래 주인의 손패로 되돌려 보냅니다!' },
      { name: '눈사태 (Avalanche)', type: 'spell', cost: 4, spell: 'avalanche', desc: '스펠: 전장 왼쪽 절반(1~4열)의 모든 적에게 4 피해 & 기절!' },
      { name: '여우의 형상', type: 'spell', cost: 1, spell: 'aspect_fox', desc: '스펠: 대상 적 하수인을 능력 없는 3/3 여우로 변신시킵니다!' },
      { name: '콜드바이터', type: 'artifact', cost: 2, atkBonus: 1, art: 'artifact_ice', desc: '아티팩트 (내구도 3): 장군 공격력 +1 & 턴 종료 시 주변 적 2 피해!' }
    ]
  }
};

// 공용 중립 카드 10종
const NEUTRAL_CARDS = [
  { name: '단검의 검객', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'paladin', keywords: ['gambit_buff_ally'], desc: '전투의 함성: 무작위 아군 하수인 1기에게 공격력 +2 부여.' },
  { name: '치유의 신비술사', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'archer', keywords: ['gambit_heal_all'], desc: '전투의 함성: 아군 장군의 체력을 2 회복합니다.' },
  { name: '검은호랑이', type: 'minion', cost: 3, atk: 3, hp: 2, sprite: 'fox', keywords: ['rush'], desc: '돌진: 어느 덱에서나 활약하는 날렵한 중립 돌격 야수.' },
  { name: '축출 야수', type: 'minion', cost: 3, atk: 2, hp: 2, sprite: 'wolf', keywords: ['gambit_repulse'], desc: '전투의 함성: 가장 가까운 적 하수인을 구석으로 날려버립니다!' },
  { name: '에메랄드 명사수', type: 'minion', cost: 3, atk: 2, hp: 3, sprite: 'archer', keywords: ['ranged'], desc: '원거리: 먼 거리에서 반격 없이 지원 사격합니다.' },
  { name: '빛의 굴절자', type: 'minion', cost: 4, atk: 3, hp: 3, sprite: 'paladin', keywords: ['gambit_dispel_aoe'], desc: '전투의 함성: 주변 8칸 모든 유닛의 특수 능력을 침묵(해제)!' },
  { name: '춤추는 칼날', type: 'minion', cost: 5, atk: 4, hp: 6, sprite: 'assassin', keywords: ['gambit_front3'], desc: '전투의 함성: 바로 앞 칸의 적에게 3 피해를 입힙니다!' },
  { name: '석화 토템 수호자', type: 'minion', cost: 3, atk: 2, hp: 5, sprite: 'golem', keywords: ['provoke'], desc: '도발: 인접한 적들의 발을 묶는 단단한 수호자입니다.' },
  { name: '화염 피의 흑마법사', type: 'minion', cost: 2, atk: 3, hp: 1, sprite: 'wraith', keywords: ['gambit_both3'], desc: '전투의 함성: 양쪽 장군 모두에게 3 피해를 입힙니다!' },
  { name: '집정관 스펠바인더', type: 'minion', cost: 6, atk: 7, hp: 7, sprite: 'golem', keywords: ['frenzy'], desc: '광란: 거대한 마력 구체로 주변 모든 적을 동시 타격!' }
];

// =========================================================================
// 3. 게임 상태 및 전장 상수
// =========================================================================
const ROWS = 5, COLS = 9;
const BOARD_X = 62, BOARD_Y = 128, TILE_W = 92, TILE_H = 78, GAP = 4;

let state = {
  screen: 'title',
  selectedFaction: 'argeon',
  difficultyIdx: 1, // 0: easy, 1: normal, 2: hard, 3: master
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
  pArtifacts: [],
  eArtifacts: [],
  replacedThisTurn: false,
  replaceMode: false,
  targetMode: null,
  selectedPos: null,
  selectedCardIdx: null,
  hoverTile: null,
  hoverCardIdx: null,
  aiBusy: false,
  winner: null,
  logs: [],
  effects: [],
  shake: 0,
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

function triggerShake(amount = 6) {
  state.shake = Math.max(state.shake, amount);
}

function spawnFloatText(r, c, text, color) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'text', x: pt.x, y: pt.y - 22, text, color, t: 0, maxT: 62 });
}

function spawnBeam(r1, c1, r2, c2, color) {
  const p1 = tileCenter(r1, c1);
  const p2 = tileCenter(r2, c2);
  state.effects.push({ type: 'beam', x: p1.x, y: p1.y, x2: p2.x, y2: p2.y, color, t: 0, maxT: 24 });
}

function spawnSlash(r, c, color = '#fef08a') {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'slash', x: pt.x, y: pt.y, color, t: 0, maxT: 20 });
}

function spawnRing(r, c, color) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'ring', x: pt.x, y: pt.y, color, t: 0, maxT: 28 });
}

function spawnBurst(r, c, color, count = 16) {
  const pt = tileCenter(r, c);
  for (let i = 0; i < count; i++) {
    const ang = (Math.PI * 2 * i) / count;
    const spd = 1.6 + Math.random() * 3.0;
    state.effects.push({
      type: 'particle', x: pt.x, y: pt.y,
      vx: Math.cos(ang) * spd, vy: Math.sin(ang) * spd,
      color, t: 0, maxT: 32
    });
  }
}

function buildDeck30(factionId) {
  const fCards = FACTIONS[factionId].cards;
  const deck = [];
  // 진영 카드 9종 x 2장 = 18장
  for (const c of fCards) {
    deck.push({ ...c, keywords: [...(c.keywords || [])] });
    deck.push({ ...c, keywords: [...(c.keywords || [])] });
  }
  // 중립 카드 10종 중 6종 x 2장 = 12장 -> 총 30장 덱
  const shuffledNeutral = [...NEUTRAL_CARDS].sort(() => Math.random() - 0.5).slice(0, 6);
  for (const c of shuffledNeutral) {
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
  const diff = DIFFICULTIES[state.difficultyIdx];

  const board = Array.from({ length: ROWS }, () => Array(COLS).fill(null));
  board[2][0] = {
    name: pf.name, owner: 'player', isGeneral: true, sprite: pf.sprite,
    baseAtk: 2, atk: 2, hp: 25, maxHp: 25, keywords: [], stunned: false, canMove: true, canAttack: true
  };
  board[2][8] = {
    name: ef.name, owner: 'enemy', isGeneral: true, sprite: ef.sprite,
    baseAtk: 2, atk: 2, hp: diff.eHp, maxHp: diff.eHp, keywords: [], stunned: false, canMove: true, canAttack: true
  };

  const pDeck = buildDeck30(pFid);
  const eDeck = buildDeck30(eFid);
  const eStartCount = 5 + diff.bonusCard;

  state.screen = 'battle';
  state.playerFaction = pf;
  state.enemyFaction = ef;
  state.board = board;
  state.manaOrbs = [{ r: 0, c: 4 }, { r: 2, c: 4 }, { r: 4, c: 4 }];
  state.turn = 1;
  state.pMana = 2; state.pMaxMana = 2;
  state.eMana = 3; state.eMaxMana = 3;
  state.pDeck = pDeck;
  state.pHand = Array.from({ length: 5 }, () => pDeck.pop());
  state.eDeck = eDeck;
  state.eHand = Array.from({ length: Math.min(6, eStartCount) }, () => eDeck.pop());
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
  state.logs = [`⚔️ [${diff.name}] ${pf.name} vs ${ef.name} 개전!`];
}

// =========================================================================
// 4. 전술 판정 & 동시 반격 & 전투의 함성(Opening Gambit)
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
  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const u = state.board[r][c];
    if (u && u.owner === owner && u.isGeneral) return { r, c, unit: u };
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
      addLog(`💔 [${arts[i].name}] 파괴됨!`);
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
    for (let tr = 0; tr < ROWS; tr++) for (let tc = 0; tc < COLS; tc++) {
      const t = state.board[tr][tc];
      if (t && t.owner !== u.owner) targets.push({ r: tr, c: tc });
    }
  } else {
    for (const n of neighbors8(r, c)) {
      const t = state.board[n.r][n.c];
      if (t && t.owner !== u.owner) targets.push(n);
    }
  }
  return targets;
}

// 기습(Backstab) 판정: 플레이어 유닛(오른쪽을 봄)이 적(왼쪽을 봄)의 오른쪽 칸(c1 > c2)에서 공격할 때
function isBackstabPosition(atkU, r1, c1, r2, c2) {
  if (!atkU || !atkU.keywords.includes('backstab')) return false;
  if (Math.abs(r1 - r2) > 1 || Math.abs(c1 - c2) > 1) return false;
  return atkU.owner === 'player' ? c1 > c2 : c1 < c2;
}

function getValidSummonTiles(owner) {
  const map = new Map();
  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const u = state.board[r][c];
    if (u && u.owner === owner) {
      for (const n of neighbors8(r, c)) {
        if (!state.board[n.r][n.c]) map.set(`${n.r},${n.c}`, n);
      }
    }
  }
  return Array.from(map.values());
}

function getValidSpellTargets(card, owner) {
  const targets = [];
  const sp = card.spell;
  if (['holy_immolation', 'divine_bond', 'inner_focus', 'mist_seal', 'scions_wish', 'greater_fortitude'].includes(sp)) {
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
  } else if (['entropic_decay', 'daemonic_lure', 'chromatic_cold', 'hailstone', 'dark_ritual', 'aspect_fox'].includes(sp)) {
    const g = findGeneral(owner);
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (!u || u.owner === owner || u.isGeneral) continue;
      if (sp === 'entropic_decay' && g && (Math.abs(r - g.r) > 1 || Math.abs(c - g.c) > 1)) continue;
      targets.push({ r, c });
    }
  } else {
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
    spawnBurst(r, c, '#38bdf8', 20);
    spawnFloatText(r, c, '+1 MANA', '#38bdf8');
    if (owner === 'player') { state.pMana++; addLog('💎 플레이어 마나 샘 흡수! (+1 마나)'); }
    else { state.eMana++; addLog('💎 적 AI 마나 샘 흡수! (+1 마나)'); }
  }
}

function dealDamageToUnit(r, c, dmg, color = '#ef4444') {
  const u = state.board[r][c];
  if (!u || dmg <= 0) return false;
  let finalDmg = dmg;
  // 아클라이트 성갑 피해 경감
  if (u.isGeneral) {
    const arts = u.owner === 'player' ? state.pArtifacts : state.eArtifacts;
    if (arts.some(a => a.art === 'artifact_regalia')) finalDmg = Math.max(0, finalDmg - 2);
    if (finalDmg > 0) damageArtifacts(u.owner);
  }
  u.hp -= finalDmg;
  spawnFloatText(r, c, `-${finalDmg}`, color);
  spawnBurst(r, c, color, 14);
  if (finalDmg >= 4) triggerShake(7);
  if (u.hp <= 0) {
    addLog(`💥 [${u.name}] 처치됨!`);
    state.board[r][c] = null;
    return true;
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

// =========================================================================
// 핵심 수정: 동시 반격(Simultaneous Counterattack) 구현
// =========================================================================
function attackUnit(r1, c1, r2, c2) {
  const atkU = state.board[r1][c1];
  const defU = state.board[r2][c2];
  if (!atkU || !defU) return;

  atkU.canAttack = false;
  atkU.canMove = false;

  const isRanged = atkU.keywords.includes('ranged');
  const isFrenzy = atkU.keywords.includes('frenzy');
  const backstab = isBackstabPosition(atkU, r1, c1, r2, c2);

  // 교전 시작 시점의 양측 공격력을 미리 스냅샷 저장 (방어자가 죽어도 반격 데미지는 동시에 들어옴!)
  const totalAtkDmg = atkU.atk + (backstab ? 2 : 0);
  const simultaneousCounterDmg = defU.atk;
  const shouldCounter = !isRanged && !backstab;

  spawnBeam(r1, c1, r2, c2, backstab ? '#f43f5e' : (isRanged ? '#38bdf8' : '#fbbf24'));
  spawnSlash(r2, c2, backstab ? '#f43f5e' : '#fef08a');
  triggerShake(5);

  const victims = [{ r: r2, c: c2 }];
  if (isFrenzy && !isRanged) {
    for (const n of neighbors8(r1, c1)) {
      const adj = state.board[n.r][n.c];
      if (adj && adj.owner !== atkU.owner && !(n.r === r2 && n.c === c2)) victims.push(n);
    }
  }

  let anyKilled = false;
  for (const v of victims) {
    if (dealDamageToUnit(v.r, v.c, totalAtkDmg, backstab ? '#f43f5e' : '#ef4444')) anyKilled = true;
  }

  // 유령의 칼날 흡혈
  if (anyKilled && atkU.isGeneral) {
    const arts = atkU.owner === 'player' ? state.pArtifacts : state.eArtifacts;
    if (arts.some(a => a.art === 'artifact_void')) {
      atkU.hp = Math.min(atkU.maxHp, atkU.hp + 2);
      spawnFloatText(r1, c1, '+2 HP', '#e879f9');
    }
  }

  // 동시 반격 실행: 방어자가 이번 공격에 죽었더라도 근접 교전이면 공격자에게 동시에 반격 피해를 입힘!
  if (shouldCounter && simultaneousCounterDmg > 0) {
    spawnSlash(r1, c1, '#fb923c');
    dealDamageToUnit(r1, c1, simultaneousCounterDmg, '#fb923c');
  }

  addLog(backstab
    ? `🗡️ [기습!] ${atkU.name} → ${defU.name} (${totalAtkDmg} 피해, 반격 무시)`
    : `⚔️ ${atkU.name} ↔ ${defU.name} 동시 교전 (${totalAtkDmg} / ${shouldCounter ? simultaneousCounterDmg : 0})`
  );
  checkGameOver();
}

function triggerOpeningGambit(unit, r, c) {
  const owner = unit.owner;
  const opp = owner === 'player' ? 'enemy' : 'player';
  const g = findGeneral(owner);
  const oppG = findGeneral(opp);

  if (unit.keywords.includes('gambit_heal_all') && g) {
    const heal = unit.name.includes('아이마르') ? 5 : (unit.name.includes('태양') ? 4 : 2);
    g.unit.hp = Math.min(g.unit.maxHp, g.unit.hp + heal);
    spawnRing(g.r, g.c, '#34d399');
    spawnFloatText(g.r, g.c, `+${heal} HP`, '#34d399');
  }
  if (unit.keywords.includes('gambit_ping')) {
    const enemies = [];
    for (let er = 0; er < ROWS; er++) for (let ec = 0; ec < COLS; ec++) {
      const eu = state.board[er][ec];
      if (eu && eu.owner === opp) enemies.push({ r: er, c: ec, hp: eu.hp });
    }
    if (enemies.length) {
      enemies.sort((a, b) => a.hp - b.hp);
      spawnBeam(r, c, enemies[0].r, enemies[0].c, '#c084fc');
      dealDamageToUnit(enemies[0].r, enemies[0].c, 1, '#c084fc');
    }
  }
  if (unit.keywords.includes('gambit_nova2')) {
    spawnRing(r, c, '#38bdf8');
    for (const n of neighbors8(r, c)) {
      if (state.board[n.r][n.c]) dealDamageToUnit(n.r, n.c, 2, '#38bdf8');
    }
  }
  if (unit.keywords.includes('gambit_buff_ally')) {
    const allies = [];
    for (let ar = 0; ar < ROWS; ar++) for (let ac = 0; ac < COLS; ac++) {
      const au = state.board[ar][ac];
      if (au && au.owner === owner && !au.isGeneral && !(ar === r && ac === c)) allies.push({ r: ar, c: ac, u: au });
    }
    if (allies.length) {
      const pick = allies[Math.floor(Math.random() * allies.length)];
      pick.u.atk += 2;
      spawnFloatText(pick.r, pick.c, '+2 ATK', '#fbbf24');
    }
  }
  if (unit.keywords.includes('gambit_repulse')) {
    const enemies = [];
    for (let er = 0; er < ROWS; er++) for (let ec = 0; ec < COLS; ec++) {
      const eu = state.board[er][ec];
      if (eu && eu.owner === opp && !eu.isGeneral) enemies.push({ r: er, c: ec });
    }
    if (enemies.length) {
      enemies.sort((a, b) => (Math.abs(a.r - r) + Math.abs(a.c - c)) - (Math.abs(b.r - r) + Math.abs(b.c - c)));
      const target = enemies[0];
      const backCol = owner === 'player' ? 8 : 0;
      for (let rr = 0; rr < ROWS; rr++) {
        if (!state.board[rr][backCol]) {
          state.board[rr][backCol] = state.board[target.r][target.c];
          state.board[target.r][target.c] = null;
          spawnBeam(target.r, target.c, rr, backCol, '#38bdf8');
          spawnFloatText(rr, backCol, 'REPULSED!', '#38bdf8');
          break;
        }
      }
    }
  }
  if (unit.keywords.includes('gambit_dispel_aoe')) {
    spawnRing(r, c, '#fef08a');
    for (const n of neighbors8(r, c)) {
      const u = state.board[n.r][n.c];
      if (u && !u.isGeneral) {
        u.keywords = [];
        spawnFloatText(n.r, n.c, 'DISPEL', '#fef08a');
      }
    }
  }
  if (unit.keywords.includes('gambit_front3')) {
    const fc = c + (owner === 'player' ? 1 : -1);
    if (fc >= 0 && fc < COLS && state.board[r][fc] && state.board[r][fc].owner === opp) {
      spawnSlash(r, fc, '#f43f5e');
      dealDamageToUnit(r, fc, 3, '#f43f5e');
    }
  }
  if (unit.keywords.includes('gambit_both3')) {
    if (g) dealDamageToUnit(g.r, g.c, 3, '#f97316');
    if (oppG) dealDamageToUnit(oppG.r, oppG.c, 3, '#f97316');
  }
  checkGameOver();
}

function summonMinion(card, r, c, owner) {
  const rush = card.keywords.includes('rush');
  const unit = {
    name: card.name, owner, isGeneral: false, sprite: card.sprite,
    atk: card.atk, hp: card.hp, maxHp: card.hp,
    keywords: [...card.keywords], stunned: false, canMove: rush, canAttack: rush
  };
  state.board[r][c] = unit;
  spawnRing(r, c, '#10b981');
  spawnBurst(r, c, '#10b981', 14);
  spawnFloatText(r, c, card.name, '#34d399');
  addLog(`✨ ${owner === 'player' ? '아군' : '적'} [${card.name}] 소환!`);
  checkOrbPickup(r, c, owner);
  triggerOpeningGambit(unit, r, c);
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
  triggerShake(4);

  if (sp === 'divine_bond' && t) {
    t.atk += t.hp;
    spawnRing(r, c, '#fbbf24'); spawnFloatText(r, c, `+${t.hp} ATK!`, '#fbbf24');
  } else if (sp === 'holy_immolation' && t) {
    t.hp = Math.min(t.maxHp, t.hp + 4);
    spawnRing(r, c, '#fef08a'); spawnFloatText(r, c, '+4 HP', '#34d399');
    for (const n of neighbors8(r, c)) {
      const adj = state.board[n.r][n.c];
      if (adj && adj.owner !== owner) dealDamageToUnit(n.r, n.c, 4, '#fbbf24');
    }
  } else if (sp === 'martyrdom' && t) {
    const heal = t.hp;
    const tGen = findGeneral(t.owner);
    state.board[r][c] = null;
    spawnBurst(r, c, '#fef08a', 20);
    if (tGen) {
      tGen.unit.hp = Math.min(tGen.unit.maxHp, tGen.unit.hp + heal);
      spawnFloatText(tGen.r, tGen.c, `+${heal} HP`, '#34d399');
    }
  } else if (sp === 'tempest') {
    for (let tr = 0; tr < ROWS; tr++) for (let tc = 0; tc < COLS; tc++) {
      if (state.board[tr][tc]) dealDamageToUnit(tr, tc, 2, '#fbbf24');
    }
  } else if (sp === 'war_surge') {
    for (let ar = 0; ar < ROWS; ar++) for (let ac = 0; ac < COLS; ac++) {
      const au = state.board[ar][ac];
      if (au && au.owner === owner && !au.isGeneral) {
        au.atk += 1; au.hp += 1; au.maxHp += 1;
        spawnFloatText(ar, ac, '+1/+1', '#fbbf24');
      }
    }
  } else if (sp === 'phoenix_fire' && t) {
    dealDamageToUnit(r, c, 3, '#f97316'); drawCards(owner, 1);
  } else if (sp === 'inner_focus' && t) {
    t.canMove = true; t.canAttack = true; t.stunned = false;
    spawnRing(r, c, '#38bdf8'); spawnFloatText(r, c, 'REACTIVATE!', '#38bdf8');
  } else if (sp === 'mist_seal' && t && step2Pos) {
    t.atk += 1; t.hp += 1; t.maxHp += 1;
    state.board[step2Pos.r][step2Pos.c] = t; state.board[r][c] = null;
    spawnRing(step2Pos.r, step2Pos.c, '#f43f5e'); checkOrbPickup(step2Pos.r, step2Pos.c, owner);
  } else if (sp === 'ghost_lightning') {
    for (let er = 0; er < ROWS; er++) for (let ec = 0; ec < COLS; ec++) {
      const eu = state.board[er][ec];
      if (eu && eu.owner !== owner && !eu.isGeneral) dealDamageToUnit(er, ec, 1, '#f43f5e');
    }
  } else if (sp === 'scions_wish' && t) {
    t.atk += 2; t.hp += 2; t.maxHp += 2;
    spawnRing(r, c, '#14b8a6'); spawnFloatText(r, c, '+2/+2', '#14b8a6'); drawCards(owner, 1);
  } else if (sp === 'entropic_decay' && t) {
    spawnBurst(r, c, '#14b8a6', 22); state.board[r][c] = null;
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
  } else if (sp === 'bone_swarm' && oppG) {
    dealDamageToUnit(oppG.r, oppG.c, 2, '#d97706');
    for (const n of neighbors8(oppG.r, oppG.c)) {
      const adj = state.board[n.r][n.c];
      if (adj && adj.owner !== owner) dealDamageToUnit(n.r, n.c, 2, '#d97706');
    }
  } else if (sp === 'void_pulse' && t) {
    dealDamageToUnit(r, c, 2, '#c084fc');
    if (g) { g.unit.hp = Math.min(g.unit.maxHp, g.unit.hp + 3); spawnFloatText(g.r, g.c, '+3 HP', '#34d399'); }
  } else if (sp === 'dark_ritual' && t) {
    dealDamageToUnit(r, c, 4, '#c084fc');
    if (g) { g.unit.hp = Math.min(g.unit.maxHp, g.unit.hp + 2); spawnFloatText(g.r, g.c, '+2 HP', '#34d399'); }
  } else if (sp === 'daemonic_lure' && t && step2Pos) {
    const dead = dealDamageToUnit(r, c, 1, '#c084fc');
    if (!dead && state.board[r][c]) {
      state.board[step2Pos.r][step2Pos.c] = state.board[r][c]; state.board[r][c] = null;
      spawnRing(step2Pos.r, step2Pos.c, '#c084fc');
    }
  } else if (sp === 'soulshatter') {
    for (let ar = 0; ar < ROWS; ar++) for (let ac = 0; ac < COLS; ac++) {
      const au = state.board[ar][ac];
      if (au && au.owner === owner && !au.isGeneral) { au.atk += 2; spawnFloatText(ar, ac, '+2 ATK', '#e879f9'); }
    }
  } else if (sp === 'natural_select' && t) {
    spawnBurst(r, c, '#10b981', 20); state.board[r][c] = null;
  } else if (sp === 'plasma_storm') {
    for (let mr = 0; mr < ROWS; mr++) for (let mc = 0; mc < COLS; mc++) {
      const mu = state.board[mr][mc];
      if (mu && !mu.isGeneral && mu.atk <= 3) { spawnBurst(mr, mc, '#10b981', 16); state.board[mr][mc] = null; }
    }
  } else if (sp === 'earth_sphere' && g) {
    g.unit.hp = Math.min(g.unit.maxHp, g.unit.hp + 7);
    spawnRing(g.r, g.c, '#10b981'); spawnFloatText(g.r, g.c, '+7 HP', '#10b981');
  } else if (sp === 'greater_fortitude' && t) {
    t.atk += 2; t.hp += 2; t.maxHp += 2;
    spawnRing(r, c, '#10b981'); spawnFloatText(r, c, '+2/+2', '#10b981');
  } else if (sp === 'chromatic_cold' && t) {
    t.keywords = []; spawnFloatText(r, c, 'DISPELLED!', '#bae6fd'); dealDamageToUnit(r, c, 2, '#38bdf8');
  } else if (sp === 'hailstone' && t) {
    const tHand = t.owner === 'player' ? state.pHand : state.eHand;
    if (tHand.length < 6) {
      tHand.push({
        name: t.name, type: 'minion', cost: Math.max(1, Math.min(6, Math.round((t.atk + t.maxHp) / 2))),
        atk: t.atk, hp: t.maxHp, sprite: t.sprite, keywords: [...t.keywords], desc: '우박 감옥에서 귀환한 하수인입니다.'
      });
    }
    spawnBurst(r, c, '#38bdf8', 18); state.board[r][c] = null;
  } else if (sp === 'avalanche') {
    for (let ar = 0; ar < ROWS; ar++) for (let ac = 0; ac <= 3; ac++) {
      const au = state.board[ar][ac];
      if (au && au.owner !== owner) { au.stunned = true; dealDamageToUnit(ar, ac, 4, '#38bdf8'); }
    }
  } else if (sp === 'aspect_fox' && t) {
    state.board[r][c] = {
      name: '서리 여우', owner: t.owner, isGeneral: false, sprite: 'fox',
      atk: 3, hp: 3, maxHp: 3, keywords: [], stunned: false, canMove: false, canAttack: false
    };
    spawnRing(r, c, '#38bdf8'); spawnFloatText(r, c, 'FOX!', '#38bdf8');
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
    g.unit.baseAtk += 1; recalcGeneralStats(owner);
    spawnRing(g.r, g.c, '#10b981'); spawnFloatText(g.r, g.c, '+1 ATK', '#10b981');
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
      allies[0].u.atk += 2; spawnFloatText(allies[0].r, allies[0].c, '+2 ATK', '#fbbf24');
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
// 6. 난이도별 AI 전술 사고 엔진
// =========================================================================
function endPlayerTurn() {
  if (state.winner || state.aiBusy) return;
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

  const diff = DIFFICULTIES[state.difficultyIdx].id;
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

  // Step 1: 카드 전개 (숙련/마스터 난이도는 마나 샘 근처 우선 소환)
  steps.push(() => {
    for (let idx = state.eHand.length - 1; idx >= 0; idx--) {
      if (diff === 'easy' && Math.random() < 0.3) continue;
      const card = state.eHand[idx];
      if (card.cost > state.eMana) continue;

      if (card.type === 'minion') {
        const tiles = getValidSummonTiles('enemy');
        if (tiles.length) {
          tiles.sort((a, b) => {
            const aOrb = state.manaOrbs.some(o => o.r === a.r && o.c === a.c) ? -10 : 0;
            const bOrb = state.manaOrbs.some(o => o.r === b.r && o.c === b.c) ? -10 : 0;
            return (a.c + aOrb) - (b.c + bOrb);
          });
          state.eMana -= card.cost; state.eHand.splice(idx, 1);
          summonMinion(card, tiles[0].r, tiles[0].c, 'enemy');
        }
      } else if (card.type === 'artifact') {
        state.eMana -= card.cost; state.eHand.splice(idx, 1);
        equipArtifact(card, 'enemy');
      } else if (card.type === 'spell') {
        const targets = getValidSpellTargets(card, 'enemy');
        if (targets.length) {
          // 공격 스펠은 플레이어 장군이나 가장 강한 아군 우선
          targets.sort((a, b) => {
            const ua = state.board[a.r][a.c], ub = state.board[b.r][b.c];
            if (!ua || !ub) return 0;
            return (ub.isGeneral ? 50 : ub.atk) - (ua.isGeneral ? 50 : ua.atk);
          });
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

  // Step 2: 고유 스킬 사용
  steps.push(() => { if (!state.winner && diff !== 'easy') triggerBBS('enemy'); });

  // Step 3: 전술 이동 & 동시 반격 교전
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

      const pg = findGeneral('player') || { r: 2, c: 0, unit: { hp: 25 } };
      let atks = getValidAttacks(pos.r, pos.c);

      if (atks.length) {
        // 숙련 이상은 플레이어 장군 킬각이면 무조건 장군 타격
        const lethal = atks.find(a => state.board[a.r][a.c].isGeneral && state.board[a.r][a.c].hp <= u.atk);
        if (lethal && (diff === 'hard' || diff === 'master')) {
          attackUnit(pos.r, pos.c, lethal.r, lethal.c);
          continue;
        }
        atks.sort((a, b) => state.board[a.r][a.c].hp - state.board[b.r][b.c].hp);
        attackUnit(pos.r, pos.c, atks[0].r, atks[0].c);
        continue;
      }

      const moves = getValidMoves(pos.r, pos.c);
      if (moves.length) {
        moves.sort((a, b) => {
          // 마나 구슬 우선 점수
          const orbA = (diff !== 'easy' && state.manaOrbs.some(o => o.r === a.r && o.c === a.c)) ? -6 : 0;
          const orbB = (diff !== 'easy' && state.manaOrbs.some(o => o.r === b.r && o.c === b.c)) ? -6 : 0;
          if (u.isGeneral && u.hp <= 9 && diff !== 'easy') return (b.c + orbB) - (a.c + orbA);
          const distA = Math.abs(a.r - pg.r) + Math.abs(a.c - pg.c) + orbA;
          const distB = Math.abs(b.r - pg.r) + Math.abs(b.c - pg.c) + orbB;
          return distA - distB;
        });
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

  // Step 4: 플레이어 턴 복귀
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

  steps.forEach((fn, i) => setTimeout(fn, (i + 1) * 410));
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
    if (inside(x, y, cx, 560, 146, 230)) state.hoverCardIdx = i;
  }
});

canvas.addEventListener('click', (e) => {
  const { x, y } = getMousePos(e);

  if (state.screen === 'title') {
    if (inside(x, y, W / 2 - 175, 535, 350, 70)) state.screen = 'select';
    return;
  }

  if (state.screen === 'select') {
    const keys = Object.keys(FACTIONS);
    keys.forEach((fid, idx) => {
      const cx = 55 + idx * 196;
      if (inside(x, y, cx, 95, 184, 132)) state.selectedFaction = fid;
    });
    // 난이도 4단계 버튼
    DIFFICULTIES.forEach((d, idx) => {
      const dx = 55 + idx * 175;
      if (inside(x, y, dx, 705, 165, 52)) state.difficultyIdx = idx;
    });
    // 상대 AI 진영 토글
    if (inside(x, y, 785, 705, 225, 52)) {
      const opts = ['random', ...keys];
      state.enemyChoice = opts[(opts.indexOf(state.enemyChoice) + 1) % opts.length];
    }
    // 전투 시작
    if (inside(x, y, 1025, 705, 200, 52)) {
      startBattle(state.selectedFaction, state.enemyChoice);
    }
    return;
  }

  if (state.winner) {
    if (inside(x, y, W / 2 - 150, H / 2 + 40, 300, 58)) state.screen = 'select';
    return;
  }
  if (state.aiBusy) return;

  if (inside(x, y, 225, 24, 72, 72)) {
    if (state.targetMode) state.targetMode = null;
    else triggerBBS('player');
    return;
  }
  if (inside(x, y, 55, 585, 118, 185)) {
    if (!state.replacedThisTurn && state.pDeck.length > 0) {
      state.replaceMode = !state.replaceMode;
      state.selectedCardIdx = null; state.selectedPos = null; state.targetMode = null;
    }
    return;
  }
  if (inside(x, y, 1135, 585, 115, 115)) { endPlayerTurn(); return; }
  if (inside(x, y, 1135, 710, 115, 60)) { state.screen = 'select'; return; }

  for (let i = 0; i < state.pHand.length; i++) {
    const cx = 195 + i * 155;
    if (inside(x, y, cx, 560, 146, 230)) {
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
      if (card.type === 'artifact' && state.selectedCardIdx === i && card.cost <= state.pMana) {
        state.pMana -= card.cost; state.pHand.splice(i, 1);
        equipArtifact(card, 'player'); state.selectedCardIdx = null;
        return;
      }
      state.selectedCardIdx = state.selectedCardIdx === i ? null : i;
      state.selectedPos = null; state.targetMode = null;
      return;
    }
  }

  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const tx = BOARD_X + c * (TILE_W + GAP);
    const ty = BOARD_Y + r * (TILE_H + GAP);
    if (!inside(x, y, tx, ty, TILE_W, TILE_H)) continue;

    const u = state.board[r][c];

    if (state.targetMode) {
      const tm = state.targetMode;
      if (tm.kind === 'bbs_argeon') {
        const pg = findGeneral('player');
        if (u && u.owner === 'player' && !u.isGeneral && pg && Math.abs(r - pg.r) <= 1 && Math.abs(c - pg.c) <= 1) {
          u.atk += 2; state.pMana -= state.playerFaction.bbsCost; state.pBbsCd = 2;
          spawnFloatText(r, c, '+2 ATK', '#fbbf24'); spawnRing(r, c, '#fbbf24');
          addLog(`👑 [왕의 포효] ${u.name} 공격력 +2!`);
        }
        state.targetMode = null; return;
      }
      if (tm.kind === 'bbs_kaleos_1') {
        if (u && u.owner === 'player' && !u.isGeneral) {
          state.targetMode = { kind: 'bbs_kaleos_2', firstPos: { r, c } };
          addLog('🦊 이동할 빈 칸(2칸 이내)을 클릭하세요!');
        } else state.targetMode = null;
        return;
      }
      if (tm.kind === 'bbs_kaleos_2') {
        const fp = tm.firstPos;
        if (!u && Math.abs(r - fp.r) + Math.abs(c - fp.c) <= 2) {
          state.board[r][c] = state.board[fp.r][fp.c]; state.board[fp.r][fp.c] = null;
          state.pMana -= state.playerFaction.bbsCost; state.pBbsCd = 2;
          spawnRing(r, c, '#f43f5e'); checkOrbPickup(r, c, 'player');
        }
        state.targetMode = null; return;
      }
      if (tm.kind === 'spell_step2') {
        if (!u) {
          const card = state.pHand[tm.cardIdx];
          state.pMana -= card.cost; state.pHand.splice(tm.cardIdx, 1);
          castSpell(card, tm.firstPos.r, tm.firstPos.c, 'player', { r, c });
        }
        state.targetMode = null; state.selectedCardIdx = null; return;
      }
    }

    if (state.selectedCardIdx !== null) {
      const card = state.pHand[state.selectedCardIdx];
      if (card.cost <= state.pMana) {
        if (card.type === 'minion' && getValidSummonTiles('player').some(t => t.r === r && t.c === c)) {
          state.pMana -= card.cost; state.pHand.splice(state.selectedCardIdx, 1);
          summonMinion(card, r, c, 'player'); state.selectedCardIdx = null; return;
        }
        if (card.type === 'artifact') {
          state.pMana -= card.cost; state.pHand.splice(state.selectedCardIdx, 1);
          equipArtifact(card, 'player'); state.selectedCardIdx = null; return;
        }
        if (card.type === 'spell' && getValidSpellTargets(card, 'player').some(t => t.r === r && t.c === c)) {
          if (['mist_seal', 'daemonic_lure'].includes(card.spell)) {
            state.targetMode = { kind: 'spell_step2', cardIdx: state.selectedCardIdx, firstPos: { r, c } };
            addLog('✨ 이동시킬 목적지 빈 칸을 클릭하세요!'); return;
          }
          state.pMana -= card.cost; state.pHand.splice(state.selectedCardIdx, 1);
          castSpell(card, r, c, 'player'); state.selectedCardIdx = null; return;
        }
      }
      state.selectedCardIdx = null;
    }

    if (state.selectedPos) {
      const sp = state.selectedPos;
      if (sp.r === r && sp.c === c) { state.selectedPos = null; return; }
      if (getValidMoves(sp.r, sp.c).some(m => m.r === r && m.c === c)) {
        moveUnit(sp.r, sp.c, r, c); state.selectedPos = { r, c }; return;
      }
      if (getValidAttacks(sp.r, sp.c).some(a => a.r === r && a.c === c)) {
        attackUnit(sp.r, sp.c, r, c); state.selectedPos = null; return;
      }
    }

    if (u && u.owner === 'player') { state.selectedPos = { r, c }; state.selectedCardIdx = null; }
    else state.selectedPos = null;
  }
});

// =========================================================================
// 8. 고퀄리티 렌더링 헬퍼 (32x32 스프라이트, 입체 타일, 카드 아트워크)
// =========================================================================
function roundRect(x, y, w, h, r, fill, stroke, lw = 2) {
  ctx.beginPath(); ctx.roundRect(x, y, w, h, r);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.stroke(); }
}

function drawSprite32(key, cx, cy, size, flipX = false, bob = 0) {
  const img = SPRITES[key] || SPRITES.paladin;
  ctx.save();
  ctx.imageSmoothingEnabled = false;
  ctx.translate(cx, cy + bob);
  if (flipX) ctx.scale(-1, 1);
  ctx.drawImage(img, -size / 2, -size / 2, size, size);
  ctx.restore();
}

function drawCardArt(card, x, y, w, h, bob = 0) {
  ctx.save();
  ctx.beginPath(); ctx.roundRect(x, y, w, h, 4); ctx.clip();

  const grad = ctx.createLinearGradient(x, y, x, y + h);
  if (card.type === 'spell') { grad.addColorStop(0, '#3b0764'); grad.addColorStop(1, '#090d16'); }
  else if (card.type === 'artifact') { grad.addColorStop(0, '#78350f'); grad.addColorStop(1, '#090d16'); }
  else { grad.addColorStop(0, '#0f172a'); grad.addColorStop(1, '#1e293b'); }
  ctx.fillStyle = grad; ctx.fillRect(x, y, w, h);

  const cx = x + w / 2, cy = y + h / 2;
  if (card.type === 'spell') {
    ctx.strokeStyle = 'rgba(232, 121, 249, 0.5)'; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(cx, cy, 24, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = '#38bdf8';
    ctx.beginPath(); ctx.moveTo(cx, cy - 20); ctx.lineTo(cx + 18, cy + 10); ctx.lineTo(cx - 18, cy + 10); ctx.closePath(); ctx.stroke();
    const rg = ctx.createRadialGradient(cx, cy, 2, cx, cy, 20);
    rg.addColorStop(0, '#ffffff'); rg.addColorStop(0.45, '#c084fc'); rg.addColorStop(1, 'rgba(192,132,252,0)');
    ctx.fillStyle = rg; ctx.beginPath(); ctx.arc(cx, cy, 20, 0, Math.PI * 2); ctx.fill();
  } else if (card.type === 'artifact') {
    const rg = ctx.createRadialGradient(cx, cy, 4, cx, cy, 26);
    rg.addColorStop(0, '#fef08a'); rg.addColorStop(0.55, '#f59e0b'); rg.addColorStop(1, 'rgba(245,158,11,0)');
    ctx.fillStyle = rg; ctx.beginPath(); ctx.arc(cx, cy, 26, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#fef08a'; ctx.lineWidth = 2;
    ctx.strokeRect(cx - 14, cy - 14, 28, 28);
  } else {
    ctx.fillStyle = 'rgba(0,0,0,0.55)';
    ctx.beginPath(); ctx.ellipse(cx, y + h - 6, 20, 5, 0, 0, Math.PI * 2); ctx.fill();
    drawSprite32(card.sprite, cx, cy + 2, 54, false, bob);
  }
  ctx.restore();
}

function drawAtmosphereBg() {
  const bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#03060f'); bg.addColorStop(0.5, '#081022'); bg.addColorStop(1, '#03050a');
  ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

  const sun = ctx.createRadialGradient(W / 2, 240, 20, W / 2, 240, 520);
  sun.addColorStop(0, 'rgba(56, 189, 248, 0.14)'); sun.addColorStop(1, 'rgba(3, 6, 15, 0)');
  ctx.fillStyle = sun; ctx.fillRect(0, 0, W, H);

  const pillars = [
    { x: 95, y: 170, w: 48, h: 185, spd: 0.02 },
    { x: 215, y: 115, w: 32, h: 130, spd: 0.03 },
    { x: 1035, y: 120, w: 34, h: 135, spd: 0.025 },
    { x: 1140, y: 180, w: 50, h: 195, spd: 0.018 }
  ];
  pillars.forEach((p, idx) => {
    const py = p.y + Math.sin(state.tick * p.spd + idx) * 8;
    ctx.fillStyle = '#0a1226'; ctx.fillRect(p.x, py, p.w, p.h);
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.25)'; ctx.strokeRect(p.x, py, p.w, p.h);
    ctx.fillStyle = 'rgba(56, 189, 248, 0.45)'; ctx.fillRect(p.x + p.w / 2 - 1, py + 16, 2, p.h - 32);
  });

  for (let i = 0; i < 50; i++) {
    const px = (i * 173 + state.tick * 0.22) % W;
    const py = (H - ((i * 97 + state.tick * 0.45) % H));
    ctx.fillStyle = i % 2 === 0 ? 'rgba(56,189,248,0.45)' : 'rgba(251,191,36,0.35)';
    ctx.fillRect(px, py, 2, 2);
  }
}

// [0] 타이틀 화면
function drawTitleScreen() {
  drawAtmosphereBg();
  const bob = Math.sin(state.tick * 0.05) * 6;

  ctx.save();
  ctx.translate(W / 2, 265);
  ctx.rotate(state.tick * 0.004);
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)'; ctx.lineWidth = 2;
  ctx.strokeRect(-105, -105, 210, 210);
  ctx.rotate(Math.PI / 4);
  ctx.strokeStyle = 'rgba(251, 191, 36, 0.35)';
  ctx.strokeRect(-105, -105, 210, 210);
  ctx.restore();

  drawSprite32('argeon', W / 2 - 230, 275, 144, false, bob);
  drawSprite32('vaath', W / 2 + 230, 275, 144, true, -bob);

  ctx.textAlign = 'center';
  ctx.font = '900 58px "Cinzel", serif'; ctx.fillStyle = '#f8fafc';
  ctx.fillText('DUELYST II', W / 2, 255);

  ctx.font = '700 16px "Press Start 2P", monospace'; ctx.fillStyle = '#38bdf8';
  ctx.fillText('CHRONICLES OF MYTHRON', W / 2, 298);

  ctx.font = '15px "Noto Sans KR"'; ctx.fillStyle = '#94a3b8';
  ctx.fillText('64종 확장 카드 풀 · 동시 반격 & 기습 전투 · 4단계 난이도 · 32x32 도트 전술 배틀', W / 2, 470);

  const pulse = 0.6 + Math.sin(state.tick * 0.08) * 0.4;
  roundRect(W / 2 - 175, 535, 350, 70, 8, '#0284c7', `rgba(56, 189, 248, ${pulse})`, 3);
  ctx.font = '900 22px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText('⚔️ PLAY NOW', W / 2, 578);
}

// [1] 진영 & 9장 카드 프리뷰 & 난이도 선택 화면
function drawSelectScreen() {
  drawAtmosphereBg();
  const keys = Object.keys(FACTIONS);
  const bob = Math.sin(state.tick * 0.07) * 4;

  ctx.textAlign = 'center';
  ctx.font = '900 24px "Cinzel", serif'; ctx.fillStyle = '#f8fafc';
  ctx.fillText('SELECT FACTION, DECK & DIFFICULTY', W / 2, 46);

  keys.forEach((fid, idx) => {
    const f = FACTIONS[fid];
    const cx = 55 + idx * 196;
    const isSel = state.selectedFaction === fid;
    roundRect(cx, 95, 184, 132, 8, isSel ? '#111d38' : '#090e1c', isSel ? f.color : '#1e293b', isSel ? 3 : 1.5);
    drawSprite32(f.sprite, cx + 92, 148, 70, false, isSel ? bob : 0);
    ctx.textAlign = 'center';
    ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = isSel ? f.color : '#cbd5e1';
    ctx.fillText(f.name, cx + 92, 200);
    ctx.font = '11px "Noto Sans KR"'; ctx.fillStyle = '#64748b';
    ctx.fillText(f.title.split(' ')[0], cx + 92, 217);
  });

  const sel = FACTIONS[state.selectedFaction];
  roundRect(55, 242, 1170, 445, 10, 'rgba(9, 14, 28, 0.94)', sel.color, 2);

  // 좌측 장군 프리뷰
  ctx.fillStyle = 'rgba(0,0,0,0.55)';
  ctx.beginPath(); ctx.ellipse(165, 415, 52, 14, 0, 0, Math.PI * 2); ctx.fill();
  drawSprite32(sel.sprite, 165, 350, 128, false, bob);

  ctx.textAlign = 'center';
  ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = sel.color;
  ctx.fillText(sel.title, 165, 446);
  ctx.font = '900 19px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText(sel.name, 165, 472);

  roundRect(72, 492, 186, 175, 6, '#050811', '#1e293b', 1.5);
  ctx.textAlign = 'left';
  ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = '#38bdf8';
  ctx.fillText(`⭐ ${sel.bbsName}`, 82, 514);
  ctx.font = '11px "Noto Sans KR"'; ctx.fillStyle = '#e2e8f0';
  ctx.fillText(sel.bbsDesc.slice(0, 16), 82, 535);
  ctx.fillText(sel.bbsDesc.slice(16, 32), 82, 552);
  ctx.fillStyle = '#fbbf24';
  ctx.fillText(`• 30장 덱 (진영 18 + 중립 12)`, 82, 582);
  ctx.fillText(`• 동시 반격 & 기습 적용`, 82, 600);
  ctx.fillStyle = '#94a3b8';
  ctx.fillText(DIFFICULTIES[state.difficultyIdx].desc.slice(0, 16), 82, 628);
  ctx.fillText(DIFFICULTIES[state.difficultyIdx].desc.slice(16, 32), 82, 645);

  // 우측 전용 카드 9장 (5 + 4 2줄 전시)
  ctx.font = '900 14px "Noto Sans KR"'; ctx.fillStyle = '#fbbf24';
  ctx.fillText(`🃏 [${sel.title}] 전용 덱 카드 9종 (하수인 · 스펠 · 아티팩트)`, 280, 272);

  sel.cards.forEach((c, idx) => {
    const col = idx % 5;
    const row = Math.floor(idx / 5);
    const kx = 280 + col * 186;
    const ky = 285 + row * 195;
    const bCol = c.type === 'spell' ? '#c084fc' : (c.type === 'artifact' ? '#f59e0b' : '#38bdf8');
    roundRect(kx, ky, 176, 184, 6, '#0c1324', bCol, 1.5);

    ctx.fillStyle = '#0284c7';
    ctx.beginPath(); ctx.arc(kx + 16, ky + 16, 11, 0, Math.PI * 2); ctx.fill();
    ctx.textAlign = 'center';
    ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
    ctx.fillText(c.cost, kx + 16, ky + 20);

    ctx.textAlign = 'left';
    ctx.font = '900 12.5px "Noto Sans KR"'; ctx.fillStyle = '#f8fafc';
    ctx.fillText(c.name, kx + 32, ky + 20);

    if (c.type === 'minion') {
      drawSprite32(c.sprite, kx + 34, ky + 62, 46, false, 0);
      ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = '#fbbf24';
      ctx.fillText(`⚔️ ${c.atk}   ❤️ ${c.hp}`, kx + 66, ky + 58);
      ctx.font = '10.5px "Noto Sans KR"'; ctx.fillStyle = '#38bdf8';
      ctx.fillText(c.keywords.length ? c.keywords[0].toUpperCase() : 'MINION', kx + 66, ky + 76);
    } else {
      ctx.font = 'bold 12px "Noto Sans KR"';
      ctx.fillStyle = c.type === 'spell' ? '#e879f9' : '#fbbf24';
      ctx.fillText(c.type === 'spell' ? '🔮 SPELL (주문)' : `🛡️ ARTIFACT (+${c.atkBonus} ATK)`, kx + 14, ky + 56);
    }

    ctx.font = '10.5px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
    for (let line = 0; line < 4; line++) {
      ctx.fillText(c.desc.slice(line * 16, (line + 1) * 16), kx + 12, ky + 102 + line * 17);
    }
  });

  // 하단 난이도 4단계 버튼 + 상대 AI + 전투 시작
  DIFFICULTIES.forEach((d, idx) => {
    const dx = 55 + idx * 175;
    const isD = state.difficultyIdx === idx;
    roundRect(dx, 705, 165, 52, 8, isD ? '#172554' : '#0f172a', isD ? d.color : '#334155', isD ? 2.5 : 1.5);
    ctx.textAlign = 'center';
    ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = isD ? d.color : '#94a3b8';
    ctx.fillText(d.name, dx + 82, 736);
  });

  const eLabel = state.enemyChoice === 'random' ? '🎲 상대 AI: 랜덤' : `🤖 AI: ${FACTIONS[state.enemyChoice].name.split(' ')[0]}`;
  roundRect(785, 705, 225, 52, 8, '#0f172a', '#475569', 2);
  ctx.textAlign = 'center';
  ctx.font = 'bold 14px "Noto Sans KR"'; ctx.fillStyle = '#e2e8f0';
  ctx.fillText(eLabel, 897, 736);

  roundRect(1025, 705, 200, 52, 8, '#0284c7', '#38bdf8', 2);
  ctx.font = '900 17px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText('⚔️ 전투 시작', 1125, 736);
}

// [2] 전투 화면
function drawBattleScreen() {
  ctx.save();
  if (state.shake > 0) {
    const sx = (Math.random() - 0.5) * state.shake * 2;
    const sy = (Math.random() - 0.5) * state.shake * 2;
    ctx.translate(sx, sy);
    state.shake *= 0.82;
    if (state.shake < 0.4) state.shake = 0;
  }

  drawAtmosphereBg();

  const pf = state.playerFaction;
  const ef = state.enemyFaction;
  const diff = DIFFICULTIES[state.difficultyIdx];
  const pg = findGeneral('player');
  const eg = findGeneral('enemy');
  const pHp = pg ? pg.unit.hp : 0;
  const eHp = eg ? eg.unit.hp : 0;
  const bob = Math.sin(state.tick * 0.08) * 2.5;

  // 좌측 플레이어 장군 HUD
  roundRect(55, 16, 158, 96, 8, '#0b1224', pf.color, 2);
  drawSprite32(pf.sprite, 102, 60, 72, false, 0);
  ctx.textAlign = 'center';
  ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = pf.color;
  ctx.fillText(pf.name.split(' ')[0], 102, 104);
  ctx.fillStyle = '#be123c';
  ctx.beginPath(); ctx.arc(176, 48, 22, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = '#fda4af'; ctx.lineWidth = 2; ctx.stroke();
  ctx.font = '900 16px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText(pHp, 176, 54);
  roundRect(156, 78, 40, 22, 4, '#ca8a04', '#fef08a', 1.5);
  ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText(`⚔️${pg ? pg.unit.atk : 0}`, 176, 94);

  // BBS 스킬 원형 슬롯
  const bbsReady = state.pBbsCd === 0 && state.pMana >= pf.bbsCost;
  ctx.fillStyle = bbsReady ? '#172554' : '#0f172a';
  ctx.beginPath(); ctx.arc(261, 60, 34, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = state.targetMode ? '#fbbf24' : (bbsReady ? '#38bdf8' : '#334155');
  ctx.lineWidth = 3; ctx.stroke();
  ctx.font = '900 11px "Noto Sans KR"';
  ctx.fillStyle = bbsReady ? '#38bdf8' : '#64748b';
  ctx.fillText('BBS 스킬', 261, 56);
  ctx.fillText(state.pBbsCd === 0 ? `${pf.bbsCost}마나` : `${state.pBbsCd}턴대기`, 261, 73);

  // 마나 크리스탈 & 아티팩트
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

  state.pArtifacts.forEach((a, idx) => {
    roundRect(310 + idx * 118, 56, 112, 38, 5, '#451a03', '#f59e0b', 1.5);
    ctx.font = 'bold 10.5px "Noto Sans KR"'; ctx.fillStyle = '#fef08a';
    ctx.fillText(a.name.slice(0, 7), 316 + idx * 118, 72);
    ctx.fillStyle = '#fbbf24';
    ctx.fillText(`내구도: ${'◆'.repeat(a.dur)}`, 316 + idx * 118, 87);
  });

  // 상단 중앙: 턴 & 난이도 배지
  ctx.textAlign = 'center';
  ctx.font = '900 16px "Cinzel", serif'; ctx.fillStyle = '#f8fafc';
  ctx.fillText(`TURN ${state.turn}`, W / 2 + 45, 38);
  ctx.font = 'bold 11.5px "Noto Sans KR"'; ctx.fillStyle = diff.color;
  ctx.fillText(`[${diff.name}]`, W / 2 + 45, 57);
  ctx.font = '11.5px "Noto Sans KR"'; ctx.fillStyle = state.aiBusy ? '#f43f5e' : '#38bdf8';
  ctx.fillText(state.aiBusy ? '적 AI 작전 수행 중...' : '동시 반격 & 기습 활성', W / 2 + 45, 76);

  // 우측 적 장군 HUD
  roundRect(1067, 16, 158, 96, 8, '#0b1224', ef.color, 2);
  drawSprite32(ef.sprite, 1178, 60, 72, true, 0);
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

  // 중앙 5x9 전술 보드
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

      // 3D 베벨 타일
      ctx.fillStyle = '#03050c';
      ctx.fillRect(tx, ty + 5, TILE_W, TILE_H);

      let fill = (r + c) % 2 === 0 ? 'rgba(15, 23, 42, 0.9)' : 'rgba(21, 32, 58, 0.9)';
      let stroke = '#1e293b';
      let lw = 1.5;

      if (isMove) { fill = 'rgba(14, 116, 144, 0.58)'; stroke = '#38bdf8'; lw = 2.5; }
      if (isSum) { fill = 'rgba(6, 95, 70, 0.62)'; stroke = '#10b981'; lw = 2.5; }
      if (isAtk || isSpl) { fill = 'rgba(159, 18, 57, 0.68)'; stroke = '#f43f5e'; lw = 2.5; }
      if (isSel) { fill = 'rgba(30, 58, 138, 0.78)'; stroke = '#fbbf24'; lw = 3; }
      if (isHov) { stroke = '#f8fafc'; lw = 2.5; }

      roundRect(tx, ty, TILE_W, TILE_H, 5, fill, stroke, lw);
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.08)';
      ctx.strokeRect(tx + 7, ty + 7, TILE_W - 14, TILE_H - 14);

      if (state.manaOrbs.some(o => o.r === r && o.c === c)) {
        const pulse = Math.sin(state.tick * 0.1) * 3;
        const mg = ctx.createRadialGradient(tx + TILE_W / 2, ty + TILE_H / 2, 2, tx + TILE_W / 2, ty + TILE_H / 2, 22 + pulse);
        mg.addColorStop(0, '#ffffff'); mg.addColorStop(0.45, '#38bdf8'); mg.addColorStop(1, 'rgba(56,189,248,0)');
        ctx.fillStyle = mg;
        ctx.beginPath(); ctx.arc(tx + TILE_W / 2, ty + TILE_H / 2, 22 + pulse, 0, Math.PI * 2); ctx.fill();
      }

      const u = state.board[r][c];
      if (u) {
        const cx = tx + TILE_W / 2;
        const cy = ty + TILE_H / 2 - 8;

        ctx.fillStyle = 'rgba(0,0,0,0.6)';
        ctx.beginPath(); ctx.ellipse(cx, ty + TILE_H - 14, 24, 7, 0, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = u.owner === 'player' ? '#38bdf8' : '#f43f5e';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.ellipse(cx, ty + TILE_H - 14, 24, 7, 0, 0, Math.PI * 2); ctx.stroke();

        // 상단 키워드 & 기습(Backstab) 표기
        ctx.textAlign = 'center';
        ctx.font = 'bold 10px "Noto Sans KR"';
        const isBsTarget = isAtk && state.selectedPos && isBackstabPosition(state.board[state.selectedPos.r][state.selectedPos.c], state.selectedPos.r, state.selectedPos.c, r, c);
        if (isBsTarget) { ctx.fillStyle = '#f43f5e'; ctx.fillText('🗡️기습(+2)', cx, ty + 13); }
        else if (u.stunned) { ctx.fillStyle = '#38bdf8'; ctx.fillText('❄️기절', cx, ty + 13); }
        else if (u.keywords.includes('provoke')) { ctx.fillStyle = '#fbbf24'; ctx.fillText('🛡️도발', cx, ty + 13); }
        else if (u.keywords.includes('ranged')) { ctx.fillStyle = '#38bdf8'; ctx.fillText('🏹원거리', cx, ty + 13); }
        else if (u.keywords.includes('frenzy')) { ctx.fillStyle = '#10b981'; ctx.fillText('💥광란', cx, ty + 13); }
        else if (u.keywords.includes('backstab')) { ctx.fillStyle = '#f43f5e'; ctx.fillText('🗡️기습', cx, ty + 13); }

        drawSprite32(u.sprite, cx, cy, u.isGeneral ? 68 : 58, u.owner === 'enemy', bob);

        roundRect(tx + 6, ty + TILE_H - 22, 25, 18, 4, '#ca8a04', '#fef08a', 1);
        ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
        ctx.fillText(u.atk, tx + 18, ty + TILE_H - 9);

        roundRect(tx + TILE_W - 31, ty + TILE_H - 22, 25, 18, 4, '#be123c', '#fda4af', 1);
        ctx.fillText(u.hp, tx + TILE_W - 18, ty + TILE_H - 9);
      }
    }
  }

  // 우측 전술 기록 & 동시 반격 교전 미리보기 창
  roundRect(940, 128, 285, 406, 8, 'rgba(9, 14, 28, 0.92)', '#1e293b', 2);
  ctx.textAlign = 'left';
  ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = '#38bdf8';
  ctx.fillText(`📜 전투 로그 (남은 덱: ${state.pDeck.length}장)`, 954, 152);
  ctx.font = '11.5px "Noto Sans KR"';
  state.logs.slice(0, 10).forEach((l, i) => {
    ctx.fillStyle = i === 0 ? '#f8fafc' : '#94a3b8';
    ctx.fillText(l.slice(0, 27), 954, 174 + i * 19);
  });

  if (state.hoverTile) {
    const hu = state.board[state.hoverTile.r][state.hoverTile.c];
    if (hu) {
      roundRect(952, 382, 261, 140, 6, '#050811', hu.owner === 'player' ? '#38bdf8' : '#f43f5e', 1.5);
      drawSprite32(hu.sprite, 992, 434, 62, hu.owner === 'enemy', 0);
      ctx.font = '900 14px "Noto Sans KR"'; ctx.fillStyle = '#f8fafc';
      ctx.fillText(hu.name, 1030, 408);
      ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = '#fbbf24';
      ctx.fillText(`공격력 ${hu.atk}  |  체력 ${hu.hp}/${hu.maxHp}`, 1030, 428);
      ctx.font = '11px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
      ctx.fillText(`특성: ${hu.keywords.length ? hu.keywords.join(', ').toUpperCase() : '기본'}`, 1030, 448);

      // 선택된 내 유닛으로 공격 가능할 때 동시 반격 피해 미리보기 표시!
      if (state.selectedPos && hu.owner === 'enemy' && attacks.some(a => a.r === state.hoverTile.r && a.c === state.hoverTile.c)) {
        const myU = state.board[state.selectedPos.r][state.selectedPos.c];
        const bs = isBackstabPosition(myU, state.selectedPos.r, state.selectedPos.c, state.hoverTile.r, state.hoverTile.c);
        const ranged = myU.keywords.includes('ranged');
        const myDmg = myU.atk + (bs ? 2 : 0);
        const counterDmg = (ranged || bs) ? 0 : hu.atk;
        ctx.fillStyle = '#f43f5e';
        ctx.font = 'bold 11.5px "Noto Sans KR"';
        ctx.fillText(`⚔️ 예상 교전: 적 -${myDmg} / 나 -${counterDmg}`, 962, 508);
      } else {
        ctx.fillStyle = '#38bdf8';
        ctx.fillText(hu.stunned ? '상태: 기절 (행동 불가)' : (hu.canAttack ? '상태: 행동 가능' : '상태: 행동 완료'), 1030, 468);
      }
    }
  }

  // 하단 REPLACE + 손패 6장 + END TURN
  const canRep = !state.replacedThisTurn && state.pDeck.length > 0;
  roundRect(55, 585, 118, 185, 10, state.replaceMode ? '#78350f' : '#0b1224', state.replaceMode ? '#fbbf24' : (canRep ? '#38bdf8' : '#1e293b'), 2);
  ctx.textAlign = 'center';
  ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = canRep ? '#38bdf8' : '#475569';
  ctx.fillText('REPLACE', 114, 655);
  ctx.font = '11px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
  ctx.fillText(state.replaceMode ? '교체할 카드 클릭' : (canRep ? '카드 교체 (1회)' : '교체 완료'), 114, 680);

  for (let i = 0; i < state.pHand.length; i++) {
    const c = state.pHand[i];
    const isSel = state.selectedCardIdx === i;
    const isHov = state.hoverCardIdx === i;
    const cx = 195 + i * 155;
    const cy = 560 - (isSel || isHov ? 22 : 0);
    const ok = c.cost <= state.pMana;
    const borderCol = isSel ? '#fbbf24' : (ok ? (c.type === 'spell' ? '#c084fc' : (c.type === 'artifact' ? '#f59e0b' : '#38bdf8')) : '#334155');

    roundRect(cx, cy, 146, 230, 8, isSel ? '#172554' : '#0b1224', borderCol, isSel ? 3 : 2);
    drawCardArt(c, cx + 8, cy + 32, 130, 82, isHov ? bob : 0);

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

  roundRect(1135, 585, 115, 115, 10, state.aiBusy ? '#1e293b' : '#0284c7', '#38bdf8', 2.5);
  ctx.textAlign = 'center';
  ctx.font = '900 16px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText('END', 1192, 636);
  ctx.fillText('TURN', 1192, 658);

  roundRect(1135, 710, 115, 60, 8, '#0f172a', '#475569', 1.5);
  ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
  ctx.fillText('🔙 진영/난이도', 1192, 744);

  // 이펙트 레이어
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
      ctx.strokeStyle = '#000000'; ctx.lineWidth = 3;
      ctx.strokeText(efObj.text, efObj.x, efObj.y);
      ctx.fillStyle = efObj.color;
      ctx.fillText(efObj.text, efObj.x, efObj.y);
    } else if (efObj.type === 'beam') {
      ctx.strokeStyle = efObj.color; ctx.lineWidth = 5 * alpha;
      ctx.beginPath(); ctx.moveTo(efObj.x, efObj.y); ctx.lineTo(efObj.x2, efObj.y2); ctx.stroke();
    } else if (efObj.type === 'slash') {
      ctx.strokeStyle = efObj.color; ctx.lineWidth = 4 * alpha;
      ctx.beginPath();
      ctx.moveTo(efObj.x - 24, efObj.y - 24); ctx.lineTo(efObj.x + 24, efObj.y + 24);
      ctx.moveTo(efObj.x + 24, efObj.y - 24); ctx.lineTo(efObj.x - 24, efObj.y + 24);
      ctx.stroke();
    } else if (efObj.type === 'ring') {
      ctx.strokeStyle = efObj.color; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(efObj.x, efObj.y, 12 + efObj.t * 1.4, 0, Math.PI * 2); ctx.stroke();
    } else if (efObj.type === 'particle') {
      efObj.x += efObj.vx; efObj.y += efObj.vy;
      ctx.fillStyle = efObj.color; ctx.fillRect(efObj.x - 2, efObj.y - 2, 4, 4);
    }
    ctx.restore();
  }

  ctx.restore();

  if (state.winner) {
    ctx.fillStyle = 'rgba(3, 5, 10, 0.85)';
    ctx.fillRect(0, 0, W, H);
    ctx.textAlign = 'center';
    ctx.font = '900 46px "Cinzel", serif';
    ctx.fillStyle = state.winner === 'PLAYER' ? '#38bdf8' : '#f43f5e';
    ctx.fillText(state.winner === 'PLAYER' ? 'VICTORY' : 'DEFEAT', W / 2, H / 2 - 20);

    roundRect(W / 2 - 150, H / 2 + 40, 300, 58, 8, '#0284c7', '#38bdf8', 2);
    ctx.font = '900 18px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
    ctx.fillText('🔄 진영 / 난이도 선택으로', W / 2, H / 2 + 75);
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

components.html(GAME_HTML, height=830, scrolling=False)
