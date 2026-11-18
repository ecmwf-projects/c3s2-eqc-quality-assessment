// Number figures and tables that have no label, as Jupyter Book 1 did.
// MyST only shows the number of a figure or table in its caption if it has a label.
import path from 'node:path';

const plugin = {
  name: 'Number all figures',
  transforms: [
    {
      name: 'label-figures',
      doc: 'Give unlabelled figures and tables a label, so their captions show their number.',
      stage: 'document',
      plugin: (_, utils) => (tree, vfile) => {
        const page = path.parse(vfile.path).name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
        utils.selectAll('container', tree).forEach((node, index) => {
          if (node.identifier || node.subcontainer) return;
          node.identifier = `${page}-${node.kind ?? 'container'}-${index + 1}`;
          node.label = node.identifier;
          node.html_id = node.identifier;
          node.implicit = true;
        });
      },
    },
  ],
};

export default plugin;
