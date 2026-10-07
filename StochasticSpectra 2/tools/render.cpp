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
    stoch::Settings s; auto bank=stoch::makeBank(s); stoch::Engine e;
    std::vector<double> demo;
    // 5 segments of 8 seconds, separated by 1 second silence.
    for(int segment=0;segment<5;++segment) {
        s.motion=segment<2?0:segment==2?1:2;
        s.tau=segment==2?1.5:segment==3?0.4:0.02;
        ++s.reset; bank=stoch::makeBank(s); e.configure(bank);
        for(int n=0;n<8*48000;++n) {
            auto f=e.sample(); double value=segment==0?f.wavetable:f.modal;
            double fade=std::min({1.0,n/960.0,(8*48000-1-n)/960.0}); demo.push_back(value*fade);
        }
        if(segment!=4) demo.insert(demo.end(),48000,0);
    }
    wav(dir+"/stochastic_spectra_demo.wav",demo,1);
    s.motion=0; ++s.reset; bank=stoch::makeBank(s); e.configure(bank);
    std::vector<double> matched; matched.reserve(2*8*48000);
    for(int n=0;n<8*48000;++n) {
        auto f=e.sample(); double fade=std::min({1.0,n/960.0,(8*48000-1-n)/960.0});
        matched.push_back(f.wavetable*fade); matched.push_back(f.modal*fade);
    }
    wav(dir+"/matched_wavetable_L_modal_R.wav",matched,2);
    std::ofstream raw(dir+"/cycle_raw.f64",std::ios::binary);
    raw.write(reinterpret_cast<const char*>(bank.table.data()),sizeof(double)*stoch::TableSize);
}
