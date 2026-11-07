import test from 'node:test';
import assert from 'node:assert/strict';
import { createSession, reveal, grade, nextCycle, restoreSession } from './quiz.mjs';

const ids = ['a', 'b', 'c'];

test('only failed cards enter the next cycle after the whole cycle ends', () => {
  let state = createSession(ids, 'v1');
  assert.equal(state.phase, 'question');
  state = grade(reveal(state), false);
  assert.equal(state.queue[state.index], 'b');
  assert.equal(state.phase, 'question');
  state = grade(reveal(state), true);
  state = grade(reveal(state), false);
  assert.equal(state.phase, 'summary');
  assert.deepEqual(state.failed, ['a', 'c']);
  state = nextCycle(state);
  assert.equal(state.cycle, 2);
  assert.deepEqual(state.queue, ['a', 'c']);
  state = grade(reveal(state), true);
  state = grade(reveal(state), true);
  assert.equal(state.phase, 'summary');
  assert.deepEqual(state.failed, []);
  assert.deepEqual(nextCycle(state), state);
});

test('grading a hidden answer and duplicate grading cannot skip cards', () => {
  let state = createSession(ids, 'v1');
  assert.deepEqual(grade(state, true), state);
  state = grade(reveal(state), false);
  assert.deepEqual(grade(state, false), state);
  assert.deepEqual(nextCycle(state), state);
});

test('resume preserves answer visibility and wrong answers', () => {
  let state = grade(reveal(createSession(ids, 'v1')), false);
  state = reveal(state);
  assert.deepEqual(restoreSession(JSON.stringify(state), ids, 'v1'), state);
});

test('corrupt, stale and invalid queues reset safely', () => {
  const fresh = createSession(ids, 'v1');
  const cases = ['{', 'null', '{}', JSON.stringify({ ...fresh, version: 'old' }),
    JSON.stringify({ ...fresh, index: -1 }), JSON.stringify({ ...fresh, queue: ['unknown'] }),
    JSON.stringify({ ...fresh, queue: ['a', 'a'] }), JSON.stringify({ ...fresh, failed: ['c'] }),
    JSON.stringify({ ...fresh, phase: 'summary' }), JSON.stringify({ ...fresh, passed: 1 })];
  for (const raw of cases) assert.deepEqual(restoreSession(raw, ids, 'v1'), fresh);
});

test('a completed cycle and a one-card deck resume correctly', () => {
  const state = grade(reveal(createSession(['a'], 'v1')), true);
  assert.deepEqual(restoreSession(JSON.stringify(state), ['a'], 'v1'), state);
  assert.throws(() => createSession([], 'v1'));
});

test('a truncated first-cycle queue resets instead of silently skipping words', () => {
  const state = { ...createSession(ids, 'v1'), queue: ['a'] };
  assert.deepEqual(restoreSession(JSON.stringify(state), ids, 'v1'), createSession(ids, 'v1'));
});

test('repeated cycle continuation cannot reset the retry queue', async () => {
  const { continueSession } = await import('./quiz.mjs');
  let state = grade(reveal(createSession(['a'], 'v1')), false);
  state = continueSession(state, ids);
  assert.deepEqual(state.queue, ['a']);
  assert.equal(state.cycle, 2);
  assert.deepEqual(continueSession(state, ids), state);
  state = grade(reveal(state), true);
  assert.deepEqual(continueSession(state, ids), createSession(ids, 'v1'));
});
