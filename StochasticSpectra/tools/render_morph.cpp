#include "../source/stochastic_core.hpp"
#include <fstream>
#include <string>
#include <iostream>
#include <vector>
#include <stdexcept>
static void u16(std::ostream& o,uint16_t x) { o.put(char(x)); o.put(char(x>>8)); }
static void u32(std::ostream& o,uint32_t x) { u16(o,uint16_t(x)); u16(o,uint16_t(x>>16)); }
static void wav(const std::string& path,const std::vector<double>& data,int channels) {
    std::ofstream o(path,std::ios::binary); if(!o) throw std::runtime_error("cannot open "+path);
    uint32_t bytes=uint32_t(data.size()*3); o.write("RIFF",4); u32(o,36+bytes); o.write("WAVEfmt ",8);
    u32(o,16); u16(o,1); u16(o,uint16_t(channels)); u32(o,48000); u32(o,48000*channels*3);
    u16(o,uint16_t(channels*3)); u16(o,24); o.write("data",4); u32(o,bytes);
    double peak=0;
    for(double x:data) { if(!std::isfinite(x)||std::abs(x)>=1) throw std::runtime_error("invalid/clipping audio");
        peak=std::max(peak,std::abs(x)); int32_t v=int32_t(std::llround(x*8388607));
        o.put(char(v)); o.put(char(v>>8)); o.put(char(v>>16)); }
    std::cout<<path<<": "<<double(data.size())/channels/48000<<" seconds, peak "<<peak<<"\n";
}
int main(int argc,char** argv) {
    std::string dir=argc>1?argv[1]:"audio";
    stoch::Settings s; s.modes=24; s.slope=0.5; s.rate=2; s.gain=0.15;
    std::vector<double> demo;
    for(int segment=0;segment<4;++segment) {
        s.evolve=segment!=0; s.interpMs=segment==2 ? 400 : 30;
        s.slewMs=segment==3 ? 250 : 5;
        ++s.reset; stoch::Engine e; e.configure(stoch::makeBank(s));
        int length=(segment==0?4:8)*48000;
        for(int n=0;n<length;++n) {
            auto f=e.sample();
            double fade=std::min({1.0,n/960.0,(length-1-n)/960.0});
            demo.push_back(f.wavetable*fade);
        }
        if(segment!=3) demo.insert(demo.end(),48000,0);
    }
    wav(dir+"/evolving_spectra_interp_slew.wav",demo,1);

    // Matched rate comparison: only stochastic target arrivals per second vary.
    demo.clear();
    const double rates[]={0.5,2.0,8.0};
    for(int segment=0;segment<3;++segment) {
        stoch::Settings rateSettings;
        rateSettings.modes=24; rateSettings.slope=0; rateSettings.gain=0.12;
        rateSettings.evolve=1; rateSettings.rate=rates[segment];
        rateSettings.interpMs=400; rateSettings.slewMs=20;
        stoch::Engine engine; engine.configure(stoch::makeBank(rateSettings));
        constexpr int length=6*48000;
        for(int n=0;n<length;++n) {
            const double fade=std::min({1.0,n/960.0,(length-1-n)/960.0});
            demo.push_back(engine.sample().wavetable*fade);
        }
        if(segment!=2) demo.insert(demo.end(),48000,0);
    }
    wav(dir+"/evolving_rate_comparison.wav",demo,1);
}
