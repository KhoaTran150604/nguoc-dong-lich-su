const topo=require('./node_modules/world-atlas/countries-50m.json');
const {feature}=require('topojson-client');
const fc=feature(topo, topo.objects.countries);
const vn=fc.features.find(f=>f.id==='704');
console.log(vn.properties, vn.geometry.type, vn.geometry.coordinates.length);
require('fs').writeFileSync('vn.json', JSON.stringify(vn.geometry));
