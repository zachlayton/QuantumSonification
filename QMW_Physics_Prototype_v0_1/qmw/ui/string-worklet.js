/* Exact zero-order-hold mechanical modes, coefficients from StiffString. */
class PhysicalString extends AudioWorkletProcessor {
  constructor(options) {
    super();this.c=options.processorOptions;
    this.q=new Float64Array(this.c.k.length);this.v=new Float64Array(this.q.length);
    this.forces=new Float64Array(this.q.length);this.contacts=[];
    this.pickups=[.18,.31];this.updatePickups();this.meterSamples=0;this.peak=0;
    this.port.onmessage=({data})=>{
      if(data.clearContacts)this.contacts.length=0;
      if(data.pickups){this.pickups=data.pickups;this.updatePickups();}
      if(data.event){
        const e=data.event;
        if(!Number.isFinite(e.impulse_ns)||!Number.isFinite(e.contact_s)||e.contact_s<=0||!Number.isFinite(e.position)||e.position<=0||e.position>=1||!Number.isFinite(e.width_m)||e.width_m<0)return;
        const count=Math.max(2,Math.round(e.contact_s*sampleRate));
        const pulse=new Float64Array(count),weights=this.weights(e.position,e.width_m);
        for(let i=0;i<count;i++)pulse[i]=e.impulse_ns*sampleRate/count*(1-Math.cos(2*Math.PI*(i+.5)/count));
        this.contacts.push({pulse,weights,count,index:0,delay:Math.max(0,Math.round((data.delay_s||0)*sampleRate))});
      }
    };
  }
  weights(position,width){
    const length=this.c.length_m||.86;
    return Float64Array.from(this.c.k,k=>{const z=k*width/2;return Math.sin(k*position*length)*(z===0?1:Math.sin(z)/z);});
  }
  updatePickups(){this.pickupWeights=this.pickups.map(position=>this.weights(position,.008));}
  process(inputs,outputs){
    const out=outputs[0],c=this.c;
    for(let s=0;s<out[0].length;s++){
      const forces=this.forces;forces.fill(0);
      for(const contact of this.contacts){
        if(contact.delay>0){contact.delay--;continue;}
        const f=contact.pulse[contact.index];
        for(let m=0;m<forces.length;m++)forces[m]+=f*contact.weights[m];
        contact.index++;
      }
      for(let i=this.contacts.length-1;i>=0;i--)if(this.contacts[i].index>=this.contacts[i].count)this.contacts.splice(i,1);
      for(let m=0;m<forces.length;m++){
        const q=this.q[m],v=this.v[m],f=forces[m];
        this.q[m]=c.a11[m]*q+c.a12[m]*v+c.bq[m]*f;
        this.v[m]=c.a21[m]*q+c.a22[m]*v+c.bv[m]*f;
      }
      for(let channel=0;channel<out.length;channel++){
        let velocity=0;
        for(let m=0;m<forces.length;m++)velocity+=this.v[m]*this.pickupWeights[channel%this.pickupWeights.length][m];
        out[channel][s]=velocity;this.peak=Math.max(this.peak,Math.abs(velocity));
      }
      if(++this.meterSamples>=sampleRate*.25){this.port.postMessage({peak:this.peak});this.peak=0;this.meterSamples=0;}
    }
    return true;
  }
}
registerProcessor('physical-string',PhysicalString);
