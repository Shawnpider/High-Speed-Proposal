// -*- c-basic-offset: 4; indent-tabs-mode: nil -*-        
#ifndef PIPE_H
#define PIPE_H

/*
 * A pipe is a dumb device which simply delays all incoming packets
 */

#include <list>
#include <utility>
#include "config.h"
#include "eventlist.h"
#include "network.h"
#include "loggertypes.h"
#include "drawable.h"

/* =======================
 * Core link utilization
 * ======================= */
extern std::map<std::string, uint64_t> core_link_bytes;

// dump function declaration
void dump_core_link_bytes();

typedef struct pktrecord {
    simtime_picosec time;
    Packet* pkt;
} pktrecord_t;

class Switch;

class Pipe : public EventSource, public PacketSink, public Drawable {
 public:
    Pipe(simtime_picosec delay, EventList& eventlist=EventList::getTheEventList());
    virtual void receivePacket(Packet& pkt); // inherited from PacketSink
    virtual void doNextEvent(); // inherited from EventSource
    simtime_picosec delay() { return _delay; }
    const string& nodename() { return _nodename; }
    void forceName(string name) {_nodename = name;}
    
    void setNext(PacketSink* next_sink) {
            _next_sink = next_sink;
    }
    PacketSink* next() const {
            return _next_sink;
    }
    void setSwitch(Switch* sw) { _switch = sw; }
    Switch* getSwitch() const { return _switch; }
protected:
    string _nodename;
    //typedef pair<simtime_picosec,Packet*> pktrecord_t;
    //list<pktrecord_t> _inflight; // the packets in flight (or being serialized)
    vector<pktrecord_t> _inflight_v;
    int _next_insert, _next_pop, _count, _size;
private:
    simtime_picosec _delay;
    PacketSink* _next_sink{nullptr}; // used in generic topology for linkage
    Switch* _switch = nullptr;
};


#endif
