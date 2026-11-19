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
        padding: 0.15rem 0.35rem 0rem 0.35rem !important;
        max-width: 100% !important;
    }
    .stApp { background-color: #020307; }
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
    background: #020307;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Noto Sans KR', sans-serif;
    overflow: hidden;
  }
  canvas {
    background: #04060e;
    border: 2px solid #2b3c56;
    border-radius: 8px;
    box-shadow: 0 0 75px rgba(14, 165, 233, 0.22), 0 0 100px rgba(0, 0, 0, 0.98);
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
// 1. 고밀도 32x32 4프레임 픽셀 스프라이트 컴포지터 (음영 + 림라이팅 + 망토/눈 발광)
// =========================================================================
function createAnimatedSprite(palette, rows, rimColor = '#7dd3fc', glowChars = ['W', 'C', 'T', 'P', 'O']) {
  const S = 32;
  const grid = Array.from({ length: S }, (_, y) => {
    const line = (rows[y] || '').padEnd(S, '.').slice(0, S);
    return line.split('').map(ch => (ch !== '.' && palette[ch]) ? { ch, col: palette[ch] } : null);
  });

  function renderFrame(frameIdx, mode = 'normal') {
    const off = document.createElement('canvas');
    off.width = S;
    off.height = S;
    const octx = off.getContext('2d');

    const yShiftUpper = (frameIdx === 1 || frameIdx === 2) ? 1 : 0;
    const capeShift = (frameIdx === 2 || frameIdx === 3) ? -1 : 0;

    const shifted = Array.from({ length: S }, () => Array(S).fill(null));
    for (let y = 0; y < S; y++) {
      for (let x = 0; x < S; x++) {
        const cell = grid[y][x];
        if (!cell) continue;
        let ny = y < 20 ? Math.max(1, Math.min(S - 2, y + yShiftUpper)) : y;
        let nx = x;
        // 좌측 외곽 망토/날개 미세 흔들림
        if (x <= 7 && y >= 10 && y <= 24) {
          nx = Math.max(1, Math.min(S - 2, x + capeShift));
        }
        shifted[ny][nx] = cell;
      }
    }

    if (mode !== 'ghost') {
      octx.fillStyle = '#03050a';
      for (let y = 1; y < S - 1; y++) {
        for (let x = 1; x < S - 1; x++) {
          if (shifted[y][x]) continue;
          if (shifted[y - 1][x] || shifted[y + 1][x] || shifted[y][x - 1] || shifted[y][x + 1]) {
            octx.fillRect(x, y, 1, 1);
          }
        }
      }
    }

    for (let y = 1; y < S - 1; y++) {
      for (let x = 1; x < S - 1; x++) {
        const cell = shifted[y][x];
        if (!cell) continue;
        if (mode === 'flash') {
          octx.fillStyle = '#ffffff';
          octx.fillRect(x, y, 1, 1);
        } else if (mode === 'ghost') {
          octx.fillStyle = rimColor;
          octx.fillRect(x, y, 1, 1);
        } else {
          octx.fillStyle = cell.col;
          octx.fillRect(x, y, 1, 1);

          // 역광 림 라이팅 (상단 & 좌측)
          if (!shifted[y - 1][x] || !shifted[y][x - 1]) {
            octx.fillStyle = rimColor;
            octx.globalAlpha = 0.45;
            octx.fillRect(x, y, 1, 1);
            octx.globalAlpha = 1.0;
          }
          // 입체 하단/우측 그림자
          if (!shifted[y + 1][x] || !shifted[y][x + 1]) {
            octx.fillStyle = '#000000';
            octx.globalAlpha = 0.36;
            octx.fillRect(x, y, 1, 1);
            octx.globalAlpha = 1.0;
          }
          // 눈/코어/무기 맥동 글로우
          if (glowChars.includes(cell.ch) && (frameIdx === 1 || frameIdx === 2)) {
            octx.fillStyle = '#ffffff';
            octx.globalAlpha = 0.35;
            octx.fillRect(x, y, 1, 1);
            octx.globalAlpha = 1.0;
          }
        }
      }
    }
    return off;
  }

  return {
    frames: [renderFrame(0), renderFrame(1), renderFrame(2), renderFrame(3)],
    flash: renderFrame(0, 'flash'),
    ghost: renderFrame(0, 'ghost')
  };
}

const PAL = {
  W: '#ffffff', S: '#e2e8f0', M: '#94a3b8', D: '#475569', K: '#1e293b',
  Y: '#fef08a', G: '#f59e0b', B: '#b45309', U: '#1d4ed8', C: '#38bdf8',
  R: '#fda4af', E: '#e11d48', N: '#881337', O: '#f97316',
  T: '#5eead4', V: '#0d9488', A: '#d97706',
  P: '#f0abfc', X: '#9333ea', Z: '#4c1d95',
  L: '#6ee7b7', Q: '#059669', J: '#064e3b',
  I: '#bae6fd', F: '#0284c7', H: '#1e3a8a'
};

const SPRITES = {
  argeon: createAnimatedSprite(PAL, [
    '.........YY..........YY.........',
    '........YGGY........YGGY........',
    '.......YGGGGYYYYYYYYGGGGY.......',
    '......GGGGGGGGGGGGGGGGGGGG......',
    '.....GGWWWWWWWWWWWWWWWWWWGG.....',
    '.....GWCCCCCCCCCCCCCCCCCCWG.....',
    '.....GWCCCCCCCCCCCCCCCCCCWG.....',
    '......GGGGGGGGGGGGGGGGGGGG......',
    '.......BBBBBBBBBBBBBBBBBB.......',
    '..UBBBBGGGGGGGGGGGGGGGGGGGBBBB..',
    '.UYYYBGGGGGGGYYYYYYGGGGGGGGBYYYW',
    'UUYYBGGGGGGGYYYYYYYYGGGGGGGGBYYW',
    'UBBGGGGGGGGGGYYYYYYGGGGGGGGGGGBW',
    'UUBGGGGGGGGGGGYYYYGGGGGGGGGGGGBW',
    'UUBBGGGGGGGGGGGGGGGGGGGGGGGGGBBW',
    '.UU.BBBBBBBBBBBBBBBBBBBBBBBB.G..',
    '.....GGGGGGGGGGGGGGGGGGGGGG..B..',
    '......GGGGGGG......GGGGGGG......',
    '......GGGGGGG......GGGGGGG......',
    '.....BBBBBBBB......BBBBBBBB.....'
  ], '#fef08a'),

  kaleos: createAnimatedSprite(PAL, [
    '........EEEE........EEEE........',
    '.......EEEEEE......EEEEEE.......',
    '........EEEEEEEEEEEEEEEE........',
    '.......EEEEEEEEEEEEEEEEEE.......',
    '......EEKKKKKKKKKKKKKKKKEE......',
    '......EKRRRRRRRRRRRRRRRRKE......',
    '......EKKKKKKKKKKKKKKKKKKE......',
    '.......EEEEEEEEEEEEEEEEEE.......',
    '........NNNNNNNNNNNNNNNN........',
    '..NNNNNNKKKKKKKKKKKKKKKKNNNNN...',
    '.NEEEENNKKKKKKKKKKKKKKKKNNEEEE..',
    'NNEEENNKKKKKKEEEEEEKKKKKKNNEEEE.',
    'NNNKKKKKKKKKEEEEEEEEKKKKKKKKNN..',
    'NNWWKKKKKKKKKEEEEEEKKKKKKKKKWW..',
    'NWWWKKKKKKKKKNNNNNNKKKKKKKKKWWW.',
    '.WW..NNNNNNNNNNNNNNNNNNNNNN..WW.',
    '......NNNNNNN......NNNNNNN......',
    '......KKKKKKK......KKKKKKK......',
    '.....NNNNNNNN......NNNNNNNN.....'
  ], '#fda4af'),

  zirix: createAnimatedSprite(PAL, [
    '......GGG..............GGG......',
    '.....GGGGG............GGGGG.....',
    '.....GGGGGGGGGGGGGGGGGGGGGG.....',
    '.....GGGTTTTTTTTTTTTTTTTGGG.....',
    '.....GGGTVVVVVVVVVVVVVVTGGG.....',
    '......GGGGGGGGGGGGGGGGGGGG......',
    '.......AAAAAAAAAAAAAAAAAA.......',
    '..AAAAAAGGGGGGGGGGGGGGGGAAAAA...',
    '.ATTTTAAGGGGGGTTTTGGGGGGAAATTTT.',
    'ATTTTTAAGGGGGGTTTTTTGGGGGGAAATTT',
    'ATAAAAGGGGGGGGGTTTTGGGGGGGGAAAA.',
    'AT.GGGGGGGGGGGGGGGGGGGGGGGGGG...',
    'A...TTTTTTTTTTTTTTTTTTTTTTTT....',
    '.....AAAAAAAAAAAAAAAAAAAAAA.....',
    '......GGGGGGG......GGGGGGG......',
    '......AAAAAAA......AAAAAAA......',
    '.....GGGGGGGG......GGGGGGGG.....'
  ], '#5eead4'),

  lilithe: createAnimatedSprite(PAL, [
    '....PPP..................PPP....',
    '...PPXXP................PXXPP...',
    '....PPXXPPPPPPPPPPPPPPPPXXPP....',
    '.....PXXXXXXXXXXXXXXXXXXXXP.....',
    '.....PXWWWWWWWWWWWWWWWWWWXP.....',
    '.....PXWPPWWWWWWWWWWWWPPWXP.....',
    '......PXXXXXXXXXXXXXXXXXXP......',
    '.ZZZZZZXXXXXXXXXXXXXXXXXXZZZZZZ.',
    'ZZZZZZZZXXXXXXXXXXXXXXXXZZZZZZZZ',
    'ZZZPPZZZZXXXXXPPPPXXXXXZZZZPPZZZ',
    'ZZZ..ZZZXXXXXXXXXXXXXXXXZZZ..ZZZ',
    'ZZ...ZZZXXXXXXXXXXXXXXXXZZZ...ZZ',
    '......ZZZXXXXXXXXXXXXXXZZZ......',
    '......ZZZZZXXXXXXXXXXZZZZZ......',
    '.....ZZZZZZZ........ZZZZZZZ.....',
    '.....ZZZZZZ..........ZZZZZZ.....',
    '....ZZZZZZ............ZZZZZZ....'
  ], '#f0abfc'),

  vaath: createAnimatedSprite(PAL, [
    '..OOO......................OOO..',
    '.OOLLOO..................OOLLOO.',
    '..OLLLLLLLLLLLLLLLLLLLLLLLLLLO..',
    '..LLLLLLLLLLLLLLLLLLLLLLLLLLLL..',
    '..LLOOOOOOOOOOOOOOOOOOOOOOOLLL..',
    '..LLORRRRRRRRRRRRRRRRRRRRRROLL..',
    '...LLLLLLLLLLLLLLLLLLLLLLLLLL...',
    '.JJJJLLLLLLLLLLLLLLLLLLLLLLJJJJ.',
    'JJJJJJLLLLLLOOOOOOOOLLLLLLJJJJJJ',
    'JJJJJJLLLLLOOOOOOOOOOLLLLLJJJJJJ',
    'JJJJJJLLLLLLOOOOOOOOLLLLLLJJJJJJ',
    '.JJJJLLLLLLLLLLLLLLLLLLLLLLJJJJ.',
    '..JJJJJLLLLLLLLLLLLLLLLLLJJJJJ..',
    '...JJJJJJ..............JJJJJJ...',
    '.....LLLLLL..........LLLLLL.....',
    '....JJJJJJJ..........JJJJJJJ....'
  ], '#6ee7b7'),

  faie: createAnimatedSprite(PAL, [
    '....III..................III....',
    '...IFFI..................IFFI...',
    '....IFIIIIIIIIIIIIIIIIIIIIFI....',
    '.....IIIIIIIIIIIIIIIIIIIIII.....',
    '.....IIWWWWWWWWWWWWWWWWWWII.....',
    '.....IIWCCWWWWWWWWWWWWCCWII.....',
    '......IIIIIIIIIIIIIIIIIIII......',
    '..HHHHFFFFFFFFFFFFFFFFFFFFHHHH..',
    '.SSSSHHIIIIIIIIIIIIIIIIIIHHSSSS.',
    'SSSSSSHHIIIIIIWWWWIIIIIIHHSSSSSS',
    'SSS..HHIIIIIIIIIIIIIIIIIIHH..SSS',
    'SS...HHFFFFFFFFFFFFFFFFFFHH...SS',
    '......IIIIIIIIIIIIIIIIIIII......',
    '......HHHHHH........HHHHHH......',
    '.....IIIIIII........IIIIIII.....',
    '.....FFFFFFF........FFFFFFF.....'
  ], '#bae6fd'),

  paladin: createAnimatedSprite(PAL, [
    '........YYYYYYYYYYYYYY..........',
    '.......GGGGGGGGGGGGGGGG.........',
    '.......GCCCCCCCCCCCCCCCG........',
    '........GGGGGGGGGGGGGGG.........',
    '....BBBBGGGGGGGGGGGGGGGBBBB.....',
    '...YYYBGGGGGGGGGGGGGGGGGBWWW....',
    '..YYYGBGGGGGGGGGGGGGGGGGBWWW....',
    '..YYYGBGGGGGGGGGGGGGGGGGBWWW....',
    '...BBBBBBBBBBBBBBBBBBBBBBWWW....',
    '......GGGGGGGGGGGGGGGGGGWW......',
    '......GGGGGG......GGGGGG........',
    '......BBBBBB......BBBBBB........'
  ], '#fef08a'),

  assassin: createAnimatedSprite(PAL, [
    '........EEEEEEEEEEEEEE..........',
    '.......KKKKKKKKKKKKKKKK.........',
    '.......KRRRRRRRRRRRRRRK.........',
    '........KKKKKKKKKKKKKK..........',
    '...NNNNKKKKKKKKKKKKKKKKNNNN.....',
    '..EEEENKKKKKKKKKKKKKKKKNEEEE....',
    '...NNKKKKKKKKKKKKKKKKKKKKNN.....',
    '....KKKKKKKKKKKKKKKKKKKKKK......',
    '...WWKKKKKKKKNNNNKKKKKKKKWW.....',
    '..WWWW..NNNN........NNNN..WWWW..',
    '.......KKKKKK......KKKKKK.......',
    '......NNNNNNN......NNNNNNN......'
  ], '#fda4af'),

  chakri: createAnimatedSprite(PAL, [
    '.....EEE..............EEE.......',
    '....EEEEEEEEEEEEEEEEEEEEEE......',
    '...EEOOOOOOOOOOOOOOOOOOOOEE.....',
    '...EOWWWWWWWWWWWWWWWWWWWWOE.....',
    '..EEEEEEEEEEEEEEEEEEEEEEEEEE....',
    '.WWWEEEEEEEEEEEEEEEEEEEEEEWWW...',
    '..WWWWWEEEEEEEEEEEEEEEEWWWWW....',
    '....EEEEEE..........EEEEEE......',
    '....OOOOOO..........OOOOOO......',
    '...EEEEEEE..........EEEEEEE.....'
  ], '#fb923c'),

  obelysk: createAnimatedSprite(PAL, [
    '............GGGGGG..............',
    '...........GGGGGGGG.............',
    '..........GGTTTTTTGG............',
    '..........GGTVVVVTGG............',
    '..........GGGGGGGGGG............',
    '.........AAAATTTTAAAA...........',
    '.........AAAATTTTAAAA...........',
    '.........GGGGTTTTGGGG...........',
    '.........AAAATTTTAAAA...........',
    '........AAAAATTTTAAAAA..........',
    '........GGGGGGGGGGGGGG..........',
    '.......AAAAAAAAAAAAAAAA.........',
    '......GGGGGGGGGGGGGGGGGG........',
    '.....AAAAAAAAAAAAAAAAAAAA.......'
  ], '#5eead4'),

  dervish: createAnimatedSprite(PAL, [
    '........TTTTTTTTTTTTTT..........',
    '.......TYYYYYYYYYYYYYYT.........',
    '.......TVVVVVVVVVVVVVVT.........',
    '........TTTTTTTTTTTTTT..........',
    '....AAAATTTTTTTTTTTTTTAAAA......',
    '...GGGGTTTTTTTTTTTTTTTTGGGG.....',
    '....AAAATTTTTTTTTTTTTTAAAA......',
    '......TTTTTTTTTTTTTTTTTT........',
    '.......TTTTTTTTTTTTTTTT.........',
    '........TTTTTTTTTTTTTT..........',
    '.........TTTTTTTTTTTT...........',
    '..........TTTTTTTTTT............',
    '...........TTTTTTTT.............'
  ], '#5eead4'),

  wraith: createAnimatedSprite(PAL, [
    '........PPPPPPPPPPPPPP..........',
    '.......PXXXXXXXXXXXXXXP.........',
    '.......PWWXXXXXXXXXXWWP.........',
    '........PXXXXXXXXXXXXP..........',
    '...ZZZZXXXXXXXXXXXXXXXXZZZZ.....',
    '..PXXXZZZXXXXXXXXXXXXZZZXXXP....',
    '...ZZZZZXXXXXXXXXXXXXXZZZZZ.....',
    '....ZZZZXXXXXXXXXXXXXXZZZZ......',
    '.....ZZZXXXXXXXXXXXXXXZZZ.......',
    '......ZZ....XXXXXX....ZZ........'
  ], '#f0abfc'),

  revenant: createAnimatedSprite(PAL, [
    '...PPP..................PPP.....',
    '..PPXPP................PPXPP....',
    '...PXXXXXXXXXXXXXXXXXXXXXXP.....',
    '..PXWWWWWWWWWWWWWWWWWWWWWWXP....',
    '..PXWPPWWWWWWWWWWWWWWWWPPWXP....',
    '.ZZZZXXXXXXXXXXXXXXXXXXXXZZZZ...',
    'ZZZZZZXXXXXXXXXXXXXXXXXXZZZZZZ..',
    'ZZZZZZXXXXPPPPPPPPPPXXXXZZZZZZ..',
    '.ZZZZXXXXXXXXXXXXXXXXXXXXZZZZ...',
    '..ZZZZXXXXXXXXXXXXXXXXXXZZZZ....',
    '...ZZZZZ..............ZZZZZ.....'
  ], '#f0abfc'),

  beast: createAnimatedSprite(PAL, [
    '...OOO..................OOO.....',
    '..OOLLOO..............OOLLOO....',
    '...OLLLLLLLLLLLLLLLLLLLLLLO.....',
    '..LLLLLLLLLLLLLLLLLLLLLLLLLL....',
    '..LLRRRRRRRRRRRRRRRRRRRRRRLL....',
    '.LLLLLLLLLLLLLLLLLLLLLLLLLLLL...',
    'JJJLLLLLLOOOOOOOOOOOOLLLLLLJJJ..',
    'JJJLLLLLLOOOOOOOOOOOOLLLLLLJJJ..',
    '.JJJLLLLLLLLLLLLLLLLLLLLLLJJJ...',
    '..JJJJLLLLLLLLLLLLLLLLLLJJJJ....',
    '..JJJJ................JJJJ......',
    '.LLLLLL..............LLLLLL.....'
  ], '#6ee7b7'),

  egg: createAnimatedSprite(PAL, [
    '..........LLLLLLLLLL............',
    '........LLLLQQQQQQLLLL..........',
    '.......LLLQQLLLLLLQQLLL.........',
    '......LLLQQLLLLLLLLQQLLL........',
    '......LLQQLLLLLLLLLLQQLL........',
    '......LLQQLLOOOOOOLLQQLL........',
    '......LLLQQLLLLLLLLQQLLL........',
    '.......LLLQQQQQQQQQQLLL.........',
    '........LLLLLLLLLLLLLL..........',
    '.........JJJJJJJJJJJJ...........',
    '........JJJJJJJJJJJJJJ..........'
  ], '#6ee7b7'),

  wolf: createAnimatedSprite(PAL, [
    '....II..................II......',
    '...IIII................IIII.....',
    '...IIIIIIIIIIIIIIIIIIIIIIII.....',
    '..IIFFFFFFFFFFFFFFFFFFFFFFII....',
    '..IFCCCCCCCCCCCCCCCCCCCCCCFI....',
    '.IIIIIIIIIIIIIIIIIIIIIIIIIIII...',
    'SSSSIIIIIIIIIIIIIIIIIIIIIISSSS..',
    '.SSIIIIIIIIIIIIIIIIIIIIIIIIIS...',
    '..IIIIII..............IIIIII....',
    '..FFFFFF..............FFFFFF....',
    '.IIIIIII..............IIIIIII...'
  ], '#bae6fd'),

  wall: createAnimatedSprite(PAL, [
    '......IIII..........IIII........',
    '.....IIFFII........IIFFII.......',
    '....IIFFFFII..II..IIFFFFII......',
    '....IFFFFFFIIIIFIIIFFFFFFI......',
    '...IIFFFFFFIFFFFFIIFFFFFFII.....',
    '...IFFFFFFFIFFFFFIIFFFFFFFI.....',
    '..IIFFFFFFFIFFFFFIIFFFFFFFII....',
    '..IFFFFFFFFIFFFFFIIFFFFFFFFI....',
    '.IIFFFFFFFFFFFFFFFFFFFFFFFFII...',
    '.HHHHHHHHHHHHHHHHHHHHHHHHHHHH...'
  ], '#ffffff'),

  archer: createAnimatedSprite(PAL, [
    '........LLLLLLLLLLLLLL..........',
    '.......LYYYYYYYYYYYYYYL.........',
    '........LLLLLLLLLLLLLL..........',
    '....QQQQLLLLLLLLLLLLLLQQQQ......',
    '...QQQQLLLLLLLLLLLLLLLLQQQQAA...',
    '....QQQQLLLLLLLLLLLLLLQQQQAWA...',
    '......LLLLLLLLLLLLLLLLLLAWA.....',
    '......QQQQQ........QQQQQAA......',
    '.....LLLLLL........LLLLLL.......'
  ], '#6ee7b7'),

  golem: createAnimatedSprite(PAL, [
    '.....SSSSSSSSSSSSSSSSSSSS.......',
    '....DDDDDDDDDDDDDDDDDDDDDD......',
    '....DSSCCCCCCCCCCCCCCCCSSD......',
    '....DDDDDDDDDDDDDDDDDDDDDD......',
    '..KKKKKKKKKKKKKKKKKKKKKKKKKK....',
    '.KKKKKKKKKKKKKKKKKKKKKKKKKKKK...',
    '.KKKKCCCCCCCCCCCCCCCCCCCCKKKK...',
    '.KKKKKKKKKKKKKKKKKKKKKKKKKKKK...',
    '..KKKKKKKKKKKKKKKKKKKKKKKKKK....',
    '...DDDDDDD..........DDDDDDD.....',
    '..SSSSSSSS..........SSSSSSSS....'
  ], '#94a3b8')
};

const KEYWORD_GLOSSARY = {
  zeal_atk2: '☀️ 열성: 내 장군 주변 8칸 안에 있을 때 공격력 +2',
  provoke: '🛡️ 도발: 인접한 적 유닛의 이동을 봉쇄하고 공격을 강제함',
  airdrop: '🪂 공수: 보드의 빈 칸 어디든 자유롭게 소환 배치 가능',
  backstab: '🗡️ 기습: 적의 등 뒤(오른쪽) 공격 시 +2 피해 & 반격 무시',
  celerity: '⚡ 질풍: 한 턴에 2회 이동 및 2회 공격 가능',
  blast: '⚡ 폭발: 같은 가로줄의 모든 적을 반격 없이 관통 타격',
  flying: '🕊️ 비행: 거리 제한 없이 보드 어디로든 이동 가능',
  structure: '🏛️ 구조물: 스스로 이동하거나 공격하지 못하는 설치물',
  dw_grow: '👁️ 죽음의 주시: 전장에서 유닛이 죽을 때마다 +1/+1 성장',
  dw_wraith: '👁️ 죽음의 주시: 전장에서 유닛이 죽을 때마다 망령 소환',
  rush: '💨 돌진: 소환된 턴에도 즉시 이동과 공격이 가능',
  rebirth: '🥚 환생: 사망 시 0/1 알을 남기고 내 다음 턴 시작 시 부활',
  grow1: '🌿 성장: 내 턴 시작마다 +1/+1씩 영구 성장',
  frenzy: '🌪️ 광란: 공격 시 주위 8칸의 모든 적을 동시에 타격',
  infiltrate_atk2: '❄️ 침투: 적 진영(F~I열)에 있을 때 공격력 +2',
  ranged: '🏹 원거리: 거리 상관없이 보드 어디든 반격 없이 공격'
};

// =========================================================================
// 2. 난이도 & 6대 진영 고유 키워드/카드 풀
// =========================================================================
const DIFFICULTIES = [
  { id: 'easy', name: '입문 (EASY)', color: '#34d399', eHp: 20, bonusCard: 0, desc: '입문 AI. 기본 소환과 근접 교전 위주로 행동합니다.' },
  { id: 'normal', name: '보통 (NORMAL)', color: '#38bdf8', eHp: 25, bonusCard: 0, desc: '표준 AI. 진영 키워드와 마나 샘을 적절히 활용합니다.' },
  { id: 'hard', name: '숙련 (HARD)', color: '#fbbf24', eHp: 25, bonusCard: 1, desc: '숙련 AI. 킬각 계산, 알 파괴, 침투 및 스펠 콤보를 구사합니다.' },
  { id: 'master', name: '마스터 (MASTER)', color: '#f43f5e', eHp: 30, bonusCard: 1, desc: '최상위 AI. 치밀한 포지셔닝과 광역기로 전장을 압박합니다.' }
];

const FACTIONS = {
  argeon: {
    id: 'argeon', name: '아르게온 하이메이', title: '라이오나르 왕국 (LYONAR)',
    color: '#fbbf24', sprite: 'argeon', ambient: 'gold',
    mechanicTag: '열성 (ZEAL) · 도발 · 수동 치유',
    mechanicDesc: '장군 주변 8칸 배치 시 열성 버프가 켜지며, 치유 대상 직접 지정으로 전선을 유지합니다.',
    bbsName: '왕의 포효 (Roar)', bbsCost: 1, bbsDesc: '주변 아군 1기에게 공격력 +2 영구 부여',
    cards: [
      { name: '바람칼날 기사', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'paladin', keywords: ['zeal_atk2'], desc: '열성(Zeal): 아군 장군 주변 8칸 배치 시 공격력 +2 (4/3).' },
      { name: '은빛 방패기사', type: 'minion', cost: 3, atk: 1, hp: 5, sprite: 'golem', keywords: ['provoke', 'zeal_atk2'], desc: '도발 · 열성: 장군 주변에서 3/5 도발 벽이 됩니다.' },
      { name: '선홍빛 예언자', type: 'minion', cost: 3, atk: 3, hp: 3, sprite: 'paladin', keywords: ['airdrop', 'zeal_atk2'], desc: '공수(Airdrop) · 열성: 보드 어디든 투하 배치 가능!' },
      { name: '태양의 성기사', type: 'minion', cost: 4, atk: 4, hp: 4, sprite: 'paladin', keywords: ['gambit_heal4'], desc: '함성(대상 지정): 선택한 아군 유닛/장군 체력 +4 회복!' },
      { name: '신성한 결속', type: 'spell', cost: 2, spell: 'divine_bond', vfx: 'holy', desc: '스펠: 아군 하수인 1기에게 현재 체력만큼 공격력 부여!' },
      { name: '성스러운 제물', type: 'spell', cost: 4, spell: 'holy_immolation', vfx: 'holy', desc: '스펠: 아군 1기 체력 +4 회복 & 주변 모든 적에게 4 피해!' },
      { name: '순교 (Martyrdom)', type: 'spell', cost: 2, spell: 'martyrdom', vfx: 'holy', desc: '스펠: 대상 하수인 즉시 처치 & 그 주인 장군을 체력만큼 회복.' },
      { name: '폭풍의 심판', type: 'spell', cost: 2, spell: 'tempest', vfx: 'lightning', desc: '스펠: 전장의 모든 유닛과 장군에게 2 광역 피해!' },
      { name: '아클라이트 성갑', type: 'artifact', cost: 3, atkBonus: 2, art: 'artifact_regalia', desc: '아티팩트 (내구도 3): 장군 공격력 +2 & 받는 피해 2 경감!' }
    ]
  },
  kaleos: {
    id: 'kaleos', name: '칼레오스 잔', title: '송하이 제국 (SONGHAI)',
    color: '#f43f5e', sprite: 'kaleos', ambient: 'ember',
    mechanicTag: '기습 (BACKSTAB) · 공수 · 질풍',
    mechanicDesc: '적 등 뒤(오른쪽) 배치 및 침투로 반격 없는 치명타와 연쇄 주문을 폭발시킵니다.',
    bbsName: '점멸 (Blink)', bbsCost: 1, bbsDesc: '아군 하수인 1기를 2칸 이내 빈 칸으로 순간이동',
    cards: [
      { name: '차크리 아바타', type: 'minion', cost: 2, atk: 1, hp: 2, sprite: 'chakri', keywords: ['spell_grow'], desc: '주문 연쇄: 당신이 스펠을 시전할 때마다 +1/+1 영구 성장!' },
      { name: '카이도 암살자', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'assassin', keywords: ['backstab'], desc: '기습(+2): 적 등 뒤(오른쪽) 공격 시 4 피해 & 반격 무시!' },
      { name: '그림자 공수병', type: 'minion', cost: 3, atk: 2, hp: 2, sprite: 'assassin', keywords: ['airdrop', 'backstab'], desc: '공수 · 기습(+2): 적의 등 뒤 빈 칸에 직접 투하 배치 가능!' },
      { name: '등불 여우', type: 'minion', cost: 3, atk: 2, hp: 4, sprite: 'chakri', keywords: ['celerity'], desc: '질풍(Celerity): 한 턴에 2회 이동 및 2회 공격이 가능합니다!' },
      { name: '불사조의 불꽃', type: 'spell', cost: 2, spell: 'phoenix_fire', vfx: 'fire', desc: '스펠: 대상 적에게 3 피해를 입히고 카드 1장을 뽑습니다.' },
      { name: '내면의 집중', type: 'spell', cost: 1, spell: 'inner_focus', vfx: 'fire', desc: '스펠: 공격력 3 이하 아군 하수인 1기를 즉시 재행동!' },
      { name: '자리 바꾸기', type: 'spell', cost: 1, spell: 'juxtaposition', vfx: 'void', desc: '스펠: 전장의 두 하수인 위치를 서로 맞바꿉니다!' },
      { name: '유령 번개', type: 'spell', cost: 1, spell: 'ghost_lightning', vfx: 'lightning', desc: '스펠: 모든 적 하수인에게 1 피해를 입힙니다.' },
      { name: '그림자 가면', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_mask', desc: '아티팩트 (내구도 3): 장군 공격력 +2 및 원거리(Ranged) 부여!' }
    ]
  },
  zirix: {
    id: 'zirix', name: '지릭스 스타스트라이더', title: '베트루비안 제국 (VETRUVIAN)',
    color: '#14b8a6', sprite: 'zirix', ambient: 'sand',
    mechanicTag: '폭발 레이저 (BLAST) · 오벨리스크 · 비행',
    mechanicDesc: '가로줄 전체를 반격 없이 관통하는 폭발 광선과 오벨리스크 구조물을 전장에 세웁니다.',
    bbsName: '바람의 소환', bbsCost: 1, bbsDesc: '장군 주변 빈 칸에 2/2 돌진 데르비시 소환',
    cards: [
      { name: '천상의 오벨리스크', type: 'minion', cost: 2, atk: 0, hp: 6, sprite: 'obelysk', keywords: ['structure', 'spawn_dervish'], desc: '구조물: 이동 불가. 내 턴 시작마다 2/2 돌진 데르비시 소환!' },
      { name: '화염술사', type: 'minion', cost: 2, atk: 2, hp: 1, sprite: 'archer', keywords: ['blast'], desc: '폭발(Blast): 같은 가로줄의 모든 적을 반격 없이 관통 공격!' },
      { name: '모래 날개 정령', type: 'minion', cost: 3, atk: 3, hp: 3, sprite: 'dervish', keywords: ['flying'], desc: '비행(Flying): 거리와 장애물 상관없이 보드 어디로든 이동!' },
      { name: '사막 스캐럽', type: 'minion', cost: 5, atk: 3, hp: 5, sprite: 'golem', keywords: ['blast'], desc: '폭발(Blast): 3 공격력으로 가로줄 전체를 휩쓰는 고대 병기!' },
      { name: '자손의 축복', type: 'spell', cost: 2, spell: 'scions_wish', vfx: 'holy', desc: '스펠: 아군 하수인에게 +2/+2를 부여하고 카드 1장 드로우.' },
      { name: '엔트로피 붕괴', type: 'spell', cost: 3, spell: 'entropic_decay', vfx: 'lightning', desc: '스펠: 아군 장군 주변 8칸 내 적 하수인 1기 즉시 소멸!' },
      { name: '별의 분노', type: 'spell', cost: 4, spell: 'stars_fury', vfx: 'holy', desc: '스펠: 모든 적 유닛 바로 앞 칸에 2/2 돌진 데르비시 소환!' },
      { name: '모래의 뼈무리', type: 'spell', cost: 2, spell: 'bone_swarm', vfx: 'fire', desc: '스펠: 적 장군과 그 주변 모든 적에게 2 광역 피해!' },
      { name: '이키르의 지팡이', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_staff', desc: '아티팩트 (내구도 3): 아군 장군에게 공격력 +2를 부여합니다.' }
    ]
  },
  lilithe: {
    id: 'lilithe', name: '리리스 블라이트체이서', title: '어비시안 군단 (ABYSSIAN)',
    color: '#c084fc', sprite: 'lilithe', ambient: 'void',
    mechanicTag: '죽음의 주시 (DEATHWATCH) · 그림자 역병',
    mechanicDesc: '유닛이 쓰러질 때마다 능력치가 폭증하며, 그림자 역병 타일을 깔아 전장을 장악합니다.',
    bbsName: '망령의 부름', bbsCost: 1, bbsDesc: '장군 주변 빈 칸에 1/1 돌진 망령 2기 소환',
    cards: [
      { name: '심연의 기어다니는 자', type: 'minion', cost: 1, atk: 2, hp: 1, sprite: 'wraith', keywords: ['gambit_creep'], desc: '함성: 배치한 칸을 그림자 역병으로 오염 (턴 종료 시 적 피해)!' },
      { name: '그림자 감시자', type: 'minion', cost: 2, atk: 2, hp: 2, sprite: 'wraith', keywords: ['dw_grow'], desc: '죽음의 주시: 전장에서 어떤 유닛이든 죽을 때마다 +1/+1 성장!' },
      { name: '핏빛달 여사제', type: 'minion', cost: 4, atk: 3, hp: 3, sprite: 'wraith', keywords: ['dw_wraith'], desc: '죽음의 주시: 어떤 유닛이든 죽을 때마다 주변에 1/1 망령 소환!' },
      { name: '망령의 군주', type: 'minion', cost: 6, atk: 6, hp: 6, sprite: 'revenant', keywords: ['rush', 'revenant_passive'], desc: '돌진: 적 하수인 공격 시 적 장군에게도 4 피해를 입힙니다!' },
      { name: '그림자 폭발', type: 'spell', cost: 4, spell: 'shadow_nova', vfx: 'void', desc: '스펠: 지정한 2x2 구역에 2 피해 & 그림자 역병 타일 생성!' },
      { name: '영혼 착취', type: 'spell', cost: 2, spell: 'void_pulse', vfx: 'void', desc: '스펠: 대상 적에게 2 피해를 입히고 아군 장군 체력 +3 회복.' },
      { name: '악마의 유혹', type: 'spell', cost: 2, spell: 'daemonic_lure', vfx: 'void', desc: '스펠: 적 하수인에게 1 피해 후 원하는 빈 칸으로 강제 이동!' },
      { name: '영혼 파쇄 서약', type: 'spell', cost: 2, spell: 'soulshatter', vfx: 'void', desc: '스펠: 모든 아군 하수인에게 공격력 +2를 부여합니다!' },
      { name: '유령의 칼날', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_void', desc: '아티팩트 (내구도 3): 장군 공격력 +2 & 적 처치 시 체력 +2!' }
    ]
  },
  vaath: {
    id: 'vaath', name: '바스 디 이모탈', title: '마그마르 위상 (MAGMAR)',
    color: '#10b981', sprite: 'vaath', ambient: 'magmar',
    mechanicTag: '환생 알 (REBIRTH) · 성장 (GROW) · 광란',
    mechanicDesc: '죽으면 0/1 알을 남겨 부활하는 환생과 매 턴 거대해지는 성장 용족으로 전선을 밀어붙입니다.',
    bbsName: '과부하 (Overload)', bbsCost: 1, bbsDesc: '아군 장군의 공격력이 영구적으로 +1 증가',
    cards: [
      { name: '어린 실리타르', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'beast', keywords: ['rebirth'], desc: '환생(Rebirth): 죽으면 0/1 알을 남기고 다음 턴 부활합니다!' },
      { name: '대지 보행자', type: 'minion', cost: 3, atk: 3, hp: 3, sprite: 'beast', keywords: ['grow1'], desc: '성장(+1/+1): 내 턴 시작마다 +1/+1씩 영구적으로 거대해집니다!' },
      { name: '베테랑 실리타르', type: 'minion', cost: 4, atk: 4, hp: 4, sprite: 'beast', keywords: ['rebirth'], desc: '환생(Rebirth): 처치해도 알을 깨지 않으면 4/4로 다시 부활!' },
      { name: '마칸토르 전투야수', type: 'minion', cost: 5, atk: 4, hp: 4, sprite: 'beast', keywords: ['rush', 'frenzy'], desc: '돌진 · 광란: 소환 즉시 돌격해 인접 모든 적을 동시 타격!' },
      { name: '자연의 선택', type: 'spell', cost: 2, spell: 'natural_select', vfx: 'void', desc: '스펠: 전장에서 공격력이 가장 낮은 하수인 1기 즉시 처치.' },
      { name: '플라즈마 폭풍', type: 'spell', cost: 4, spell: 'plasma_storm', vfx: 'lightning', desc: '스펠: 공격력 3 이하인 모든 하수인을 전장에서 일소!' },
      { name: '알 변이 (Egg Morph)', type: 'spell', cost: 3, spell: 'egg_morph', vfx: 'holy', desc: '스펠: 적 하수인을 0/1 알로 만들거나, 아군 알을 즉시 부화!' },
      { name: '대지의 구체', type: 'spell', cost: 3, spell: 'earth_sphere', vfx: 'holy', desc: '스펠: 아군 장군의 체력을 7 회복합니다.' },
      { name: '아다만타이트 발톱', type: 'artifact', cost: 3, atkBonus: 3, art: 'artifact_claw', desc: '아티팩트 (내구도 3): 아군 장군에게 공격력 +3 부여!' }
    ]
  },
  faie: {
    id: 'faie', name: '페이 블러드윙', title: '바나르 혈족 (VANAR)',
    color: '#38bdf8', sprite: 'faie', ambient: 'snow',
    mechanicTag: '침투 (INFILTRATE) · 빙벽 · 광란 아티팩트',
    mechanicDesc: '적 진영(F~I열)으로 넘어가면 강력해지는 침투 능력과 빙벽 배치로 전장을 봉쇄합니다.',
    bbsName: '전쟁의 새 (Warbird)', bbsCost: 1, bbsDesc: '적 장군과 같은 세로줄(열)의 모든 적에게 2 피해',
    cards: [
      { name: '수정 은신자', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'wolf', keywords: ['infiltrate_atk2'], desc: '침투(Infiltrate): 적 진영(F~I열) 배치/진입 시 공격력 +2 (4/3)!' },
      { name: '펜리르 전쟁군주', type: 'minion', cost: 3, atk: 3, hp: 2, sprite: 'wolf', keywords: ['dying_wolf'], desc: '유언: 처치되면 그 자리에 3/2 서리 늑대를 소환합니다!' },
      { name: '중력의 빙벽', type: 'spell', cost: 2, spell: 'gravity_well', vfx: 'ice', desc: '스펠: 보드 어디든 지정한 칸과 위아래에 0/3 도발 빙벽 3개 배치!' },
      { name: '빙하의 파수꾼', type: 'minion', cost: 4, atk: 3, hp: 6, sprite: 'golem', keywords: ['provoke', 'infiltrate_atk2'], desc: '도발 · 침투: 적 진영에서 5/6 도발 괴수로 변모합니다.' },
      { name: '냉혹한 한기', type: 'spell', cost: 2, spell: 'chromatic_cold', vfx: 'ice', desc: '스펠: 대상 하수인의 능력을 침묵(해제)시키고 2 피해!' },
      { name: '우박 감옥', type: 'spell', cost: 2, spell: 'hailstone', vfx: 'ice', desc: '스펠: 대상 적 하수인을 원래 주인의 손패로 되돌려 보냅니다!' },
      { name: '여우의 형상', type: 'spell', cost: 1, spell: 'aspect_fox', vfx: 'ice', desc: '스펠: 대상 적 하수인을 능력 없는 3/3 여우로 변신!' },
      { name: '눈사태 (Avalanche)', type: 'spell', cost: 4, spell: 'avalanche', vfx: 'ice', desc: '스펠: 전장 왼쪽 절반(A~D열)의 모든 적에게 4 피해 & 기절!' },
      { name: '콜드바이터', type: 'artifact', cost: 2, atkBonus: 2, art: 'artifact_ice', desc: '아티팩트 (내구도 3): 장군 공격력 +2 및 직접 공격 시 광란(Frenzy)!' }
    ]
  }
};

const NEUTRAL_CARDS = [
  { name: '피눈물 연금술사', type: 'minion', cost: 1, atk: 2, hp: 1, sprite: 'wraith', keywords: ['gambit_ping1'], desc: '함성(대상 지정): 직접 선택한 적 유닛/장군에게 1 피해!' },
  { name: '치유의 신비술사', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'archer', keywords: ['gambit_heal2'], desc: '함성(대상 지정): 직접 선택한 유닛/장군 체력 +2 회복!' },
  { name: '단검의 검객', type: 'minion', cost: 2, atk: 2, hp: 3, sprite: 'paladin', keywords: ['gambit_buff2'], desc: '함성(대상 지정): 직접 선택한 아군 하수인에게 공격력 +2 부여!' },
  { name: '축출 야수', type: 'minion', cost: 3, atk: 2, hp: 2, sprite: 'wolf', keywords: ['gambit_repulse'], desc: '함성(대상 지정): 적 하수인을 선택해 원하는 빈 칸으로 강제 추방!' },
  { name: '춤추는 칼날', type: 'minion', cost: 5, atk: 4, hp: 6, sprite: 'assassin', keywords: ['gambit_front3'], desc: '함성(전방 배치): 배치한 칸 바로 앞(→) 적에게 3 피해!' },
  { name: '집정관 스펠바인더', type: 'minion', cost: 6, atk: 7, hp: 7, sprite: 'golem', keywords: ['frenzy'], desc: '광란: 거대한 마력 구체로 주변 모든 적을 동시 타격!' }
];

// =========================================================================
// 3. 게임 상태 및 전장 좌표 상수 (A1 ~ I5)
// =========================================================================
const ROWS = 5, COLS = 9;
const COL_LABELS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'];
const BOARD_X = 62, BOARD_Y = 128, TILE_W = 92, TILE_H = 78, GAP = 4;

let state = {
  screen: 'title',
  selectedFaction: 'argeon',
  difficultyIdx: 1,
  useBbsMode: false,
  enemyChoice: 'random',
  playerFaction: null,
  enemyFaction: null,
  board: [],
  manaOrbs: [],
  creepTiles: [],
  decals: [],
  turn: 1,
  mulliganSelected: new Set(),
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
  projectiles: [],
  screenFlash: { color: '#ffffff', alpha: 0 },
  hitstop: 0,
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

// =========================================================================
// 시네마틱 VFX & 지면 데칼 스포너 라이브러리
// =========================================================================
function triggerShake(amount = 7) { state.shake = Math.max(state.shake, amount); }
function triggerScreenFlash(color = '#ffffff', alpha = 0.22) {
  state.screenFlash = { color, alpha };
}
function spawnDecal(r, c, kind = 'crack') {
  state.decals.push({ r, c, kind, t: 0, maxT: 320 });
  if (state.decals.length > 25) state.decals.shift();
}
function spawnFloatText(r, c, text, color) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'text', x: pt.x, y: pt.y - 24, text, color, t: 0, maxT: 68 });
}
function spawnArcSlash(r, c, dirX = 1, color = '#fef08a', scale = 1.0) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'arcSlash', x: pt.x, y: pt.y, dirX, color, scale, t: 0, maxT: 22 });
}
function spawnStarburst(r, c, color = '#fef08a') {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'starburst', x: pt.x, y: pt.y, color, t: 0, maxT: 20 });
}
function spawnBackstabX(r, c) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'backstabX', x: pt.x, y: pt.y, t: 0, maxT: 26 });
}
function spawnBlastBeam(r1, c1, r2, c2) {
  const p1 = tileCenter(r1, c1), p2 = tileCenter(r2, c2);
  state.effects.push({ type: 'blastBeam', x: p1.x, y: p1.y, x2: p2.x, y2: p2.y, t: 0, maxT: 28 });
}
function spawnWhirlwind(r, c) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'whirlwind', x: pt.x, y: pt.y, t: 0, maxT: 26 });
}
function spawnRing(r, c, color, maxR = 54) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'ring', x: pt.x, y: pt.y, color, maxR, t: 0, maxT: 26 });
}
function spawnPillar(r, c, color = '#38bdf8') {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'pillar', x: pt.x, y: pt.y + 18, color, t: 0, maxT: 32 });
}
function spawnLightning(r, c, color = '#38bdf8') {
  const pt = tileCenter(r, c);
  const segs = [];
  let cx = pt.x + (Math.random() - 0.5) * 44, cy = pt.y - 250;
  const steps = 9;
  for (let i = 1; i <= steps; i++) {
    const nx = i === steps ? pt.x : pt.x + (Math.random() - 0.5) * 40;
    const ny = cy + 250 / steps;
    segs.push({ x1: cx, y1: cy, x2: nx, y2: ny });
    cx = nx; cy = ny;
  }
  state.effects.push({ type: 'lightning', x: pt.x, y: pt.y, segs, color, t: 0, maxT: 24 });
  spawnDecal(r, c, 'scorch');
}
function spawnIceSpikes(r, c) {
  const pt = tileCenter(r, c);
  const spikes = Array.from({ length: 7 }, (_, i) => ({
    dx: (i - 3) * 10,
    h: 28 + Math.random() * 24,
    tilt: (i - 3) * 0.13
  }));
  state.effects.push({ type: 'iceSpikes', x: pt.x, y: pt.y + 16, spikes, t: 0, maxT: 34 });
  spawnDecal(r, c, 'frost');
}
function spawnVoidVortex(r, c) {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'voidVortex', x: pt.x, y: pt.y, t: 0, maxT: 34 });
}
function spawnHealHelix(r, c, color = '#34d399') {
  const pt = tileCenter(r, c);
  state.effects.push({ type: 'healHelix', x: pt.x, y: pt.y + 16, color, t: 0, maxT: 36 });
}
function spawnDeathBurst(r, c, color = '#f43f5e') {
  const pt = tileCenter(r, c);
  for (let i = 0; i < 28; i++) {
    const ang = Math.random() * Math.PI * 2;
    const spd = 1.6 + Math.random() * 5.6;
    state.effects.push({
      type: 'shard', x: pt.x, y: pt.y,
      vx: Math.cos(ang) * spd, vy: Math.sin(ang) * spd - 2.4,
      color: i % 3 === 0 ? '#ffffff' : color, t: 0, maxT: 38
    });
  }
  state.effects.push({ type: 'soulOrb', x: pt.x, y: pt.y, color, t: 0, maxT: 46 });
  spawnDecal(r, c, 'crack');
}
function spawnManaTether(r, c, owner) {
  const pt = tileCenter(r, c);
  const destX = owner === 'player' ? 405 : 1010;
  const destY = 38;
  for (let i = 0; i < 8; i++) {
    state.projectiles.push({
      x: pt.x, y: pt.y, x1: pt.x, y1: pt.y, x2: destX, y2: destY,
      arcOffset: (i - 3.5) * 28, color: '#38bdf8', t: -i * 2, maxT: 26
    });
  }
}
function spawnDirectionalSparks(r, c, dirX, color, count = 20) {
  const pt = tileCenter(r, c);
  for (let i = 0; i < count; i++) {
    const spread = (Math.random() - 0.5) * 2.0;
    const baseAng = dirX >= 0 ? 0 : Math.PI;
    const ang = baseAng + spread;
    const spd = 2.5 + Math.random() * 4.8;
    state.effects.push({
      type: 'spark', x: pt.x, y: pt.y,
      vx: Math.cos(ang) * spd, vy: Math.sin(ang) * spd,
      color, t: 0, maxT: 28
    });
  }
}
function spawnProjectile(r1, c1, r2, c2, color = '#38bdf8') {
  const p1 = tileCenter(r1, c1), p2 = tileCenter(r2, c2);
  state.projectiles.push({
    x: p1.x, y: p1.y, x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
    arcOffset: 22, color, t: 0, maxT: 14
  });
}

function buildDeck30(factionId) {
  const fCards = FACTIONS[factionId].cards;
  const deck = [];
  for (const c of fCards) {
    deck.push({ ...c, keywords: [...(c.keywords || [])] });
    deck.push({ ...c, keywords: [...(c.keywords || [])] });
  }
  for (const c of NEUTRAL_CARDS) {
    deck.push({ ...c, keywords: [...(c.keywords || [])] });
    deck.push({ ...c, keywords: [...(c.keywords || [])] });
  }
  for (let i = deck.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [deck[i], deck[j]] = [deck[j], deck[i]];
  }
  return deck;
}

function createUnitObj(data) {
  return {
    ...data,
    animX: 0, animY: 0, flashT: 0, trail: []
  };
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
  board[2][0] = createUnitObj({
    name: pf.name, owner: 'player', isGeneral: true, sprite: pf.sprite,
    baseAtk: 2, atk: 2, hp: 25, maxHp: 25, keywords: [], stunned: false,
    movesLeft: 1, attacksLeft: 1
  });
  board[2][8] = createUnitObj({
    name: ef.name, owner: 'enemy', isGeneral: true, sprite: ef.sprite,
    baseAtk: 2, atk: 2, hp: diff.eHp, maxHp: diff.eHp, keywords: [], stunned: false,
    movesLeft: 1, attacksLeft: 1
  });

  const pDeck = buildDeck30(pFid);
  const eDeck = buildDeck30(eFid);

  state.screen = 'mulligan';
  state.playerFaction = pf;
  state.enemyFaction = ef;
  state.board = board;
  state.manaOrbs = [{ r: 0, c: 4 }, { r: 4, c: 4 }, { r: 2, c: 5 }];
  state.creepTiles = [];
  state.decals = [];
  state.turn = 1;
  state.mulliganSelected = new Set();
  state.pMana = 2; state.pMaxMana = 2;
  state.eMana = 3; state.eMaxMana = 3;
  state.pDeck = pDeck;
  state.pHand = Array.from({ length: 5 }, () => pDeck.pop());
  state.eDeck = eDeck;
  state.eHand = Array.from({ length: Math.min(6, 5 + diff.bonusCard) }, () => eDeck.pop());
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
  state.projectiles = [];
  state.logs = [`⚔️ [${diff.name}] ${pf.name} vs ${ef.name} 결투 시작!`];
}

function confirmMulligan() {
  if (state.mulliganSelected.size > 0) {
    const idxs = Array.from(state.mulliganSelected);
    const oldCards = idxs.map(i => state.pHand[i]);
    for (const i of idxs) {
      if (state.pDeck.length) state.pHand[i] = state.pDeck.pop();
    }
    for (const oc of oldCards) state.pDeck.unshift(oc);
    addLog(`🔄 오프닝 멀리건으로 카드 ${idxs.length}장 교체!`);
  }
  state.screen = 'battle';
}

// =========================================================================
// 4. 듀얼리스트 II 정통 배치 · 기동 · 동적 능력치 판정
// =========================================================================
function neighbors8(r, c) {
  const res = [];
  for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
    if (dr === 0 && dc === 0) continue;
    const nr = r + dr, nc = c + dc;
    if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS) res.push({ r: nr, c: nc });
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

function getEffectiveAtk(u, r, c) {
  if (!u) return 0;
  let atk = u.atk;
  if (u.keywords.includes('zeal_atk2')) {
    const g = findGeneral(u.owner);
    if (g && Math.abs(r - g.r) <= 1 && Math.abs(c - g.c) <= 1) atk += 2;
  }
  if (u.keywords.includes('infiltrate_atk2')) {
    const infiltrated = u.owner === 'player' ? c >= 5 : c <= 3;
    if (infiltrated) atk += 2;
  }
  return atk;
}

function isKeywordActive(u, r, c, kw) {
  if (!u || !u.keywords.includes(kw)) return false;
  if (kw === 'zeal_atk2') {
    const g = findGeneral(u.owner);
    return g && Math.abs(r - g.r) <= 1 && Math.abs(c - g.c) <= 1;
  }
  if (kw === 'infiltrate_atk2') {
    return u.owner === 'player' ? c >= 5 : c <= 3;
  }
  return true;
}

function recalcGeneralStats(owner) {
  const g = findGeneral(owner);
  if (!g) return;
  const arts = owner === 'player' ? state.pArtifacts : state.eArtifacts;
  const bonus = arts.reduce((acc, a) => acc + a.atkBonus, 0);
  g.unit.atk = g.unit.baseAtk + bonus;
  const kws = [];
  if (arts.some(a => a.art === 'artifact_mask')) kws.push('ranged');
  if (arts.some(a => a.art === 'artifact_ice')) kws.push('frenzy');
  g.unit.keywords = kws;
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
  if (!u || u.movesLeft <= 0 || u.stunned || u.keywords.includes('structure')) return [];
  if (getAdjacentProvokers(r, c, u.owner).length > 0) return [];

  if (u.keywords.includes('flying')) {
    const fly = [];
    for (let fr = 0; fr < ROWS; fr++) for (let fc = 0; fc < COLS; fc++) {
      if (!state.board[fr][fc]) fly.push({ r: fr, c: fc });
    }
    return fly;
  }

  const visited = new Set([`${r},${c}`]);
  const q = [{ r, c, dist: 0 }];
  const valid = [];
  while (q.length) {
    const cur = q.shift();
    if (cur.dist === 2) continue;
    for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
      const nr = cur.r + dr, nc = cur.c + dc;
      const key = `${nr},${nc}`;
      if (nr < 0 || nr >= ROWS || nc < 0 || nc >= COLS || visited.has(key)) continue;
      const occ = state.board[nr][nc];
      if (occ && occ.owner !== u.owner) continue;
      visited.add(key);
      if (!occ) valid.push({ r: nr, c: nc });
      q.push({ r: nr, c: nc, dist: cur.dist + 1 });
    }
  }
  return valid;
}

function getValidAttacks(r, c) {
  const u = state.board[r][c];
  if (!u || u.attacksLeft <= 0 || u.stunned || u.keywords.includes('structure')) return [];
  if (getEffectiveAtk(u, r, c) <= 0) return [];
  const prov = getAdjacentProvokers(r, c, u.owner);
  if (prov.length > 0) return prov;

  const targets = [];
  if (u.keywords.includes('ranged')) {
    for (let tr = 0; tr < ROWS; tr++) for (let tc = 0; tc < COLS; tc++) {
      const t = state.board[tr][tc];
      if (t && t.owner !== u.owner) targets.push({ r: tr, c: tc });
    }
  } else if (u.keywords.includes('blast')) {
    for (let tc = 0; tc < COLS; tc++) {
      if (tc === c) continue;
      const t = state.board[r][tc];
      if (t && t.owner !== u.owner) targets.push({ r, c: tc });
    }
  } else {
    for (const n of neighbors8(r, c)) {
      const t = state.board[n.r][n.c];
      if (t && t.owner !== u.owner) targets.push(n);
    }
  }
  return targets;
}

function isBackstabPosition(atkU, r1, c1, r2, c2) {
  if (!atkU || !atkU.keywords.includes('backstab')) return false;
  if (Math.abs(r1 - r2) > 1 || Math.abs(c1 - c2) > 1) return false;
  return atkU.owner === 'player' ? c1 > c2 : c1 < c2;
}

function getValidSummonTiles(owner, card = null) {
  if (card && card.keywords && card.keywords.includes('airdrop')) {
    const all = [];
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      if (!state.board[r][c]) all.push({ r, c });
    }
    return all;
  }
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
  if (['holy_immolation', 'divine_bond', 'inner_focus', 'scions_wish', 'egg_morph'].includes(sp)) {
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (!u) continue;
      if (sp === 'egg_morph' && !u.isGeneral) targets.push({ r, c });
      else if (u.owner === owner) {
        if (sp === 'holy_immolation') targets.push({ r, c });
        else if (!u.isGeneral) {
          if (sp === 'inner_focus' && getEffectiveAtk(u, r, c) > 3) continue;
          targets.push({ r, c });
        }
      }
    }
  } else if (['martyrdom', 'natural_select'].includes(sp)) {
    let minAtk = 999;
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && !u.isGeneral && getEffectiveAtk(u, r, c) < minAtk) minAtk = getEffectiveAtk(u, r, c);
    }
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && !u.isGeneral) {
        if (sp === 'natural_select' && getEffectiveAtk(u, r, c) !== minAtk) continue;
        targets.push({ r, c });
      }
    }
  } else if (['phoenix_fire', 'void_pulse'].includes(sp)) {
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && u.owner !== owner) targets.push({ r, c });
    }
  } else if (['entropic_decay', 'daemonic_lure', 'chromatic_cold', 'hailstone', 'aspect_fox'].includes(sp)) {
    const g = findGeneral(owner);
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (!u || u.owner === owner || u.isGeneral) continue;
      if (sp === 'entropic_decay' && g && (Math.abs(r - g.r) > 1 || Math.abs(c - g.c) > 1)) continue;
      targets.push({ r, c });
    }
  } else if (sp === 'juxtaposition') {
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && !u.isGeneral) targets.push({ r, c });
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
    spawnRing(r, c, '#38bdf8', 66);
    spawnManaTether(r, c, owner);
    spawnFloatText(r, c, '+1 MANA', '#38bdf8');
    if (owner === 'player') { state.pMana++; addLog('💎 플레이어 마나 샘 흡수! (+1 마나)'); }
    else { state.eMana++; addLog('💎 적 AI 마나 샘 흡수! (+1 마나)'); }
  }
}

function healUnit(r, c, amount) {
  const u = state.board[r][c];
  if (!u || amount <= 0) return;
  const before = u.hp;
  u.hp = Math.min(u.maxHp, u.hp + amount);
  const actual = u.hp - before;
  if (actual > 0) {
    spawnRing(r, c, '#34d399', 54);
    spawnHealHelix(r, c, '#34d399');
    spawnFloatText(r, c, `+${actual} HP`, '#34d399');
  }
}

function onMinionDied(deadUnit, r, c) {
  for (let dr = 0; dr < ROWS; dr++) for (let dc = 0; dc < COLS; dc++) {
    const dw = state.board[dr][dc];
    if (!dw) continue;
    if (dw.keywords.includes('dw_grow')) {
      dw.atk += 1; dw.hp += 1; dw.maxHp += 1;
      spawnHealHelix(dr, dc, '#e879f9');
      spawnFloatText(dr, dc, '+1/+1', '#e879f9');
    }
    if (dw.keywords.includes('dw_wraith')) {
      const empties = neighbors8(dr, dc).filter(n => !state.board[n.r][n.c]);
      if (empties.length) {
        const pos = empties[Math.floor(Math.random() * empties.length)];
        state.board[pos.r][pos.c] = createUnitObj({
          name: '심연의 망령', owner: dw.owner, isGeneral: false, sprite: 'wraith',
          atk: 1, hp: 1, maxHp: 1, keywords: [], stunned: false, movesLeft: 0, attacksLeft: 0
        });
        spawnPillar(pos.r, pos.c, '#c084fc');
      }
    }
  }

  if (deadUnit.keywords.includes('rebirth')) {
    state.board[r][c] = createUnitObj({
      name: `${deadUnit.name}의 알`, owner: deadUnit.owner, isGeneral: false, sprite: 'egg',
      atk: 0, hp: 1, maxHp: 1, keywords: ['structure'], stunned: false, movesLeft: 0, attacksLeft: 0,
      hatchesInto: { ...deadUnit, hp: deadUnit.maxHp, keywords: [...deadUnit.keywords] }
    });
    spawnRing(r, c, '#10b981', 54);
    spawnFloatText(r, c, '🥚 REBIRTH EGG', '#6ee7b7');
  } else if (deadUnit.keywords.includes('dying_wolf')) {
    state.board[r][c] = createUnitObj({
      name: '서리 늑대', owner: deadUnit.owner, isGeneral: false, sprite: 'wolf',
      atk: 3, hp: 2, maxHp: 2, keywords: [], stunned: false, movesLeft: 0, attacksLeft: 0
    });
    spawnIceSpikes(r, c);
  }
}

function dealDamageToUnit(r, c, dmg, color = '#ef4444', dirX = 0) {
  const u = state.board[r][c];
  if (!u || dmg <= 0) return false;
  let finalDmg = dmg;
  if (u.isGeneral) {
    const arts = u.owner === 'player' ? state.pArtifacts : state.eArtifacts;
    if (arts.some(a => a.art === 'artifact_regalia')) finalDmg = Math.max(0, finalDmg - 2);
    if (finalDmg > 0) damageArtifacts(u.owner);
  }
  u.hp -= finalDmg;
  u.flashT = 12;
  u.animX += dirX * 16;
  spawnFloatText(r, c, `-${finalDmg}`, color);
  spawnDirectionalSparks(r, c, dirX, color, 20);
  if (finalDmg >= 3) {
    spawnStarburst(r, c, color);
    spawnDecal(r, c, 'crack');
    triggerShake(9);
  }
  if (u.hp <= 0) {
    addLog(`💥 [${u.name}] 처치됨!`);
    spawnDeathBurst(r, c, u.owner === 'player' ? '#38bdf8' : '#f43f5e');
    state.board[r][c] = null;
    if (!u.isGeneral) onMinionDied(u, r, c);
    return true;
  }
  return false;
}

function moveUnit(r1, c1, r2, c2) {
  const u = state.board[r1][c1];
  state.board[r2][c2] = u;
  state.board[r1][c1] = null;
  u.movesLeft = Math.max(0, u.movesLeft - 1);
  u.animX = (c1 - c2) * 46;
  u.animY = (r1 - r2) * 38;
  spawnRing(r2, c2, '#38bdf8', 40);
  checkOrbPickup(r2, c2, u.owner);
}

function attackUnit(r1, c1, r2, c2) {
  const atkU = state.board[r1][c1];
  const defU = state.board[r2][c2];
  if (!atkU || !defU) return;

  atkU.attacksLeft = Math.max(0, atkU.attacksLeft - 1);
  if (!atkU.keywords.includes('celerity')) atkU.movesLeft = 0;

  const dirX = Math.sign(c2 - c1) || (atkU.owner === 'player' ? 1 : -1);
  const isRanged = atkU.keywords.includes('ranged');
  const isBlast = atkU.keywords.includes('blast');
  const isFrenzy = atkU.keywords.includes('frenzy');
  const backstab = isBackstabPosition(atkU, r1, c1, r2, c2);

  const effAtk = getEffectiveAtk(atkU, r1, c1) + (backstab ? 2 : 0);
  const simultaneousCounter = getEffectiveAtk(defU, r2, c2);
  const shouldCounter = !isRanged && !isBlast && !backstab && !defU.keywords.includes('structure');

  if (isBlast) {
    const endCol = dirX > 0 ? COLS - 1 : 0;
    spawnBlastBeam(r1, c1, r1, endCol);
    triggerScreenFlash('#14b8a6', 0.16);
    triggerShake(10);
  } else if (isRanged) {
    spawnProjectile(r1, c1, r2, c2, '#38bdf8');
    triggerShake(5);
  } else {
    atkU.animX = dirX * 50;
    atkU.animY = Math.sign(r2 - r1) * 32;
    state.hitstop = 3;
    if (backstab) {
      spawnBackstabX(r2, c2);
      spawnFloatText(r2, c2, 'BACKSTAB!', '#f43f5e');
      triggerScreenFlash('#f43f5e', 0.22);
      triggerShake(11);
    } else if (isFrenzy) {
      spawnWhirlwind(r1, c1);
      spawnArcSlash(r2, c2, dirX, '#10b981', 1.35);
      triggerScreenFlash('#10b981', 0.15);
      triggerShake(10);
    } else {
      spawnArcSlash(r2, c2, dirX, '#fef08a', 1.25);
      spawnRing(r2, c2, '#fbbf24', 60);
      triggerShake(8);
    }
  }

  const victims = [{ r: r2, c: c2 }];
  if (isBlast) {
    const step = Math.sign(c2 - c1);
    for (let tc = c1 + step; tc >= 0 && tc < COLS; tc += step) {
      if (tc === c2) continue;
      const bu = state.board[r1][tc];
      if (bu && bu.owner !== atkU.owner) victims.push({ r: r1, c: tc });
    }
  } else if (isFrenzy && !isRanged) {
    for (const n of neighbors8(r1, c1)) {
      const adj = state.board[n.r][n.c];
      if (adj && adj.owner !== atkU.owner && !(n.r === r2 && n.c === c2)) victims.push(n);
    }
  }

  let anyKilled = false;
  for (const v of victims) {
    const target = state.board[v.r][v.c];
    if (!target) continue;
    const wasMinion = !target.isGeneral;
    if (isBlast) spawnRing(v.r, v.c, '#14b8a6', 54);
    if (dealDamageToUnit(v.r, v.c, effAtk, isBlast ? '#14b8a6' : (backstab ? '#f43f5e' : '#ef4444'), dirX)) anyKilled = true;
    if (atkU.keywords.includes('revenant_passive') && wasMinion) {
      const oppG = findGeneral(atkU.owner === 'player' ? 'enemy' : 'player');
      if (oppG) {
        spawnVoidVortex(oppG.r, oppG.c);
        dealDamageToUnit(oppG.r, oppG.c, 4, '#c084fc', dirX);
      }
    }
  }

  if (anyKilled && atkU.isGeneral) {
    const arts = atkU.owner === 'player' ? state.pArtifacts : state.eArtifacts;
    if (arts.some(a => a.art === 'artifact_void')) healUnit(r1, c1, 2);
  }

  if (shouldCounter && simultaneousCounter > 0) {
    spawnArcSlash(r1, c1, -dirX, '#fb923c', 1.1);
    dealDamageToUnit(r1, c1, simultaneousCounter, '#fb923c', -dirX);
  }

  addLog(`⚔️ ${atkU.name} ↔ ${defU.name} 교전 (${effAtk} / ${shouldCounter ? simultaneousCounter : 0})`);
  checkGameOver();
}

// =========================================================================
// 5. 수동 전투의 함성 & 소환 · 마법 시스템
// =========================================================================
function enterManualGambitIfNeeded(unit, r, c) {
  if (unit.owner !== 'player') return;
  const kws = unit.keywords;
  if (kws.includes('gambit_ping1')) {
    const hasEnemy = state.board.some(row => row.some(u => u && u.owner === 'enemy'));
    if (hasEnemy) {
      state.targetMode = { kind: 'gambit_ping1', src: { r, c } };
      addLog('🎯 [함성] 1 피해를 입힐 적을 클릭하세요!');
    }
  } else if (kws.includes('gambit_heal2') || kws.includes('gambit_heal4')) {
    const amt = kws.includes('gambit_heal4') ? 4 : 2;
    state.targetMode = { kind: 'gambit_heal', amount: amt, src: { r, c } };
    addLog(`💚 [함성] 체력 +${amt} 회복할 유닛/장군을 클릭하세요!`);
  } else if (kws.includes('gambit_buff2')) {
    const hasAlly = state.board.some(row => row.some(u => u && u.owner === 'player' && !u.isGeneral));
    if (hasAlly) {
      state.targetMode = { kind: 'gambit_buff2', src: { r, c } };
      addLog('⚔️ [함성] 공격력 +2 부여할 아군 하수인을 클릭하세요!');
    }
  } else if (kws.includes('gambit_repulse')) {
    const hasEnemyMinion = state.board.some(row => row.some(u => u && u.owner === 'enemy' && !u.isGeneral));
    if (hasEnemyMinion) {
      state.targetMode = { kind: 'gambit_repulse_1', src: { r, c } };
      addLog('🌀 [함성] 추방할 적 하수인을 클릭하세요!');
    }
  }
}

function triggerImmediateGambit(unit, r, c) {
  const owner = unit.owner;
  const opp = owner === 'player' ? 'enemy' : 'player';

  if (unit.keywords.includes('gambit_creep')) {
    if (!state.creepTiles.some(t => t.r === r && t.c === c)) state.creepTiles.push({ r, c, owner });
    spawnVoidVortex(r, c);
  }
  if (unit.keywords.includes('gambit_front3')) {
    const fc = c + (owner === 'player' ? 1 : -1);
    if (fc >= 0 && fc < COLS && state.board[r][fc] && state.board[r][fc].owner === opp) {
      spawnArcSlash(r, fc, owner === 'player' ? 1 : -1, '#f43f5e', 1.35);
      dealDamageToUnit(r, fc, 3, '#f43f5e', owner === 'player' ? 1 : -1);
    }
  }
  if (owner === 'enemy') {
    const g = findGeneral('enemy');
    const pg = findGeneral('player');
    if (unit.keywords.includes('gambit_ping1') && pg) {
      spawnProjectile(r, c, pg.r, pg.c, '#c084fc');
      dealDamageToUnit(pg.r, pg.c, 1, '#c084fc', -1);
    }
    if ((unit.keywords.includes('gambit_heal2') || unit.keywords.includes('gambit_heal4')) && g) {
      healUnit(g.r, g.c, unit.keywords.includes('gambit_heal4') ? 4 : 2);
    }
    if (unit.keywords.includes('gambit_buff2')) {
      for (let ar = 0; ar < ROWS; ar++) for (let ac = 0; ac < COLS; ac++) {
        const au = state.board[ar][ac];
        if (au && au.owner === 'enemy' && !au.isGeneral) { au.atk += 2; spawnHealHelix(ar, ac, '#fbbf24'); break; }
      }
    }
  }
  checkGameOver();
}

function summonMinion(card, r, c, owner) {
  const rush = card.keywords.includes('rush');
  const celerity = card.keywords.includes('celerity');
  const isStruct = card.keywords.includes('structure');
  const unit = createUnitObj({
    name: card.name, owner, isGeneral: false, sprite: card.sprite,
    atk: card.atk, hp: card.hp, maxHp: card.hp,
    keywords: [...card.keywords], stunned: false,
    movesLeft: (rush && !isStruct) ? (celerity ? 2 : 1) : 0,
    attacksLeft: (rush && !isStruct) ? (celerity ? 2 : 1) : 0
  });
  state.board[r][c] = unit;
  spawnPillar(r, c, owner === 'player' ? '#38bdf8' : '#f43f5e');
  spawnRing(r, c, '#10b981', 56);
  spawnFloatText(r, c, card.name, '#34d399');
  addLog(`✨ ${owner === 'player' ? '아군' : '적'} [${card.name}] (${COL_LABELS[c]}${r + 1}) 배치!`);
  checkOrbPickup(r, c, owner);
  triggerImmediateGambit(unit, r, c);
  enterManualGambitIfNeeded(unit, r, c);
}

function equipArtifact(card, owner) {
  const g = findGeneral(owner);
  if (!g) return;
  const list = owner === 'player' ? state.pArtifacts : state.eArtifacts;
  if (list.length >= 3) list.shift();
  list.push({ name: card.name, atkBonus: card.atkBonus, dur: 3, art: card.art });
  recalcGeneralStats(owner);
  spawnPillar(g.r, g.c, '#fbbf24');
  spawnHealHelix(g.r, g.c, '#fbbf24');
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

function triggerSpellSurge(owner) {
  const oppG = findGeneral(owner === 'player' ? 'enemy' : 'player');
  const myG = findGeneral(owner);
  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const u = state.board[r][c];
    if (!u || u.owner !== owner) continue;
    if (u.keywords.includes('spell_grow')) {
      u.atk += 1; u.hp += 1; u.maxHp += 1;
      spawnHealHelix(r, c, '#fb923c');
      spawnFloatText(r, c, '+1/+1', '#fb923c');
    }
    if (u.keywords.includes('spell_ping')) {
      if (oppG) dealDamageToUnit(oppG.r, oppG.c, 1, '#f43f5e', owner === 'player' ? 1 : -1);
      if (myG) healUnit(myG.r, myG.c, 1);
    }
  }
}

function castSpell(card, r, c, owner, step2Pos = null) {
  const sp = card.spell;
  const t = state.board[r][c];
  const g = findGeneral(owner);
  const opp = owner === 'player' ? 'enemy' : 'player';
  const oppG = findGeneral(opp);
  if (g) spawnProjectile(g.r, g.c, r, c, '#c084fc');
  triggerShake(6);

  if (sp === 'divine_bond' && t) {
    t.atk += t.hp; spawnPillar(r, c, '#fef08a'); spawnHealHelix(r, c, '#fbbf24'); spawnFloatText(r, c, `+${t.hp} ATK!`, '#fbbf24');
  } else if (sp === 'holy_immolation' && t) {
    spawnPillar(r, c, '#fef08a'); triggerScreenFlash('#fef08a', 0.22);
    healUnit(r, c, 4);
    for (const n of neighbors8(r, c)) {
      const adj = state.board[n.r][n.c];
      if (adj && adj.owner !== owner) dealDamageToUnit(n.r, n.c, 4, '#fbbf24', Math.sign(n.c - c));
    }
  } else if (sp === 'martyrdom' && t) {
    const heal = t.hp;
    const tGen = findGeneral(t.owner);
    spawnDeathBurst(r, c, '#fef08a');
    state.board[r][c] = null;
    if (tGen) healUnit(tGen.r, tGen.c, heal);
  } else if (sp === 'tempest') {
    triggerScreenFlash('#38bdf8', 0.24);
    for (let tr = 0; tr < ROWS; tr++) for (let tc = 0; tc < COLS; tc++) {
      if (state.board[tr][tc]) {
        spawnLightning(tr, tc, '#38bdf8');
        dealDamageToUnit(tr, tc, 2, '#fbbf24', 0);
      }
    }
  } else if (sp === 'phoenix_fire' && t) {
    spawnStarburst(r, c, '#f97316');
    spawnDecal(r, c, 'scorch');
    dealDamageToUnit(r, c, 3, '#f97316', owner === 'player' ? 1 : -1); drawCards(owner, 1);
  } else if (sp === 'inner_focus' && t) {
    const cel = t.keywords.includes('celerity');
    t.movesLeft = cel ? 2 : 1; t.attacksLeft = cel ? 2 : 1; t.stunned = false;
    spawnPillar(r, c, '#38bdf8'); spawnHealHelix(r, c, '#38bdf8'); spawnFloatText(r, c, 'REACTIVATE!', '#38bdf8');
  } else if (sp === 'juxtaposition' && t && step2Pos) {
    const t2 = state.board[step2Pos.r][step2Pos.c];
    state.board[step2Pos.r][step2Pos.c] = t;
    state.board[r][c] = t2;
    spawnVoidVortex(r, c); spawnVoidVortex(step2Pos.r, step2Pos.c);
  } else if (sp === 'ghost_lightning') {
    for (let er = 0; er < ROWS; er++) for (let ec = 0; ec < COLS; ec++) {
      const eu = state.board[er][ec];
      if (eu && eu.owner !== owner && !eu.isGeneral) {
        spawnLightning(er, ec, '#f43f5e');
        dealDamageToUnit(er, ec, 1, '#f43f5e', 0);
      }
    }
  } else if (sp === 'scions_wish' && t) {
    t.atk += 2; t.hp += 2; t.maxHp += 2;
    spawnPillar(r, c, '#14b8a6'); spawnHealHelix(r, c, '#14b8a6'); spawnFloatText(r, c, '+2/+2', '#14b8a6'); drawCards(owner, 1);
  } else if (sp === 'entropic_decay' && t) {
    spawnLightning(r, c, '#14b8a6'); spawnDeathBurst(r, c, '#14b8a6'); state.board[r][c] = null;
  } else if (sp === 'stars_fury') {
    triggerScreenFlash('#14b8a6', 0.18);
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
    spawnStarburst(oppG.r, oppG.c, '#d97706');
    spawnDecal(oppG.r, oppG.c, 'scorch');
    dealDamageToUnit(oppG.r, oppG.c, 2, '#d97706', 0);
    for (const n of neighbors8(oppG.r, oppG.c)) {
      const adj = state.board[n.r][n.c];
      if (adj && adj.owner !== owner) dealDamageToUnit(n.r, n.c, 2, '#d97706', 0);
    }
  } else if (sp === 'shadow_nova') {
    triggerScreenFlash('#9333ea', 0.22);
    for (let dr = 0; dr <= 1; dr++) for (let dc = 0; dc <= 1; dc++) {
      const nr = Math.min(ROWS - 1, r + dr), nc = Math.min(COLS - 1, c + dc);
      if (!state.creepTiles.some(ct => ct.r === nr && ct.c === nc)) state.creepTiles.push({ r: nr, c: nc, owner });
      spawnVoidVortex(nr, nc);
      const eu = state.board[nr][nc];
      if (eu && eu.owner !== owner) dealDamageToUnit(nr, nc, 2, '#9333ea', 0);
    }
  } else if (sp === 'void_pulse' && t) {
    spawnVoidVortex(r, c);
    dealDamageToUnit(r, c, 2, '#c084fc', 0);
    if (g) healUnit(g.r, g.c, 3);
  } else if (sp === 'daemonic_lure' && t && step2Pos) {
    spawnVoidVortex(r, c);
    const dead = dealDamageToUnit(r, c, 1, '#c084fc', 0);
    if (!dead && state.board[r][c]) {
      state.board[step2Pos.r][step2Pos.c] = state.board[r][c]; state.board[r][c] = null;
      spawnVoidVortex(step2Pos.r, step2Pos.c);
    }
  } else if (sp === 'soulshatter') {
    triggerScreenFlash('#c084fc', 0.16);
    for (let ar = 0; ar < ROWS; ar++) for (let ac = 0; ac < COLS; ac++) {
      const au = state.board[ar][ac];
      if (au && au.owner === owner && !au.isGeneral) { au.atk += 2; spawnHealHelix(ar, ac, '#e879f9'); spawnFloatText(ar, ac, '+2 ATK', '#e879f9'); }
    }
  } else if (sp === 'natural_select' && t) {
    spawnVoidVortex(r, c); spawnDeathBurst(r, c, '#10b981'); state.board[r][c] = null;
  } else if (sp === 'plasma_storm') {
    triggerScreenFlash('#10b981', 0.24);
    for (let mr = 0; mr < ROWS; mr++) for (let mc = 0; mc < COLS; mc++) {
      const mu = state.board[mr][mc];
      if (mu && !mu.isGeneral && getEffectiveAtk(mu, mr, mc) <= 3) {
        spawnLightning(mr, mc, '#10b981'); spawnDeathBurst(mr, mc, '#10b981'); state.board[mr][mc] = null;
      }
    }
  } else if (sp === 'egg_morph' && t) {
    if (t.hatchesInto) {
      const cel = t.hatchesInto.keywords.includes('celerity');
      state.board[r][c] = createUnitObj({ ...t.hatchesInto, movesLeft: cel ? 2 : 1, attacksLeft: cel ? 2 : 1 });
      spawnPillar(r, c, '#10b981');
      spawnFloatText(r, c, 'HATCHED!', '#6ee7b7');
    } else {
      state.board[r][c] = createUnitObj({
        name: '변이된 알', owner: t.owner, isGeneral: false, sprite: 'egg',
        atk: 0, hp: 1, maxHp: 1, keywords: ['structure'], stunned: false, movesLeft: 0, attacksLeft: 0
      });
      spawnRing(r, c, '#10b981', 50);
      spawnFloatText(r, c, 'EGG MORPH!', '#10b981');
    }
  } else if (sp === 'earth_sphere' && g) {
    spawnPillar(g.r, g.c, '#10b981');
    healUnit(g.r, g.c, 7);
  } else if (sp === 'gravity_well') {
    for (const dr of [-1, 0, 1]) {
      const nr = r + dr;
      if (nr >= 0 && nr < ROWS && !state.board[nr][c]) {
        state.board[nr][c] = createUnitObj({
          name: '빙하의 방벽', owner, isGeneral: false, sprite: 'wall',
          atk: 0, hp: 3, maxHp: 3, keywords: ['structure', 'provoke'], stunned: false, movesLeft: 0, attacksLeft: 0
        });
        spawnIceSpikes(nr, c);
      }
    }
  } else if (sp === 'chromatic_cold' && t) {
    t.keywords = []; t.hatchesInto = null;
    spawnIceSpikes(r, c);
    spawnFloatText(r, c, 'DISPELLED!', '#bae6fd'); dealDamageToUnit(r, c, 2, '#38bdf8', 0);
  } else if (sp === 'hailstone' && t) {
    const tHand = t.owner === 'player' ? state.pHand : state.eHand;
    if (tHand.length < 6) {
      tHand.push({
        name: t.name, type: 'minion', cost: Math.max(1, Math.min(6, Math.round((t.atk + t.maxHp) / 2))),
        atk: t.atk, hp: t.maxHp, sprite: t.sprite, keywords: [...t.keywords], desc: '우박 감옥에서 귀환한 하수인입니다.'
      });
    }
    spawnIceSpikes(r, c); state.board[r][c] = null;
  } else if (sp === 'aspect_fox' && t) {
    state.board[r][c] = createUnitObj({
      name: '서리 여우', owner: t.owner, isGeneral: false, sprite: 'wolf',
      atk: 3, hp: 3, maxHp: 3, keywords: [], stunned: false, movesLeft: 0, attacksLeft: 0
    });
    spawnIceSpikes(r, c);
  } else if (sp === 'avalanche') {
    triggerScreenFlash('#38bdf8', 0.25);
    for (let ar = 0; ar < ROWS; ar++) for (let ac = 0; ac <= 3; ac++) {
      spawnIceSpikes(ar, ac);
      const au = state.board[ar][ac];
      if (au && au.owner !== owner) { au.stunned = true; dealDamageToUnit(ar, ac, 4, '#38bdf8', 0); }
    }
  }

  triggerSpellSurge(owner);
  addLog(`🔮 [${card.name}] 시전!`);
  checkGameOver();
}

function processTurnStartEffects(owner) {
  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const u = state.board[r][c];
    if (!u || u.owner !== owner) continue;

    if (u.hatchesInto) {
      const cel = u.hatchesInto.keywords.includes('celerity');
      state.board[r][c] = createUnitObj({ ...u.hatchesInto, movesLeft: cel ? 2 : 1, attacksLeft: cel ? 2 : 1 });
      spawnPillar(r, c, '#10b981');
      spawnFloatText(r, c, '🥚 HATCHED!', '#6ee7b7');
      continue;
    }
    if (u.keywords.includes('grow1')) {
      u.atk += 1; u.hp += 1; u.maxHp += 1;
      spawnHealHelix(r, c, '#6ee7b7');
      spawnFloatText(r, c, 'GROW +1/+1', '#6ee7b7');
    }
    if (u.keywords.includes('spawn_dervish')) {
      const empties = neighbors8(r, c).filter(n => !state.board[n.r][n.c]);
      if (empties.length) {
        const pos = empties[Math.floor(Math.random() * empties.length)];
        summonMinion({ name: '바람의 데르비시', atk: 2, hp: 2, sprite: 'dervish', keywords: ['rush'] }, pos.r, pos.c, owner);
      }
    }
  }
}

function processTurnEndEffects(owner) {
  const myCreepCount = state.creepTiles.filter(ct => ct.owner === owner).length;
  if (myCreepCount > 0) {
    for (const ct of state.creepTiles) {
      if (ct.owner !== owner) continue;
      const victim = state.board[ct.r][ct.c];
      if (victim && victim.owner !== owner) {
        spawnVoidVortex(ct.r, ct.c);
        dealDamageToUnit(ct.r, ct.c, myCreepCount, '#c084fc', 0);
      }
    }
  }
  checkGameOver();
}

// =========================================================================
// 6. BBS 스킬 & 턴 종료 AI
// =========================================================================
function triggerBBS(owner) {
  if (!state.useBbsMode) return false;
  const fac = owner === 'player' ? state.playerFaction : state.enemyFaction;
  const mana = owner === 'player' ? state.pMana : state.eMana;
  const cd = owner === 'player' ? state.pBbsCd : state.eBbsCd;
  if (cd > 0 || mana < fac.bbsCost) return false;
  const g = findGeneral(owner);
  if (!g) return false;

  if (fac.id === 'vaath') {
    g.unit.baseAtk += 1; recalcGeneralStats(owner);
    spawnPillar(g.r, g.c, '#10b981'); spawnHealHelix(g.r, g.c, '#10b981'); spawnFloatText(g.r, g.c, '+1 ATK', '#10b981');
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
      spawnLightning(r, oppG.c, '#38bdf8');
      const u = state.board[r][oppG.c];
      if (u && u.owner !== owner) dealDamageToUnit(r, oppG.c, 2, '#38bdf8', 0);
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
      allies[0].u.atk += 2;
      spawnHealHelix(allies[0].r, allies[0].c, '#fbbf24');
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

function endPlayerTurn() {
  if (state.winner || state.aiBusy || state.targetMode) return;
  processTurnEndEffects('player');
  if (state.winner) return;

  const diff = DIFFICULTIES[state.difficultyIdx].id;
  state.aiBusy = true;
  state.selectedPos = null; state.selectedCardIdx = null; state.replaceMode = false;

  state.eMaxMana = Math.min(9, state.eMaxMana + 1);
  state.eMana = state.eMaxMana;
  if (state.eBbsCd > 0) state.eBbsCd--;
  drawCards('enemy', 2);

  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const u = state.board[r][c];
    if (u && u.owner === 'enemy') {
      if (!u.keywords.includes('structure')) {
        const cel = u.keywords.includes('celerity');
        u.movesLeft = cel ? 2 : 1;
        u.attacksLeft = cel ? 2 : 1;
      }
      u.stunned = false;
    }
  }
  processTurnStartEffects('enemy');

  const steps = [];
  steps.push(() => {
    for (let idx = state.eHand.length - 1; idx >= 0; idx--) {
      if (diff === 'easy' && Math.random() < 0.35) continue;
      const card = state.eHand[idx];
      if (card.cost > state.eMana) continue;

      if (card.type === 'minion') {
        const tiles = getValidSummonTiles('enemy', card);
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
        if (['daemonic_lure', 'juxtaposition'].includes(card.spell)) continue;
        const targets = getValidSpellTargets(card, 'enemy');
        if (targets.length) {
          targets.sort((a, b) => {
            const ua = state.board[a.r][a.c], ub = state.board[b.r][b.c];
            if (!ua || !ub) return 0;
            return (ub.isGeneral ? 50 : getEffectiveAtk(ub, b.r, b.c)) - (ua.isGeneral ? 50 : getEffectiveAtk(ua, a.r, a.c));
          });
          state.eMana -= card.cost; state.eHand.splice(idx, 1);
          castSpell(card, targets[0].r, targets[0].c, 'enemy');
        }
      }
    }
  });

  steps.push(() => { if (!state.winner && state.useBbsMode && diff !== 'easy') triggerBBS('enemy'); });

  steps.push(() => {
    if (state.winner) return;
    const units = [];
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const u = state.board[r][c];
      if (u && u.owner === 'enemy' && !u.keywords.includes('structure')) units.push({ r, c });
    }
    for (const pos of units) {
      if (state.winner) break;
      const u = state.board[pos.r][pos.c];
      if (!u || u.owner !== 'enemy' || u.stunned) continue;

      const pg = findGeneral('player') || { r: 2, c: 0, unit: { hp: 25 } };
      let atks = getValidAttacks(pos.r, pos.c);

      if (atks.length) {
        const myDmg = getEffectiveAtk(u, pos.r, pos.c);
        const lethal = atks.find(a => state.board[a.r][a.c].isGeneral && state.board[a.r][a.c].hp <= myDmg);
        if (lethal && (diff === 'hard' || diff === 'master')) {
          attackUnit(pos.r, pos.c, lethal.r, lethal.c);
          continue;
        }
        const eggTarget = atks.find(a => state.board[a.r][a.c].hatchesInto);
        if (eggTarget && (diff === 'hard' || diff === 'master')) {
          attackUnit(pos.r, pos.c, eggTarget.r, eggTarget.c);
          continue;
        }
        atks.sort((a, b) => state.board[a.r][a.c].hp - state.board[b.r][b.c].hp);
        attackUnit(pos.r, pos.c, atks[0].r, atks[0].c);
        continue;
      }

      const moves = getValidMoves(pos.r, pos.c);
      if (moves.length) {
        moves.sort((a, b) => {
          const orbA = (diff !== 'easy' && state.manaOrbs.some(o => o.r === a.r && o.c === a.c)) ? -6 : 0;
          const orbB = (diff !== 'easy' && state.manaOrbs.some(o => o.r === b.r && o.c === b.c)) ? -6 : 0;
          if (u.isGeneral && u.hp <= 9 && diff !== 'easy') return (b.c + orbB) - (a.c + orbA);
          return (Math.abs(a.r - pg.r) + Math.abs(a.c - pg.c) + orbA) - (Math.abs(b.r - pg.r) + Math.abs(b.c - pg.c) + orbB);
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

  steps.push(() => {
    if (!state.winner) {
      processTurnEndEffects('enemy');
      if (!state.winner) {
        state.turn++;
        state.pMaxMana = Math.min(9, state.pMaxMana + 1);
        state.pMana = state.pMaxMana;
        if (state.pBbsCd > 0) state.pBbsCd--;
        state.replacedThisTurn = false;
        drawCards('player', 2);
        for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
          const u = state.board[r][c];
          if (u && u.owner === 'player') {
            if (!u.keywords.includes('structure')) {
              const cel = u.keywords.includes('celerity');
              u.movesLeft = cel ? 2 : 1;
              u.attacksLeft = cel ? 2 : 1;
            }
            u.stunned = false;
          }
        }
        processTurnStartEffects('player');
        addLog(`🔵 TURN ${state.turn} — 당신의 차례`);
      }
    }
    state.aiBusy = false;
  });

  steps.forEach((fn, i) => setTimeout(fn, (i + 1) * 420));
}

// =========================================================================
// 7. 입력 처리
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
      if (inside(x, y, cx, 92, 184, 130)) state.selectedFaction = fid;
    });
    DIFFICULTIES.forEach((d, idx) => {
      const dx = 55 + idx * 145;
      if (inside(x, y, dx, 708, 136, 50)) state.difficultyIdx = idx;
    });
    if (inside(x, y, 645, 708, 200, 50)) state.useBbsMode = !state.useBbsMode;
    if (inside(x, y, 855, 708, 175, 50)) {
      const opts = ['random', ...keys];
      state.enemyChoice = opts[(opts.indexOf(state.enemyChoice) + 1) % opts.length];
    }
    if (inside(x, y, 1040, 708, 185, 50)) startBattle(state.selectedFaction, state.enemyChoice);
    return;
  }

  if (state.screen === 'mulligan') {
    for (let i = 0; i < state.pHand.length; i++) {
      const cx = 175 + i * 190;
      if (inside(x, y, cx, 260, 172, 265)) {
        if (state.mulliganSelected.has(i)) state.mulliganSelected.delete(i);
        else if (state.mulliganSelected.size < 2) state.mulliganSelected.add(i);
        return;
      }
    }
    if (inside(x, y, W / 2 - 165, 580, 330, 64)) confirmMulligan();
    return;
  }

  if (state.winner) {
    if (inside(x, y, W / 2 - 150, H / 2 + 40, 300, 58)) state.screen = 'select';
    return;
  }
  if (state.aiBusy) return;

  if (state.targetMode && inside(x, y, 1135, 585, 115, 115)) {
    state.targetMode = null;
    addLog('⏭️ 대상 지정 건너뜀');
    return;
  }

  if (state.useBbsMode && inside(x, y, 225, 24, 72, 72)) {
    if (state.targetMode) state.targetMode = null;
    else triggerBBS('player');
    return;
  }
  if (inside(x, y, 55, 585, 118, 185)) {
    if (!state.replacedThisTurn && state.pDeck.length > 0 && !state.targetMode) {
      state.replaceMode = !state.replaceMode;
      state.selectedCardIdx = null; state.selectedPos = null;
    }
    return;
  }
  if (inside(x, y, 1135, 585, 115, 115)) { endPlayerTurn(); return; }
  if (inside(x, y, 1135, 710, 115, 60)) { state.screen = 'select'; return; }

  for (let i = 0; i < state.pHand.length; i++) {
    const cx = 195 + i * 155;
    if (inside(x, y, cx, 560, 146, 230)) {
      if (state.targetMode) return;
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
      state.selectedPos = null;
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
      if (tm.kind === 'gambit_ping1') {
        if (u && u.owner === 'enemy') {
          spawnProjectile(tm.src.r, tm.src.c, r, c, '#c084fc');
          dealDamageToUnit(r, c, 1, '#c084fc', 1);
          checkGameOver();
          state.targetMode = null;
        }
        return;
      }
      if (tm.kind === 'gambit_heal') {
        if (u && u.owner === 'player') {
          healUnit(r, c, tm.amount);
          state.targetMode = null;
        }
        return;
      }
      if (tm.kind === 'gambit_buff2') {
        if (u && u.owner === 'player' && !u.isGeneral) {
          u.atk += 2;
          spawnHealHelix(r, c, '#fbbf24');
          spawnFloatText(r, c, '+2 ATK', '#fbbf24');
          state.targetMode = null;
        }
        return;
      }
      if (tm.kind === 'gambit_repulse_1') {
        if (u && u.owner === 'enemy' && !u.isGeneral) {
          state.targetMode = { kind: 'gambit_repulse_2', enemyPos: { r, c } };
          addLog('🌀 적을 추방할 빈 칸을 클릭하세요!');
        }
        return;
      }
      if (tm.kind === 'gambit_repulse_2') {
        if (!u) {
          const ep = tm.enemyPos;
          state.board[r][c] = state.board[ep.r][ep.c];
          state.board[ep.r][ep.c] = null;
          spawnProjectile(ep.r, ep.c, r, c, '#38bdf8');
          spawnVoidVortex(r, c);
          state.targetMode = null;
        }
        return;
      }
      if (tm.kind === 'bbs_argeon') {
        const pg = findGeneral('player');
        if (u && u.owner === 'player' && !u.isGeneral && pg && Math.abs(r - pg.r) <= 1 && Math.abs(c - pg.c) <= 1) {
          u.atk += 2; state.pMana -= state.playerFaction.bbsCost; state.pBbsCd = 2;
          spawnHealHelix(r, c, '#fbbf24'); spawnFloatText(r, c, '+2 ATK', '#fbbf24');
        }
        state.targetMode = null; return;
      }
      if (tm.kind === 'bbs_kaleos_1') {
        if (u && u.owner === 'player' && !u.isGeneral && !u.keywords.includes('structure')) {
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
          spawnVoidVortex(r, c); checkOrbPickup(r, c, 'player');
        }
        state.targetMode = null; return;
      }
      if (tm.kind === 'spell_step2') {
        const card = state.pHand[tm.cardIdx];
        if (card.spell === 'juxtaposition') {
          if (u && !u.isGeneral && !(r === tm.firstPos.r && c === tm.firstPos.c)) {
            state.pMana -= card.cost; state.pHand.splice(tm.cardIdx, 1);
            castSpell(card, tm.firstPos.r, tm.firstPos.c, 'player', { r, c });
          }
        } else if (!u) {
          state.pMana -= card.cost; state.pHand.splice(tm.cardIdx, 1);
          castSpell(card, tm.firstPos.r, tm.firstPos.c, 'player', { r, c });
        }
        state.targetMode = null; state.selectedCardIdx = null; return;
      }
    }

    if (state.selectedCardIdx !== null) {
      const card = state.pHand[state.selectedCardIdx];
      if (card.cost <= state.pMana) {
        if (card.type === 'minion' && getValidSummonTiles('player', card).some(t => t.r === r && t.c === c)) {
          state.pMana -= card.cost; state.pHand.splice(state.selectedCardIdx, 1);
          summonMinion(card, r, c, 'player'); state.selectedCardIdx = null; return;
        }
        if (card.type === 'artifact') {
          state.pMana -= card.cost; state.pHand.splice(state.selectedCardIdx, 1);
          equipArtifact(card, 'player'); state.selectedCardIdx = null; return;
        }
        if (card.type === 'spell' && getValidSpellTargets(card, 'player').some(t => t.r === r && t.c === c)) {
          if (['daemonic_lure', 'juxtaposition'].includes(card.spell)) {
            state.targetMode = { kind: 'spell_step2', cardIdx: state.selectedCardIdx, firstPos: { r, c } };
            addLog(card.spell === 'juxtaposition' ? '✨ 위치를 맞바꿀 두 번째 하수인을 클릭하세요!' : '✨ 이동시킬 목적지 빈 칸을 클릭하세요!');
            return;
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
        attackUnit(sp.r, sp.c, r, c);
        if (state.board[sp.r][sp.c] && state.board[sp.r][sp.c].attacksLeft > 0) state.selectedPos = { r: sp.r, c: sp.c };
        else state.selectedPos = null;
        return;
      }
    }

    if (u && u.owner === 'player') { state.selectedPos = { r, c }; state.selectedCardIdx = null; }
    else state.selectedPos = null;
  }
});

// =========================================================================
// 8. 고해상도 아트 · 2.5D 전장 · 전술 예측 · 다중 레이어 이펙트 렌더링
// =========================================================================
function roundRect(x, y, w, h, r, fill, stroke, lw = 2) {
  ctx.beginPath(); ctx.roundRect(x, y, w, h, r);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.stroke(); }
}

function drawUnitSprite(key, cx, cy, size, flipX = false, mode = 'normal', alpha = 1.0) {
  const sp = SPRITES[key] || SPRITES.paladin;
  const frameIdx = Math.floor(state.tick / 14) % 4;
  const img = mode === 'flash' ? sp.flash : (mode === 'ghost' ? sp.ghost : sp.frames[frameIdx]);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.imageSmoothingEnabled = false;
  ctx.translate(cx, cy);
  if (flipX) ctx.scale(-1, 1);
  ctx.drawImage(img, -size / 2, -size / 2, size, size);
  ctx.restore();
}

function drawCardArt(card, x, y, w, h, isHovered = false) {
  ctx.save();
  ctx.beginPath(); ctx.roundRect(x, y, w, h, 5); ctx.clip();
  const cx = x + w / 2, cy = y + h / 2;

  const grad = ctx.createLinearGradient(x, y, x, y + h);
  if (card.type === 'spell') {
    const vfx = card.vfx || 'void';
    if (vfx === 'fire') { grad.addColorStop(0, '#9a3412'); grad.addColorStop(1, '#070a12'); }
    else if (vfx === 'ice') { grad.addColorStop(0, '#075985'); grad.addColorStop(1, '#070a12'); }
    else if (vfx === 'holy') { grad.addColorStop(0, '#854d0e'); grad.addColorStop(1, '#070a12'); }
    else if (vfx === 'lightning') { grad.addColorStop(0, '#1d4ed8'); grad.addColorStop(1, '#070a12'); }
    else { grad.addColorStop(0, '#581c87'); grad.addColorStop(1, '#070a12'); }
    ctx.fillStyle = grad; ctx.fillRect(x, y, w, h);

    if (vfx === 'fire') {
      const fg = ctx.createRadialGradient(cx, cy + 4, 2, cx, cy, 34);
      fg.addColorStop(0, '#ffffff'); fg.addColorStop(0.4, '#fef08a'); fg.addColorStop(0.75, '#f97316'); fg.addColorStop(1, 'rgba(249,115,22,0)');
      ctx.fillStyle = fg; ctx.beginPath(); ctx.arc(cx, cy, 34, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#fde047'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(cx, cy, 18, 0, Math.PI * 2); ctx.stroke();
    } else if (vfx === 'ice') {
      ctx.fillStyle = '#bae6fd';
      for (let i = -3; i <= 3; i++) {
        const sh = (4 - Math.abs(i)) * 9;
        ctx.beginPath(); ctx.moveTo(cx + i * 10 - 4, y + h); ctx.lineTo(cx + i * 10, cy + 16 - sh); ctx.lineTo(cx + i * 10 + 4, y + h); ctx.fill();
      }
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(cx, cy - 22); ctx.lineTo(cx, cy + 10); ctx.stroke();
    } else if (vfx === 'lightning') {
      ctx.strokeStyle = '#38bdf8'; ctx.lineWidth = 5;
      ctx.beginPath(); ctx.moveTo(cx + 12, y + 4); ctx.lineTo(cx - 8, cy - 2); ctx.lineTo(cx + 8, cy + 4); ctx.lineTo(cx - 10, y + h - 4); ctx.stroke();
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(cx + 12, y + 4); ctx.lineTo(cx - 8, cy - 2); ctx.lineTo(cx + 8, cy + 4); ctx.lineTo(cx - 10, y + h - 4); ctx.stroke();
    } else if (vfx === 'holy') {
      const hg = ctx.createLinearGradient(cx - 22, y, cx + 22, y);
      hg.addColorStop(0, 'rgba(254,240,138,0)'); hg.addColorStop(0.5, 'rgba(254,240,138,0.85)'); hg.addColorStop(1, 'rgba(254,240,138,0)');
      ctx.fillStyle = hg; ctx.fillRect(cx - 22, y, 44, h);
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(cx, cy, 18, 0, Math.PI * 2); ctx.stroke();
    } else {
      ctx.strokeStyle = '#e879f9'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(cx, cy, 22, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.arc(cx, cy, 12, 0, Math.PI * 2); ctx.stroke();
      ctx.fillStyle = '#f0abfc';
      ctx.beginPath(); ctx.arc(cx, cy, 4, 0, Math.PI * 2); ctx.fill();
    }
  } else if (card.type === 'artifact') {
    grad.addColorStop(0, '#92400e'); grad.addColorStop(1, '#070a12');
    ctx.fillStyle = grad; ctx.fillRect(x, y, w, h);
    const rg = ctx.createRadialGradient(cx, cy, 3, cx, cy, 32);
    rg.addColorStop(0, '#ffffff'); rg.addColorStop(0.45, '#fbbf24'); rg.addColorStop(1, 'rgba(245,158,11,0)');
    ctx.fillStyle = rg; ctx.beginPath(); ctx.arc(cx, cy, 32, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#fef08a'; ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.moveTo(cx, cy - 24); ctx.lineTo(cx + 20, cy); ctx.lineTo(cx, cy + 24); ctx.lineTo(cx - 20, cy); ctx.closePath(); ctx.stroke();
  } else {
    grad.addColorStop(0, '#0f172a'); grad.addColorStop(1, '#1e293b');
    ctx.fillStyle = grad; ctx.fillRect(x, y, w, h);
    const pg = ctx.createRadialGradient(cx, y + h - 8, 2, cx, y + h - 8, 36);
    pg.addColorStop(0, 'rgba(56, 189, 248, 0.42)'); pg.addColorStop(1, 'rgba(56, 189, 248, 0)');
    ctx.fillStyle = pg; ctx.fillRect(x, y, w, h);
    ctx.fillStyle = 'rgba(0,0,0,0.65)';
    ctx.beginPath(); ctx.ellipse(cx, y + h - 7, 24, 5, 0, 0, Math.PI * 2); ctx.fill();
    drawUnitSprite(card.sprite, cx, cy + 2, 62, false, 'normal');
  }

  // 카드 호버 시 홀로그램 광택 스윕
  if (isHovered) {
    const sweep = ((state.tick * 4) % (w + h + 80)) - 40;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.lineWidth = 14;
    ctx.beginPath();
    ctx.moveTo(x + sweep - 30, y);
    ctx.lineTo(x + sweep + 30, y + h);
    ctx.stroke();
  }
  ctx.restore();
}

function drawAtmosphereBg() {
  const ambient = (state.playerFaction && state.playerFaction.ambient) || FACTIONS[state.selectedFaction].ambient;

  // 1. 깊은 성운 스카이 그라데이션
  const bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#020308');
  bg.addColorStop(0.45, '#081226');
  bg.addColorStop(0.85, '#040914');
  bg.addColorStop(1, '#010205');
  ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

  // 2. 천상 신전 빛줄기 (Volumetric God-Rays)
  ctx.save();
  for (let i = -2; i <= 2; i++) {
    const rx = W / 2 + i * 165;
    const rg = ctx.createLinearGradient(W / 2, 0, rx, 540);
    rg.addColorStop(0, 'rgba(56, 189, 248, 0.08)');
    rg.addColorStop(1, 'rgba(56, 189, 248, 0)');
    ctx.fillStyle = rg;
    ctx.beginPath();
    ctx.moveTo(W / 2 - 42, 0);
    ctx.lineTo(W / 2 + 42, 0);
    ctx.lineTo(rx + 95, 540);
    ctx.lineTo(rx - 95, 540);
    ctx.closePath();
    ctx.fill();
  }
  ctx.restore();

  // 3. 회전하는 천문 아스트롤라베 룬 링
  ctx.save();
  ctx.translate(W / 2 - 140, 320);
  ctx.rotate(state.tick * 0.0018);
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.09)';
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(0, 0, 275, 0, Math.PI * 2); ctx.stroke();
  ctx.beginPath(); ctx.arc(0, 0, 220, 0, Math.PI * 2); ctx.stroke();
  ctx.strokeRect(-195, -195, 390, 390);
  ctx.rotate(Math.PI / 4);
  ctx.strokeRect(-195, -195, 390, 390);
  ctx.restore();

  // 4. 패럴랙스 부유 신전 기둥 & 룬 에너지 라인
  const pillars = [
    { x: 24, y: 150, w: 30, h: 250, spd: 0.018 },
    { x: 904, y: 140, w: 28, h: 260, spd: 0.022 },
    { x: 1236, y: 165, w: 34, h: 240, spd: 0.016 }
  ];
  pillars.forEach((p, idx) => {
    const py = p.y + Math.sin(state.tick * p.spd + idx) * 9;
    const pg = ctx.createLinearGradient(p.x, py, p.x + p.w, py + p.h);
    pg.addColorStop(0, '#101d38'); pg.addColorStop(1, '#040812');
    ctx.fillStyle = pg; ctx.fillRect(p.x, py, p.w, p.h);
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.28)'; ctx.strokeRect(p.x, py, p.w, p.h);
    ctx.fillStyle = 'rgba(56, 189, 248, 0.6)';
    ctx.fillRect(p.x + p.w / 2 - 1, py + 16, 2, p.h - 32);
  });

  // 5. 진영별 환경 파티클 (눈송이, 불티, 모래 입자, 심연 포자, 에메랄드 에너지)
  for (let i = 0; i < 70; i++) {
    let px, py, col;
    if (ambient === 'snow') {
      px = (i * 173 + Math.sin(state.tick * 0.02 + i) * 28) % W;
      py = (i * 97 + state.tick * 0.75) % H;
      col = 'rgba(186, 230, 253, 0.55)';
    } else if (ambient === 'sand') {
      px = (i * 173 + state.tick * 1.1) % W;
      py = (i * 97 + Math.sin(state.tick * 0.02 + i) * 16) % H;
      col = 'rgba(94, 234, 212, 0.42)';
    } else if (ambient === 'void') {
      px = (i * 173 + Math.sin(state.tick * 0.015 + i) * 22) % W;
      py = H - ((i * 97 + state.tick * 0.35) % H);
      col = 'rgba(192, 132, 252, 0.48)';
    } else if (ambient === 'magmar') {
      px = (i * 173 + Math.sin(state.tick * 0.015 + i) * 20) % W;
      py = H - ((i * 97 + state.tick * 0.45) % H);
      col = 'rgba(16, 185, 129, 0.48)';
    } else {
      px = (i * 173 + Math.sin(state.tick * 0.015 + i) * 20) % W;
      py = H - ((i * 97 + state.tick * 0.52) % H);
      col = ambient === 'ember' ? 'rgba(244, 63, 94, 0.52)' : 'rgba(251, 191, 36, 0.48)';
    }
    const sz = i % 5 === 0 ? 3 : 2;
    ctx.fillStyle = col;
    ctx.fillRect(px, py, sz, sz);
  }
}

function drawTitleScreen() {
  drawAtmosphereBg();
  ctx.save();
  ctx.translate(W / 2, 265);
  ctx.rotate(state.tick * 0.005);
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)'; ctx.lineWidth = 2.5;
  ctx.strokeRect(-115, -115, 230, 230);
  ctx.rotate(Math.PI / 4);
  ctx.strokeStyle = 'rgba(251, 191, 36, 0.45)';
  ctx.strokeRect(-115, -115, 230, 230);
  ctx.restore();

  drawUnitSprite('argeon', W / 2 - 245, 275, 160, false, 'normal');
  drawUnitSprite('kaleos', W / 2 + 245, 275, 160, true, 'normal');

  ctx.textAlign = 'center';
  ctx.font = '900 60px "Cinzel", serif'; ctx.fillStyle = '#f8fafc';
  ctx.fillText('DUELYST II', W / 2, 255);

  ctx.font = '700 16px "Press Start 2P", monospace'; ctx.fillStyle = '#38bdf8';
  ctx.fillText('CHRONICLES OF MYTHRON', W / 2, 298);

  ctx.font = '15px "Noto Sans KR"'; ctx.fillStyle = '#94a3b8';
  ctx.fillText('고밀도 4프레임 픽셀 아트 · 전술 경로 예측 · 시네마틱 전투 VFX', W / 2, 470);

  const pulse = 0.6 + Math.sin(state.tick * 0.08) * 0.4;
  roundRect(W / 2 - 175, 535, 350, 70, 8, '#0284c7', `rgba(56, 189, 248, ${pulse})`, 3);
  ctx.font = '900 22px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText('⚔️ PLAY NOW', W / 2, 578);
}

function drawSelectScreen() {
  drawAtmosphereBg();
  const keys = Object.keys(FACTIONS);

  ctx.textAlign = 'center';
  ctx.font = '900 23px "Cinzel", serif'; ctx.fillStyle = '#f8fafc';
  ctx.fillText('CHOOSE YOUR GENERAL, RULESET & DIFFICULTY', W / 2, 44);

  keys.forEach((fid, idx) => {
    const f = FACTIONS[fid];
    const cx = 55 + idx * 196;
    const isSel = state.selectedFaction === fid;
    roundRect(cx, 92, 184, 130, 8, isSel ? '#111d38' : '#090e1c', isSel ? f.color : '#1e293b', isSel ? 3 : 1.5);
    drawUnitSprite(f.sprite, cx + 92, 144, 76, false, 'normal');
    ctx.textAlign = 'center';
    ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = isSel ? f.color : '#cbd5e1';
    ctx.fillText(f.name, cx + 92, 196);
    ctx.font = '10.5px "Noto Sans KR"'; ctx.fillStyle = '#94a3b8';
    ctx.fillText(f.mechanicTag.split('·')[0], cx + 92, 214);
  });

  const sel = FACTIONS[state.selectedFaction];
  roundRect(55, 238, 1170, 452, 10, 'rgba(9, 14, 28, 0.94)', sel.color, 2);

  ctx.fillStyle = 'rgba(0,0,0,0.55)';
  ctx.beginPath(); ctx.ellipse(165, 405, 52, 14, 0, 0, Math.PI * 2); ctx.fill();
  drawUnitSprite(sel.sprite, 165, 340, 140, false, 'normal');

  ctx.textAlign = 'center';
  ctx.font = 'bold 11.5px "Noto Sans KR"'; ctx.fillStyle = sel.color;
  ctx.fillText(sel.title, 165, 436);
  ctx.font = '900 19px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText(sel.name, 165, 462);

  roundRect(72, 480, 186, 194, 6, '#050811', sel.color, 1.5);
  ctx.textAlign = 'left';
  ctx.font = '900 11px "Noto Sans KR"'; ctx.fillStyle = sel.color;
  ctx.fillText(`🔥 ${sel.mechanicTag}`, 80, 502);
  ctx.font = '11px "Noto Sans KR"'; ctx.fillStyle = '#e2e8f0';
  for (let i = 0; i < 4; i++) {
    ctx.fillText(sel.mechanicDesc.slice(i * 16, (i + 1) * 16), 80, 524 + i * 17);
  }
  ctx.fillStyle = '#38bdf8';
  ctx.fillText(`• 전술 경로 예측 & 킬각 표시`, 80, 608);
  ctx.fillText(`• 지면 데칼 & 4프레임 애니메이션`, 80, 626);
  ctx.fillStyle = '#fbbf24';
  ctx.fillText(`• 100% 수동 타겟팅 & 멀리건`, 80, 646);

  ctx.font = '900 14px "Noto Sans KR"'; ctx.fillStyle = '#fbbf24';
  ctx.fillText(`🃏 [${sel.title}] 전용 덱 핵심 카드 9종`, 280, 268);

  sel.cards.forEach((c, idx) => {
    const col = idx % 5;
    const row = Math.floor(idx / 5);
    const kx = 280 + col * 186;
    const ky = 282 + row * 198;
    const bCol = c.type === 'spell' ? '#c084fc' : (c.type === 'artifact' ? '#f59e0b' : '#38bdf8');
    roundRect(kx, ky, 176, 186, 6, '#0c1324', bCol, 1.5);

    ctx.fillStyle = '#0284c7';
    ctx.beginPath(); ctx.arc(kx + 16, ky + 16, 11, 0, Math.PI * 2); ctx.fill();
    ctx.textAlign = 'center';
    ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
    ctx.fillText(c.cost, kx + 16, ky + 20);

    ctx.textAlign = 'left';
    ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#f8fafc';
    ctx.fillText(c.name, kx + 32, ky + 20);

    if (c.type === 'minion') {
      drawUnitSprite(c.sprite, kx + 34, ky + 62, 50, false, 'normal');
      ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = '#fbbf24';
      ctx.fillText(`⚔️ ${c.atk}   ❤️ ${c.hp}`, kx + 66, ky + 58);
      ctx.font = '10px "Noto Sans KR"'; ctx.fillStyle = '#38bdf8';
      ctx.fillText(c.keywords.length ? c.keywords[0].toUpperCase() : 'MINION', kx + 66, ky + 76);
    } else {
      ctx.font = 'bold 11.5px "Noto Sans KR"';
      ctx.fillStyle = c.type === 'spell' ? '#e879f9' : '#fbbf24';
      ctx.fillText(c.type === 'spell' ? '🔮 SPELL (주문)' : `🛡️ ARTIFACT (+${c.atkBonus} ATK)`, kx + 14, ky + 56);
    }

    ctx.font = '10.5px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
    for (let line = 0; line < 4; line++) {
      ctx.fillText(c.desc.slice(line * 16, (line + 1) * 16), kx + 12, ky + 102 + line * 17);
    }
  });

  DIFFICULTIES.forEach((d, idx) => {
    const dx = 55 + idx * 145;
    const isD = state.difficultyIdx === idx;
    roundRect(dx, 708, 136, 50, 8, isD ? '#172554' : '#0f172a', isD ? d.color : '#334155', isD ? 2.5 : 1.5);
    ctx.textAlign = 'center';
    ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = isD ? d.color : '#94a3b8';
    ctx.fillText(d.name, dx + 68, 738);
  });

  roundRect(645, 708, 200, 50, 8, '#0f172a', state.useBbsMode ? '#fbbf24' : '#38bdf8', 2);
  ctx.textAlign = 'center';
  ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = state.useBbsMode ? '#fbbf24' : '#38bdf8';
  ctx.fillText(state.useBbsMode ? '⭐ 모드: BBS 스킬 활성' : '📜 모드: 듀얼리스트 II 정통', 745, 738);

  const eLabel = state.enemyChoice === 'random' ? '🎲 AI: 랜덤' : `🤖 AI: ${FACTIONS[state.enemyChoice].name.split(' ')[0]}`;
  roundRect(855, 708, 175, 50, 8, '#0f172a', '#475569', 2);
  ctx.font = 'bold 13px "Noto Sans KR"'; ctx.fillStyle = '#e2e8f0';
  ctx.fillText(eLabel, 942, 738);

  roundRect(1040, 708, 185, 50, 8, '#0284c7', '#38bdf8', 2);
  ctx.font = '900 17px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText('⚔️ 전투 시작', 1132, 738);
}

function drawMulliganScreen() {
  drawAtmosphereBg();
  ctx.fillStyle = 'rgba(3, 5, 10, 0.78)';
  ctx.fillRect(0, 0, W, H);

  ctx.textAlign = 'center';
  ctx.font = '900 30px "Cinzel", serif'; ctx.fillStyle = '#f8fafc';
  ctx.fillText('OPENING HAND MULLIGAN', W / 2, 130);

  ctx.font = '15px "Noto Sans KR"'; ctx.fillStyle = '#38bdf8';
  ctx.fillText(`교체할 카드를 최대 2장까지 선택하세요 (${state.mulliganSelected.size}/2 선택됨)`, W / 2, 172);

  for (let i = 0; i < state.pHand.length; i++) {
    const c = state.pHand[i];
    const isSel = state.mulliganSelected.has(i);
    const cx = 175 + i * 190;
    const cy = 260 - (isSel ? 18 : 0);

    roundRect(cx, cy, 172, 265, 8, isSel ? '#3b0764' : '#0b1224', isSel ? '#fbbf24' : '#38bdf8', isSel ? 3 : 2);
    drawCardArt(c, cx + 10, cy + 36, 152, 95, isSel);

    ctx.fillStyle = '#0284c7';
    ctx.beginPath(); ctx.arc(cx + 22, cy + 20, 12, 0, Math.PI * 2); ctx.fill();
    ctx.textAlign = 'center';
    ctx.font = '900 14px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
    ctx.fillText(c.cost, cx + 22, cy + 25);

    ctx.font = '900 13.5px "Noto Sans KR"'; ctx.fillStyle = '#f8fafc';
    ctx.fillText(c.name, cx + 86, cy + 152);

    ctx.font = '11px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
    for (let line = 0; line < 4; line++) {
      ctx.fillText(c.desc.slice(line * 14, (line + 1) * 14), cx + 86, cy + 176 + line * 17);
    }

    if (isSel) {
      roundRect(cx + 26, cy + 230, 120, 26, 4, '#f59e0b', null);
      ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#000000';
      ctx.fillText('🔄 교체 예정', cx + 86, cy + 247);
    }
  }

  roundRect(W / 2 - 165, 580, 330, 64, 8, '#0284c7', '#38bdf8', 2.5);
  ctx.font = '900 20px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
  ctx.fillText('⚔️ 결투 시작 (CONFIRM)', W / 2, 619);
}

function drawTacticalArrow(r1, c1, r2, c2, color) {
  const p1 = tileCenter(r1, c1);
  const p2 = tileCenter(r2, c2);
  const ang = Math.atan2(p2.y - p1.y, p2.x - p1.x);

  ctx.save();
  ctx.strokeStyle = color;
  ctx.lineWidth = 4;
  ctx.setLineDash([8, 6]);
  ctx.lineDashOffset = -state.tick * 0.8;
  ctx.beginPath();
  ctx.moveTo(p1.x, p1.y);
  ctx.lineTo(p2.x, p2.y);
  ctx.stroke();

  ctx.setLineDash([]);
  ctx.fillStyle = color;
  ctx.translate(p2.x, p2.y);
  ctx.rotate(ang);
  ctx.beginPath();
  ctx.moveTo(4, 0);
  ctx.lineTo(-14, -9);
  ctx.lineTo(-14, 9);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function drawBattleScreen() {
  ctx.save();
  if (state.shake > 0) {
    ctx.translate((Math.random() - 0.5) * state.shake * 2, (Math.random() - 0.5) * state.shake * 2);
    state.shake *= 0.80;
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

  // 좌측 플레이어 HUD
  roundRect(55, 16, 158, 96, 8, '#0b1224', pf.color, 2);
  drawUnitSprite(pf.sprite, 102, 60, 78, false, 'normal');
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

  if (state.useBbsMode) {
    const bbsReady = state.pBbsCd === 0 && state.pMana >= pf.bbsCost;
    ctx.fillStyle = bbsReady ? '#172554' : '#0f172a';
    ctx.beginPath(); ctx.arc(261, 60, 34, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = state.targetMode ? '#fbbf24' : (bbsReady ? '#38bdf8' : '#334155');
    ctx.lineWidth = 3; ctx.stroke();
    ctx.font = '900 11px "Noto Sans KR"';
    ctx.fillStyle = bbsReady ? '#38bdf8' : '#64748b';
    ctx.fillText('BBS 스킬', 261, 56);
    ctx.fillText(state.pBbsCd === 0 ? `${pf.bbsCost}마나` : `${state.pBbsCd}턴대기`, 261, 73);
  } else {
    roundRect(225, 24, 72, 72, 8, '#0b1224', '#1e293b', 1.5);
    ctx.font = 'bold 10px "Noto Sans KR"'; ctx.fillStyle = '#94a3b8';
    ctx.fillText('DUELYST II', 261, 55);
    ctx.fillStyle = '#38bdf8';
    ctx.fillText('2-DRAW', 261, 72);
  }

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

  // 중앙 턴 & 타겟 모드 배너
  ctx.textAlign = 'center';
  ctx.font = '900 16px "Cinzel", serif'; ctx.fillStyle = '#f8fafc';
  ctx.fillText(`TURN ${state.turn}`, W / 2 + 45, 36);
  ctx.font = 'bold 11.5px "Noto Sans KR"'; ctx.fillStyle = diff.color;
  ctx.fillText(`[${diff.name}]`, W / 2 + 45, 55);

  if (state.targetMode) {
    roundRect(W / 2 - 95, 64, 280, 26, 4, '#78350f', '#fbbf24', 1.5);
    ctx.font = 'bold 11.5px "Noto Sans KR"'; ctx.fillStyle = '#fef08a';
    ctx.fillText('🎯 수동 대상 지정 중 — 보드 위 유닛 클릭', W / 2 + 45, 81);
  } else {
    ctx.font = '11px "Noto Sans KR"'; ctx.fillStyle = '#94a3b8';
    ctx.fillText('A~D: 아군 진영 | E: 중앙선 | F~I: 적 진영(침투)', W / 2 + 45, 76);
  }

  // 우측 적 HUD
  roundRect(1067, 16, 158, 96, 8, '#0b1224', ef.color, 2);
  drawUnitSprite(ef.sprite, 1178, 60, 78, true, 'normal');
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
  ctx.fillStyle = ef.color;
  ctx.fillText(ef.mechanicTag.split('·')[0], 1052, 64);

  // 중앙 2.5D 전술 보드
  let moves = [], attacks = [], summons = [], spells = [];
  if (state.selectedPos) {
    moves = getValidMoves(state.selectedPos.r, state.selectedPos.c);
    attacks = getValidAttacks(state.selectedPos.r, state.selectedPos.c);
  }
  const activeHandCard = state.selectedCardIdx !== null ? state.pHand[state.selectedCardIdx] : null;
  if (activeHandCard) {
    if (activeHandCard.type === 'minion') summons = getValidSummonTiles('player', activeHandCard);
    else if (activeHandCard.type === 'spell') spells = getValidSpellTargets(activeHandCard, 'player');
  }

  // Pass 1: 타일 바닥 + 지면 데칼 + 그림자 역병 + 입체 마나 크리스탈 + 배치 미리보기
  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const tx = BOARD_X + c * (TILE_W + GAP);
    const ty = BOARD_Y + r * (TILE_H + GAP);
    const isMove = moves.some(m => m.r === r && m.c === c);
    const isAtk = attacks.some(a => a.r === r && a.c === c);
    const isSum = summons.some(s => s.r === r && s.c === c);
    const isSpl = spells.some(s => s.r === r && s.c === c);
    const isSel = state.selectedPos && state.selectedPos.r === r && state.selectedPos.c === c;
    const isHov = state.hoverTile && state.hoverTile.r === r && state.hoverTile.c === c;
    const creep = state.creepTiles.find(ct => ct.r === r && ct.c === c);

    // 2.5D 타일 측면 석재 두께
    ctx.fillStyle = '#03060e';
    ctx.beginPath(); ctx.roundRect(tx, ty + 6, TILE_W, TILE_H, 5); ctx.fill();

    let fill = (r + c) % 2 === 0 ? 'rgba(15, 24, 44, 0.94)' : 'rgba(22, 35, 62, 0.94)';
    if (c >= 5) fill = (r + c) % 2 === 0 ? 'rgba(26, 22, 48, 0.94)' : 'rgba(34, 28, 58, 0.94)';
    let stroke = c === 4 ? '#38bdf8' : '#24344d';
    let lw = c === 4 ? 1.8 : 1.3;

    if (creep) { fill = 'rgba(76, 29, 149, 0.78)'; stroke = '#c084fc'; }
    if (isMove) { fill = 'rgba(14, 116, 144, 0.62)'; stroke = '#38bdf8'; lw = 2.5; }
    if (isSum) {
      const isAirdrop = activeHandCard && activeHandCard.keywords.includes('airdrop');
      fill = isAirdrop ? 'rgba(8, 145, 178, 0.48)' : 'rgba(6, 95, 70, 0.64)';
      stroke = isAirdrop ? '#22d3ee' : '#10b981';
      lw = 2.5;
    }
    if (isAtk || isSpl) { fill = 'rgba(159, 18, 57, 0.70)'; stroke = '#f43f5e'; lw = 2.5; }
    if (isSel) { fill = 'rgba(30, 58, 138, 0.82)'; stroke = '#fbbf24'; lw = 3; }
    if (isHov) { stroke = '#f8fafc'; lw = 2.5; }

    roundRect(tx, ty, TILE_W, TILE_H, 5, fill, stroke, lw);

    // 타일 상단 베벨 하이라이트 & 코너 리벳 디테일
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(tx + 5, ty + 2); ctx.lineTo(tx + TILE_W - 5, ty + 2); ctx.stroke();
    ctx.fillStyle = 'rgba(148, 163, 184, 0.25)';
    ctx.fillRect(tx + 3, ty + 3, 2, 2);
    ctx.fillRect(tx + TILE_W - 5, ty + 3, 2, 2);

    ctx.textAlign = 'left';
    ctx.font = '9px monospace';
    ctx.fillStyle = c >= 5 ? 'rgba(244, 63, 94, 0.45)' : 'rgba(148, 163, 184, 0.36)';
    ctx.fillText(`${COL_LABELS[c]}${r + 1}`, tx + 7, ty + 12);

    // 지면 데칼 렌더링 (균열, 화염 그을음, 서리 결정)
    for (let di = state.decals.length - 1; di >= 0; di--) {
      const dec = state.decals[di];
      if (dec.r !== r || dec.c !== c) continue;
      dec.t++;
      if (dec.t >= dec.maxT) { state.decals.splice(di, 1); continue; }
      const dAlpha = (1 - dec.t / dec.maxT) * 0.65;
      const dcx = tx + TILE_W / 2, dcy = ty + TILE_H / 2 + 6;
      ctx.save();
      ctx.globalAlpha = dAlpha;
      if (dec.kind === 'scorch') {
        const sg = ctx.createRadialGradient(dcx, dcy, 2, dcx, dcy, 26);
        sg.addColorStop(0, '#090d16'); sg.addColorStop(0.6, '#7c2d12'); sg.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = sg; ctx.beginPath(); ctx.arc(dcx, dcy, 26, 0, Math.PI * 2); ctx.fill();
      } else if (dec.kind === 'frost') {
        ctx.strokeStyle = '#bae6fd'; ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(dcx - 16, dcy); ctx.lineTo(dcx + 16, dcy);
        ctx.moveTo(dcx, dcy - 14); ctx.lineTo(dcx, dcy + 14);
        ctx.moveTo(dcx - 11, dcy - 11); ctx.lineTo(dcx + 11, dcy + 11);
        ctx.stroke();
      } else {
        ctx.strokeStyle = '#020408'; ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(dcx - 14, dcy - 6); ctx.lineTo(dcx - 2, dcy + 2); ctx.lineTo(dcx + 15, dcy - 4);
        ctx.moveTo(dcx - 2, dcy + 2); ctx.lineTo(dcx + 5, dcy + 12);
        ctx.stroke();
      }
      ctx.restore();
    }

    // 그림자 역병(Shadow Creep) 부글거리는 심연 문양
    if (creep) {
      const pulse = Math.sin(state.tick * 0.08 + r + c) * 3;
      ctx.strokeStyle = 'rgba(232, 121, 249, 0.65)';
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(tx + TILE_W / 2, ty + TILE_H / 2, 16 + pulse, 0, Math.PI * 2); ctx.stroke();
      ctx.fillStyle = 'rgba(192, 132, 252, 0.5)';
      ctx.fillRect(tx + TILE_W / 2 - 8 + pulse, ty + TILE_H / 2 - 6, 3, 3);
      ctx.fillRect(tx + TILE_W / 2 + 6, ty + TILE_H / 2 + 4 - pulse, 3, 3);
    }

    // 입체 마나 샘 크리스탈 + 룬 마법진
    if (state.manaOrbs.some(o => o.r === r && o.c === c)) {
      const ocx = tx + TILE_W / 2;
      const ocy = ty + TILE_H / 2 - 2 + Math.sin(state.tick * 0.08) * 4;
      const pulse = Math.sin(state.tick * 0.1) * 3;

      ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)';
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.ellipse(ocx, ty + TILE_H / 2 + 12, 20, 7, 0, 0, Math.PI * 2); ctx.stroke();

      const mg = ctx.createRadialGradient(ocx, ocy, 2, ocx, ocy, 26 + pulse);
      mg.addColorStop(0, '#ffffff'); mg.addColorStop(0.4, '#38bdf8'); mg.addColorStop(1, 'rgba(56,189,248,0)');
      ctx.fillStyle = mg;
      ctx.beginPath(); ctx.arc(ocx, ocy, 26 + pulse, 0, Math.PI * 2); ctx.fill();

      ctx.fillStyle = '#bae6fd';
      ctx.beginPath(); ctx.moveTo(ocx, ocy - 14); ctx.lineTo(ocx + 10, ocy); ctx.lineTo(ocx, ocy + 14); ctx.closePath(); ctx.fill();
      ctx.fillStyle = '#0284c7';
      ctx.beginPath(); ctx.moveTo(ocx, ocy - 14); ctx.lineTo(ocx - 10, ocy); ctx.lineTo(ocx, ocy + 14); ctx.closePath(); ctx.fill();
    }

    // 소환 미리보기 (Ghost Preview)
    if (isSum && isHov && activeHandCard && !state.board[r][c]) {
      const gx = tx + TILE_W / 2;
      const gy = ty + TILE_H / 2 - 8;
      drawUnitSprite(activeHandCard.sprite, gx, gy, 62, false, 'normal', 0.6);

      ctx.textAlign = 'center';
      ctx.font = 'bold 10px "Noto Sans KR"';
      if (activeHandCard.keywords.includes('zeal_atk2') && pg && Math.abs(r - pg.r) <= 1 && Math.abs(c - pg.c) <= 1) {
        ctx.fillStyle = '#fef08a'; ctx.fillText('☀️열성 +2 ATK', gx, ty + 13);
      } else if (activeHandCard.keywords.includes('infiltrate_atk2') && c >= 5) {
        ctx.fillStyle = '#38bdf8'; ctx.fillText('❄️침투 +2 ATK', gx, ty + 13);
      } else if (activeHandCard.keywords.includes('airdrop')) {
        ctx.fillStyle = '#22d3ee'; ctx.fillText('🪂공수 투하', gx, ty + 13);
      } else {
        ctx.fillStyle = '#34d399'; ctx.fillText('✨소환 위치', gx, ty + 13);
      }

      if (activeHandCard.keywords.includes('gambit_front3') && c + 1 < COLS) {
        const fx = BOARD_X + (c + 1) * (TILE_W + GAP);
        roundRect(fx, ty, TILE_W, TILE_H, 5, 'rgba(244, 63, 94, 0.25)', '#f43f5e', 2);
        ctx.fillStyle = '#f43f5e';
        ctx.fillText('⚔️전방 3피해', fx + TILE_W / 2, ty + 15);
      }
    }

    if (isSpl && isHov && activeHandCard && activeHandCard.spell === 'gravity_well') {
      for (const dr of [-1, 0, 1]) {
        const nr = r + dr;
        if (nr >= 0 && nr < ROWS && !state.board[nr][c]) {
          const wy = BOARD_Y + nr * (TILE_H + GAP);
          drawUnitSprite('wall', tx + TILE_W / 2, wy + TILE_H / 2 - 8, 56, false, 'normal', 0.58);
        }
      }
    }
  }

  // 전술 경로 예측 화살표 (선택 유닛 -> 마우스 호버 타일)
  if (state.selectedPos && state.hoverTile) {
    const sp = state.selectedPos;
    const ht = state.hoverTile;
    if (moves.some(m => m.r === ht.r && m.c === ht.c)) {
      drawTacticalArrow(sp.r, sp.c, ht.r, ht.c, '#38bdf8');
    } else if (attacks.some(a => a.r === ht.r && a.c === ht.c)) {
      drawTacticalArrow(sp.r, sp.c, ht.r, ht.c, '#f43f5e');
    }
  }

  // Pass 2: 유닛 + 잔상 트레일 + 바닥 오라 + 교전 킬각 배지
  for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
    const u = state.board[r][c];
    if (!u) continue;

    const tx = BOARD_X + c * (TILE_W + GAP);
    const ty = BOARD_Y + r * (TILE_H + GAP);
    const isAtk = attacks.some(a => a.r === r && a.c === c);
    const isHov = state.hoverTile && state.hoverTile.r === r && state.hoverTile.c === c;

    u.animX *= 0.76;
    u.animY *= 0.76;
    if (u.flashT > 0) u.flashT--;

    const cx = tx + TILE_W / 2 + u.animX;
    const cy = ty + TILE_H / 2 - 8 + u.animY;

    if (Math.abs(u.animX) > 4 || Math.abs(u.animY) > 4) {
      u.trail.push({ x: cx, y: cy, alpha: 0.55 });
      if (u.trail.length > 5) u.trail.shift();
    } else if (u.trail.length > 0) {
      u.trail.shift();
    }
    for (const tr of u.trail) {
      drawUnitSprite(u.sprite, tr.x, tr.y, u.isGeneral ? 74 : 64, u.owner === 'enemy', 'ghost', tr.alpha * 0.52);
      tr.alpha *= 0.85;
    }

    const effAtk = getEffectiveAtk(u, r, c);
    const buffed = effAtk > u.atk;

    ctx.fillStyle = 'rgba(0,0,0,0.65)';
    ctx.beginPath(); ctx.ellipse(cx, ty + TILE_H - 14, 25, 7, 0, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = u.owner === 'player' ? '#38bdf8' : '#f43f5e';
    ctx.lineWidth = 2.2;
    ctx.beginPath(); ctx.ellipse(cx, ty + TILE_H - 14, 25, 7, 0, 0, Math.PI * 2); ctx.stroke();

    ctx.fillStyle = u.owner === 'player' ? '#38bdf8' : '#f43f5e';
    ctx.font = 'bold 11px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(u.owner === 'player' ? '▸' : '◂', u.owner === 'player' ? cx + 28 : cx - 28, ty + TILE_H - 10);

    // 상단 상태/키워드 배지
    ctx.font = 'bold 9.5px "Noto Sans KR"';
    const isBsTarget = isAtk && state.selectedPos && isBackstabPosition(state.board[state.selectedPos.r][state.selectedPos.c], state.selectedPos.r, state.selectedPos.c, r, c);
    if (isBsTarget) { ctx.fillStyle = '#f43f5e'; ctx.fillText('🗡️기습(+2)', cx, ty + 13); }
    else if (u.stunned) { ctx.fillStyle = '#38bdf8'; ctx.fillText('❄️기절', cx, ty + 13); }
    else if (isKeywordActive(u, r, c, 'zeal_atk2')) { ctx.fillStyle = '#fef08a'; ctx.fillText('☀️열성 활성', cx, ty + 13); }
    else if (isKeywordActive(u, r, c, 'infiltrate_atk2')) { ctx.fillStyle = '#38bdf8'; ctx.fillText('❄️침투 활성', cx, ty + 13); }
    else if (u.keywords.includes('provoke')) { ctx.fillStyle = '#fbbf24'; ctx.fillText('🛡️도발', cx, ty + 13); }
    else if (u.keywords.includes('blast')) { ctx.fillStyle = '#14b8a6'; ctx.fillText('⚡폭발', cx, ty + 13); }
    else if (u.keywords.includes('ranged')) { ctx.fillStyle = '#38bdf8'; ctx.fillText('🏹원거리', cx, ty + 13); }
    else if (u.keywords.includes('flying')) { ctx.fillStyle = '#a5f3fc'; ctx.fillText('🕊️비행', cx, ty + 13); }
    else if (u.keywords.includes('celerity')) { ctx.fillStyle = '#fde047'; ctx.fillText('⚡질풍', cx, ty + 13); }
    else if (u.keywords.includes('rebirth')) { ctx.fillStyle = '#6ee7b7'; ctx.fillText('🥚환생', cx, ty + 13); }

    drawUnitSprite(u.sprite, cx, cy, u.isGeneral ? 74 : 64, u.owner === 'enemy', u.flashT > 0 ? 'flash' : 'normal');

    roundRect(tx + 6, ty + TILE_H - 22, 25, 18, 4, buffed ? '#15803d' : '#ca8a04', '#fef08a', 1);
    ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
    ctx.fillText(effAtk, tx + 18, ty + TILE_H - 9);

    roundRect(tx + TILE_W - 31, ty + TILE_H - 22, 25, 18, 4, '#be123c', '#fda4af', 1);
    ctx.fillText(u.hp, tx + TILE_W - 18, ty + TILE_H - 9);

    // 적 타겟 호버 시 실시간 킬각/반격 플로팅 예측 배지
    if (isAtk && isHov && state.selectedPos) {
      const myU = state.board[state.selectedPos.r][state.selectedPos.c];
      const bs = isBackstabPosition(myU, state.selectedPos.r, state.selectedPos.c, r, c);
      const noCounter = myU.keywords.includes('ranged') || myU.keywords.includes('blast') || bs || u.keywords.includes('structure');
      const myDmg = getEffectiveAtk(myU, state.selectedPos.r, state.selectedPos.c) + (bs ? 2 : 0);
      const cDmg = noCounter ? 0 : effAtk;
      const isKill = myDmg >= u.hp;

      roundRect(cx - 48, ty - 24, 96, 22, 4, isKill ? '#9f1239' : '#0f172a', isKill ? '#fef08a' : '#f43f5e', 1.5);
      ctx.textAlign = 'center';
      ctx.font = '900 10.5px "Noto Sans KR"';
      ctx.fillStyle = isKill ? '#fef08a' : '#ffffff';
      ctx.fillText(isKill ? `💀 처치! (-${myDmg})` : `⚔️-${myDmg} / 🛡️-${cDmg}`, cx, ty - 9);
    }
  }

  // 우측 전투 기록 & 교전 미리보기
  roundRect(940, 128, 285, 406, 8, 'rgba(9, 14, 28, 0.92)', '#1e293b', 2);
  ctx.textAlign = 'left';
  ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = '#38bdf8';
  ctx.fillText(`📜 전투 기록 (남은 덱: ${state.pDeck.length}장)`, 954, 152);
  ctx.font = '11.5px "Noto Sans KR"';
  state.logs.slice(0, 10).forEach((l, i) => {
    ctx.fillStyle = i === 0 ? '#f8fafc' : '#94a3b8';
    ctx.fillText(l.slice(0, 27), 954, 174 + i * 19);
  });

  if (state.hoverTile) {
    const hu = state.board[state.hoverTile.r][state.hoverTile.c];
    if (hu) {
      const hAtk = getEffectiveAtk(hu, state.hoverTile.r, state.hoverTile.c);
      roundRect(952, 382, 261, 140, 6, '#050811', hu.owner === 'player' ? '#38bdf8' : '#f43f5e', 1.5);
      drawUnitSprite(hu.sprite, 992, 434, 66, hu.owner === 'enemy', 'normal');
      ctx.font = '900 14px "Noto Sans KR"'; ctx.fillStyle = '#f8fafc';
      ctx.fillText(`${hu.name} (${COL_LABELS[state.hoverTile.c]}${state.hoverTile.r + 1})`, 1030, 408);
      ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = '#fbbf24';
      ctx.fillText(`공격력 ${hAtk}  |  체력 ${hu.hp}/${hu.maxHp}`, 1030, 428);
      ctx.font = '10.5px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
      ctx.fillText(`특성: ${hu.keywords.length ? hu.keywords.join(', ').toUpperCase() : '기본'}`, 1030, 448);

      if (state.selectedPos && hu.owner === 'enemy' && attacks.some(a => a.r === state.hoverTile.r && a.c === state.hoverTile.c)) {
        const myU = state.board[state.selectedPos.r][state.selectedPos.c];
        const bs = isBackstabPosition(myU, state.selectedPos.r, state.selectedPos.c, state.hoverTile.r, state.hoverTile.c);
        const noCounter = myU.keywords.includes('ranged') || myU.keywords.includes('blast') || bs || hu.keywords.includes('structure');
        const myDmg = getEffectiveAtk(myU, state.selectedPos.r, state.selectedPos.c) + (bs ? 2 : 0);
        const counterDmg = noCounter ? 0 : hAtk;
        ctx.fillStyle = '#f43f5e';
        ctx.font = 'bold 11.5px "Noto Sans KR"';
        ctx.fillText(`⚔️ 동시 교전: 적 -${myDmg} / 나 -${counterDmg}`, 962, 508);
      } else {
        ctx.fillStyle = '#38bdf8';
        ctx.fillText(hu.stunned ? '상태: 기절' : (hu.attacksLeft > 0 ? `상태: 공격 가능 (${hu.attacksLeft}회)` : '상태: 행동 완료'), 1030, 468);
      }
    }
  }

  // 하단 REPLACE + 손패 + END TURN / SKIP
  const canRep = !state.replacedThisTurn && state.pDeck.length > 0 && !state.targetMode;
  roundRect(55, 585, 118, 185, 10, state.replaceMode ? '#78350f' : '#0b1224', state.replaceMode ? '#fbbf24' : (canRep ? '#38bdf8' : '#1e293b'), 2);
  ctx.textAlign = 'center';
  ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = canRep ? '#38bdf8' : '#475569';
  ctx.fillText('REPLACE', 114, 655);
  ctx.font = '11px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
  ctx.fillText(state.replaceMode ? '교체할 카드 클릭' : (canRep ? '카드 교체 (1회)' : '교체 불가'), 114, 680);

  for (let i = 0; i < state.pHand.length; i++) {
    const c = state.pHand[i];
    const isSel = state.selectedCardIdx === i;
    const isHov = state.hoverCardIdx === i;
    const cx = 195 + i * 155;
    const cy = 560 - (isSel || isHov ? 22 : 0);
    const ok = c.cost <= state.pMana;
    const borderCol = isSel ? '#fbbf24' : (ok ? (c.type === 'spell' ? '#c084fc' : (c.type === 'artifact' ? '#f59e0b' : '#38bdf8')) : '#334155');

    roundRect(cx, cy, 146, 230, 8, isSel ? '#172554' : '#0b1224', borderCol, isSel ? 3 : 2);
    drawCardArt(c, cx + 8, cy + 32, 130, 82, isHov || isSel);

    ctx.fillStyle = '#0284c7';
    ctx.beginPath(); ctx.arc(cx + 18, cy + 16, 11, 0, Math.PI * 2); ctx.fill();
    ctx.textAlign = 'center';
    ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
    ctx.fillText(c.cost, cx + 18, cy + 21);

    ctx.font = 'bold 10px "Noto Sans KR"';
    ctx.fillStyle = c.type === 'spell' ? '#e879f9' : (c.type === 'artifact' ? '#fbbf24' : '#38bdf8');
    ctx.fillText(c.type.toUpperCase(), cx + 84, cy + 20);

    ctx.font = '900 12px "Noto Sans KR"'; ctx.fillStyle = '#f8fafc';
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

  // 호버 중인 카드 상세 키워드 & 전문 툴팁
  if (state.hoverCardIdx !== null && state.pHand[state.hoverCardIdx]) {
    const hc = state.pHand[state.hoverCardIdx];
    const tx = Math.min(820, Math.max(195, 195 + state.hoverCardIdx * 155 - 80));
    const kws = (hc.keywords || []).filter(k => KEYWORD_GLOSSARY[k]);
    const boxH = 66 + kws.length * 20;
    const ty = 528 - boxH;
    roundRect(tx, ty, 320, boxH, 8, 'rgba(6, 10, 22, 0.96)', '#fbbf24', 2);
    ctx.textAlign = 'left';
    ctx.font = '900 13px "Noto Sans KR"'; ctx.fillStyle = '#fbbf24';
    ctx.fillText(`[${hc.cost} 마나] ${hc.name}`, tx + 12, ty + 20);
    ctx.font = '11px "Noto Sans KR"'; ctx.fillStyle = '#f8fafc';
    ctx.fillText(hc.desc.slice(0, 34), tx + 12, ty + 38);
    if (hc.desc.length > 34) ctx.fillText(hc.desc.slice(34, 68), tx + 12, ty + 54);
    kws.forEach((kw, idx) => {
      ctx.font = 'bold 10.5px "Noto Sans KR"'; ctx.fillStyle = '#38bdf8';
      ctx.fillText(KEYWORD_GLOSSARY[kw], tx + 12, ty + 74 + idx * 18);
    });
  }

  if (state.targetMode) {
    roundRect(1135, 585, 115, 115, 10, '#78350f', '#fbbf24', 2.5);
    ctx.textAlign = 'center';
    ctx.font = '900 15px "Noto Sans KR"'; ctx.fillStyle = '#fef08a';
    ctx.fillText('SKIP', 1192, 636);
    ctx.font = '12px "Noto Sans KR"';
    ctx.fillText('대상 건너뛰기', 1192, 658);
  } else {
    roundRect(1135, 585, 115, 115, 10, state.aiBusy ? '#1e293b' : '#0284c7', '#38bdf8', 2.5);
    ctx.textAlign = 'center';
    ctx.font = '900 16px "Noto Sans KR"'; ctx.fillStyle = '#ffffff';
    ctx.fillText('END', 1192, 636);
    ctx.fillText('TURN', 1192, 658);
  }

  roundRect(1135, 710, 115, 60, 8, '#0f172a', '#475569', 1.5);
  ctx.font = 'bold 12px "Noto Sans KR"'; ctx.fillStyle = '#cbd5e1';
  ctx.fillText('🔙 진영/난이도', 1192, 744);

  // 투사체 & 마나 흡수 테더 레이어
  for (let i = state.projectiles.length - 1; i >= 0; i--) {
    const p = state.projectiles[i];
    p.t++;
    if (p.t < 0) continue;
    if (p.t >= p.maxT) { state.projectiles.splice(i, 1); continue; }
    const prog = p.t / p.maxT;
    const cx = p.x1 + (p.x2 - p.x1) * prog;
    const cy = p.y1 + (p.y2 - p.y1) * prog - Math.sin(prog * Math.PI) * (p.arcOffset || 18);
    ctx.save();
    ctx.strokeStyle = p.color; ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(cx - (p.x2 - p.x1) * 0.12, cy);
    ctx.lineTo(cx, cy);
    ctx.stroke();
    ctx.fillStyle = '#ffffff';
    ctx.beginPath(); ctx.arc(cx, cy, 4.5, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  // 시네마틱 전투 & 마법 이펙트 레이어
  for (let i = state.effects.length - 1; i >= 0; i--) {
    const efObj = state.effects[i];
    efObj.t++;
    if (efObj.t >= efObj.maxT) { state.effects.splice(i, 1); continue; }
    const prog = efObj.t / efObj.maxT;
    const alpha = 1 - prog;
    ctx.save();
    ctx.globalAlpha = alpha;

    if (efObj.type === 'text') {
      efObj.y -= 0.78;
      ctx.textAlign = 'center';
      ctx.font = '900 18px "Noto Sans KR"';
      ctx.strokeStyle = '#000000'; ctx.lineWidth = 3.5;
      ctx.strokeText(efObj.text, efObj.x, efObj.y);
      ctx.fillStyle = efObj.color;
      ctx.fillText(efObj.text, efObj.x, efObj.y);
    } else if (efObj.type === 'pillar') {
      const w = (1 - prog * 0.5) * 46;
      const pg = ctx.createLinearGradient(efObj.x - w, efObj.y, efObj.x + w, efObj.y);
      pg.addColorStop(0, 'rgba(255,255,255,0)');
      pg.addColorStop(0.5, efObj.color);
      pg.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = pg;
      ctx.fillRect(efObj.x - w, efObj.y - 230, w * 2, 230);
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.ellipse(efObj.x, efObj.y, 12 + prog * 36, 6 + prog * 15, 0, 0, Math.PI * 2); ctx.stroke();
    } else if (efObj.type === 'lightning') {
      ctx.strokeStyle = efObj.color; ctx.lineWidth = 10 * alpha;
      ctx.beginPath();
      efObj.segs.forEach(s => { ctx.moveTo(s.x1, s.y1); ctx.lineTo(s.x2, s.y2); });
      ctx.stroke();
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 4 * alpha;
      ctx.beginPath();
      efObj.segs.forEach(s => { ctx.moveTo(s.x1, s.y1); ctx.lineTo(s.x2, s.y2); });
      ctx.stroke();
    } else if (efObj.type === 'iceSpikes') {
      const scaleH = Math.sin(Math.min(1, prog * 2) * (Math.PI / 2));
      efObj.spikes.forEach(sp => {
        ctx.save();
        ctx.translate(efObj.x + sp.dx, efObj.y);
        ctx.rotate(sp.tilt);
        ctx.fillStyle = '#38bdf8';
        ctx.beginPath(); ctx.moveTo(-6, 0); ctx.lineTo(0, -sp.h * scaleH); ctx.lineTo(6, 0); ctx.closePath(); ctx.fill();
        ctx.fillStyle = '#ffffff';
        ctx.beginPath(); ctx.moveTo(-2, 0); ctx.lineTo(0, -sp.h * scaleH * 0.9); ctx.lineTo(2, 0); ctx.closePath(); ctx.fill();
        ctx.restore();
      });
    } else if (efObj.type === 'voidVortex') {
      ctx.translate(efObj.x, efObj.y);
      ctx.rotate(prog * Math.PI * 3);
      const vg = ctx.createRadialGradient(0, 0, 2, 0, 0, 44 * (1 - prog * 0.3));
      vg.addColorStop(0, '#090d16'); vg.addColorStop(0.6, '#9333ea'); vg.addColorStop(1, 'rgba(147,51,234,0)');
      ctx.fillStyle = vg;
      ctx.beginPath(); ctx.arc(0, 0, 44, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#f0abfc'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(0, 0, 25, 0, Math.PI * 1.3); ctx.stroke();
    } else if (efObj.type === 'healHelix') {
      for (let k = 0; k < 2; k++) {
        const ang = prog * Math.PI * 4 + k * Math.PI;
        const hx = efObj.x + Math.cos(ang) * 25;
        const hy = efObj.y - prog * 60;
        ctx.fillStyle = efObj.color;
        ctx.beginPath(); ctx.arc(hx, hy, 4.5, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(hx - 1.5, hy - 1.5, 3, 3);
      }
    } else if (efObj.type === 'starburst') {
      const r = 10 + prog * 52;
      ctx.strokeStyle = efObj.color; ctx.lineWidth = 5.5 * alpha;
      ctx.beginPath();
      ctx.moveTo(efObj.x - r, efObj.y); ctx.lineTo(efObj.x + r, efObj.y);
      ctx.moveTo(efObj.x, efObj.y - r); ctx.lineTo(efObj.x, efObj.y + r);
      ctx.stroke();
    } else if (efObj.type === 'shard') {
      efObj.x += efObj.vx; efObj.y += efObj.vy;
      efObj.vy += 0.28;
      ctx.fillStyle = efObj.color;
      ctx.fillRect(efObj.x - 3, efObj.y - 3, 6, 6);
    } else if (efObj.type === 'soulOrb') {
      efObj.y -= 1.35;
      ctx.fillStyle = efObj.color;
      ctx.beginPath(); ctx.arc(efObj.x, efObj.y, 8 * alpha, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.beginPath(); ctx.arc(efObj.x, efObj.y, 4 * alpha, 0, Math.PI * 2); ctx.fill();
    } else if (efObj.type === 'arcSlash') {
      ctx.translate(efObj.x, efObj.y);
      if (efObj.dirX < 0) ctx.scale(-1, 1);
      const r = 34 * efObj.scale;
      ctx.strokeStyle = efObj.color;
      ctx.lineWidth = (1 - prog * 0.6) * 9.5;
      ctx.beginPath(); ctx.arc(-8, 0, r, -Math.PI * 0.42, Math.PI * 0.42); ctx.stroke();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = (1 - prog * 0.6) * 4;
      ctx.beginPath(); ctx.arc(-5, 0, r * 0.92, -Math.PI * 0.36, Math.PI * 0.36); ctx.stroke();
    } else if (efObj.type === 'backstabX') {
      ctx.strokeStyle = '#f43f5e'; ctx.lineWidth = 7 * alpha;
      ctx.beginPath();
      ctx.moveTo(efObj.x - 36, efObj.y - 36); ctx.lineTo(efObj.x + 36, efObj.y + 36);
      ctx.moveTo(efObj.x + 36, efObj.y - 36); ctx.lineTo(efObj.x - 36, efObj.y + 36);
      ctx.stroke();
      ctx.strokeStyle = '#fef08a'; ctx.lineWidth = 3 * alpha;
      ctx.beginPath();
      ctx.moveTo(efObj.x - 30, efObj.y - 30); ctx.lineTo(efObj.x + 30, efObj.y + 30);
      ctx.moveTo(efObj.x + 30, efObj.y - 30); ctx.lineTo(efObj.x - 30, efObj.y + 30);
      ctx.stroke();
    } else if (efObj.type === 'blastBeam') {
      ctx.strokeStyle = '#14b8a6'; ctx.lineWidth = 18 * alpha;
      ctx.beginPath(); ctx.moveTo(efObj.x, efObj.y); ctx.lineTo(efObj.x2, efObj.y2); ctx.stroke();
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 6 * alpha;
      ctx.beginPath(); ctx.moveTo(efObj.x, efObj.y); ctx.lineTo(efObj.x2, efObj.y2); ctx.stroke();
    } else if (efObj.type === 'whirlwind') {
      ctx.translate(efObj.x, efObj.y);
      ctx.rotate(prog * Math.PI * 3);
      ctx.strokeStyle = '#6ee7b7'; ctx.lineWidth = 6 * alpha;
      ctx.beginPath(); ctx.arc(0, 0, 76, 0, Math.PI * 1.4); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 0, 76, Math.PI, Math.PI * 2.4); ctx.stroke();
    } else if (efObj.type === 'ring') {
      ctx.strokeStyle = efObj.color; ctx.lineWidth = 3.5 * alpha;
      ctx.beginPath(); ctx.arc(efObj.x, efObj.y, 10 + prog * efObj.maxR, 0, Math.PI * 2); ctx.stroke();
    } else if (efObj.type === 'spark') {
      efObj.x += efObj.vx; efObj.y += efObj.vy;
      efObj.vx *= 0.92; efObj.vy *= 0.92;
      ctx.fillStyle = efObj.color;
      ctx.fillRect(efObj.x - 2.5, efObj.y - 2.5, 5, 5);
    }
    ctx.restore();
  }

  // 풀스크린 충격 플래시
  if (state.screenFlash.alpha > 0.01) {
    ctx.save();
    ctx.fillStyle = state.screenFlash.color;
    ctx.globalAlpha = state.screenFlash.alpha;
    ctx.fillRect(0, 0, W, H);
    ctx.restore();
    state.screenFlash.alpha *= 0.82;
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
  if (state.hitstop > 0) {
    state.hitstop--;
    requestAnimationFrame(loop);
    return;
  }
  state.tick++;
  if (state.screen === 'title') drawTitleScreen();
  else if (state.screen === 'select') drawSelectScreen();
  else if (state.screen === 'mulligan') drawMulliganScreen();
  else drawBattleScreen();
  requestAnimationFrame(loop);
}
loop();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=830, scrolling=False)
