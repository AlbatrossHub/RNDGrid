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
        Public endpoint to create a new res.partner object.
        """
        name = payload.get('name')
        if not name:
            return {'status': 'error', 'message': 'Name is required'}
            
        partner_vals = {
            'name': name,
            'rndgrid_segment': payload.get('user_type'),
            'email': payload.get('email'),
            'phone': payload.get('phone'),
            'vat': payload.get('gst_no'),
            'zip': payload.get('zip'),
            'city': payload.get('city'),
            'street': payload.get('street'),
        }
        
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
            partner = request.env['res.partner'].sudo().create(partner_vals)
            
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
                'message': 'Partner created successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
