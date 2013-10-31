'''
Created on Oct 1, 2013

@author: kpaskov
'''
#locust -f backend_test/backend_locustfile.py -H http://sgd-ng1.stanford.edu/webservice
from locust import Locust, TaskSet, task

class WebsiteTasks(TaskSet):
    def on_start(self):
        pass

    # Interaction
    @task
    def interaction_overview(self):
        self.client.get("/locus/ABF1/interaction_overview")
        
    @task
    def interaction_details(self):
        self.client.get("/locus/ABF1/interaction_details")
        
    @task
    def interaction_graph(self):
        self.client.get("/locus/ABF1/interaction_graph")
        
    @task
    def interaction_resources(self):
        self.client.get("/locus/ABF1/interaction_resources")
     
    #Literature   
    @task
    def literature_overview(self):
        self.client.get("/locus/ABF1/literature_overview")
        
    @task
    def literature_details(self):
        self.client.get("/locus/ABF1/literature_details")
        
    @task
    def literature_graph(self):
        self.client.get("/locus/ABF1/literature_graph")
        
    # Regulation
    @task
    def regulation_overview(self):
        self.client.get("/locus/ABF1/regulation_overview")
        
    @task
    def regulation_details(self):
        self.client.get("/locus/ABF1/regulation_details")
        
    @task
    def regulation_graph(self):
        self.client.get("/locus/ABF1/regulation_graph")
        
    @task
    def regulation_target_enrichment(self):
        self.client.get("/locus/ABF1/regulation_target_enrichment")
        
    @task
    def protein_domain_details(self):
        self.client.get("/locus/ABF1/protein_domain_details")
        
    @task
    def binding_site_details(self):
        self.client.get("/locus/ABF1/binding_site_details")

class WebsiteUser(Locust):
    task_set = WebsiteTasks
    min_wait = 5000
    max_wait = 15000
    host = "http://sgd-ng1.stanford.edu/webservice"