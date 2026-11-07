/** Pure quiz transitions; the deck's existing order preserves vocabulary groups. */
export function createSession(ids, version) {
  if (!ids.length || new Set(ids).size !== ids.length) throw new Error('단어장이 비었거나 ID가 중복됩니다.');
  return { version, cycle: 1, queue: [...ids], index: 0, failed: [], passed: 0, phase: 'question' };
}

export function reveal(state) {
  return state.phase === 'question' ? { ...state, phase: 'answer' } : state;
}

export function grade(state, success) {
  if (state.phase !== 'answer') return state;
  const index = state.index + 1;
  return { ...state, index, passed: state.passed + (success ? 1 : 0),
    failed: success ? [...state.failed] : [...state.failed, state.queue[state.index]],
    phase: index === state.queue.length ? 'summary' : 'question' };
}

export function nextCycle(state) {
  if (state.phase !== 'summary' || !state.failed.length) return state;
  return { ...state, cycle: state.cycle + 1, queue: [...state.failed], index: 0,
    failed: [], passed: 0, phase: 'question' };
}

export function continueSession(state, allIds) {
  if (state.phase !== 'summary') return state;
  return state.failed.length ? nextCycle(state) : createSession(allIds, state.version);
}

export function restoreSession(raw, ids, version) {
  const fresh = () => createSession(ids, version);
  try {
    const s = JSON.parse(raw);
    const validIds = new Set(ids);
    if (!s || s.version !== version || !Number.isInteger(s.cycle) || s.cycle < 1
      || !Array.isArray(s.queue) || !s.queue.length || !s.queue.every(id => validIds.has(id))
      || new Set(s.queue).size !== s.queue.length
      || (s.cycle === 1 && (s.queue.length !== ids.length || !s.queue.every((id, i) => id === ids[i])))
      || !Number.isInteger(s.index) || s.index < 0 || s.index > s.queue.length
      || !Number.isInteger(s.passed) || s.passed < 0
      || !Array.isArray(s.failed) || new Set(s.failed).size !== s.failed.length
      || !s.failed.every(id => s.queue.slice(0, s.index).includes(id))
      || s.passed + s.failed.length !== s.index
      || !['question', 'answer', 'summary'].includes(s.phase)
      || (s.phase === 'summary') !== (s.index === s.queue.length)) return fresh();
    return { version: s.version, cycle: s.cycle, queue: s.queue, index: s.index,
      failed: s.failed, passed: s.passed, phase: s.phase };
  } catch {
    return fresh();
  }
}
