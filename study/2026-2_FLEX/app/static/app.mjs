import { createSession, reveal, grade, continueSession, restoreSession } from './quiz.mjs';

const $ = id => document.getElementById(id);
const STORAGE_KEY = 'flex-wort-progress-v1';
let cards, ids, version, state, cardMap;

function notice(message) {
  $('notice').textContent = message;
  $('notice').hidden = false;
}

function save() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
  catch { notice('이 브라우저에서 진행 상황을 저장할 수 없어요. 창을 닫으면 학습 기록이 초기화됩니다.'); }
}

function render(moveFocus = false) {
  const summary = state.phase === 'summary';
  $('study').hidden = summary;
  $('summary').hidden = !summary;
  if (summary) {
    const failed = state.failed.length;
    $('summary-cycle').textContent = `CYCLE ${state.cycle} COMPLETE`;
    $('summary-title').textContent = failed ? '한 번 더, 더 확실하게.' : '모든 단어를 기억했어요!';
    $('summary-copy').textContent = failed ? `이번 사이클에서 실패한 ${failed}개만 다음 사이클에서 다시 만나요.` : `총 ${cards.length}개 단어를 ${state.cycle}사이클에 걸쳐 공부했어요.`;
    $('summary-passed').textContent = state.passed;
    $('summary-failed').textContent = failed;
    $('continue').textContent = failed ? `실패 ${failed}개 다시 풀기 →` : '전체 단어 다시 시작하기 →';
    if (moveFocus) $('summary').focus({ preventScroll: true });
    return;
  }
  const card = cardMap.get(state.queue[state.index]);
  const answer = state.phase === 'answer';
  $('cycle').textContent = `사이클 ${state.cycle}`;
  $('position').textContent = `${state.index + 1} / ${state.queue.length}`;
  $('counts').textContent = `성공 ${state.passed} · 실패 ${state.failed.length}`;
  $('progress').max = state.queue.length;
  $('progress').value = state.index;
  $('card-number').textContent = `DE · ${String(state.index + 1).padStart(3, '0')}`;
  $('term').textContent = card.term;
  $('sentence').textContent = card.sentence;
  $('meaning').textContent = answer ? card.meaning : '';
  $('answer').hidden = !answer;
  $('prompt').hidden = answer;
  $('reveal').hidden = answer;
  $('grading').hidden = !answer;
  $('phase-label').textContent = answer ? 'WORT & BEDEUTUNG' : 'WORT';
  $('keyboard-help').textContent = answer ? '1 또는 ← 실패 · 2 또는 → 성공' : 'Space 또는 Enter로 뜻 확인';
  if (moveFocus) $(answer ? 'success' : 'reveal').focus({ preventScroll: true });
}

function update(next) {
  if (next === state) return;
  state = next;
  save();
  render(true);
}

function reset() { update(createSession(ids, version)); }
$('reveal').addEventListener('click', () => update(reveal(state)));
$('failure').addEventListener('click', () => update(grade(state, false)));
$('success').addEventListener('click', () => update(grade(state, true)));
$('continue').addEventListener('click', () => update(continueSession(state, ids)));
$('reset').addEventListener('click', () => {
  if (confirm('저장된 진행 상황을 지우고 전체 단어를 처음부터 공부할까요?')) reset();
});
$('audio').addEventListener('error', () => { $('audio-error').hidden = false; });

document.addEventListener('keydown', event => {
  if (!state || event.altKey || event.ctrlKey || event.metaKey) return;
  if (event.repeat) {
    if ([' ', 'Enter', '1', '2', 'ArrowLeft', 'ArrowRight'].includes(event.key)) event.preventDefault();
    return;
  }
  if (['AUDIO', 'INPUT', 'TEXTAREA', 'SELECT', 'SUMMARY'].includes(event.target.tagName)) return;
  // Keep native button keyboard activation; avoid handling the same key twice.
  if (event.target.tagName === 'BUTTON' && [' ', 'Enter'].includes(event.key)) return;
  if (state.phase === 'question' && [' ', 'Enter'].includes(event.key)) {
    event.preventDefault(); update(reveal(state));
  } else if (state.phase === 'answer' && ['1', 'ArrowLeft', '2', 'ArrowRight'].includes(event.key)) {
    event.preventDefault(); update(grade(state, ['2', 'ArrowRight'].includes(event.key)));
  }
});

try {
  const response = await fetch('/api/cards', { cache: 'no-store' });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || '단어장을 불러올 수 없습니다.');
  ({ cards, version } = data);
  ids = cards.map(card => card.id);
  cardMap = new Map(cards.map(card => [card.id, card]));
  let stored = null;
  try { stored = localStorage.getItem(STORAGE_KEY); }
  catch { notice('진행 상황을 저장할 수 없는 브라우저 모드입니다.'); }
  state = restoreSession(stored, ids, version);
  save();
  $('loading').hidden = true;
  $('reset').disabled = false;
  render();
} catch (error) {
  $('loading').textContent = '단어장을 불러오지 못했어요. 수정 후 새로고침해 주세요.';
  notice(error.message);
}
