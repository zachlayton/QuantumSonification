"""Execute the actual AudioWorklet against the independent Python string model."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

import numpy as np
from qmw.sound.stiff_string import StiffString


WORKLET = Path(__file__).resolve().parents[1] / 'qmw/ui/harmonic-worklet.js'


class HarmonicWorkletTests(unittest.TestCase):
    def run_worklet(self, events, samples=512):
        model = StiffString(sample_rate=48000)
        coefficients = {name: getattr(model, name).tolist()
                        for name in ('k', 'a11', 'a12', 'a21', 'a22', 'bq', 'bv')}
        coefficients['length_m'] = model.parameters.length_m
        script = r'''
const fs=require('fs'), vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
let Processor;
global.sampleRate=48000; global.currentFrame=0; global.currentTime=0;
global.AudioWorkletProcessor=class { constructor(){this.port={onmessage:null,postMessage(){}};} };
global.registerProcessor=(name, cls)=>{Processor=cls;};
vm.runInThisContext(fs.readFileSync(input.path,'utf8'));
const p=new Processor({processorOptions:input.coefficients}), output=[];
for(let i=0;i<input.samples;i++) {
  global.currentFrame=i; global.currentTime=i/sampleRate;
  for(const e of input.events) if(e.delivery_sample===i) p.port.onmessage({data:{event:e,delay_s:e.delay_s||0}});
  const channels=[new Float32Array(1),new Float32Array(1)];
  p.process([], [channels]); output.push([channels[0][0],channels[1][0]]);
}
process.stdout.write(JSON.stringify({q:Array.from(p.q),v:Array.from(p.v),output}));
'''
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node is required to execute the worklet')
        result = subprocess.run([node, '-e', script], input=json.dumps({
            'path': str(WORKLET), 'coefficients': coefficients,
            'events': events, 'samples': samples}), text=True,
            capture_output=True, check=True)
        return model, json.loads(result.stdout)

    @staticmethod
    def event(n, delivery=0):
        return dict(harmonic_index=n, delivery_sample=delivery, impulse_ns=.0002,
                    contact_s=.0015, position=.4, width_m=.006, t=delivery/48000)

    def test_silent_string_has_no_self_excitation(self):
        _, result = self.run_worklet([])
        self.assertTrue(np.all(np.asarray(result['output']) == 0))
        self.assertTrue(np.all(np.asarray(result['q']) == 0))
        self.assertTrue(np.all(np.asarray(result['v']) == 0))

    def test_selected_modes_match_independent_python_evolution(self):
        for n in (2, 3, 5, 7):
            with self.subTest(harmonic=n):
                event = self.event(n)
                model, result = self.run_worklet([event])
                count = round(event['contact_s']*48000)
                pulse = event['impulse_ns']*48000/count*(1-np.cos(2*np.pi*(np.arange(count)+.5)/count))
                forces = np.zeros((model.count, 512))
                forces[n-1, :count] = pulse
                expected = model.process(forces)
                np.testing.assert_allclose(result['output'], expected, rtol=2e-6, atol=2e-8)
                np.testing.assert_allclose(result['q'], model.q, rtol=2e-8, atol=2e-12)
                np.testing.assert_allclose(result['v'], model.v, rtol=2e-8, atol=2e-10)
                inactive = np.arange(model.count) != n-1
                self.assertTrue(np.all(np.asarray(result['q'])[inactive] == 0))
                self.assertTrue(np.all(np.asarray(result['v'])[inactive] == 0))

    def test_second_selection_preserves_first_modes_tail(self):
        _, first = self.run_worklet([self.event(2)], samples=768)
        _, both = self.run_worklet([self.event(2), self.event(7, 256)], samples=768)
        self.assertNotEqual(first['v'][1], 0)
        self.assertEqual(first['q'][1], both['q'][1])
        self.assertEqual(first['v'][1], both['v'][1])
        self.assertNotEqual(both['v'][6], 0)

    def test_delayed_contacts_retain_chronological_spacing(self):
        early = self.event(2)
        later = self.event(7)
        later['delay_s'] = 256/48000
        _, scheduled = self.run_worklet([early, later], samples=768)
        _, delivered = self.run_worklet([early, self.event(7, 256)], samples=768)
        np.testing.assert_array_equal(scheduled['output'], delivered['output'])
        np.testing.assert_array_equal(scheduled['q'], delivered['q'])
        np.testing.assert_array_equal(scheduled['v'], delivered['v'])

    def test_physical_contact_still_projects_force_spatially(self):
        event = self.event(2)
        del event['harmonic_index']
        model, result = self.run_worklet([event])
        count = round(event['contact_s']*48000)
        pulse = event['impulse_ns']*48000/count*(1-np.cos(2*np.pi*(np.arange(count)+.5)/count))
        force = np.zeros(512)
        force[:count] = pulse
        expected = model.process(force, position=event['position'], contact_width_m=event['width_m'])
        np.testing.assert_allclose(result['output'], expected, rtol=2e-6, atol=2e-8)
        np.testing.assert_allclose(result['q'], model.q, rtol=2e-8, atol=2e-12)
        self.assertGreater(np.count_nonzero(result['v']), 1)
