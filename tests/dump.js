// Print date-holidays public holidays for the regions in data/regions.csv, 2026-2028, as JSON.
const Holidays = require('date-holidays');
const out = {};
for (const reg of process.argv.slice(2)) {
  const [cc, sd] = reg.split('-');
  const h = sd ? new Holidays(cc, sd) : new Holidays(cc);
  out[reg] = {};
  for (const y of [2026, 2027, 2028]) {
    out[reg][y] = h.getHolidays(y).filter(x => x.type === 'public').map(x =>
      [x.date.slice(0, 10), Math.max(1, Math.round((x.end - x.start) / 86400000)), x.substitute ? 1 : 0]);
  }
}
process.stdout.write(JSON.stringify(out));
