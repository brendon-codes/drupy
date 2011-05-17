from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from drupy.base import utils
from drupy.plugins.node.models import Node


def test(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('Node Test Successful')


def admin_content(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('admin_content')


def overview(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('overview')


def configure(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('configure')


def configure_rebuild_confirm(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('configure_rebuild_confirm')


def overview_types(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('overview_types')


def types_list(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('types_list')


def type_form(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('type_form')


def page_default(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('page_default')


def add_page(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('add_page')


def feed(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('feed')


def add(request, node_id):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('add')


def type_form(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('type_form')


def edit(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('edit')


def type_delete_confirm(request):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('type_delete_confirm')


def page_view(request, node_id):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('page_view')


def view(request, node_id):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('view')


def page_edit(request, node_id):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('page_edit')


def delete_confirm(request, node_id):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('delete_confirm')


def revision_overview(request, node_id):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('revision_overview')


def revision_show(request, node_id, rev_id):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    node = load({'nid':node_id}, rev_id)
    return show(request, node);


def load(nid, vid=None, reset=False):
    """
    Load a node object from the database.
    
    @param nid Int
       The node ID.
    @param vid Int
        The revision ID.
    @param reset Bool
        Whether to reset the internal node_load cache.
    @return
        A fully-populated node object.
    """
    vid = ({'vid':vid} if vid is not None else None)
    node = load_multiple((nid,), vid, reset)
    return (node[nid] if node else False);


def load_multiple(nids=None, conditions=None, reset=False):
    """
    Load node objects from the database.
    
    This function should be used whenever you need to load more
    than one node from the database. Nodes are loaded into memory and
    will not require database access if loaded again during the same
    page request.
    
    @param nids Tuple
        An array of node IDs.
    @param conditions Tuple
        An array of conditions on the {node} table in the
        form 'field' : 'value'.
    @param $reset
        Whether to reset the internal node_load cache.
    @return
        An array of node objects indexed by nid.
    """
    if nids is None:
      nids = tuple()
    if conditions is None:
      conditions = {}
    load_multiple.node_cache = []
    if (reset):
      load_multiple.node_cache = []
    nodes = []
    # Create a new variable which is either a prepared version of the $nids
    # array for later comparison with the node cache, or FALSE if no $nids were
    # passed. The $nids array is reduced as items are loaded from cache, and we
    # need to know if it's empty for this reason to avoid querying the database
    # when all requested nodes are loaded from cache.
    if len(nids) > 0:
        passed_nids = utils.array_flip(nids)
    else:
        passed_nids = False
    # Revisions are not statically cached, and require a different query to
    # other conditions, so separate vid into its own variable.
    if conditions.has_key('vid'):
        vid = conditions['vid']
        del(conditions['vid'])
    else:
        vid = False
    # Load any available nodes from the internal cache.
    if len(load_multiple.node_cache) > 0 and not vid:
        if (len(nids) > 0):
            nodes.append( utils.array_intersect_key(node_cache, passed_nids))
            # If any nodes were loaded, remove them from the $nids still to load.
            nids = utils.array_keys(utils.array_diff_key(passed_nids, nodes))
        # If loading nodes only by conditions, fetch all available nodes from
        # the cache. Nodes which don't match are removed later.
        elif (conditions is not None):
            nodes = node_cache
    # Exclude any nodes loaded from cache if they don't match $conditions.
    # This ensures the same behavior whether loading from memory or database.
    if conditions is not None:
      for node in nodes:
        node_values = node
        if utils.array_diff_assoc(conditions, node_values):
          del(nodes[node.nid])
    # Load any remaining nodes from the database. This is the case if there are
    # any $nids left to load, if loading a revision, or if $conditions was
    # passed without $nids.
    if len(nids) > 0 or vid or (conditions and not passed_nids):
        # The query being generated here:
        #
        #  SELECT 
        #    r.nid AS nid,
        #    r.vid AS vid,
        #    n.type AS type,
        #    n.language AS language,
        #    r.title AS title, r.uid AS uid,
        #    n.status AS status
        #    n.created AS created,
        #    n.changed AS changed,
        #    n.comment AS comment,
        #    n.promote AS promote,
        #    n.moderate AS moderate,
        #    n.sticky AS sticky,
        #    n.tnid AS tnid,
        #    n.translate AS translate,
        #    r.timestamp AS revision_timestamp,
        #    r.body AS body,
        #    r.teaser AS teaser,
        #    r.log AS log,
        #    r.timestamp AS timestamp,
        #    r.format AS format, 
        #    u.name AS name,
        #    u.picture AS picture,
        #    u.data AS data
        #  FROM node AS n
        #  INNER JOIN node_revision AS r ON r.vid = n.vid
        #  INNER JOIN users AS u ON u.uid = n.uid
        #  WHERE  (n.nid IN (1,2,3,4,5) 
        #
        query_args = {}
        if len(nids) > 0:
            query_args['id__in'] = nids
        if vid:
            query_args['revision__id'] = vid
        for k,v in conditions.items():
            query_args[field] = value
        found_query_nodes = True
        try:
            queried_nodes = Node.objects.filter(**query_args)
        except Node.DoesNotExist:
            found_query_nodes = False
    # Pass all nodes loaded from the database through the node type specific
    # callbacks and hook_nodeapi_load(), then add them to the internal cache.
    if (found_query_nodes):
        # Create an array of nodes for each content type and pass this to the
        # node type specific callback.
        typed_nodes = {}
        for node in queried_nodes:
            if not typed_nodes.has_key(node.node_type):
                typed_nodes[node.node_type] = {}
            typed_nodes[node.node_type][node.id] = node;
        # Call node type specific callbacks on each typed array of nodes.
        for node_type,nodes_of_type in typed_nodes.items():
            if hook(node_type, 'load'):
                function = get_types('base', node_type) + '_load'
                function(nodes_of_type);
        # Call hook_nodeapi_load(), pass the node types so modules can return early
        # if not acting on types in the array.
        for plugin in lib_plugin.implements('nodeapi_load'):
            function = getattr(plugin, 'nodeapi_load')
            function(queried_nodes, utils.array_keys(typed_nodes))
        nodes += queried_nodes
        # Add nodes to the cache if we're not loading a revision.
        if not vid:
            node_cache += queried_nodes
    # Ensure that the returned array is ordered the same as the original $nids
    # array if this was passed in and remove any invalid nids.
    if passed_nids:
      # Remove any invalid nids from the array.
      passed_nids = utils.array_intersect_key(passed_nids, nodes)
      for node in nodes:
        passed_nids[node.id] = node
      nodes = passed_nids
    return nodes



def show(request, node):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('show')


def revision_revert_confirm(request, node_id, rev_id):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('revision_revert_confirm`')


def revision_delete_confirm(request, node_id, rev_id):
    """
    Menu Callback
      
    @param request
    @return HttpResponse
    """
    return HttpResponse('revision_delete_confirm')

