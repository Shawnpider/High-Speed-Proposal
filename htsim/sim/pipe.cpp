// -*- c-basic-offset: 4; indent-tabs-mode: nil -*-        
#include "pipe.h"
#include <iostream>
#include <sstream>
#include <fstream>
#include "switch.h"

std::map<std::string, uint64_t> core_link_bytes;

void dump_core_link_bytes() {
    std::ofstream out("core_link_bytes.csv");
    out << "link_name,total_bytes\n";
    for (auto &kv : core_link_bytes) {
        out << kv.first << "," << kv.second << "\n";
    }
    out.close();
}

Pipe::Pipe(simtime_picosec delay, EventList& eventlist)
: EventSource(eventlist,"pipe"), _delay(delay)
{
    _count = 0;
    _next_insert = 0;
    _next_pop = 0;
    _size = 16; // initial size; we'll resize if needed
    _inflight_v.resize(_size);
    stringstream ss;
    ss << "pipe(" << delay/1000000 << "us)";
    _nodename= ss.str();
}

void
Pipe::receivePacket(Packet& pkt)
{
    //pkt.flow().logTraffic(pkt,*this,TrafficLogger::PKT_ARRIVE);
    //if (_inflight.empty()){
    if (_count == 0){
        /* no packets currently inflight; need to notify the eventlist
           we've an event pending */
            eventlist().sourceIsPendingRel(*this,_delay);
    }
    _count++;
    if (_count == _size) {
        _inflight_v.resize(_size*2);
        if (_next_insert < _next_pop) {
                //   456789*123
                // NI *, NP 1
            for (int i=0; i < _next_insert; i++) {
                // move 4-9 into new space
                _inflight_v.at(_size+i) = _inflight_v.at(i);
            }
            _next_insert += _size;
        } else {
            // 123456789*
            // nothing to do
        }
        _size += _size;
    }
    _inflight_v[_next_insert].time = eventlist().now() + _delay;
    _inflight_v[_next_insert].pkt = &pkt;
    _next_insert = (_next_insert +1) % _size;
    //_inflight.push_front(make_pair(eventlist().now() + _delay, &pkt));
}

void
Pipe::doNextEvent() {

    /*cout << "[DEBUG][EVENT] pipe "
     << _nodename
     << " this=" << this
     << " switch=" << _switch
     << endl;*/

    /*if (_switch == nullptr) {
        static int cnt = 0;
        if (cnt < 10) {
            std::cout << "[DEBUG] pipe " << _nodename
                      << " has NULL switch" << std::endl;
            cnt++;
        }
    } else {
        cout << "[DEBUG][HIT] pipe "
        << _nodename
        << " switch=" << _switch->nodename()
        << endl;
    }*/

    //if (_inflight.size() == 0) 
    if (_count == 0) 
            return;

    //Packet *pkt = _inflight.back().second;
    //_inflight.pop_back();
    Packet *pkt = _inflight_v[_next_pop].pkt;
    _next_pop = (_next_pop +1) % _size;
    _count--;
    pkt->flow().logTraffic(*pkt, *this,TrafficLogger::PKT_DEPART);

    // ===== Core link utilization accounting (FINAL, CORRECT) =====
    if (_switch && _switch->nodename().find("Switch_Core_") != std::string::npos) {
        core_link_bytes[_switch->nodename()] += pkt->size();
    }

    static int hit = 0;
    if (_nodename.find("CS") != std::string::npos && hit < 10) {
        std::cout << "[DEBUG] packet passes core pipe "
                << _nodename
                << " size=" << pkt->size()
                << std::endl;
        hit++;
    }


    // tell the packet to move itself on to the next hop
    pkt->sendOn();

    //if (!_inflight.empty()) {
    if (_count > 0) {
        // notify the eventlist we've another event pending
        simtime_picosec nexteventtime = _inflight_v[_next_pop].time;
        _eventlist.sourceIsPending(*this, nexteventtime);
    }
}
