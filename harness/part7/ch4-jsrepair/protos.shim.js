// DOCTOR-JS-0 shim js.protos — reflectable interface prototypes (WebIDL §3.7.3 interface prototype objects).
// Problem found by the doctor's API census: our host objects resolve their members natively and the interface prototypes are empty,
// so Object.getOwnPropertyNames(Node.prototype) is [] and Object.getOwnPropertyDescriptor(Node.prototype, 'firstChild') is
// undefined — polyfills (webcomponents-sd / ShadyDOM) that copy native descriptors patch nothing and then fail.
// Fix: for each name Chrome exposes on a prototype (DATA: name → kind, observed output only), install a descriptor that forwards to
// the host member — but only when a sample host object really resolves that name natively. Host members win over prototype entries
// when a node reads them, so a forwarder never recurses. Dormant switch: window.__omr_off_protos = true before this runs.
var samples = {
  EventTarget: function () { return document.createElement('div'); }, Node: function () { return document.createElement('div'); },
  Element: function () { return document.createElement('div'); }, HTMLElement: function () { return document.createElement('div'); },
  Document: function () { return document; }, DocumentFragment: function () { return document.createDocumentFragment(); },
  CharacterData: function () { return document.createTextNode('x'); }, Text: function () { return document.createTextNode('x'); },
  Event: function () { return new Event('x'); }
};
var made = 0, iface, n, k;
for (iface in DATA) {
  var C = g[iface]; if (!C || !C.prototype || !samples[iface]) continue;
  var proto = C.prototype, sample;
  try { sample = samples[iface](); } catch (e) { continue; }
  for (n in DATA[iface]) {
    if (n === 'constructor') continue;
    k = DATA[iface][n];
    if (Object.prototype.hasOwnProperty.call(proto, n)) continue;
    var v; try { v = sample[n]; } catch (e) { continue; }
    var constant = (k === 'v' && typeof C[n] === 'number');
    if (constant) { try { Object.defineProperty(proto, n, { value: C[n], writable: false, enumerable: true, configurable: false }); made++; } catch (e) {} continue; }
    if (v === undefined) continue; // the host does not implement it: no descriptor (an honest gap, not a lie)
    (function (name, kind, isFn) {
      try {
        if (kind === 'm' || isFn) {
          var fwd = function () { var f = this[name]; if (f === fwd || typeof f !== 'function') throw new TypeError(name + ' is not a function on this object'); return f.apply(this, arguments); };
          Object.defineProperty(proto, name, { value: fwd, writable: true, enumerable: true, configurable: true });
        } else {
          var busy = false;
          var d = { get: function () { if (busy) return undefined; busy = true; try { return this[name]; } finally { busy = false; } }, enumerable: true, configurable: true };
          if (kind === 'gs') d.set = function (x) { if (busy) return; busy = true; try { this[name] = x; } finally { busy = false; } };
          Object.defineProperty(proto, name, d);
        }
        made++;
      } catch (e) {}
    })(n, k, typeof v === 'function');
  }
}
g.__omr_protos_made = made;
