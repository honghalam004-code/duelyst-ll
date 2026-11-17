import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DUEL GRID // 2D Tactical Pixel Card Battler",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Streamlit 기본 여백 제거 (전체 게임 화면처럼 표시)
st.markdown(
    """
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }
    .stApp {
        background-color: #05070d;
    }
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
  @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Noto+Sans+KR:wght@400;700;900&display=swap');
  * { box-sizing: border-box; user-select: none; }
  body {
    margin: 0;
    padding: 0;
    background: #05070d;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Noto Sans KR', sans-serif;
    overflow: hidden;
  }
  canvas {
    background: #070a12;
    border: 2px solid #1e293b;
    border-radius: 6px;
    box-shadow: 0 0 35px rgba(0, 0, 0, 0.9);
    image-rendering: pixelated;
    max-width: 100vw;
    max-height: 98vh;
  }
</style>
</head>
<body>
<canvas id="game" width="1240" height="780"></canvas>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const W = canvas.width;
const H = canvas.height;

// =========================================================
// 1. 16x16 도트 스프라이트 생성 엔진 (외부 이미지 없이 고퀄 도트 렌더링)
// =========================================================
function makeSprite(palette, rows) {
  const off = document.createElement('canvas');
  off.width = 16;
  off.height = 16;
  const octx = off.getContext('2d');
  for (let y = 0; y < 16; y++) {
    const row = (rows[y] || '').padEnd(16, '.').slice(0, 16);
    for (let x = 0; x < 16; x++) {
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
  // 공통
  K: '#0b0f19', W: '#f8fafc', S: '#fde68a', E: '#38bdf8', R: '#ef4444',
  // 라이오나르 (금빛 성기사)
  G: '#fbbf24', Y: '#fef08a', B: '#2563eb', L: '#93c5fd',
  // 송하이 (붉은 닌자)
  C: '#e11d48', P: '#9f1239', D: '#1e293b',
  // 베트루비안 (사막 황금/청록)
  T: '#14b8a6', O: '#d97706',
  // 어비시안 (보라/심연)
  V: '#a855f7', M: '#581c87', N: '#f472b6',
  // 마그마르 (에메랄드/용족)
  A: '#10b981', Z: '#065f46', H: '#f97316',
  // 바나르 (얼음/서리)
  I: '#38bdf8', U: '#e0f2fe', F: '#0284c7'
};

const SPRITES = {
  // 6대 진영 장군 스프라이트
  argeon: makeSprite(PAL, [
    '.....YYYY.......',
    '....YGGGGY......',
    '....GWWWWG..Y...',
    '....GWEEWG..G...',
    '.....GGGG...G...',
    '...BBGGGGGB.G...',
    '..BGGGGGGGGBG...',
    '..BGGYYYYGGGB...',
    '..BGGGGGGGGGY...',
    '...BGGGGGGGB....',
    '....BBBBBBB.....',
    '....GG...GG.....',
    '....GG...GG.....',
    '...GGG...GGG....',
    '................',
    '................'
  ]),
  kaleos: makeSprite(PAL, [
    '.....CCCC.......',
    '....CCCCCC......',
    '...CCSSSSCC.....',
    '...CCRRRRCC.....',
    '....CCCCCC......',
    '..PPDDDDDDPP.W..',
    '.PPDDDDDDDDPW...',
    '.PDDCCCCCCDW....',
    '..PDDDDDDDW.....',
    '...DDDDDDD......',
    '....PP.PP.......',
    '...PP...PP......',
    '..PP.....PP.....',
    '................',
    '................',
    '................'
  ]),
  zirix: makeSprite(PAL, [
    '....G....G......',
    '....GG..GG......',
    '....GGGGGG......',
    '....GTTTTG......',
    '.....GGGG.......',
    '...OOGGGGOO..T..',
    '..OOGTTTTGOO.T..',
    '..OGGGGGGGGO.G..',
    '...OOGGGGOO..G..',
    '....TTTTTT......',
    '....OO..OO......',
    '...OO....OO.....',
    '..GG......GG....',
    '................',
    '................',
    '................'
  ]),
  lilithe: makeSprite(PAL, [
    '...V......V.....',
    '....VV..VV......',
    '....VVVVVV......',
    '....VNNNNV......',
    '.....VVVV.......',
    '..MMVVVVVVMM.N..',
    '.MMVVMMMMVVMMV..',
    '.MVVVVVVVVVVM...',
    '..MMVVVVVVMM....',
    '...MMMMMMMM.....',
    '....VV..VV......',
    '...VV....VV.....',
    '................',
    '................',
    '................',
    '................'
  ]),
  vaath: makeSprite(PAL, [
    '..HH......HH....',
    '...HHAAAAHH.....',
    '...AAAAAAAA.....',
    '...AARRRRAA.....',
    '....AAAAAA......',
    '.ZZAAAAAAAAZZ.H.',
    'ZZAAHHHHHHAAZZH.',
    'ZAAAAAAAAAAAAZH.',
    '.ZZAAAAAAAAZZ...',
    '..ZZAAAAAAZZ....',
    '...AA....AA.....',
    '..ZZZ....ZZZ....',
    '................',
    '................',
    '................',
    '................'
  ]),
  faie: makeSprite(PAL, [
    '.....UUUU.......',
    '....UIIIIU......',
    '....ISSSSI..U...',
    '....ISEESI..I...',
    '.....IIII...I...',
    '..FFIIIIIIFFI...',
    '.FFIIUUUUIIFF...',
    '.FIIIIIIIIIF....',
    '..FFIIIIIIFF....',
    '...FFFFFFFF.....',
    '....II..II......',
    '...UU....UU.....',
    '................',
    '................',
    '................',
    '................'
  ]),

  // 공용 & 진영 하수인 스프라이트
  knight: makeSprite(PAL, [
    '.....LLLL.......',
    '....LLLLLL......',
    '....LKKKKL......',
    '.....LLLL...W...',
    '..BBLLLLLLB.W...',
    '.BBLLLLLLLLBW...',
    '.BBLLGGGGLLBL...',
    '..BBLLLLLLB.....',
    '....BB..BB......',
    '...LL....LL.....',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................'
  ]),
  shield: makeSprite(PAL, [
    '....GGGGGG......',
    '...GGGGGGGG.....',
    '...GGWWWWGG.....',
    '..GGGGGGGGGG....',
    '..GGGBBBBGGG....',
    '..GGGBBBBGGG....',
    '..GGGGGGGGGG....',
    '...GGGGGGGG.....',
    '....GGGGGG......',
    '.....GGGG.......',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................'
  ]),
  archer: makeSprite(PAL, [
    '.....AAAA.......',
    '....AAAAAA......',
    '....ASSSSA...O..',
    '.....AAAA...O.W.',
    '...ZZAAAAZZO..W.',
    '..ZZAAAAAAO...W.',
    '...ZZAAAAZZO.W..',
    '....ZZ..ZZ..O...',
    '...AA....AA.....',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................'
  ]),
  assassin: makeSprite(PAL, [
    '.....DDDD.......',
    '....DDDDDD......',
    '....DRRRRD......',
    '.....DDDD.......',
    '..PPDDDDDDPP.W..',
    '.PPDDDDDDDDPW...',
    '..PPDDDDDDPP....',
    '....PP..PP......',
    '...DD....DD.....',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................'
  ]),
  wraith: makeSprite(PAL, [
    '.....VVVV.......',
    '....VVVVVV......',
    '...VVNNNNVV.....',
    '...VVVVVVVV.....',
    '..MMVVVVVVMM....',
    '.MMVVVVVVVVMM...',
    '..VVVVVVVVVV....',
    '...VV.VV.VV.....',
    '....V..V..V.....',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................'
  ]),
  dervish: makeSprite(PAL, [
    '.....TTTT.......',
    '....TTTTTT......',
    '...TTYYYYTT.....',
    '....TTTTTT..G...',
    '..OOTTTTTTOOG...',
    '.OOTTTTTTTTO....',
    '...TTTTTTTT.....',
    '....TTTTTT......',
    '.....TTTT.......',
    '......TT........',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................'
  ]),
  beast: makeSprite(PAL, [
    '..HH......HH....',
    '...HHHHHHHH.....',
    '..HHRRRRRRHH....',
    '.HHHHHHHHHHHH...',
    '.HHHHAAAAHHHH...',
    '.HHHHHHHHHHHH...',
    '..HH..HH..HH....',
    '.ZZZ..ZZ..ZZZ...',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................'
  ]),
  wolf: makeSprite(PAL, [
    '..UU......UU....',
    '...UUUUUUUU.....',
    '..UUIIIIIIUU....',
    '.UUUUUUUUUUUU...',
    '.UUFFFFFFFFUU...',
    '..UU..UU..UU....',
    '.II...II...II...',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................'
  ]),
  golem: makeSprite(PAL, [
    '....DDDDDD......',
    '...DDDDDDDD.....',
    '...DDIIIIDD.....',
    '..DDDDDDDDDD....',
    '.DDDDDDDDDDDD...',
    '.DDDDIIIIDDDD...',
    '.DDDDDDDDDDDD...',
    '..DDDD..DDDD....',
    '.DDDDD..DDDDD...',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................'
  ])
};

// =========================================================
// 2. 듀얼리스트 2 오리지널 6개 진영 & 카드 풀
// =========================================================
const FACTIONS = {
  argeon: {
    id: 'argeon', name: '아르게온 하이메이', faction: '라이오나르 왕국',
    color: '#fbbf24', sprite: 'argeon',
    bbsName: '왕의 포효', bbsCost: 1,
    bbsDesc: '아군 장군 주변 아군 1기에게 공격력 +2 영구 부여',
    style: '단단한 도발 기사와 아군 강화 마법으로 전선을 압도하는 빛의 기사단',
    cards: [
      { name: '은빛 방패기사', type: 'minion', cost: 2, atk: 1, hp: 4, sprite: 'shield', keywords: ['provoke'], desc: '도발: 인접 적의 이동 및 원거리 공격 봉쇄' },
      { name: '태양의 돌격병', type: 'minion', cost: 3, atk: 3, hp: 3, sprite: 'knight', keywords: ['rush'], desc: '돌진: 소환된 턴에 즉시 이동 및 공격' },
      { name: '신성한 축복', type: 'spell', cost: 2, sprite: 'argeon', spell: 'divine_bond', desc: '아군 1기 공격력 +2 및 체력 +3 회복' }
    ]
  },
  kaleos: {
    id: 'kaleos', name: '칼레오스 잔', faction: '송하이 제국',
    color: '#f43f5e', sprite: 'kaleos',
    bbsName: '점멸 (Blink)', bbsCost: 1,
    bbsDesc: '아군 하수인 1기를 최대 2칸 떨어진 빈 칸으로 순간이동',
    style: '순간이동과 원거리 암살, 직격 주문으로 적 장군을 노리는 암살단',
    cards: [
      { name: '카게 번개사수', type: 'minion', cost: 2, atk: 2, hp: 2, sprite: 'archer', keywords: ['ranged'], desc: '원거리: 맵 어디서든 반격 없이 공격' },
      { name: '붉은 달 암살자', type: 'minion', cost: 3, atk: 4, hp: 2, sprite: 'assassin', keywords: ['rush'], desc: '돌진: 기습에 특화된 고화력 암살자' },
      { name: '불사조의 불꽃', type: 'spell', cost: 2, sprite: 'kaleos', spell: 'phoenix_fire', desc: '대상 적에게 3 피해 & 카드 1장 드로우' }
    ]
  },
  zirix: {
    id: 'zirix', name: '지릭스 스타스트라이더', faction: '베트루비안 제국',
    color: '#14b8a6', sprite: 'zirix',
    bbsName: '바람의 소환', bbsCost: 1,
    bbsDesc: '장군 주변 빈 칸에 2/2 돌진 바람의 데르비시 소환',
    style: '돌진 데르비시와 사막의 강화 주문으로 몰아치는 고대 사막 제국',
    cards: [
      { name: '사막의 수호석상', type: 'minion', cost: 3, atk: 2, hp: 5, sprite: 'golem', keywords: ['provoke'], desc: '도발: 높은 체력으로 중앙 마나 샘을 장악' },
      { name: '모래폭풍 정령', type: 'minion', cost: 3, atk: 3, hp: 2, sprite: 'dervish', keywords: ['rush'], desc: '돌진: 소환 즉시 적진을 파고드는 정령' },
      { name: '자손의 축복', type: 'spell', cost: 2, sprite: 'zirix', spell: 'scions_wish', desc: '아군 하수인 1기에게 공격력 +2 / 체력 +2' }
    ]
  },
  lilithe: {
    id: 'lilithe', name: '리리스 블라이트체이서', faction: '어비시안 군단',
    color: '#c084fc', sprite: 'lilithe',
    bbsName: '망령의 부름', bbsCost: 1,
    bbsDesc: '장군 주변 빈 칸에 1/1 돌진 심연의 망령 2기 소환',
    style: '끝없이 쏟아지는 망령 물량과 생명력 흡수로 적을 고사시키는 심연 군단',
    cards: [
      { name: '어둠의 추적자', type: 'minion', cost: 3, atk: 3, hp: 3, sprite: 'wraith', keywords: ['rush'], desc: '돌진: 어둠 속에서 튀어나오는 기습 병력' },
      { name: '심연의 거신', type: 'minion', cost: 5, atk: 6, hp: 5, sprite: 'golem', keywords: ['provoke'], desc: '도발: 압도적인 능력치의 심연 수호자' },
      { name: '영혼 착취', type: 'spell', cost: 2, sprite: 'lilithe', spell: 'void_pulse', desc: '적에게 2 피해 & 아군 장군 체력 +3 회복' }
    ]
  },
  vaath: {
    id: 'vaath', name: '바스 디 이모탈', faction: '마그마르 위상',
    color: '#10b981', sprite: 'vaath',
    bbsName: '과부하 (Overload)', bbsCost: 1,
    bbsDesc: '아군 장군의 공격력이 영구적으로 +1 증가',
    style: '장군 스스로 괴물이 되어 광란의 야수들과 전장을 부수는 용족 군단',
    cards: [
      { name: '태고의 야수', type: 'minion', cost: 3, atk: 3, hp: 4, sprite: 'beast', keywords: ['frenzy'], desc: '광란: 공격 시 인접한 모든 적을 동시 타격' },
      { name: '용암 돌격수', type: 'minion', cost: 4, atk: 4, hp: 4, sprite: 'beast', keywords: ['rush'], desc: '돌진: 전장을 휩쓰는 흉포한 돌격 야수' },
      { name: '자연의 분노', type: 'spell', cost: 3, sprite: 'vaath', spell: 'natural_select', desc: '적 하수인 1기를 즉시 처치' }
    ]
  },
  faie: {
    id: 'faie', name: '페이 블러드윙', faction: '바나르 혈족',
    color: '#38bdf8', sprite: 'faie',
    bbsName: '전쟁의 새 (Warbird)', bbsCost: 1,
    bbsDesc: '적 장군과 같은 세로줄(열)의 모든 적에게 2 피해',
    style: '광역 냉기 피해와 서리 늑대로 적의 진형을 얼려버리는 북방 결사대',
    cards: [
      { name: '서리 송곳니 늑대', type: 'minion', cost: 2, atk: 3, hp: 2, sprite: 'wolf', keywords: ['rush'], desc: '돌진: 날렵한 빙원의 사냥꾼' },
      { name: '빙하의 파수꾼', type: 'minion', cost: 4, atk: 3, hp: 6, sprite: 'golem', keywords: ['provoke'], desc: '도발: 뚫기 힘든 얼음 성벽' },
      { name: '혹한의 파동', type: 'spell', cost: 3, sprite: 'faie', spell: 'chromatic_cold', desc: '적 하수인에게 4 피해 & 적 장군에게 1 피해' }
    ]
  }
};

const NEUTRAL_CARDS = [
  { name: '전장의 척후병', type: 'minion', cost: 1, atk: 2, hp: 1, sprite: 'knight', keywords: ['rush'], desc: '돌진: 초반 마나 샘 선점에 유리' },
  { name: '치유의 신비술사', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'archer', keywords: [], desc: '균형 잡힌 능력치의 2코스트 전사' },
  { name: '바위 수호자', type: 'minion', cost: 2, atk: 1, hp: 4, sprite: 'shield', keywords: ['provoke'], desc: '도발: 인접 적의 움직임을 묶어둠' },
  { name: '비전 명사수', type: 'minion', cost: 3, atk: 2, hp: 3, sprite: 'archer', keywords: ['ranged'], desc: '원거리: 먼 거리에서 안전하게 저격' },
  { name: '검투사 챔피언', type: 'minion', cost: 4, atk: 4, hp: 5, sprite: 'knight', keywords: ['frenzy'], desc: '광란: 주변 모든 적을 동시에 베어버림' },
  { name: '화염 폭풍', type: 'spell', cost: 2, sprite: 'kaleos', spell: 'fireball', desc: '대상 적에게 3 피해' }
];

// =========================================================
// 3. 게임 상태 & 보드 상수
// =========================================================
const ROWS = 5, COLS = 9;
const BOARD_X = 55, BOARD_Y = 110, TILE_W = 88, TILE_H = 74, GAP = 4;

let state = {
  screen: 'select', // 'select' | 'battle'
  selectedFaction: 'argeon',
  enemyChoice: 'random',
  playerFaction: null,
  enemyFaction: null,
  board: [],
  manaOrbs: [],
  turn: 1,
  pMana: 2, pMaxMana: 2,
  eMana: 2, eMaxMana: 2,
  pDeck: [], pHand: [],
  eDeck: [], eHand: [],
  pBbsCd: 0, eBbsCd: 0,
  replacedThisTurn: false,
  replaceMode: false,
  bbsMode: null, // null | 'argeon' | 'kaleos_unit' | 'kaleos_dest'
  bbsUnitPos: null,
  selectedPos: null,
  selectedCardIdx: null,
  hoverTile: null,
  hoverCardIdx: null,
  aiBusy: false,
  winner: null,
  logs: [],
  effects: [], // {type, x, y, x2, y2, text, color, t, maxT}
  tick: 0
};

function addLog(msg) {
  state.logs.unshift(msg);
  if (state.logs.length > 14) state.logs.pop();
}

function tileCenter(r, c) {
  return {
    x: BOARD_X + c * (TILE_W + GAP) + TILE_W / 2,
    y: BOARD_Y + r * (TILE_H + GAP) + TILE_H / 2
  };
}

function spawnFloatText(r, c, text, color) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'text', x: pt.x, y: pt.y - 18, text, color, t: 0, maxT: 55 });
}

function spawnBeam(r1, c1, r2, c2, color) {
  const p1 = tileCenter(r1, c1);
  const p2 = tileCenter(r2, c2);
  state.effects.push({ type: 'beam', x: p1.x, y: p1.y, x2: p2.x, y2: p2.y, color, t: 0, maxT: 22 });
}

function spawnBurst(r, c, color) {
  const pt = tileCenter(r, c);
  for (let i = 0; i < 14; i++) {
    const ang = (Math.PI * 2 * i) / 14;
    const spd = 1.5 + Math.random() * 2.5;
    state.effects.push({
      type: 'particle', x: pt.x, y: pt.y,
      vx: Math.cos(ang) * spd, vy: Math.sin(ang) * spd,
      color, t: 0, maxT: 30
    });
  }
}

function buildDeck(factionId) {
  const fCards = FACTIONS[factionId].cards;
  const pool = [...NEUTRAL_CARDS, ...fCards];
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
    atk: 2, hp: 25, maxHp: 25, keywords: [], canMove: true, canAttack: true
  };
  board[2][8] = {
    name: ef.name, owner: 'enemy', isGeneral: true, sprite: ef.sprite,
    atk: 2, hp: 25, maxHp: 25, keywords: [], canMove: true, canAttack: true
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
  state.eMana = 2; state.eMaxMana = 2;
  state.pDeck = pDeck;
  state.pHand = [pDeck.pop(), pDeck.pop(), pDeck.pop(), pDeck.pop(), pDeck.pop()];
  state.eDeck = eDeck;
  state.eHand = [eDeck.pop(), eDeck.pop(), eDeck.pop(), eDeck.pop(), eDeck.pop()];
  state.pBbsCd = 0;
  state.eBbsCd = 0;
  state.replacedThisTurn = false;
  state.replaceMode = false;
  state.bbsMode = null;
  state.bbsUnitPos = null;
  state.selectedPos = null;
  state.selectedCardIdx = null;
  state.aiBusy = false;
  state.winner = null;
  state.effects = [];
  state.logs = [`⚔️ ${pf.name} vs ${ef.name} 결투 시작!`];
}

// =========================================================
// 4. 전술 판정 (이동, 도발, 원거리, 광란, 소환)
// =========================================================
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
  if (!u || !u.canMove) return [];
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
  if (!u || !u.canAttack) return [];
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
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (!u) continue;
      if (['fireball', 'phoenix_fire', 'void_pulse'].includes(sp) && u.owner !== owner) targets.push({ r, c });
      if (['divine_bond', 'scions_wish'].includes(sp) && u.owner === owner) targets.push({ r, c });
      if (['natural_select', 'chromatic_cold'].includes(sp) && u.owner !== owner && !u.isGeneral) targets.push({ r, c });
    }
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
    spawnBurst(r, c, '#38bdf8');
    spawnFloatText(r, c, '+1 MANA!', '#38bdf8');
    if (owner === 'player') {
      state.pMana++;
      addLog('💎 플레이어가 마나 샘(+1 마나)을 획득!');
    } else {
      state.eMana++;
      addLog('💎 적이 마나 샘(+1 마나)을 획득!');
    }
  }
}

function moveUnit(r1, c1, r2, c2) {
  const u = state.board[r1][c1];
  state.board[r2][c2] = u;
  state.board[r1][c1] = null;
  u.canMove = false;
  spawnBurst(r2, c2, '#94a3b8');
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

  // 광란(Frenzy): 공격 대상 및 인접 모든 적 동시 타격
  const victims = [{ r: r2, c: c2 }];
  if (isFrenzy && !isRanged) {
    for (const n of neighbors8(r1, c1)) {
      const adj = state.board[n.r][n.c];
      if (adj && adj.owner !== atkU.owner && !(n.r === r2 && n.c === c2)) {
        victims.push(n);
      }
    }
  }

  for (const v of victims) {
    const target = state.board[v.r][v.c];
    if (!target) continue;
    target.hp -= atkU.atk;
    spawnFloatText(v.r, v.c, `-${atkU.atk}`, '#ef4444');
    spawnBurst(v.r, v.c, '#ef4444');
    if (target.hp <= 0) {
      addLog(`💥 ${target.name} 처치됨!`);
      state.board[v.r][v.c] = null;
    }
  }

  // 원거리 공격이 아니면 주 대상만 반격
  if (!isRanged && defU.hp > 0) {
    atkU.hp -= defU.atk;
    spawnFloatText(r1, c1, `-${defU.atk}`, '#f97316');
    if (atkU.hp <= 0) {
      addLog(`💥 ${atkU.name} 전사!`);
      state.board[r1][c1] = null;
    }
  }
  addLog(`⚔️ ${atkU.name} → ${defU.name} 공격 (${atkU.atk} 피해)`);
  checkGameOver();
}

function summonMinion(card, r, c, owner) {
  const rush = card.keywords.includes('rush');
  state.board[r][c] = {
    name: card.name, owner, isGeneral: false, sprite: card.sprite,
    atk: card.atk, hp: card.hp, maxHp: card.hp,
    keywords: [...card.keywords], canMove: rush, canAttack: rush
  };
  spawnBurst(r, c, '#10b981');
  spawnFloatText(r, c, card.name, '#34d399');
  addLog(`✨ ${owner === 'player' ? '아군' : '적'} [${card.name}] 소환!`);
  checkOrbPickup(r, c, owner);
}

function castSpell(card, r, c, owner) {
  const t = state.board[r][c];
  const sp = card.spell;
  spawnBeam(owner === 'player' ? 2 : 2, owner === 'player' ? 0 : 8, r, c, '#c084fc');

  if (sp === 'fireball' || sp === 'phoenix_fire') {
    t.hp -= 3;
    spawnFloatText(r, c, '-3', '#ef4444');
    spawnBurst(r, c, '#f97316');
    if (t.hp <= 0) state.board[r][c] = null;
    if (sp === 'phoenix_fire') {
      if (owner === 'player' && state.pDeck.length && state.pHand.length < 6) state.pHand.push(state.pDeck.pop());
      if (owner === 'enemy' && state.eDeck.length && state.eHand.length < 6) state.eHand.push(state.eDeck.pop());
    }
  } else if (sp === 'divine_bond') {
    t.atk += 2; t.hp += 3; t.maxHp += 3;
    spawnFloatText(r, c, '+2/+3', '#fbbf24');
    spawnBurst(r, c, '#fbbf24');
  } else if (sp === 'scions_wish') {
    t.atk += 2; t.hp += 2; t.maxHp += 2;
    spawnFloatText(r, c, '+2/+2', '#14b8a6');
    spawnBurst(r, c, '#14b8a6');
  } else if (sp === 'void_pulse') {
    t.hp -= 2;
    spawnFloatText(r, c, '-2', '#c084fc');
    if (t.hp <= 0) state.board[r][c] = null;
    const g = findGeneral(owner);
    if (g) {
      g.unit.hp = Math.min(g.unit.maxHp, g.unit.hp + 3);
      spawnFloatText(g.r, g.c, '+3 HP', '#34d399');
    }
  } else if (sp === 'natural_select') {
    spawnFloatText(r, c, 'DESTROY', '#ef4444');
    spawnBurst(r, c, '#10b981');
    state.board[r][c] = null;
  } else if (sp === 'chromatic_cold') {
    t.hp -= 4;
    spawnFloatText(r, c, '-4', '#38bdf8');
    spawnBurst(r, c, '#38bdf8');
    if (t.hp <= 0) state.board[r][c] = null;
    const oppG = findGeneral(owner === 'player' ? 'enemy' : 'player');
    if (oppG) {
      oppG.unit.hp -= 1;
      spawnFloatText(oppG.r, oppG.c, '-1', '#38bdf8');
    }
  }
  addLog(`🔮 [${card.name}] 발동!`);
  checkGameOver();
}

// =========================================================
// 5. 장군 고유 스킬 (Bloodbound Spell) 실행
// =========================================================
function triggerBBS(owner) {
  const fac = owner === 'player' ? state.playerFaction : state.enemyFaction;
  const mana = owner === 'player' ? state.pMana : state.eMana;
  const cd = owner === 'player' ? state.pBbsCd : state.eBbsCd;
  if (cd > 0 || mana < fac.bbsCost) return false;

  const g = findGeneral(owner);
  if (!g) return false;

  if (fac.id === 'vaath') {
    g.unit.atk += 1;
    spawnBurst(g.r, g.c, '#10b981');
    spawnFloatText(g.r, g.c, '+1 ATK', '#10b981');
    addLog(`🦖 [${fac.bbsName}] ${g.unit.name} 공격력 영구 +1!`);
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
      if (u && u.owner !== owner) {
        u.hp -= 2;
        spawnFloatText(r, oppG.c, '-2', '#38bdf8');
        spawnBurst(r, oppG.c, '#38bdf8');
        if (u.hp <= 0 && !u.isGeneral) state.board[r][oppG.c] = null;
      }
    }
    addLog(`❄️ [${fac.bbsName}] ${oppG.c + 1}열 전체 냉기 폭격!`);
    checkGameOver();
  } else if (fac.id === 'argeon') {
    if (owner === 'player') {
      state.bbsMode = 'argeon';
      state.selectedCardIdx = null;
      state.selectedPos = null;
      addLog('👑 강화할 아군 유닛을 클릭하세요!');
      return true;
    } else {
      const allies = [];
      for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
        const u = state.board[r][c];
        if (u && u.owner === 'enemy' && !u.isGeneral) allies.push({ r, c, u });
      }
      if (!allies.length) return false;
      allies[0].u.atk += 2;
      spawnFloatText(allies[0].r, allies[0].c, '+2 ATK', '#fbbf24');
    }
  } else if (fac.id === 'kaleos') {
    if (owner === 'player') {
      state.bbsMode = 'kaleos_unit';
      state.selectedCardIdx = null;
      state.selectedPos = null;
      addLog('🦊 순간이동할 아군 하수인을 클릭하세요!');
      return true;
    } else {
      return false;
    }
  }

  if (owner === 'player') {
    state.pMana -= fac.bbsCost;
    state.pBbsCd = 2;
  } else {
    state.eMana -= fac.bbsCost;
    state.eBbsCd = 2;
  }
  return true;
}

// =========================================================
// 6. AI 턴 진행 (애니메이션 큐로 자연스럽게 연출)
// =========================================================
function startEnemyTurn() {
  if (state.winner || state.aiBusy) return;
  state.aiBusy = true;
  state.selectedPos = null;
  state.selectedCardIdx = null;
  state.bbsMode = null;
  state.replaceMode = false;

  state.eMaxMana = Math.min(9, state.eMaxMana + 1);
  state.eMana = state.eMaxMana;
  if (state.eBbsCd > 0) state.eBbsCd--;
  for (let i = 0; i < 2; i++) {
    if (state.eDeck.length && state.eHand.length < 6) state.eHand.push(state.eDeck.pop());
  }
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && u.owner === 'enemy') { u.canMove = true; u.canAttack = true; }
    }
  }

  const steps = [];
  // 1) 카드 사용 스텝
  steps.push(() => {
    for (let idx = state.eHand.length - 1; idx >= 0; idx--) {
      const card = state.eHand[idx];
      if (card.cost > state.eMana) continue;
      if (card.type === 'minion') {
        const tiles = getValidSummonTiles('enemy').sort((a, b) => a.c - b.c);
        if (tiles.length) {
          state.eMana -= card.cost;
          state.eHand.splice(idx, 1);
          summonMinion(card, tiles[0].r, tiles[0].c, 'enemy');
        }
      } else {
        const targets = getValidSpellTargets(card, 'enemy');
        if (targets.length) {
          state.eMana -= card.cost;
          state.eHand.splice(idx, 1);
          castSpell(card, targets[0].r, targets[0].c, 'enemy');
        }
      }
    }
  });

  // 2) 장군 스킬 스텝
  steps.push(() => {
    if (!state.winner) triggerBBS('enemy');
  });

  // 3) 유닛 이동 및 공격 스텝
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
      if (!u || u.owner !== 'enemy') continue;

      let atks = getValidAttacks(pos.r, pos.c);
      if (atks.length) {
        atks.sort((a, b) => state.board[a.r][a.c].hp - state.board[b.r][b.c].hp);
        attackUnit(pos.r, pos.c, atks[0].r, atks[0].c);
        continue;
      }
      const moves = getValidMoves(pos.r, pos.c);
      if (moves.length) {
        const pg = findGeneral('player') || { r: 2, c: 0 };
        moves.sort((a, b) => (Math.abs(a.r - pg.r) + Math.abs(a.c - pg.c)) - (Math.abs(b.r - pg.r) + Math.abs(b.c - pg.c)));
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

  // 4) 플레이어 턴 복귀
  steps.push(() => {
    if (!state.winner) {
      state.turn++;
      state.pMaxMana = Math.min(9, state.pMaxMana + 1);
      state.pMana = state.pMaxMana;
      if (state.pBbsCd > 0) state.pBbsCd--;
      state.replacedThisTurn = false;
      for (let i = 0; i < 2; i++) {
        if (state.pDeck.length && state.pHand.length < 6) state.pHand.push(state.pDeck.pop());
      }
      for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
        const u = state.board[r][c];
        if (u && u.owner === 'player') { u.canMove = true; u.canAttack = true; }
      }
      addLog(`🔵 TURN ${state.turn} - 플레이어 차례`);
    }
    state.aiBusy = false;
  });

  steps.forEach((fn, i) => setTimeout(fn, (i + 1) * 420));
}

// =========================================================
// 7. 마우스 클릭 & 호버 처리
// =========================================================
function getMousePos(evt) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (evt.clientX - rect.left) * (W / rect.width),
    y: (evt.clientY - rect.top) * (H / rect.height)
  };
}

function inside(mx, my, x, y, w, h) {
  return mx >= x && mx <= x + w && my >= y && my <= y + h;
}

canvas.addEventListener('mousemove', (e) => {
  const { x, y } = getMousePos(e);
  state.hoverTile = null;
  state.hoverCardIdx = null;

  if (state.screen === 'battle') {
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const tx = BOARD_X + c * (TILE_W + GAP);
        const ty = BOARD_Y + r * (TILE_H + GAP);
        if (inside(x, y, tx, ty, TILE_W, TILE_H)) state.hoverTile = { r, c };
      }
    }
    for (let i = 0; i < state.pHand.length; i++) {
      const cx = 55 + i * 172;
      const cy = 535;
      if (inside(x, y, cx, cy, 160, 210)) state.hoverCardIdx = i;
    }
  }
});

canvas.addEventListener('click', (e) => {
  const { x, y } = getMousePos(e);

  // [화면 1] 진영 & 장군 선택
  if (state.screen === 'select') {
    const keys = Object.keys(FACTIONS);
    keys.forEach((fid, idx) => {
      const col = idx % 3;
      const row = Math.floor(idx / 3);
      const cx = 75 + col * 370;
      const cy = 145 + row * 245;
      if (inside(x, y, cx, cy, 350, 225)) state.selectedFaction = fid;
    });

    // 적 상대 선택 토글
    if (inside(x, y, 320, 665, 280, 52)) {
      const opts = ['random', ...keys];
      const next = opts[(opts.indexOf(state.enemyChoice) + 1) % opts.length];
      state.enemyChoice = next;
    }
    // 출격 버튼
    if (inside(x, y, 630, 665, 290, 52)) {
      startBattle(state.selectedFaction, state.enemyChoice);
    }
    return;
  }

  // [화면 2] 전투 화면
  if (state.winner) {
    if (inside(x, y, W / 2 - 130, H / 2 + 30, 260, 54)) state.screen = 'select';
    return;
  }
  if (state.aiBusy) return;

  // 우측 패널 버튼들
  // 1) 장군 고유 스킬 (BBS)
  if (inside(x, y, 910, 115, 280, 82)) {
    if (state.bbsMode) state.bbsMode = null;
    else triggerBBS('player');
    return;
  }
  // 2) 카드 교체 (Replace)
  if (inside(x, y, 910, 210, 135, 48)) {
    if (!state.replacedThisTurn && state.pDeck.length > 0) {
      state.replaceMode = !state.replaceMode;
      state.selectedCardIdx = null;
      state.selectedPos = null;
    }
    return;
  }
  // 3) 진영 변경 버튼
  if (inside(x, y, 1055, 210, 135, 48)) {
    state.screen = 'select';
    return;
  }
  // 4) 턴 종료 버튼
  if (inside(x, y, 910, 270, 280, 54)) {
    startEnemyTurn();
    return;
  }

  // 하단 손패 카드 클릭
  for (let i = 0; i < state.pHand.length; i++) {
    const cx = 55 + i * 172;
    const cy = 535;
    if (inside(x, y, cx, cy, 160, 210)) {
      if (state.replaceMode) {
        const oldCard = state.pHand[i];
        const newCard = state.pDeck.pop();
        state.pDeck.unshift(oldCard);
        state.pHand[i] = newCard;
        state.replacedThisTurn = true;
        state.replaceMode = false;
        addLog(`🔄 [${oldCard.name}] → [${newCard.name}] 교체!`);
        return;
      }
      state.selectedCardIdx = state.selectedCardIdx === i ? null : i;
      state.selectedPos = null;
      state.bbsMode = null;
      return;
    }
  }

  // 중앙 5x9 보드 타일 클릭
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const tx = BOARD_X + c * (TILE_W + GAP);
      const ty = BOARD_Y + r * (TILE_H + GAP);
      if (!inside(x, y, tx, ty, TILE_W, TILE_H)) continue;

      const u = state.board[r][c];

      // 장군 스킬 타겟팅 모드
      if (state.bbsMode === 'argeon') {
        if (u && u.owner === 'player') {
          u.atk += 2;
          state.pMana -= state.playerFaction.bbsCost;
          state.pBbsCd = 2;
          spawnFloatText(r, c, '+2 ATK', '#fbbf24');
          spawnBurst(r, c, '#fbbf24');
          addLog(`👑 [왕의 포효] ${u.name} 공격력 +2!`);
        }
        state.bbsMode = null;
        return;
      }
      if (state.bbsMode === 'kaleos_unit') {
        if (u && u.owner === 'player' && !u.isGeneral) {
          state.bbsUnitPos = { r, c };
          state.bbsMode = 'kaleos_dest';
          addLog('🦊 이동할 빈 칸(최대 2칸)을 선택하세요.');
        } else {
          state.bbsMode = null;
        }
        return;
      }
      if (state.bbsMode === 'kaleos_dest') {
        const up = state.bbsUnitPos;
        if (!u && up && Math.abs(r - up.r) + Math.abs(c - up.c) <= 2) {
          state.board[r][c] = state.board[up.r][up.c];
          state.board[up.r][up.c] = null;
          state.pMana -= state.playerFaction.bbsCost;
          state.pBbsCd = 2;
          spawnBurst(r, c, '#f43f5e');
          checkOrbPickup(r, c, 'player');
          addLog('🦊 [점멸] 순간이동 완료!');
        }
        state.bbsMode = null;
        state.bbsUnitPos = null;
        return;
      }

      // 손패 카드 사용 모드
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
          if (card.type === 'spell' && getValidSpellTargets(card, 'player').some(t => t.r === r && t.c === c)) {
            state.pMana -= card.cost;
            state.pHand.splice(state.selectedCardIdx, 1);
            castSpell(card, r, c, 'player');
            state.selectedCardIdx = null;
            return;
          }
        }
        state.selectedCardIdx = null;
      }

      // 보드 유닛 선택 / 이동 / 공격
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
  }
});

// =========================================================
// 8. 렌더링 헬퍼 & 메인 60fps 루프
// =========================================================
function roundRect(x, y, w, h, r, fill, stroke, lineW = 2) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.lineWidth = lineW; ctx.strokeStyle = stroke; ctx.stroke(); }
}

function drawSprite(spriteKey, cx, cy, size, flipX = false, bob = 0) {
  const img = SPRITES[spriteKey] || SPRITES.knight;
  ctx.save();
  ctx.imageSmoothingEnabled = false;
  ctx.translate(cx, cy + bob);
  if (flipX) ctx.scale(-1, 1);
  ctx.drawImage(img, -size / 2, -size / 2, size, size);
  ctx.restore();
}

function drawSelectScreen() {
  // 우주 별빛 배경
  ctx.fillStyle = '#060811';
  ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 65; i++) {
    const sx = (i * 197 + state.tick * 0.15) % W;
    const sy = (i * 113) % H;
    ctx.fillStyle = i % 3 === 0 ? '#38bdf8' : '#475569';
    ctx.fillRect(sx, sy, 2, 2);
  }

  ctx.textAlign = 'center';
  ctx.font = 'bold 28px "Press Start 2P", monospace';
  ctx.fillStyle = '#38bdf8';
  ctx.fillText('DUEL GRID // FACTIONS', W / 2, 68);

  ctx.font = '15px "Noto Sans KR"';
  ctx.fillStyle = '#94a3b8';
  ctx.fillText('듀얼리스트 2 스타일 2D 픽셀 전술 배틀 — 출격할 진영과 장군을 선택하세요', W / 2, 105);

  const keys = Object.keys(FACTIONS);
  const bob = Math.sin(state.tick * 0.08) * 3;

  keys.forEach((fid, idx) => {
    const f = FACTIONS[fid];
    const col = idx % 3;
    const row = Math.floor(idx / 3);
    const cx = 75 + col * 370;
    const cy = 145 + row * 245;
    const isSel = state.selectedFaction === fid;

    roundRect(cx, cy, 350, 225, 8, isSel ? '#111c33' : '#0b0f1d', isSel ? f.color : '#1e293b', isSel ? 3 : 1.5);

    // 픽셀 장군 초상
    ctx.fillStyle = 'rgba(0,0,0,0.45)';
    ctx.beginPath();
    ctx.ellipse(cx + 55, cy + 92, 24, 8, 0, 0, Math.PI * 2);
    ctx.fill();
    drawSprite(f.sprite, cx + 55, cy + 62, 68, false, bob);

    ctx.textAlign = 'left';
    ctx.font = 'bold 12px "Noto Sans KR"';
    ctx.fillStyle = f.color;
    ctx.fillText(f.faction, cx + 105, cy + 36);

    ctx.font = '900 18px "Noto Sans KR"';
    ctx.fillStyle = '#f8fafc';
    ctx.fillText(f.name, cx + 105, cy + 62);

    ctx.font = '12px "Noto Sans KR"';
    ctx.fillStyle = '#cbd5e1';
    ctx.fillText(f.style.slice(0, 23), cx + 105, cy + 86);
    ctx.fillText(f.style.slice(23), cx + 105, cy + 104);

    // 고유 스킬 박스
    roundRect(cx + 16, cy + 122, 318, 86, 6, '#070b14', '#1e293b', 1);
    ctx.font = 'bold 12px "Noto Sans KR"';
    ctx.fillStyle = '#38bdf8';
    ctx.fillText(`⭐ 고유 스킬: ${f.bbsName} (${f.bbsCost}마나)`, cx + 26, cy + 144);
    ctx.font = '11.5px "Noto Sans KR"';
    ctx.fillStyle = '#e2e8f0';
    ctx.fillText(f.bbsDesc, cx + 26, cy + 166);
    ctx.fillStyle = '#fbbf24';
    ctx.fillText(`전용 카드: ${f.cards.map(c => c.name).join(', ')}`, cx + 26, cy + 190);
  });

  // 하단 상대 선택 & 시작 버튼
  const enemyLabel = state.enemyChoice === 'random' ? '🎲 상대 AI: 랜덤 진영' : `🤖 상대 AI: ${FACTIONS[state.enemyChoice].name}`;
  roundRect(320, 665, 280, 52, 8, '#0f172a', '#475569', 2);
  ctx.textAlign = 'center';
  ctx.font = 'bold 15px "Noto Sans KR"';
  ctx.fillStyle = '#e2e8f0';
  ctx.fillText(enemyLabel, 460, 697);

  roundRect(630, 665, 290, 52, 8, '#0284c7', '#38bdf8', 2);
  ctx.font = '900 17px "Noto Sans KR"';
  ctx.fillStyle = '#ffffff';
  ctx.fillText('⚔️ 전투 출격하기', 775, 697);
}

function drawBattleScreen() {
  // 검은 우주/어둠 배경
  ctx.fillStyle = '#060810';
  ctx.fillRect(0, 0, W, H);

  const pf = state.playerFaction;
  const ef = state.enemyFaction;
  const pg = findGeneral('player');
  const eg = findGeneral('enemy');
  const pHp = pg ? pg.unit.hp : 0;
  const eHp = eg ? eg.unit.hp : 0;

  // 상단 HUD 바
  roundRect(55, 16, 1135, 76, 8, '#0b0f1d', '#1e293b', 2);

  // 플레이어 장군 HUD (좌측)
  drawSprite(pf.sprite, 98, 54, 52, false, 0);
  ctx.textAlign = 'left';
  ctx.font = '900 16px "Noto Sans KR"';
  ctx.fillStyle = pf.color;
  ctx.fillText(`${pf.name}  (❤️ ${pHp}/25)`, 136, 44);
  // 마나 크리스탈
  for (let m = 0; m < 9; m++) {
    ctx.fillStyle = m < state.pMana ? '#38bdf8' : (m < state.pMaxMana ? '#1e3a5f' : '#1e293b');
    ctx.beginPath();
    ctx.moveTo(144 + m * 22, 56);
    ctx.lineTo(152 + m * 22, 65);
    ctx.lineTo(144 + m * 22, 74);
    ctx.lineTo(136 + m * 22, 65);
    ctx.closePath();
    ctx.fill();
  }
  ctx.font = 'bold 13px "Noto Sans KR"';
  ctx.fillStyle = '#93c5fd';
  ctx.fillText(`${state.pMana}/${state.pMaxMana}`, 345, 70);

  // 중앙 턴 표시
  ctx.textAlign = 'center';
  ctx.font = 'bold 14px "Press Start 2P", monospace';
  ctx.fillStyle = '#f8fafc';
  ctx.fillText(`TURN ${state.turn}`, W / 2, 48);
  ctx.font = '12px "Noto Sans KR"';
  ctx.fillStyle = state.aiBusy ? '#f43f5e' : '#38bdf8';
  ctx.fillText(state.aiBusy ? '상대 AI 턴 진행 중...' : '당신의 턴 (이동 · 공격 · 카드 소환)', W / 2, 72);

  // 적 장군 HUD (우측)
  drawSprite(ef.sprite, 1145, 54, 52, true, 0);
  ctx.textAlign = 'right';
  ctx.font = '900 16px "Noto Sans KR"';
  ctx.fillStyle = ef.color;
  ctx.fillText(`(❤️ ${eHp}/25)  ${ef.name}`, 1108, 44);
  ctx.font = '13px "Noto Sans KR"';
  ctx.fillStyle = '#94a3b8';
  ctx.fillText(`적 마나: ${state.eMana}/${state.eMaxMana}  |  남은 덱: ${state.eDeck.length}장`, 1108, 70);

  // 하이라이트 좌표 계산
  let moves = [], attacks = [], summons = [], spells = [];
  if (state.selectedPos) {
    moves = getValidMoves(state.selectedPos.r, state.selectedPos.c);
    attacks = getValidAttacks(state.selectedPos.r, state.selectedPos.c);
  }
  if (state.selectedCardIdx !== null) {
    const c = state.pHand[state.selectedCardIdx];
    if (c.type === 'minion') summons = getValidSummonTiles('player');
    else spells = getValidSpellTargets(c, 'player');
  }

  // 중앙 5x9 전술 격자 보드 렌더링
  const bob = Math.sin(state.tick * 0.08) * 2.5;
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

      let fill = (r + c) % 2 === 0 ? '#0e1424' : '#11182b';
      let stroke = '#1e293b';
      let lw = 1.5;

      if (isMove) { fill = '#0c2d48'; stroke = '#38bdf8'; lw = 2; }
      if (isSum) { fill = '#0b3326'; stroke = '#10b981'; lw = 2; }
      if (isAtk || isSpl) { fill = '#3b101d'; stroke = '#f43f5e'; lw = 2.5; }
      if (isSel) { fill = '#172a4a'; stroke = '#fbbf24'; lw = 2.5; }
      if (isHov) { stroke = '#e2e8f0'; lw = 2; }

      roundRect(tx, ty, TILE_W, TILE_H, 5, fill, stroke, lw);

      // 중앙 보너스 마나 구슬
      if (state.manaOrbs.some(o => o.r === r && o.c === c)) {
        const pulse = Math.sin(state.tick * 0.1) * 3;
        ctx.fillStyle = 'rgba(56, 189, 248, 0.25)';
        ctx.beginPath();
        ctx.arc(tx + TILE_W / 2, ty + TILE_H / 2, 16 + pulse, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#38bdf8';
        ctx.beginPath();
        ctx.moveTo(tx + TILE_W / 2, ty + 22);
        ctx.lineTo(tx + TILE_W / 2 + 12, ty + 37);
        ctx.lineTo(tx + TILE_W / 2, ty + 52);
        ctx.lineTo(tx + TILE_W / 2 - 12, ty + 37);
        ctx.closePath();
        ctx.fill();
      }

      // 유닛 렌더링
      const u = state.board[r][c];
      if (u) {
        const cx = tx + TILE_W / 2;
        const cy = ty + TILE_H / 2 - 6;
        // 진영 발판 링
        ctx.strokeStyle = u.owner === 'player' ? '#38bdf8' : '#f43f5e';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.ellipse(cx, ty + TILE_H - 16, 22, 7, 0, 0, Math.PI * 2);
        ctx.stroke();

        // 도발 방패 아이콘 표시
        if (u.keywords.includes('provoke')) {
          ctx.fillStyle = '#fbbf24';
          ctx.font = 'bold 10px "Noto Sans KR"';
          ctx.textAlign = 'center';
          ctx.fillText('🛡️도발', cx, ty + 13);
        } else if (u.keywords.includes('ranged')) {
          ctx.fillStyle = '#38bdf8';
          ctx.font = 'bold 10px "Noto Sans KR"';
          ctx.textAlign = 'center';
          ctx.fillText('🏹원거리', cx, ty + 13);
        } else if (u.keywords.includes('frenzy')) {
          ctx.fillStyle = '#10b981';
          ctx.font = 'bold 10px "Noto Sans KR"';
          ctx.textAlign = 'center';
          ctx.fillText('💥광란', cx, ty + 13);
        }

        // 행동 가능 아군 강조 오라
        if (u.owner === 'player' && (u.canMove || u.canAttack)) {
          ctx.fillStyle = 'rgba(56, 189, 248, 0.14)';
          ctx.beginPath();
          ctx.arc(cx, cy, 24, 0, Math.PI * 2);
          ctx.fill();
        }

        drawSprite(u.sprite, cx, cy, u.isGeneral ? 54 : 46, u.owner === 'enemy', bob);

        // 좌하단 공격력 배지 (노랑) & 우하단 체력 배지 (빨강)
        roundRect(tx + 5, ty + TILE_H - 22, 24, 18, 4, '#ca8a04', '#fef08a', 1);
        ctx.textAlign = 'center';
        ctx.font = '900 12px "Noto Sans KR"';
        ctx.fillStyle = '#ffffff';
        ctx.fillText(u.atk, tx + 17, ty + TILE_H - 9);

        roundRect(tx + TILE_W - 29, ty + TILE_H - 22, 24, 18, 4, '#be123c', '#fda4af', 1);
        ctx.fillText(u.hp, tx + TILE_W - 17, ty + TILE_H - 9);
      }
    }
  }

  // 우측 전술 패널
  roundRect(895, 110, 305, 390, 8, '#0b0f1d', '#1e293b', 2);

  // 1. 장군 고유 스킬 (BBS)
  const bbsReady = state.pBbsCd === 0 && state.pMana >= pf.bbsCost;
  roundRect(910, 122, 275, 76, 6, bbsReady ? '#172554' : '#0f172a', state.bbsMode ? '#fbbf24' : (bbsReady ? '#38bdf8' : '#334155'), 2);
  ctx.textAlign = 'left';
  ctx.font = '900 14px "Noto Sans KR"';
  ctx.fillStyle = bbsReady ? '#38bdf8' : '#64748b';
  ctx.fillText(state.pBbsCd === 0 ? `⭐ ${pf.bbsName} (${pf.bbsCost}마나)` : `⏳ ${pf.bbsName} (${state.pBbsCd}턴 대기)`, 922, 146);
  ctx.font = '11.5px "Noto Sans KR"';
  ctx.fillStyle = '#cbd5e1';
  ctx.fillText(pf.bbsDesc.slice(0, 22), 922, 168);
  ctx.fillText(pf.bbsDesc.slice(22), 922, 185);

  // 2. 카드 교체 버튼
  const canRep = !state.replacedThisTurn && state.pDeck.length > 0;
  roundRect(910, 210, 132, 46, 6, state.replaceMode ? '#78350f' : (canRep ? '#1e293b' : '#0f172a'), state.replaceMode ? '#fbbf24' : '#475569', 1.5);
  ctx.textAlign = 'center';
  ctx.font = 'bold 13px "Noto Sans KR"';
  ctx.fillStyle = canRep ? '#f8fafc' : '#64748b';
  ctx.fillText(state.replaceMode ? '교체할 카드 클릭' : `🔄 카드 교체 (${canRep ? 1 : 0})`, 976, 238);

  // 3. 진영 변경 버튼
  roundRect(1053, 210, 132, 46, 6, '#1e293b', '#475569', 1.5);
  ctx.fillStyle = '#cbd5e1';
  ctx.fillText('🔙 진영 변경', 1119, 238);

  // 4. 턴 종료 버튼
  roundRect(910, 268, 275, 52, 6, state.aiBusy ? '#334155' : '#0284c7', '#38bdf8', 2);
  ctx.font = '900 16px "Noto Sans KR"';
  ctx.fillStyle = '#ffffff';
  ctx.fillText('⏭️ 턴 종료 (END TURN)', 1047, 300);

  // 5. 전투 로그
  ctx.textAlign = 'left';
  ctx.font = 'bold 12px "Noto Sans KR"';
  ctx.fillStyle = '#94a3b8';
  ctx.fillText(`📜 전투 기록 (남은 덱: ${state.pDeck.length}장)`, 912, 344);
  ctx.font = '11.5px "Noto Sans KR"';
  state.logs.slice(0, 7).forEach((l, idx) => {
    ctx.fillStyle = idx === 0 ? '#f8fafc' : '#94a3b8';
    ctx.fillText(l.slice(0, 27), 912, 366 + idx * 18);
  });

  // 하단 손패 카드 렌더링 (최대 6장)
  for (let i = 0; i < state.pHand.length; i++) {
    const c = state.pHand[i];
    const isSel = state.selectedCardIdx === i;
    const isHov = state.hoverCardIdx === i;
    const cx = 55 + i * 172;
    const cy = 535 - (isSel || isHov ? 16 : 0);
    const affordable = c.cost <= state.pMana;

    roundRect(cx, cy, 160, 215, 8, isSel ? '#162847' : '#0e1424', isSel ? '#fbbf24' : (affordable ? '#38bdf8' : '#334155'), isSel ? 3 : 2);

    // 코스트 다이아몬드
    ctx.fillStyle = '#0284c7';
    ctx.beginPath();
    ctx.moveTo(cx + 22, cy + 10);
    ctx.lineTo(cx + 36, cy + 24);
    ctx.lineTo(cx + 22, cy + 38);
    ctx.lineTo(cx + 8, cy + 24);
    ctx.closePath();
    ctx.fill();
    ctx.textAlign = 'center';
    ctx.font = '900 14px "Noto Sans KR"';
    ctx.fillStyle = '#ffffff';
    ctx.fillText(c.cost, cx + 22, cy + 29);

    // 카드 일러스트(도트)
    drawSprite(c.sprite, cx + 80, cy + 68, 56, false, isHov ? bob : 0);

    // 카드 이름 & 타입
    ctx.font = '900 14px "Noto Sans KR"';
    ctx.fillStyle = '#f8fafc';
    ctx.fillText(c.name, cx + 80, cy + 114);

    // 능력치 or 마법 표기
    if (c.type === 'minion') {
      roundRect(cx + 18, cy + 124, 52, 22, 4, '#ca8a04', null);
      ctx.font = 'bold 12px "Noto Sans KR"';
      ctx.fillStyle = '#ffffff';
      ctx.fillText(`⚔️ ${c.atk}`, cx + 44, cy + 139);

      roundRect(cx + 90, cy + 124, 52, 22, 4, '#be123c', null);
      ctx.fillText(`❤️ ${c.hp}`, cx + 116, cy + 139);
    } else {
      roundRect(cx + 30, cy + 124, 100, 22, 4, '#581c87', null);
      ctx.font = 'bold 12px "Noto Sans KR"';
      ctx.fillStyle = '#f3e8ff';
      ctx.fillText('🔮 즉시 마법', cx + 80, cy + 139);
    }

    // 설명 텍스트 줄바꿈
    ctx.font = '11px "Noto Sans KR"';
    ctx.fillStyle = '#cbd5e1';
    ctx.fillText(c.desc.slice(0, 14), cx + 80, cy + 168);
    ctx.fillText(c.desc.slice(14, 28), cx + 80, cy + 185);
    ctx.fillText(c.desc.slice(28, 42), cx + 80, cy + 202);
  }

  // 이펙트 레이어 (투사체, 데미지 팝업, 파티클)
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
      ctx.lineWidth = 4 * alpha;
      ctx.beginPath();
      ctx.moveTo(efObj.x, efObj.y);
      ctx.lineTo(efObj.x2, efObj.y2);
      ctx.stroke();
    } else if (efObj.type === 'particle') {
      efObj.x += efObj.vx;
      efObj.y += efObj.vy;
      ctx.fillStyle = efObj.color;
      ctx.fillRect(efObj.x - 2, efObj.y - 2, 4, 4);
    }
    ctx.restore();
  }

  // 승패 오버레이
  if (state.winner) {
    ctx.fillStyle = 'rgba(5, 7, 13, 0.82)';
    ctx.fillRect(0, 0, W, H);
    ctx.textAlign = 'center';
    ctx.font = 'bold 34px "Press Start 2P", monospace';
    ctx.fillStyle = state.winner === 'PLAYER' ? '#38bdf8' : '#f43f5e';
    ctx.fillText(state.winner === 'PLAYER' ? 'VICTORY!' : 'DEFEAT', W / 2, H / 2 - 25);

    roundRect(W / 2 - 130, H / 2 + 30, 260, 54, 8, '#0284c7', '#38bdf8', 2);
    ctx.font = '900 17px "Noto Sans KR"';
    ctx.fillStyle = '#ffffff';
    ctx.fillText('🔄 진영 선택으로 돌아가기', W / 2, H / 2 + 63);
  }
}

function loop() {
  state.tick++;
  if (state.screen === 'select') drawSelectScreen();
  else drawBattleScreen();
  requestAnimationFrame(loop);
}
loop();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=795, scrolling=False)
