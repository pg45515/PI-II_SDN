import logging
import json

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import dpset
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.exception import RyuException
from ryu.ofproto import ofproto_v1_3
from ryu.lib import ofctl_v1_3
from ryu.app.wsgi import ControllerBase
from ryu.app.wsgi import Response
from ryu.app.wsgi import WSGIApplication

LOG = logging.getLogger('ryu.app.ofctl_rest')

# supported ofctl versions in this restful app
supported_ofctl = {ofproto_v1_3.OFP_VERSION: ofctl_v1_3}

class CommandNotFoundError(RyuException):
    message = 'No such command : %(cmd)s'


class PortNotFoundError(RyuException):
    message = 'No such port info: %(port_no)s'


def monitor_method(method):
    def wrapper(self, req, dpid, *args, **kwargs):
        # Get datapath instance from DPSet
        try:
            dp = self.dpset.get(int(str(dpid), 0))
        except ValueError:
            LOG.exception('Invalid dpid: %s', dpid)
            return Response(status=400)
        if dp is None:
            LOG.error('No such Datapath: %s', dpid)
            return Response(status=404)

        # Check OpenFlow 1.3 support
        try:
            ofctl = supported_ofctl.get(dp.ofproto.OFP_VERSION)
        except KeyError:
            LOG.exception('Unsupported OF version: %s',
                          dp.ofproto.OFP_VERSION)
            return Response(status=501)

        # Invoke MonitorController method
        try:
            ret = method(self, req, dp, ofctl, *args, **kwargs)
            return Response(content_type='application/json',
                            body=json.dumps(ret))
        except ValueError:
            LOG.exception('Invalid syntax: %s', req.body)
            return Response(status=400)
        except AttributeError:
            LOG.exception('Unsupported OF request in this version: %s',
                          dp.ofproto.OFP_VERSION)
            return Response(status=501)

    return wrapper

class MonitorController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(MonitorController, self).__init__(req, link, data, **config)
        self.dpset = data['dpset']
        self.waiters = data['waiters']

    def get_switches(self, req, **_kwargs):
        dps = list(self.dpset.dps.keys())
        body = json.dumps(dps)
        return Response(content_type='application/json', body=body)

    @monitor_method
    def get_sw_details(self, req, dp, ofctl, **kwargs):
        tmp_sw_details = ofctl.get_desc_stats(dp, self.waiters)
        sw_id = list(tmp_sw_details.keys())[0]
        return tmp_sw_details[sw_id]

    @monitor_method
    def get_sw_flows(self, req, dp, ofctl, **kwargs):
        flow = req.json if req.body else {}
        tmp_flows = ofctl.get_flow_stats(dp, self.waiters, flow)
        sw_flows = sw_id = list(tmp_flows.keys())[0]
        return tmp_flows[sw_flows][0]
        #return ofctl.get_flow_stats(dp, self.waiters, flow)

    @monitor_method
    def get_flows_stats(self, req, dp, ofctl, **kwargs):
        flow = req.json if req.body else {}
        return ofctl.get_aggregate_flow_stats(dp, self.waiters, flow)

    @monitor_method
    def get_table_stats(self, req, dp, ofctl, **kwargs):
        return ofctl.get_table_stats(dp, self.waiters)

    @monitor_method
    def get_sw_ports(self, req, dp, ofctl, **kwargs):
        tmp_sw_port = ofctl.get_port_stats(dp, self.waiters, None)
        sw_id = list(tmp_sw_port.keys())[0]
        return tmp_sw_port[sw_id]
        #return ofctl.get_port_stats(dp, self.waiters, port)

    @monitor_method
    def get_sw_port(self, req, dp, ofctl, port=None, **kwargs):
        tmp_sw_port = ofctl.get_port_stats(dp, self.waiters, port)
        sw_id = list(tmp_sw_port.keys())[0]
        return tmp_sw_port[sw_id][0]
        #return ofctl.get_port_stats(dp, self.waiters, None)

    @monitor_method
    def get_sw_ports_details(self, req, dp, ofctl, **kwargs):
        return ofctl.get_port_desc(dp, self.waiters, None)

    @monitor_method
    def get_sw_port_details(self, req, dp, ofctl, port, **kwargs):
        return ofctl.get_port_desc(dp, self.waiters, port)


class RestMonitorApi(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(RestMonitorApi, self).__init__(*args, **kwargs)
        self.dpset = kwargs['dpset']
        wsgi = kwargs['wsgi']
        self.waiters = {}
        self.data = {}
        self.data['dpset'] = self.dpset
        self.data['waiters'] = self.waiters
        mapper = wsgi.mapper

        wsgi.registory['MonitorController'] = self.data
        # BASE endpoint URL
        path = '/monitor'

        # GET /monitor/switches - list all switches
        uri = path + '/switches'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_switches',
                       conditions=dict(method=['GET']))

        # GET /monitor/switch/detail/<dpid> - summary details of switch 
        uri = path + '/switch/{dpid}/details'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_sw_details',
                       conditions=dict(method=['GET']))

        # GET /monitor/switch/flows/<dpid> - aggregate flows stats of switch
        uri = path + '/switch/{dpid}/flows'
        mapper.connect('monitor', uri,
                       controller=MonitorController,
                       action='get_sw_flows',
                       conditions=dict(method=['GET', 'POST']))

        # GET /stats/port/<dpid> - all ports stats of switchi
        uri = path + '/switch/{dpid}/ports'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_sw_ports',
                       conditions=dict(method=['GET']))
        
        # GET /stats/port/<dpid>/<port> - single ports stats of switch
        uri = path + '/switch/{dpid}/port/{port}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_sw_port',
                       conditions=dict(method=['GET']))

        # GET /stats/portdesc/<dpid>[/<port_no>] - port details of switch
        uri = path + '/switch/{dpid}/portdetails'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_sw_ports_details',
                       conditions=dict(method=['GET']))
        uri = path + '/switch/{dpid}/portdetails/{port}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_sw_port_details',
                       conditions=dict(method=['GET']))

       
    @set_ev_cls([ofp_event.EventOFPStatsReply,
                 ofp_event.EventOFPDescStatsReply,
                 ofp_event.EventOFPFlowStatsReply,
                 ofp_event.EventOFPAggregateStatsReply,
                 ofp_event.EventOFPPortStatsReply,
                 ofp_event.EventOFPPortDescStatsReply
                 ], MAIN_DISPATCHER)
    def stats_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        flags = dp.ofproto.OFPMPF_REPLY_MORE

        if msg.flags & flags:
            return
        del self.waiters[dp.id][msg.xid]
        lock.set()
