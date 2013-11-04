from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
import sys

def prep_views(chosen_backend, config):  
    
    #Reference views
    config.add_route('reference', 
                     '/reference/{identifier}/overview', 
                     view=lambda request: chosen_backend.response_wrapper('reference')(
                                getattr(chosen_backend, 'reference')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('reference'))
    
    config.add_route('reference_list', 
                     '/reference_list', 
                     view=lambda request: chosen_backend.response_wrapper('reference_list')(
                                getattr(chosen_backend, 'reference_list')(
                                        None if 'reference_ids' not in request.json_body else request.json_body['reference_ids']), request), 
                     renderer=chosen_backend.get_renderer('reference_list'))
    
    #Bioent views
    config.add_route('bioentity_list', 
                     '/bioentity_list', 
                     view=lambda request: chosen_backend.response_wrapper('bioentity_list')(
                                getattr(chosen_backend, 'bioentity_list')(
                                        None if 'bioent_ids' not in request.json_body else request.json_body['bioent_ids']), request),
                     renderer=chosen_backend.get_renderer('bioentity_list'))

    #Locus views
    config.add_route('locus', 
                     '/locus/{identifier}/overview', 
                     view=lambda request: chosen_backend.response_wrapper('locus')(
                                getattr(chosen_backend, 'locus')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('locus'))
    
    config.add_route('locustabs', 
                     '/locus/{identifier}/tabs', 
                     view=lambda request: chosen_backend.response_wrapper('locustabs')(
                                getattr(chosen_backend, 'locustabs')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('locustabs'))
    
    #Biocon views
    config.add_route('bioconcept_list', 
                     '/bioconcept_list', 
                     view=lambda request: chosen_backend.response_wrapper('bioentity_list')(
                                getattr(chosen_backend, 'bioentity_list')(
                                       None if 'biocon_ids' not in request.json_body else request.json_body['biocon_ids']), request), 
                     renderer=chosen_backend.get_renderer('bioentity_list')) 
    
    #Go views
    config.add_route('go', 
                     '/go/{identifier}/overview', 
                     view=lambda request: chosen_backend.response_wrapper('go')(
                                getattr(chosen_backend, 'go')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('go'))
    
    config.add_route('go_ontology', 
                     '/go/{identifier}/ontology', 
                     view=lambda request: chosen_backend.response_wrapper('go_ontology')(
                                getattr(chosen_backend, 'go_ontology')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('go_ontology'))
    
    config.add_route('go_overview', 
                     '/locus/{identifier}/go_overview', 
                     view=lambda request: chosen_backend.response_wrapper('go_overview')(
                                getattr(chosen_backend, 'go_overview')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('go_overview'))
    
    config.add_route('go_bioent_details', 
                     '/locus/{identifier}/go_details', 
                     view=lambda request: chosen_backend.response_wrapper('go_details')(
                                getattr(chosen_backend, 'go_details')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('go_details'))
    
    config.add_route('go_biocon_details', 
                     '/go/{identifier}/locus_details', 
                     view=lambda request: chosen_backend.response_wrapper('go_details')(
                                getattr(chosen_backend, 'go_details')(
                                        go_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('go_details'))
    
    config.add_route('go_enrichment', 
                     '/go_enrichment', 
                     view=lambda request: chosen_backend.response_wrapper('go_enrichment')(
                                getattr(chosen_backend, 'go_enrichment')(
                                       None if 'bioent_ids' not in request.json_body else request.json_body['bioent_ids']), request),
                     renderer=chosen_backend.get_renderer('go_enrichment'))

    #Phenotype views
    config.add_route('phenotype', 
                     '/phenotype/{identifier}/overview', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype')(
                                getattr(chosen_backend, 'phenotype')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('phenotype'))   

    config.add_route('phenotype_ontology', 
                     '/phenotype/{identifier}/ontology', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype_ontology')(
                                getattr(chosen_backend, 'phenotype_ontology')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('phenotype_ontology'))
        
    config.add_route('phenotype_overview', 
                     '/locus/{identifier}/phenotype_overview', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype_overview')(
                                getattr(chosen_backend, 'phenotype_overview')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('phenotype_overview'))
    
    config.add_route('phenotype_bioent_details', 
                     '/locus/{identifier}/phenotype_details', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype_details')(
                                getattr(chosen_backend, 'phenotype_details')(
                                        locus_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('phenotype_details'))
    
    config.add_route('phenotype_biocon_details', 
                     '/phenotype/{identifier}/locus_details', 
                     view=lambda request: chosen_backend.response_wrapper('phenotype_details')(
                                getattr(chosen_backend, 'phenotype_details')(
                                        phenotype_identifier=None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('phenotype_details')) 
    
    #Interaction views
    config.add_route('interaction_overview', 
                     '/locus/{identifier}/interaction_overview', 
                     view=lambda request: chosen_backend.response_wrapper('interaction_overview')(
                                getattr(chosen_backend, 'interaction_overview')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request),
                     renderer=chosen_backend.get_renderer('interaction_overview'))
    
    config.add_route('interaction_details', 
                     '/locus/{identifier}/interaction_details', 
                     view=lambda request: chosen_backend.response_wrapper('interaction_details')(
                                getattr(chosen_backend, 'interaction_details')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('interaction_overview'))
    
    config.add_route('interaction_graph', 
                     '/locus/{identifier}/interaction_graph', 
                     view=lambda request: chosen_backend.response_wrapper('interaction_graph')(
                                getattr(chosen_backend, 'interaction_graph')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('interaction_graph'))
    
    config.add_route('interaction_resources', 
                     '/locus/{identifier}/interaction_resources', 
                     view=lambda request: chosen_backend.response_wrapper('interaction_resources')(
                                getattr(chosen_backend, 'interaction_resources')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('interaction_resources'))
    
    #Regulation views
    config.add_route('regulation_overview', 
                     '/locus/{identifier}/regulation_overview', 
                     view=lambda request: chosen_backend.response_wrapper('regulation_overview')(
                                getattr(chosen_backend, 'regulation_overview')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request), 
                     renderer=chosen_backend.get_renderer('regulation_overview'))
    
    config.add_route('regulation_details', 
                     '/locus/{identifier}/regulation_details', 
                     view=lambda request: chosen_backend.response_wrapper('regulation_details')(
                                getattr(chosen_backend, 'regulation_details')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request),
                     renderer=chosen_backend.get_renderer('regulation_details'))
    
    config.add_route('regulation_target_enrichment', 
                     '/locus/{identifier}/regulation_target_enrichment', 
                     view=lambda request: chosen_backend.response_wrapper('regulation_target_enrichment')(
                                getattr(chosen_backend, 'regulation_target_enrichment')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request),
                     renderer=chosen_backend.get_renderer('regulation_target_enrichment'))
    
    config.add_route('regulation_graph', 
                     '/locus/{identifier}/regulation_graph', 
                     view=lambda request: chosen_backend.response_wrapper('all_bibentries')(
                                getattr(chosen_backend, 'regulation_graph')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request),
                     renderer=chosen_backend.get_renderer('regulation_graph'))
    
    #Literature views
    config.add_route('literature_overview', 
                     '/locus/{identifier}/literature_overview', 
                     view=lambda request: chosen_backend.response_wrapper('literature_overview')(
                                getattr(chosen_backend, 'literature_overview')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request),
                     renderer=chosen_backend.get_renderer('literature_overview'))
    
    config.add_route('literature_details', 
                     '/locus/{identifier}/literature_details', 
                     view=lambda request: chosen_backend.response_wrapper('literature_details')(
                                getattr(chosen_backend, 'literature_details')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request),
                     renderer=chosen_backend.get_renderer('literature_details'))
    
    config.add_route('literature_graph', '/locus/{identifier}/literature_graph', 
                     view=lambda request: chosen_backend.response_wrapper('literature_graph')(
                                getattr(chosen_backend, 'literature_graph')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request),
                     renderer=chosen_backend.get_renderer('literature_graph'))
    
    #Protein views
    config.add_route('protein_domain_details', 
                     '/locus/{identifier}/protein_domain_details', 
                     view=lambda request: chosen_backend.response_wrapper('protein_domain_details')(
                                getattr(chosen_backend, 'protein_domain_details')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request),
                     renderer=chosen_backend.get_renderer('protein_domain_details'))
    
    config.add_route('binding_site_details', 
                     '/locus/{identifier}/binding_site_details', 
                     view=lambda request: chosen_backend.response_wrapper('binding_site_details')(
                                getattr(chosen_backend, 'binding_site_details')(
                                        None if 'identifier' not in request.matchdict else request.matchdict['identifier']), request),
                     renderer=chosen_backend.get_renderer('binding_site_details'))

def prepare_sgdbackend(**configs):
    config = Configurator()
    config.add_static_view('static', 'static', cache_max_age=3600)
        
    from sgdbackend import SGDBackend
    chosen_backend = SGDBackend(**configs)
    
    prep_views(chosen_backend, config)
    config.scan()
    return chosen_backend, config

def prepare_perfbackend(**configs):
    config = Configurator()
    config.add_static_view('static', 'static', cache_max_age=3600)
        
    from perfbackend import PerfBackend
    chosen_backend = PerfBackend(**configs)
    
    prep_views(chosen_backend, config)
    config.scan()
    return chosen_backend, config

def sgdbackend(global_config, **configs):
    """ This function returns a Pyramid WSGI application.
    """
    _, config = prepare_sgdbackend(**configs)
    return config.make_wsgi_app()

def perfbackend(global_config, **configs):
    """ This function returns a Pyramid WSGI application.
    """
    _, config = prepare_perfbackend(**configs)
    return config.make_wsgi_app()