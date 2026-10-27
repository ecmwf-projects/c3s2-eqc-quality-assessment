// Keep doi.org links as plain links.
// MyST turns them into citations, fetching every DOI from doi.org at build time and
// appending a bibliography that repeats the references listed in each assessment.
const DOI_HOSTNAMES = new Set(['doi.org', 'www.doi.org', 'dx.doi.org']);
const HIDDEN_TYPE = 'plainDoiLink';

function isDoiLink(url) {
  try {
    return DOI_HOSTNAMES.has(new URL(url).hostname.toLowerCase());
  } catch {
    return false;
  }
}

function hasText(node) {
  return Boolean(node.value) || (node.children ?? []).some(hasText);
}

const plugin = {
  name: 'Plain DOI links',
  transforms: [
    {
      name: 'hide-doi-links',
      doc: 'Hide doi.org links from the DOI citation transform.',
      stage: 'document',
      plugin: (_, utils) => (tree) => {
        utils.selectAll('link', tree).forEach((node) => {
          if (isDoiLink(node.url)) node.type = HIDDEN_TYPE;
        });
      },
    },
    {
      name: 'restore-doi-links',
      doc: 'Turn the hidden doi.org links back into links.',
      stage: 'project',
      plugin: (_, utils) => (tree) => {
        utils.selectAll(HIDDEN_TYPE, tree).forEach((node) => {
          node.type = 'link';
          if (!hasText(node)) node.children = [{ type: 'text', value: node.url }];
        });
      },
    },
  ],
};

export default plugin;
