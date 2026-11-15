const topo=require('./node_modules/world-atlas/countries-50m.json');
const {feature}=require('topojson-client');
const fc=feature(topo, topo.objects.countries);
const out={};
for (const id of ['704','156','418','116']) { const f=fc.features.find(f=>f.id===id); out[id]=f.geometry; }
require('fs').writeFileSync('region.json', JSON.stringify(out));
