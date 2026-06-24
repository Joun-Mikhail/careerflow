import { describe, expect, it } from 'vitest';

import { toCsv } from './csv';

describe('toCsv', () => {
  const columns = [
    { key: 'role' as const, header: 'Role' },
    { key: 'company' as const, header: 'Company' },
  ];

  it('writes a header row and one row per record', () => {
    const csv = toCsv([{ role: 'Engineer', company: 'Acme' }], columns);
    const lines = csv.replace(/^\uFEFF/, '').split('\r\n');
    expect(lines[0]).toBe('Role,Company');
    expect(lines[1]).toBe('Engineer,Acme');
  });

  it('quotes fields containing commas, quotes, or newlines', () => {
    const csv = toCsv(
      [{ role: 'Eng, Sr', company: 'A "B" Co' }],
      columns,
    ).replace(/^\uFEFF/, '');
    expect(csv.split('\r\n')[1]).toBe('"Eng, Sr","A ""B"" Co"');
  });

  it('renders null and undefined as empty cells', () => {
    const csv = toCsv(
      [{ role: null as unknown as string, company: undefined as unknown as string }],
      columns,
    ).replace(/^\uFEFF/, '');
    expect(csv.split('\r\n')[1]).toBe(',');
  });

  it('prepends a UTF-8 BOM', () => {
    expect(toCsv([], columns).startsWith('\uFEFF')).toBe(true);
  });
});
