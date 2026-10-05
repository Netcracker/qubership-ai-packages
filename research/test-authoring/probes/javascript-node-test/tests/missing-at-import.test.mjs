import { noSuchExport } from 'node:test';

noSuchExport('never runs', () => {});
