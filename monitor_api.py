import logging
import json
import ast

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

        # Get lib/ofctl_* module
        try:
            ofctl = supported_ofctl.get(dp.ofproto.OFP_VERSION)
        except KeyError:
            LOG.exception('Unsupported OF version: %s',
                          dp.ofproto.OFP_VERSION)
            return Response(status=501)

        # Invoke StatsController method
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

    def get_dpids(self, req, **_kwargs):
        dps = list(self.dpset.dps.keys())
        body = json.dumps(dps)
        return Response(content_type='application/json', body=body)

    @monitor_method
    def get_sw_details(self, req, dp, ofctl, **kwargs):
        tmp_sw_details = ofctl.get_desc_stats(dp, self.waiters)
        sw_id = list(tmp_sw_details.keys())[0]
        return tmp_sw_details[sw_id]

    @monitor_method
    def get_sw_flow_details(self, req, dp, ofctl, **kwargs):
        flow = req.json if req.body else {}
        tmp_flow_details = ofctl.get_flow_desc(dp, self.waiters, flow)
        sw_id = list(tmp_flow_details.keys())[0]
        #return tmp_flow_details[sw_id]
        return ofctl.get_flow_desc(dp, self.waiters, flow)

    @monitor_method
    def get_sw_flow(self, req, dp, ofctl, **kwargs):
        flow = req.json if req.body else {}
        tmp_flows = ofctl.get_flow_stats(dp, self.waiters, flow)
        sw_flows = sw_id = list(tmp_flows.keys())[0]
        return tmp_flows[sw_flows][0]

        #return ofctl.get_flow_stats(dp, self.waiters, flow)

    @monitor_method
    def get_aggregate_flow_stats(self, req, dp, ofctl, **kwargs):
        flow = req.json if req.body else {}
        return ofctl.get_aggregate_flow_stats(dp, self.waiters, flow)

    @monitor_method
    def get_table_stats(self, req, dp, ofctl, **kwargs):
        return ofctl.get_table_stats(dp, self.waiters)

    @monitor_method
    def get_port_stats(self, req, dp, ofctl, port=None, **kwargs):
        if port == "ALL":
            port = None
        tmp_port_stats = ofctl.get_port_stats(dp, self.waiters, port)
        #print(type(tmp_port_stats))
        #print(tmp_port_stats['1'][0])
        tmp_sw_port = ofctl.get_port_stats(dp, self.waiters, port)
        sw_id = list(tmp_sw_port.keys())[0]
        return tmp_sw_port[sw_id][0]
        #try:
        #    return tmp_port_stats['1'][0]
        #except IndexError:
        #    return {port: 'no data'}

        #return ofctl.get_port_stats(dp, self.waiters, port)

    @monitor_method
    def get_ports_stats(self, req, dp, ofctl, port=None, **kwargs):
        #if port == "ALL":
        #    port = None
        #tmp_port_stats = ofctl.get_port_stats(dp, self.waiters, port)
        #print(type(tmp_port_stats))
        #print(tmp_port_stats['1'][0])
        #tmp_sw_port = ofctl.get_port_stats(dp, self.waiters, port)
        #sw_id = list(tmp_sw_port.keys())[0]
        #return tmp_sw_port[sw_id][0]
        #try:
        #    return tmp_port_stats['1'][0]
        #except IndexError:
        #    return {port: 'no data'}

        return ofctl.get_port_stats(dp, self.waiters, None)

    @monitor_method
    def get_port_desc(self, req, dp, ofctl, port_no=None, **kwargs):
        tmp_port_detail = ofctl.get_port_desc(dp, self.waiters, port_no)

        #return ofctl.get_port_desc(dp, self.waiters, port_no)

    @monitor_method
    def get_queue_stats(self, req, dp, ofctl,
                        port=None, queue_id=None, **kwargs):
        if port == "ALL":
            port = None

        if queue_id == "ALL":
            queue_id = None

        return ofctl.get_queue_stats(dp, self.waiters, port, queue_id)

    @monitor_method
    def get_queue_config(self, req, dp, ofctl, port=None, **kwargs):
        if port == "ALL":
            port = None

        return ofctl.get_queue_config(dp, self.waiters, port)

    @monitor_method
    def get_queue_desc(self, req, dp, ofctl,
                       port=None, queue=None, **_kwargs):
        if port == "ALL":
            port = None

        if queue == "ALL":
            queue = None

        return ofctl.get_queue_desc(dp, self.waiters, port, queue)

class RestStatsApi(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(RestStatsApi, self).__init__(*args, **kwargs)
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
                       controller=MonitorController, action='get_dpids',
                       conditions=dict(method=['GET']))

        # GET /monitor/details/<dpid> - summary details of switch 
        uri = path + '/details/{dpid}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_sw_details',
                       conditions=dict(method=['GET']))

        # GET /monitor/flowdetails/<dpid> - flows details of switch
        uri = path + '/flowdetails/{dpid}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_sw_flow_details',
                       conditions=dict(method=['GET', 'POST']))

        # GET /monitor/flow/<dpid> - flow of the switch
        uri = path + '/flow/{dpid}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_sw_flow',
                       conditions=dict(method=['GET', 'POST']))

        # GET /stats/aggregateflow/<dpid> - aggregate flows stats of switch
        uri = path + '/aggregateflow/{dpid}'
        mapper.connect('monitor', uri,
                       controller=MonitorController,
                       action='get_aggregate_flow_stats',
                       conditions=dict(method=['GET', 'POST']))

        # GET /stats/table/<dpid> - table of the switch
        uri = path + '/table/{dpid}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_table_stats',
                       conditions=dict(method=['GET']))

        # GET /stats/port/<dpid> - all ports stats of switchi
        uri = path + '/ports/{dpid}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_ports_stats',
                       conditions=dict(method=['GET']))
        
        # GET /stats/port/<dpid>/<port> - single ports stats of switch
        uri = path + '/port/{dpid}/{port}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_port_stats',
                       conditions=dict(method=['GET']))

        # GET /stats/portdesc/<dpid>[/<port_no>] - port details of switch
        # Note: Specification of port number is optional (OpenFlow 1.5 or later)
        uri = path + '/portdetails/{dpid}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_port_desc',
                       conditions=dict(method=['GET']))
        uri = path + '/portdetails/{dpid}/{port_no}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_port_desc',
                       conditions=dict(method=['GET']))

        # GET /stats/queue/<dpid>[/<port>[/<queue_id>]] - queues stats of switch
        # Note: Specification of port number and queue id are optional
        #       If you want to omitting the port number and setting the queue id,
        #       please specify the keyword "ALL" to the port number
        #       e.g. GET /stats/queue/1/ALL/1
        uri = path + '/queue/{dpid}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_queue_stats',
                       conditions=dict(method=['GET']))
        uri = path + '/queue/{dpid}/{port}'
        mapper.connect('stats', uri,
                       controller=MonitorController, action='get_queue_stats',
                       conditions=dict(method=['GET']))
        uri = path + '/queue/{dpid}/{port}/{queue_id}'
        mapper.connect('stats', uri,
                       controller=MonitorController, action='get_queue_stats',
                       conditions=dict(method=['GET']))

        # GET /stats/queueconfig/<dpid>[/<port>] - queues config stats of switch
        # Note: Specification of port number is optional
        uri = path + '/queueconfig/{dpid}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_queue_config',
                       conditions=dict(method=['GET']))
        uri = path + '/queueconfig/{dpid}/{port}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_queue_config',
                       conditions=dict(method=['GET']))

        # GET /stats/queuedesc/<dpid>[/<port>[/<queue_id>]] - queues details of the switch
        # Note: Specification of port number and queue id are optional
        #       If you want to omitting the port number and setting the queue id,
        #       please specify the keyword "ALL" to the port number
        #       e.g. GET /stats/queuedesc/1/ALL/1
        uri = path + '/queuedetails/{dpid}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_queue_desc',
                       conditions=dict(method=['GET']))
        uri = path + '/monitor/{dpid}/{port}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_queue_desc',
                       conditions=dict(method=['GET']))
        uri = path + '/monitor/{dpid}/{port}/{queue}'
        mapper.connect('monitor', uri,
                       controller=MonitorController, action='get_queue_desc',
                       conditions=dict(method=['GET']))

        
    @set_ev_cls([ofp_event.EventOFPStatsReply,
                 ofp_event.EventOFPDescStatsReply,
                 ofp_event.EventOFPFlowStatsReply,
                 ofp_event.EventOFPAggregateStatsReply,
                 ofp_event.EventOFPTableStatsReply,
                 ofp_event.EventOFPTableFeaturesStatsReply,
                 ofp_event.EventOFPPortStatsReply,
                 ofp_event.EventOFPQueueStatsReply,
                 ofp_event.EventOFPQueueDescStatsReply,
                 ofp_event.EventOFPMeterStatsReply,
                 ofp_event.EventOFPMeterFeaturesStatsReply,
                 ofp_event.EventOFPMeterConfigStatsReply,
                 ofp_event.EventOFPGroupStatsReply,
                 ofp_event.EventOFPGroupFeaturesStatsReply,
                 ofp_event.EventOFPGroupDescStatsReply,
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

    @set_ev_cls([ofp_event.EventOFPSwitchFeatures,
                 ofp_event.EventOFPQueueGetConfigReply,
                 ofp_event.EventOFPRoleReply,
                 ], MAIN_DISPATCHER)
    def features_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        del self.waiters[dp.id][msg.xid]
        lock.set()
