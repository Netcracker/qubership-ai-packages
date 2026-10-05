// The function under test in every probe. It returns its argument instead of refusing a negative count.
function ensureBytes(count) {
  return count;
}

module.exports = { ensureBytes };
