# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class RndGridApiController(http.Controller):

    @http.route('/api/rndgrid/submit_request', type='json', auth='public', methods=['POST'], csrf=False)
    def create_lead(self, **payload):
        print("payload\n", payload)
        """
        Public endpoint to create a CRM Lead.
        Expects a JSON payload like:
        {
            "mobile": "+1234567890",
            "expected_revenue": 500,
            "description": "Optional notes from the customer",
            "tests": [
                {
                    "material_name": "Silicon Wafer",
                    "sample_type": "thin_film",
                    "is_hazardous": False,
                    "instrument_id": 1,
                    "test_ids": [5, 6]
                }
            ]
        }
        """
        mobile = payload.get('mobile', '').strip()
        print(">>>>>>>>>>>>>", mobile)
        if not mobile:
            return {'status': 'error', 'message': 'Mobile number is required'}

        # Ensure crm module is installed in environment
        if 'crm.lead' not in request.env:
            return {'status': 'error', 'message': 'CRM module is not installed'}

        # Find the partner by mobile
        partner = request.env['res.partner'].sudo().search([('phone', 'ilike', mobile)], limit=1)
        print("partner", partner)

        if not partner:
            return {'status': 'error', 'message': f'No partner found for mobile: {mobile}'}

        # Build the lines for 'crm.lead.rndgrid.test'
        test_lines = []
        for test in payload.get('tests', []):
            test_lines.append((0, 0, {
                'rndgrid_material_name': test.get('material_name'),
                'rndgrid_sample_type': test.get('sample_type'),
                'rndgrid_is_hazardous': test.get('is_hazardous', False),
                'instrument_id': test.get('instrument_id'),
                'test_ids': [(6, 0, test.get('test_ids', []))]
            }))

        # Create the lead
        lead_vals = {
            'name': f'Request from {partner.name}',
            'partner_id': partner.id,
            'expected_revenue': payload.get('expected_revenue', 0.0),
            'description': payload.get('description', ''),
        }

        # Only add tests if the sales_and_crm_customization module is installed (fields exist)
        if 'rndgrid_test_line_ids' in request.env['crm.lead']._fields:
            lead_vals['rndgrid_test_line_ids'] = test_lines

        try:
            lead = request.env['crm.lead'].sudo().create(lead_vals)
            return {
                'status': 'success',
                'lead_id': lead.id,
                'message': 'Lead created successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/rndgrid/instruments', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_instruments(self):
        """
        Public endpoint to get all instruments and their associated tests.
        Returns a JSON array of instruments with 'tests' nested inside.
        """
        try:
            instruments = request.env['rndgrid.instrument'].sudo().search([])
            data = []
            
            for inst in instruments:
                tests = []
                for test in inst.test_ids:
                    tests.append({
                        'id': test.id,
                        'name': test.name
                    })
                
                data.append({
                    'id': inst.id,
                    'name': inst.name,
                    'tests': tests
                })

            return request.make_response(
                json.dumps({'status': 'success', 'data': data}),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/rndgrid/get/user', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_partners(self, **kwargs):
        """
        Public endpoint to get a res.partner object by phone number.
        """
        phone = kwargs.get('mobile').strip()
        if not phone:
            return request.make_response(
                json.dumps({'status': 'error', 'message': 'Phone parameter is required'}),
                headers=[('Content-Type', 'application/json')],
                status=400
            )
            
        try:
            partner = request.env['res.partner'].sudo().search([('phone', 'ilike', phone)], limit=1)
            
            if not partner:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Partner not found'}),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )
            
            data = {
                'id': partner.id,
                'name': partner.name,
                'user_type': partner.rndgrid_segment,
                'email': partner.email,
                'phone': partner.phone,
                'gst_no': partner.vat,
                'zip': partner.zip,
                'city': partner.city,
                'state': partner.state_id.name if partner.state_id else None,
                'street': partner.street,
            }

            return request.make_response(
                json.dumps({'status': 'success', 'data': data}),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/rndgrid/get/booking_history', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_booking_history(self, **kwargs):
        """
        Public endpoint to get booking history (crm.lead) for a given mobile number.
        """
        mobile = kwargs.get('mobile')
        if mobile:
            mobile = mobile.strip()
        if not mobile:
            return request.make_response(
                json.dumps({'status': 'error', 'message': 'Mobile parameter is required'}),
                headers=[('Content-Type', 'application/json')],
                status=400
            )

        try:
            partner = request.env['res.partner'].sudo().search([('phone', 'ilike', mobile)], limit=1)
            
            if not partner:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Partner not found'}),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            leads = request.env['crm.lead'].sudo().search([('partner_id', '=', partner.id)])
            data = []
            
            has_test_lines = 'rndgrid_test_line_ids' in request.env['crm.lead']._fields

            for lead in leads:
                lead_data = {
                    'id': lead.id,
                    'name': lead.name,
                    'expected_revenue': lead.expected_revenue,
                    'description': lead.description,
                    'stage': lead.stage_id.name if lead.stage_id else None,
                    'tests': []
                }
                
                if has_test_lines:
                    for line in lead.rndgrid_test_line_ids:
                        test_data = {
                            'id': line.id,
                            'instrument_id': line.instrument_id.id if line.instrument_id else None,
                            'instrument_name': line.instrument_id.name if line.instrument_id else None,
                            'material_name': line.rndgrid_material_name,
                            'sample_type': line.rndgrid_sample_type,
                            'is_hazardous': line.rndgrid_is_hazardous,
                            'test_ids': [{'id': t.id, 'name': t.name} for t in line.test_ids]
                        }
                        lead_data['tests'].append(test_data)
                
                data.append(lead_data)

            return request.make_response(
                json.dumps({'status': 'success', 'data': data}),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/rndgrid/create/user', type='json', auth='public', methods=['POST'], csrf=False)
    def create_partner(self, **payload):
        """
        Public endpoint to create or update a res.partner object based on phone number.
        """
        phone = payload.get('phone')
        if phone:
            phone = phone.strip()
        
        # Determine if we have a name (required only for creation, but good to have)
        name = payload.get('name')
        
        partner_vals = {}
        if name:
            partner_vals['name'] = name
        if 'user_type' in payload:
            partner_vals['rndgrid_segment'] = payload.get('user_type')
        if 'email' in payload:
            partner_vals['email'] = payload.get('email')
        if phone:
            partner_vals['phone'] = phone
        if 'gst_no' in payload:
            partner_vals['vat'] = payload.get('gst_no')
        if 'zip' in payload:
            partner_vals['zip'] = payload.get('zip')
        if 'city' in payload:
            partner_vals['city'] = payload.get('city')
        if 'street' in payload:
            partner_vals['street'] = payload.get('street')
        
        state_name = payload.get('state')
        if state_name:
            state = request.env['res.country.state'].sudo().search([
                '|', 
                ('name', 'ilike', state_name), 
                ('code', '=ilike', state_name)
            ], limit=1)
            if state:
                partner_vals['state_id'] = state.id
                
        try:
            partner = False
            action_msg = ''
            
            # If phone is provided, search if partner exists
            if phone:
                partner = request.env['res.partner'].sudo().search([('phone', 'ilike', phone)], limit=1)
            
            if partner:
                # Update existing partner
                # Remove empty keys so we don't overwrite existing good data with None
                update_vals = {k: v for k, v in partner_vals.items() if v is not None}
                partner.sudo().write(update_vals)
                action_msg = 'Partner updated successfully'
            else:
                # Create new partner
                if not name:
                    return {'status': 'error', 'message': 'Name is required to create a new partner'}
                partner = request.env['res.partner'].sudo().create(partner_vals)
                action_msg = 'Partner created successfully'
            
            document_url = payload.get('document_url')
            if document_url:
                # Create a URL attachment
                request.env['ir.attachment'].sudo().create({
                    'name': 'Customer Document (S3)',
                    'type': 'url',
                    'url': document_url,
                    'res_model': 'res.partner',
                    'res_id': partner.id
                })
                # Post a message to chatter with the link
                msg = f"Document uploaded via API: <a href='{document_url}' target='_blank'>View Document</a>"
                partner.sudo().message_post(body=msg)
                
            return {
                'status': 'success',
                'partner_id': partner.id,
                'message': action_msg
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/rndgrid/create/expert', type='json', auth='public', methods=['POST'], csrf=False)
    def create_expert(self, **payload):
        """
        Public endpoint to create a new res.partner object as an Expert.
        """
        name = payload.get('name')
        if not name:
            return {'status': 'error', 'message': 'Name is required'}
            
        expert_vals = {
            'name': name,
            'is_expert': True,
            'email': payload.get('email'),
            'phone': payload.get('phone'),
            'city': payload.get('city'),
            'linkedin_url': payload.get('linkedin_url'),
            'google_scholar_url': payload.get('google_scholar_url'),
            'highest_degree': payload.get('highest_degree'),
            'field_of_research': payload.get('field_of_research'),
            'current_affiliation': payload.get('current_affiliation'),
            'current_position': payload.get('current_position'),
            'services_provided': payload.get('services_provided'),
            'other_services_expert': payload.get('other_services_expert'),
        }

        # Safe integer parsing
        if payload.get('research_experience_years'):
            try: expert_vals['research_experience_years'] = int(payload.get('research_experience_years'))
            except: pass
        if payload.get('total_publications'):
            try: expert_vals['total_publications'] = int(payload.get('total_publications'))
            except: pass
        if payload.get('total_patents_ip'):
            try: expert_vals['total_patents_ip'] = int(payload.get('total_patents_ip'))
            except: pass

        try:
            partner = request.env['res.partner'].sudo().create(expert_vals)
            
            document_url = payload.get('document_url')
            if document_url:
                request.env['ir.attachment'].sudo().create({
                    'name': 'Expert Document (S3)',
                    'type': 'url',
                    'url': document_url,
                    'res_model': 'res.partner',
                    'res_id': partner.id
                })
                partner.sudo().message_post(body=f"Document uploaded via API: <a href='{document_url}' target='_blank'>View Document</a>")
                
            return {
                'status': 'success',
                'partner_id': partner.id,
                'message': 'Expert created successfully'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/rndgrid/create/startup', type='json', auth='public', methods=['POST'], csrf=False)
    def create_startup(self, **payload):
        """
        Public endpoint to create a new Startup Company and link multiple founding contacts.
        """
        startup_name = payload.get('startup_name')
        founded_year = payload.get('founded_year')
        founders = payload.get('founders', [])

        if not startup_name:
            return {'status': 'error', 'message': 'startup_name is mandatory.'}
            
        if not founders or not isinstance(founders, list):
            return {'status': 'error', 'message': 'A list of founders is required.'}

        try:
            # Duplication Check logic
            # Search if any of the provided founder emails already exist for this founding year
            for founder in founders:
                founder_email = founder.get('email')
                if not founder_email:
                    continue
                    
                existing_email_partners = request.env['res.partner'].sudo().search([('email', '=', founder_email)])
                for p in existing_email_partners:
                    # Check if the partner or its parent company has the exact same founding year
                    check_company = p.parent_id if p.parent_id else p
                    if check_company.founded_year == founded_year:
                        return {
                            'status': 'error', 
                            'message': f"Duplicate Error: A startup with founding year {founded_year} and founder email {founder_email} already exists."
                        }

            # Create Startup Company
            company_vals = {
                'name': startup_name,
                'is_company': True,
                'is_startup': True,
                'founded_year': founded_year,
                'industry_work_area': payload.get('industry_work_area'),
                'startup_overview': payload.get('startup_overview'),
                'target_market_segment': payload.get('target_market_segment'),
                'awards_recognition': payload.get('awards_recognition'),
                'patent_detail': payload.get('patent_detail'),
            }

            if payload.get('patents_filed'):
                try: company_vals['patents_filed'] = int(payload.get('patents_filed'))
                except: pass
            if payload.get('patents_granted'):
                try: company_vals['patents_granted'] = int(payload.get('patents_granted'))
                except: pass

            company = request.env['res.partner'].sudo().create(company_vals)

            # Create Founder Contacts Linked to the Company
            founder_ids = []
            for founder in founders:
                founder_vals = {
                    'name': founder.get('name', 'Unknown Founder'),
                    'is_company': False,
                    'type': 'contact',
                    'parent_id': company.id,
                    'email': founder.get('email'),
                    'phone': founder.get('phone'),
                    'comment': founder.get('intro'),
                }
                f_record = request.env['res.partner'].sudo().create(founder_vals)
                founder_ids.append(f_record.id)

            # Process Document URL
            document_url = payload.get('document_url')
            if document_url:
                request.env['ir.attachment'].sudo().create({
                    'name': 'Startup Document (S3)',
                    'type': 'url',
                    'url': document_url,
                    'res_model': 'res.partner',
                    'res_id': company.id
                })
                company.sudo().message_post(body=f"Document uploaded via API: <a href='{document_url}' target='_blank'>View Document</a>")

            return {
                'status': 'success',
                'company_id': company.id,
                'founder_ids': founder_ids,
                'message': 'Startup and Founders created successfully'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
