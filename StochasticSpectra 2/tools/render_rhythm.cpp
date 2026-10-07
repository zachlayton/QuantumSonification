#include "../source/stochastic_core.hpp"
#include "../source/packet_envelope_core.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

static void u16(std::ostream& out,uint16_t value) {
    out.put(char(value)); out.put(char(value>>8));
}
static void u32(std::ostream& out,uint32_t value) {
    u16(out,uint16_t(value)); u16(out,uint16_t(value>>16));
}
static void writeWav(const std::string& path,const std::vector<double>& data) {
    std::ofstream out(path,std::ios::binary);
    if(!out) throw std::runtime_error("cannot open "+path);
    const uint32_t bytes=uint32_t(data.size()*3);
    out.write("RIFF",4); u32(out,36+bytes); out.write("WAVEfmt ",8);
    u32(out,16); u16(out,1); u16(out,1); u32(out,48000); u32(out,48000*3);
    u16(out,3); u16(out,24); out.write("data",4); u32(out,bytes);
    double peak=0;
    for(double sample:data) {
        if(!std::isfinite(sample)||std::abs(sample)>=1)
            throw std::runtime_error("invalid or clipping audio");
        peak=std::max(peak,std::abs(sample));
        const int32_t value=int32_t(std::llround(sample*8388607));
        out.put(char(value)); out.put(char(value>>8)); out.put(char(value>>16));
    }
    std::cout<<path<<": "<<double(data.size())/48000<<" seconds, peak "<<peak<<"\n";
}

int main(int argc,char** argv) {
    const std::string directory=argc>1 ? argv[1] : "audio";
    std::vector<double> demo;
    const double shapes[]={0.5,1.0,4.0};
    for(int segment=0;segment<3;++segment) {
        stoch::Settings spectral;
        spectral.modes=24; spectral.slope=0.5; spectral.gain=0.12;
        stoch::Engine voice; voice.configure(stoch::makeBank(spectral));
        stoch::packet::Settings packet;
        packet.mode=1; packet.density=3; packet.shape=shapes[segment];
        packet.durationMs=150; packet.polyphony=16;
        stoch::packet::Engine envelope; envelope.configure(stoch::packet::makeBank(packet));
        constexpr int length=8*48000;
        for(int n=0;n<length;++n) {
            const double sample=voice.sample().wavetable*envelope.sample().envelope;
            const double fade=std::min({1.0,n/960.0,(length-1-n)/960.0});
            demo.push_back(sample*fade);
        }
        if(segment!=2) demo.insert(demo.end(),48000,0);
    }
    writeWav(directory+"/gamma_renewal_packets.wav",demo);
}
