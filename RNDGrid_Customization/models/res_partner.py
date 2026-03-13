# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_lab = fields.Boolean(string='Is Lab', default=False, help="Check this box if this contact is a testing Lab.", Tracking=True)
    
    rndgrid_segment = fields.Selection([
        ('academia', 'Academia'),
        ('startup', 'Startup'),
        ('industry', 'Industry')
    ], string='User Type', help="Segment used for specific pricing rules.", Tracking=True)

    lab_instrument_ids = fields.One2many(
        'rndgrid.lab.instrument', 'lab_id', 
        string='Lab Instruments',
        help="Instruments available at this lab."
    )
    institute_name = fields.Char(string="Institute Name", Tracking=True)
    is_expert = fields.Boolean(string='Is Expert', default=False, help="Check this box if this contact is an Expert.", Tracking=True)
    is_startup = fields.Boolean(string='Is Startup', default=False, help="Check this box if this contact is a Startup.", Tracking=True)

    # Startup Fields
    founded_year = fields.Char(string='Founded Year', Tracking=True)
    industry_work_area = fields.Char(string='Industry Work Area', Tracking=True)
    startup_overview = fields.Text(string='Startup Overview description', Tracking=True)
    target_market_segment = fields.Char(string='Target Market / Customer Segment', Tracking=True)
    awards_recognition = fields.Text(string='Awards or Recognition', Tracking=True)
    patents_filed = fields.Integer(string='Patents Filed', Tracking=True)
    patents_granted = fields.Integer(string='Patents Granted', Tracking=True)
    patent_detail = fields.Text(string='Patent Detail', Tracking=True)

    # Expert Fields
    linkedin_url = fields.Char(string='Website/ LinkedIn URL', Tracking=True)
    google_scholar_url = fields.Char(string='Google Scholar / ResearchGate URL', Tracking=True)
    highest_degree = fields.Char(string='Highest Degree', Tracking=True)
    field_of_research = fields.Char(string='Field of Research', Tracking=True)
    current_affiliation = fields.Char(string='Current Affiliation', Tracking=True)
    current_position = fields.Char(string='Current Position', Tracking=True)
    research_experience_years = fields.Integer(string='Research Experience (Years)', Tracking=True)
    total_publications = fields.Integer(string='Total Publications', Tracking=True)
    total_patents_ip = fields.Integer(string='Total Patents/IP', Tracking=True)
    services_provided = fields.Char(string='Services You Can Provide', Tracking=True)
    other_services_expert = fields.Char(string='Other Service (Optional)', Tracking=True)
