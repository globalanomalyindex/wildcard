// Render selections immediately, but coalesce their URL writes. WebKit limits
// history replacement frequency, including changes caused by held arrow keys.
export function createSelectionUrlCommitter(browser = window) {
  let scheduled = false, latest;
  return selection => {
    latest = {...selection};
    if (scheduled) return;
    scheduled = true;
    browser.setTimeout(() => {
      scheduled = false;
      // Navigation may have changed the view while this write was pending.
      const url = new URL(browser.location.href);
      for (const key of ['task','left','right']) url.searchParams.set(key, latest[key]);
      browser.history.replaceState(null, '', url);
    }, 150);
  };
}
